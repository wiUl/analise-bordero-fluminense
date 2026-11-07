import mysql.connector
from datetime import time, timedelta
from scripts.etl.normalizacao import normalizar_espacos


def normalizar_horario(valor):
    """Converte horários de Excel, pandas e MySQL para HH:MM:SS."""
    if valor is None:
        return None

    # TIME do MySQL pode vir como datetime.time; Excel/pandas pode produzir
    # Timedelta ou Timestamp, dependendo do formato da célula.
    if isinstance(valor, time):
        return valor.replace(microsecond=0).isoformat()
    if isinstance(valor, timedelta):
        segundos = int(valor.total_seconds()) % (24 * 60 * 60)
        horas, resto = divmod(segundos, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    if hasattr(valor, "to_pydatetime"):
        valor = valor.to_pydatetime()
    if hasattr(valor, "time") and not isinstance(valor, str):
        hora = valor.time()
        return hora.replace(microsecond=0).isoformat()
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return None
        try:
            return time.fromisoformat(texto).replace(microsecond=0).isoformat()
        except ValueError:
            raise ValueError(f"Formato de horário inválido: {valor!r}") from None
    raise ValueError(f"Tipo de horário não suportado: {type(valor).__name__} ({valor!r})")

def conectar_banco(host, user, password, database):
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    return conexao


def buscar_id_referencia(cursor, tabela, coluna_id, nome):
    """Busca uma referência após normalizar espaços e acusa IDs que colidiriam."""
    nome = normalizar_espacos(nome)
    if nome is None:
        raise ValueError(f"O nome da referência em {tabela} não pode ser vazio.")

    cursor.execute(f"SELECT {coluna_id}, nome FROM {tabela}")
    registros = cursor.fetchall()
    ids_correspondentes = {
        id_registro
        for id_registro, nome_registro in registros
        if normalizar_espacos(nome_registro) == nome
    }

    if len(ids_correspondentes) > 1:
        raise ValueError(
            f"A tabela {tabela} possui IDs diferentes para o nome "
            f"normalizado {nome!r}: {sorted(ids_correspondentes)}. "
            "Corrija o cadastro antes de carregar novos dados."
        )
    if ids_correspondentes:
        return next(iter(ids_correspondentes))

    # Mantém o comportamento da collation MySQL para equivalências de caixa/acento.
    cursor.execute(
        f"SELECT {coluna_id} FROM {tabela} WHERE nome = %s LIMIT 1",
        (nome,)
    )
    resultado = cursor.fetchone()
    return resultado[0] if resultado is not None else None


def garantir_referencias_ingressos(cursor, df_ingressos):
    """Retorna mapas nome->ID e cadastra nomes ainda ausentes no banco."""
    # Relaciona cada coluna da planilha à tabela e à chave primária correspondentes.
    configuracoes = [
        ('setor', 'id_setor', 'setor'),
        ('categoria_ingresso', 'id_categoria', 'categoria_ingresso'),
        ('plano_socio', 'id_plano', 'plano_socio'),
    ]

    # Guarda um dicionário nome->ID para cada tipo de referência, na ordem acima.
    mapas = []

    for coluna_planilha, coluna_id, tabela in configuracoes:
        # Normaliza antes de deduplicar para que "Sul" e " Sul  " usem a mesma chave.
        valores = df_ingressos[coluna_planilha].map(normalizar_espacos).dropna()
        nomes_planilha = valores.drop_duplicates().tolist()

        if any(not isinstance(nome, str) for nome in nomes_planilha):
            raise ValueError(
                f"A coluna {coluna_planilha} deve conter apenas nomes textuais."
            )

        mapa = {}

        # Confere referências já existentes e bloqueia IDs distintos que colidiriam
        # após a normalização de espaços.
        cursor.execute(f"SELECT {coluna_id}, nome FROM {tabela}")
        for id_existente, nome_existente in cursor.fetchall():
            chave = normalizar_espacos(nome_existente)
            if chave is None:
                raise ValueError(
                    f"A tabela {tabela} contém um nome vazio (ID {id_existente})."
                )
            if chave in mapa and mapa[chave] != id_existente:
                raise ValueError(
                    f"A tabela {tabela} possui IDs diferentes para o nome "
                    f"normalizado {chave!r}: {mapa[chave]} e {id_existente}. "
                    "Corrija o cadastro antes de carregar novos dados."
                )
            mapa[chave] = id_existente

        for nome in nomes_planilha:
            nome = normalizar_espacos(nome)
            if nome is None:
                continue

            if nome in mapa:
                continue

            # Busca usando a comparação do MySQL, que respeita a collation
            # definida no banco (incluindo equivalências de acento e caixa).
            cursor.execute(
                f"SELECT {coluna_id} FROM {tabela} WHERE nome = %s LIMIT 1",
                (nome,)
            )
            resultado = cursor.fetchone()

            if resultado is not None:
                mapa[nome] = resultado[0]
            else:
                # Só cadastra o nome quando o MySQL não encontra equivalente.
                cursor.execute(
                    f"INSERT INTO {tabela} (nome) VALUES (%s)",
                    (nome,)
                )
                mapa[nome] = cursor.lastrowid

        # Mantém este mapa para devolvê-lo junto aos outros dois.
        mapas.append(mapa)

    # A ordem retornada corresponde a setores_dict, categorias_dict e planos_dict.
    return tuple(mapas)


def garantir_competicao(cursor, nome_competicao):

    nome_competicao = normalizar_espacos(nome_competicao)
    if nome_competicao is None:
        raise ValueError("Nome da competição não pode ser nulo ou vazio.")

    id_competicao = buscar_id_referencia(
        cursor, 'competicao', 'id_competicao', nome_competicao
    )
    if id_competicao is not None:
        return id_competicao

    cursor.execute("INSERT INTO competicao (nome) VALUES (%s)", (nome_competicao,))
    return cursor.lastrowid


def garantir_temporada(cursor, ano_temporada):

    cursor.execute("SELECT id_temporada FROM temporada where ano = %s", (ano_temporada,))

    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0]
    else:
        cursor.execute("INSERT INTO temporada (ano) VALUES (%s)", (ano_temporada,))
        id_temporada = cursor.lastrowid
        return id_temporada

def garantir_adversario(cursor, nome_adversario, e_classico, e_clube_g12):

    nome_adversario = normalizar_espacos(nome_adversario)
    if nome_adversario is None:
        raise ValueError("Nome do adversário não pode ser nulo ou vazio.")

    id_adversario = buscar_id_referencia(
        cursor, 'adversario', 'id_adversario', nome_adversario
    )

    if id_adversario is not None:
        cursor.execute(
            "SELECT e_classico, e_clube_g12 FROM adversario WHERE id_adversario = %s",
            (id_adversario,)
        )
        resultado = cursor.fetchone()
        e_classico_adversario = resultado[0]
        e_clube_g12_adversario = resultado[1]
        if e_classico != e_classico_adversario:
            raise ValueError(f"Existe uma divergência no atributo e_classico: Banco de Dados - {e_classico_adversario} / Planilha - {e_classico}")
        if e_clube_g12 != e_clube_g12_adversario:
            raise ValueError(f"Existe uma divergência no atributo e_clube_g12: Banco de Dados - {e_clube_g12_adversario} / Planilha - {e_clube_g12}")
        return id_adversario

    cursor.execute(
        'INSERT INTO adversario (nome, e_classico, e_clube_g12) VALUES (%s,%s,%s)',
        (nome_adversario, e_classico, e_clube_g12)
    )
    return cursor.lastrowid

def garantir_estadio(cursor, nome_estadio, cidade, estado, pais, capacidade):

    nome_estadio = normalizar_espacos(nome_estadio)
    cidade = normalizar_espacos(cidade)
    estado = normalizar_espacos(estado)
    pais = normalizar_espacos(pais)
    if nome_estadio is None:
        raise ValueError("Nome do estádio não pode ser nulo ou vazio.")

    id_estadio = buscar_id_referencia(
        cursor, 'estadio', 'id_estadio', nome_estadio
    )

    if id_estadio is not None:
        cursor.execute(
            "SELECT nome, cidade, estado, pais, capacidade "
            "FROM estadio WHERE id_estadio = %s",
            (id_estadio,)
        )
        resultado = cursor.fetchone()
        cidade_estadio = normalizar_espacos(resultado[1])
        estado_estadio = normalizar_espacos(resultado[2])
        pais_estadio = normalizar_espacos(resultado[3])
        capacidade_estadio = resultado[4]

        if cidade != cidade_estadio:
            raise ValueError(f"Existe uma divergência no atributo cidade: Banco de Dados - {cidade_estadio} / Planilha - {cidade}")
        if estado != estado_estadio:
            raise ValueError(f"Existe uma divergência no atributo estado: Banco de Dados - {estado_estadio} / Planilha - {estado}")
        if pais != pais_estadio:
            raise ValueError(f"Existe uma divergência no atributo pais: Banco de Dados - {pais_estadio} / Planilha - {pais}")
        if capacidade != capacidade_estadio:
            raise ValueError(f"Existe uma divergência no atributo capacidade: Banco de Dados - {capacidade_estadio} / Planilha - {capacidade}")        
        
        
        return id_estadio

    cursor.execute(
        "INSERT INTO estadio (nome, cidade, estado, pais, capacidade) "
        "VALUES (%s,%s,%s,%s,%s)",
        (nome_estadio, cidade, estado, pais, capacidade)
    )
    return cursor.lastrowid

def garantir_competicao_temporada(cursor, id_competicao, id_temporada):

    cursor.execute("SELECT id_competicao_temporada FROM competicao_temporada where id_competicao = %s and id_temporada = %s", (id_competicao, id_temporada))

    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0]
    else:
        cursor.execute("INSERT INTO competicao_temporada (id_competicao, id_temporada) VALUES (%s,%s)", (id_competicao, id_temporada))
        id_competicao_temporada = cursor.lastrowid
        return id_competicao_temporada

def garantir_partida(cursor, df_partida):

    if len(df_partida) != 1:
        raise ValueError(
            f"Esperada exatamente uma partida, mas foram encontradas {len(df_partida)}."
        )

    data = df_partida['data'].iloc[0]
    horario = df_partida['horario'].iloc[0]
    id_adversario = df_partida['adversario_id'].iloc[0]
    id_competicao_temporada = df_partida['competicao_temporada_id'].iloc[0]
    id_estadio = df_partida['estadio_id'].iloc[0]
    rodada = df_partida['rodada'].iloc[0]

    cursor.execute(
        """SELECT id_partida, horario, estadio_id, rodada FROM partida
        where data = %s and adversario_id = %s and competicao_temporada_id = %s""", (data, id_adversario, id_competicao_temporada)
        )

    resultado = cursor.fetchmany(2)

    if resultado:
        if len(resultado) > 1:
            raise ValueError("Existem duplicatas para a chave natural")

        id_partida, horario_partida, estadio_partida, rodada_partida = resultado[0]
        if normalizar_horario(horario) != normalizar_horario(horario_partida):
            raise ValueError(f"Existe uma divergência no atributo horario: Banco de Dados - {horario_partida} / Planilha - {horario}")
        if id_estadio != estadio_partida:
            raise ValueError(f"Existe uma divergência no atributo estadio_id: Banco de Dados - {estadio_partida} / Planilha - {id_estadio}")
        if rodada != rodada_partida:
            raise ValueError(f"Existe uma divergência no atributo rodada: Banco de Dados - {rodada_partida} / Planilha - {rodada}")
        
        return id_partida
    else:
        cursor.execute(
            """INSERT INTO partida (data, horario, adversario_id, competicao_temporada_id, estadio_id, rodada)
            VALUES (%s,%s,%s,%s,%s,%s)""", (data, horario, id_adversario, id_competicao_temporada, id_estadio, rodada))
        id_partida = cursor.lastrowid
        return id_partida


def verificar_estado_carga_partida(cursor, id_partida, quantidades_esperadas):
    """Classifica a carga das tabelas de dados associadas a uma partida.

    Retorna ``completa`` quando as quantidades existentes coincidem com as
    esperadas, ``vazia`` quando ainda não há registros e ``parcial`` nos
    demais casos. Os nomes das tabelas são fixos no código; os valores
    esperados vêm dos DataFrames já preparados.
    """
    tabelas = [
        'ingresso_partida',
        'despesa_partida',
        'resumo_financeiro_partida',
        'contexto_partida',
        'atributos_partida',
        'desempenho_partida'
    ]

    # Conta os registros já gravados em cada tabela-fato para esta partida.
    quantidades_existentes = {}
    for tabela in tabelas:
        cursor.execute(
            f"SELECT COUNT(*) FROM {tabela} WHERE id_partida = %s",
            (id_partida,)
        )
        quantidades_existentes[tabela] = cursor.fetchone()[0]

    # Uma carga completamente nova pode prosseguir; uma carga completa pode
    # ser ignorada; qualquer combinação diferente requer conferência manual.
    if all(quantidade == 0 for quantidade in quantidades_existentes.values()):
        estado = 'vazia'
    elif quantidades_existentes == quantidades_esperadas:
        estado = 'completa'
    else:
        estado = 'parcial'

    return estado, quantidades_existentes
def validar_dataframe(df, colunas_esperadas, coluna_id=None):
    """
    Valida um DataFrame:
    - Verifica se não está vazio.
    - Verifica se possui as colunas esperadas.
    - Verifica se a coluna de identificação não possui valores nulos.
    - Verifica se existe apenas um identificador único.
    """

    # Verificar se está vazio
    if df.empty:
        raise ValueError("O DataFrame está vazio.")

    # Verificar colunas esperadas
    colunas_faltantes = set(colunas_esperadas) - set(df.columns)

    if colunas_faltantes:
        raise ValueError(f"Colunas ausentes: {colunas_faltantes}")

    # Verificar identificador, quando informado
    if coluna_id is not None:

        if df[coluna_id].isna().any():
            raise ValueError(f"Existem valores nulos em {coluna_id}.")

        if df[coluna_id].nunique() != 1:
            raise ValueError(f"Existem múltiplos valores em {coluna_id}.")

    return True

def inserir_ingressos(cursor, df_ingressos):

    colunas_esperadas = [
        'id_partida',
        'descricao_original',
        'id_setor',
        'id_categoria',
        'id_plano',
        'preco',
        'quantidade_disponivel',
        'quantidade_devolvida',
        'quantidade_utilizada',
        'arrecadacao'
    ]
    
    validar_dataframe(df=df_ingressos, colunas_esperadas=colunas_esperadas, coluna_id='id_partida')

    id_partida = int(df_ingressos['id_partida'].iloc[0])

    cursor.execute("SELECT 1 from ingresso_partida where id_partida = (%s) LIMIT 1",(id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existe ingressos carregados para essa partida")

    sql = """ INSERT INTO ingresso_partida (
            id_partida,
            descricao_original,
            id_setor,
            id_categoria,
            id_plano,
            preco,
            quantidade_disponivel,
            quantidade_devolvida,
            quantidade_utilizada,
            arrecadacao
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    registros = list(df_ingressos.itertuples(index=False, name=None))

    cursor.executemany(sql, registros)

    return cursor.rowcount


def inserir_despesas(cursor, df_despesas):
    
    colunas_esperadas = [
        'id_partida',
        'nome',
        'valor'
    ]

    validar_dataframe(df=df_despesas,colunas_esperadas=colunas_esperadas,coluna_id='id_partida')

    id_partida = int(df_despesas['id_partida'].iloc[0])

    cursor.execute('SELECT 1 FROM despesa_partida where id_partida = %s LIMIT 1', (id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existem despesas carregadas para essa partida")

    sql = "INSERT INTO despesa_partida (id_partida, nome, valor) VALUES (%s, %s, %s)"

    registros = list(df_despesas.itertuples(index=False, name=None))

    cursor.executemany(sql, registros)

    return cursor.rowcount


def inserir_resumo(cursor, df_resumo):

    colunas_esperadas = [
        'id_partida',
        'total_disponivel',
        'total_devolvido',
        'total_utilizado',
        'arrecadacao_bruta',
        'total_despesas',
        'retencoes',
        'receita_liquida',
        'consignatarios',
        'resultado_final',
        'complemento_contabil'
    ]

    validar_dataframe(df=df_resumo,colunas_esperadas=colunas_esperadas,coluna_id='id_partida')

    id_partida = int(df_resumo['id_partida'].iloc[0])

    cursor.execute('SELECT 1 FROM resumo_financeiro_partida where id_partida = (%s)', (id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existe um resumo financeiro para essa partida")

    registros = tuple(df_resumo.iloc[0].tolist())

    cursor.execute('INSERT INTO resumo_financeiro_partida (id_partida, total_disponivel, total_devolvido, total_utilizado, arrecadacao_bruta, total_despesas, retencoes, receita_liquida, consignatarios, resultado_final, complemento_contabil) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', registros)

    return cursor.rowcount

def inserir_contexto(cursor, df_contexto):

    colunas_esperadas = [
        'id_partida',
        'feriado',
        'dias_desde_ultimo_jogo_maracana'
    ]

    validar_dataframe(df=df_contexto,colunas_esperadas=colunas_esperadas,coluna_id='id_partida')

    id_partida = int(df_contexto['id_partida'].iloc[0])

    cursor.execute('SELECT 1 FROM contexto_partida where id_partida = %s', (id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existe contexto para essa partida")

    registros = tuple(df_contexto.iloc[0].tolist())

    cursor.execute('INSERT INTO contexto_partida (id_partida, feriado, dias_desde_ultimo_jogo_maracana) VALUES (%s,%s,%s)', registros)

    return cursor.rowcount

def inserir_atributos(cursor, df_atributos):

    colunas_esperadas = [
            'id_partida',
            'importancia_partida',
            'apelo_adversario'
        ]
    
    validar_dataframe(df=df_atributos,colunas_esperadas=colunas_esperadas,coluna_id='id_partida')

    id_partida = int(df_atributos['id_partida'].iloc[0])

    cursor.execute('SELECT 1 FROM atributos_partida where id_partida = %s', (id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existem atributos para essa partida")

    registros = tuple(df_atributos.iloc[0].tolist())

    cursor.execute('INSERT INTO atributos_partida (id_partida, importancia_partida, apelo_adversario) VALUES (%s,%s,%s)', registros)

    return cursor.rowcount

def inserir_desempenho(cursor, df_desempenho):

    colunas_esperadas = [
            'id_partida',
            'posicao_fluminense',
            'pontos_fluminense',
            'vitorias_ultimos_5',
            'empates_ultimos_5',
            'derrotas_ultimos_5',
            'gols_marcados_ultimos_5',
            'gols_sofridos_ultimos_5'
        ]
    
    validar_dataframe(df=df_desempenho,colunas_esperadas=colunas_esperadas,coluna_id='id_partida')

    id_partida = int(df_desempenho['id_partida'].iloc[0])

    cursor.execute('SELECT 1 FROM desempenho_partida where id_partida = %s', (id_partida,))

    resultado = cursor.fetchone()

    if resultado:
        raise ValueError("Já existe desempenho para essa partida")

    registros = tuple(df_desempenho.iloc[0].tolist())

    cursor.execute('INSERT INTO desempenho_partida (id_partida,posicao_fluminense,pontos_fluminense,vitorias_ultimos_5,empates_ultimos_5,derrotas_ultimos_5,gols_marcados_ultimos_5,gols_sofridos_ultimos_5) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', registros)

    return cursor.rowcount

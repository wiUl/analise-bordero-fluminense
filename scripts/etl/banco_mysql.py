import mysql.connector

def conectar_banco(host, user, password, database):
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    return conexao

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
        # O MySQL pode considerar equivalentes nomes que o Python diferencia,
        # como "Socio" e "Sócio". A consulta abaixo usa a collation da tabela.
        mapa = {}

        # Ignora valores ausentes: eles não representam um nome a cadastrar.
        nomes_planilha = df_ingressos[coluna_planilha].dropna().unique()

        for nome in nomes_planilha:
            # Rejeita texto composto apenas por espaços, que não identifica uma referência.
            if isinstance(nome, str) and not nome.strip():
                raise ValueError(
                    f"Valor vazio encontrado na coluna {coluna_planilha}."
                )

            # Busca usando a comparação do MySQL, que respeita a collation
            # definida no banco (incluindo equivalências de acento e caixa).
            cursor.execute(
                f"SELECT {coluna_id} FROM {tabela} WHERE nome = %s LIMIT 1",
                (nome,)
            )
            resultado = cursor.fetchone()

            if resultado is not None:
                # Usa o texto exato da planilha como chave para que o
                # preparar_ingressos encontre o ID sem alterar a descrição.
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

    cursor.execute("SELECT id_competicao FROM competicao where nome = %s", (nome_competicao,))

    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0]
    else:
        cursor.execute("INSERT INTO competicao (nome) VALUES (%s)", (nome_competicao,))
        id_competicao = cursor.lastrowid
        return id_competicao


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

    cursor.execute("SELECT id_adversario, e_classico, e_clube_g12 FROM adversario where nome = %s", (nome_adversario,))

    resultado = cursor.fetchone()

    if resultado is not None:
        id_adversario = resultado[0]
        e_classico_adversario = resultado[1]
        e_clube_g12_adversario = resultado[2]
        if e_classico != e_classico_adversario:
            raise ValueError(f"Existe uma divergência no atributo e_classico: Banco de Dados - {e_classico_adversario} / Planilha - {e_classico}")
        if e_clube_g12 != e_clube_g12_adversario:
            raise ValueError(f"Existe uma divergência no atributo e_clube_g12: Banco de Dados - {e_clube_g12_adversario} / Planilha - {e_clube_g12}")
        return id_adversario
    else:
        cursor.execute('INSERT INTO adversario (nome, e_classico, e_clube_g12) VALUES (%s,%s,%s)', (nome_adversario, e_classico, e_clube_g12))
        id_adversario = cursor.lastrowid
        return id_adversario

def garantir_estadio(cursor, nome_estadio, cidade, estado, pais, capacidade):

    cursor.execute("SELECT id_estadio, nome, cidade, estado, pais, capacidade FROM estadio where nome = %s", (nome_estadio,))

    resultado = cursor.fetchone()

    if resultado is not None:

        id_estadio = resultado[0]
        cidade_estadio = resultado[2]
        estado_estadio = resultado[3]
        pais_estadio = resultado[4]
        capacidade_estadio = resultado[5]

        if cidade != cidade_estadio:
            raise ValueError(f"Existe uma divergência no atributo cidade: Banco de Dados - {cidade_estadio} / Planilha - {cidade}")
        if estado != estado_estadio:
            raise ValueError(f"Existe uma divergência no atributo estado: Banco de Dados - {estado_estadio} / Planilha - {estado}")
        if pais != pais_estadio:
            raise ValueError(f"Existe uma divergência no atributo pais: Banco de Dados - {pais_estadio} / Planilha - {pais}")
        if capacidade != capacidade_estadio:
            raise ValueError(f"Existe uma divergência no atributo capacidade: Banco de Dados - {capacidade_estadio} / Planilha - {capacidade}")        
        
        
        return id_estadio
    else:
        cursor.execute("INSERT INTO estadio (nome, cidade, estado, pais, capacidade) VALUES (%s,%s,%s,%s,%s)", (nome_estadio, cidade, estado, pais, capacidade))
        id_estadio = cursor.lastrowid
        return id_estadio

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
        if horario != horario_partida:
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

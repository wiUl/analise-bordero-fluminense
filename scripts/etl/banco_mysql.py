import mysql.connector

from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

seu_host = os.getenv("DB_HOST")
seu_user = os.getenv("DB_USER")
seu_password = os.getenv("DB_PASSWORD")
seu_database = os.getenv("DB_NAME")


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
        # Carrega as referências já cadastradas para evitar inserir nomes repetidos.
        cursor.execute(f"SELECT {coluna_id}, nome FROM {tabela}")
        mapa = {
            nome: identificador
            for identificador, nome in cursor.fetchall()
        }

        # Ignora valores ausentes: eles não representam um nome a cadastrar.
        nomes_planilha = df_ingressos[coluna_planilha].dropna().unique()

        for nome in nomes_planilha:
            # Rejeita texto composto apenas por espaços, que não identifica uma referência.
            if isinstance(nome, str) and not nome.strip():
                raise ValueError(
                    f"Valor vazio encontrado na coluna {coluna_planilha}."
                )

            # Cadastra apenas nomes novos e guarda o ID gerado para o mapeamento dos ingressos.
            if nome not in mapa:
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

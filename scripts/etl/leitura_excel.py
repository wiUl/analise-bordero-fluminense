
# ============================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÕES
# ============================================================

from pathlib import Path
import os

import pandas as pd
import mysql.connector
from dotenv import load_dotenv


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

seu_host = os.getenv("DB_HOST")
seu_user = os.getenv("DB_USER")
seu_password = os.getenv("DB_PASSWORD")
seu_database = os.getenv("DB_NAME")


# Caminhos do projeto
diretorio_atual = Path(__file__).resolve()
raiz_projeto = diretorio_atual.parents[2]

pasta_interim = raiz_projeto / "data" / "interim"


# ============================================================
# 2. FUNÇÕES AUXILIARES
# ============================================================

def listar_arquivos_excel(caminho):
    lista_arquivos = []

    for arquivo in caminho.glob("*.xlsx"):
        lista_arquivos.append(arquivo)

    return lista_arquivos


def listar_abas_excel(caminho):
    return pd.ExcelFile(caminho).sheet_names


def verificar_abas_excel(caminho):
    abas_esperadas = [
        'LEIA-ME',
        'PARTIDA',
        'INGRESSOS',
        'DESPESAS',
        'RESUMO',
        'CONTEXTO',
        'ATRIBUTOS',
        'DESEMPENHO'
    ]

    lista_abas = listar_abas_excel(caminho)

    verificado = all(
        aba in lista_abas
        for aba in abas_esperadas
    )

    abas_ausentes = [
        aba for aba in abas_esperadas
        if aba not in lista_abas
    ]

    return verificado, abas_ausentes


def organizar_entidades(df):
    dados = {}

    entidades = df['Entidade do modelo'].dropna().unique()

    for entidade in entidades:
        data = df[df['Entidade do modelo'] == entidade]

        data = data[['Campo do modelo', 'Valor a preencher']]
        data = data.set_index("Campo do modelo")
        data = data['Valor a preencher'].to_dict()

        dados[entidade] = data

    return dados


def conectar_banco(host, user, password, database):
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    return conexao


# ============================================================
# 3. PREPARAÇÃO DOS ARQUIVOS E CONEXÃO
# ============================================================

lista = listar_arquivos_excel(pasta_interim)

total = len(lista)

aprovado = 0
reprovado = 0

# Seleção temporária para os testes
selecionado = lista[0]

# Conexão com o banco
conexao = conectar_banco(
    host=seu_host,
    user=seu_user,
    password=seu_password,
    database=seu_database
)

cursor = conexao.cursor()


# ============================================================
# 4. TESTES DE VALIDAÇÃO DOS ARQUIVOS
# ============================================================

# Teste: verificar abas de todos os arquivos
#
# for arquivo in lista:
#     flag, listagem = verificar_abas_excel(arquivo)
#
#     if flag:
#         aprovado += 1
#         print(f"ARQUIVO: {arquivo.name}")
#         print("STATUS: APROVADO\n")
#     else:
#         reprovado += 1
#         print(f"ARQUIVO: {arquivo.name}")
#         print("STATUS: REPROVADO")
#         print(f"ABAS AUSENTES: {listagem}\n")
#
# print(f"TOTAL DE ARQUIVOS: {total}")
# print(f"APROVADOS: {aprovado}")
# print(f"REPROVADOS: {reprovado}")


# ============================================================
# 5. ETL DE INGRESSOS E DESPESAS
# ============================================================

# ------------------------------------------------------------
# 5.1. Leitura das planilhas
# ------------------------------------------------------------

df_partida = pd.read_excel(
    selecionado,
    sheet_name="PARTIDA",
    header=3
)

df_geral = pd.read_excel(
    selecionado,
    sheet_name=["INGRESSOS", "DESPESAS"],
    header=5
)

df_ingressos = df_geral["INGRESSOS"]
df_despesas = df_geral["DESPESAS"]


# ------------------------------------------------------------
# 5.2. Seleção das colunas de ingressos
# ------------------------------------------------------------

df_ingressos_carga = df_ingressos[
    [
        'descricao_original',
        'setor',
        'categoria_ingresso',
        'plano_socio',
        'preco',
        'quantidade_disponivel',
        'quantidade_devolvida',
        'quantidade_utilizada',
        'arrecadacao'
    ]
].copy()


# ------------------------------------------------------------
# 5.3. Consultas das dimensões no MySQL
# ------------------------------------------------------------

cursor.execute("SELECT id_setor, nome FROM setor")
resultado = cursor.fetchall()

setores_dict = {
    nome: id_setor
    for id_setor, nome in resultado
}


cursor.execute("SELECT id_categoria, nome FROM categoria_ingresso")
resultado_categorias = cursor.fetchall()

categorias_dict = {
    nome: id_categoria
    for id_categoria, nome in resultado_categorias
}


cursor.execute("SELECT id_plano, nome FROM plano_socio")
resultado_planos = cursor.fetchall()

planos_dict = {
    nome: id_plano
    for id_plano, nome in resultado_planos
}


# ------------------------------------------------------------
# 5.4. Mapeamento dos IDs
# ------------------------------------------------------------

df_ingressos_carga['id_setor'] = (
    df_ingressos_carga['setor'].map(setores_dict)
)

df_ingressos_carga['id_categoria'] = (
    df_ingressos_carga['categoria_ingresso'].map(categorias_dict)
)

df_ingressos_carga['id_plano'] = (
    df_ingressos_carga['plano_socio'].map(planos_dict)
)


# ------------------------------------------------------------
# 5.5. Ajuste dos tipos de dados
# ------------------------------------------------------------

df_ingressos_carga['id_setor'] = (
    df_ingressos_carga['id_setor'].astype('Int64')
)

df_ingressos_carga['id_categoria'] = (
    df_ingressos_carga['id_categoria'].astype('Int64')
)

df_ingressos_carga['id_plano'] = (
    df_ingressos_carga['id_plano'].astype('Int64')
)


# ------------------------------------------------------------
# 5.6. DataFrame final para ingresso_partida
# ------------------------------------------------------------

df_ingressos_final = df_ingressos_carga[
    [
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
].copy()


# ============================================================
# 6. TESTES E INSPEÇÃO DOS RESULTADOS
# ============================================================

# Teste: inspeção dos dados originais
#
# print(df_ingressos_carga.info())
# print(df_ingressos_carga.isna().sum())
# print(df_ingressos_carga[
#     df_ingressos_carga.isna().any(axis=1)
# ])

# Teste: valores distintos das dimensões
#
# print("\nSETORES:")
# print(df_ingressos_carga['setor'].unique())
#
# print("\nCATEGORIAS:")
# print(df_ingressos_carga['categoria_ingresso'].unique())
#
# print("\nPLANOS:")
# print(df_ingressos_carga['plano_socio'].unique())

# Teste: DataFrame final
#
# print(df_ingressos_final.info())
# print(df_ingressos_final.head())


# ============================================================
# 7. ORGANIZAÇÃO DOS DADOS DA PARTIDA
# ============================================================

# A próxima etapa será organizar os dados da aba PARTIDA.
# A função organizar_entidades() já está preparada para isso.
#
dados_partida = organizar_entidades(df_partida)

ano = dados_partida['temporada']['ano']

"""cursor.execute(
    "INSERT INTO temporada (ano) VALUES (%s)",
    (ano,)
)

conexao.commit() """

id_temporada = cursor.lastrowid

nome_competicao = dados_partida['competicao']['nome']

""" cursor.execute(
    "INSERT INTO competicao (nome) VALUES (%s)",
    (nome_competicao,)          
)

conexao.commit() """

id_competicao = cursor.lastrowid

nome_adversario = dados_partida['adversario']['nome']

""" cursor.execute(
    "INSERT INTO adversario (nome) VALUES (%s)",
    (nome_adversario,)
)

conexao.commit() """

id_adversario = cursor.lastrowid

dados_estadio = dados_partida['estadio']

""" cursor.execute(
    
    INSERT INTO estadio (nome, cidade, estado, pais, capacidade)
    VALUES (%s, %s, %s, %s, %s)
    ,
    (
        dados_estadio['nome'],
        dados_estadio['cidade'],
        dados_estadio['estado'],
        dados_estadio['pais'],
        dados_estadio['capacidade']
    )
) """

conexao.commit()

id_estadio = cursor.lastrowid

cursor.execute(
    "SELECT id_temporada FROM temporada WHERE ano = %s",
    (dados_partida['temporada']['ano'],)
)
id_temporada = cursor.fetchone()[0]

cursor.execute(
    "SELECT id_competicao FROM competicao WHERE nome = %s",
    (dados_partida['competicao']['nome'],)
)
id_competicao = cursor.fetchone()[0]


""" cursor.execute(
    
    INSERT INTO competicao_temporada (id_competicao, id_temporada)
    VALUES (%s, %s)
    ,
    (id_competicao, id_temporada)
)

conexao.commit() """

id_competicao_temporada = cursor.lastrowid

cursor.execute(
    "SELECT id_adversario FROM adversario WHERE nome = %s",
    (dados_partida['adversario']['nome'],)
)
id_adversario = cursor.fetchone()[0]

cursor.execute(
    "SELECT id_estadio FROM estadio WHERE nome = %s",
    (dados_partida['estadio']['nome'],)
)
id_estadio = cursor.fetchone()[0]

cursor.execute(
    """
    SELECT id_competicao_temporada
    FROM competicao_temporada
    WHERE id_competicao = %s AND id_temporada = %s
    """,
    (id_competicao, id_temporada)
)
id_competicao_temporada = cursor.fetchone()[0]


dados_jogo = dados_partida['partida']

data = dados_jogo['data'].date()
horario = dados_jogo['horario']
rodada = str(dados_jogo['rodada'])

""" cursor.execute(
    
    INSERT INTO partida (
        data,
        horario,
        adversario_id,
        competicao_temporada_id,
        estadio_id,
        rodada
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ,
    (
        data,
        horario,
        id_adversario,
        id_competicao_temporada,
        id_estadio,
        rodada
    )
)

conexao.commit() """

id_partida = cursor.lastrowid


cursor.execute(
    """
    SELECT id_partida
    FROM partida
    WHERE data = %s
      AND adversario_id = %s
      AND competicao_temporada_id = %s
      AND estadio_id = %s
    """,
    (
        dados_partida['partida']['data'].date(),
        id_adversario,
        id_competicao_temporada,
        id_estadio
    )
)

id_partida = cursor.fetchone()[0]


df_ingressos_final.insert(0, 'id_partida', id_partida)



# ============================================================
# 8. load dos ingressos no banco
# ============================================================

df_ingressos_mysql = df_ingressos_final.astype(object).where(
    pd.notna(df_ingressos_final),
    None
)

registros_ingressos = list(
    df_ingressos_mysql.itertuples(index=False, name=None)
)

""" 
sql_ingressos = 
    INSERT INTO ingresso_partida (
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
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)


cursor.executemany(sql_ingressos, registros_ingressos)

conexao.commit()

print(f"{cursor.rowcount} registros de ingressos inseridos.") """


# ============================================================
# 9. ORGANIZAÇÃO DAS DESPESAS DA PARTIDA
# ============================================================


df_despesas_final = df_despesas[['nome_original', 'valor']].copy()
df_despesas_final = df_despesas_final.rename(columns={'nome_original': 'nome'})
df_despesas_final.insert(0, 'id_partida', id_partida)

df_despesas_final = df_despesas_final.astype(object).where(pd.notna(df_despesas_final), None)


registros_despesas = list(df_despesas_final.itertuples(index=False, name=None))

""" sql_despesas = "INSERT INTO despesa_partida (id_partida, nome, valor) VALUES (%s, %s, %s)"

cursor.executemany(sql_despesas, registros_despesas)
conexao.commit() """


# ============================================================
# 10. ORGANIZAÇÃO DO RESUMO FINANCEIRO
# ============================================================

df_resumo = pd.read_excel(selecionado, sheet_name="RESUMO", header=4)

""" print(df_resumo.info())
print(df_resumo.columns)
print(df_resumo.shape)
print(df_resumo.dtypes)
print(df_resumo.isna().sum()) """

df_resumo = df_resumo[['campo_modelo', 'valor_oficial_no_bordero']]
df_resumo = df_resumo.set_index('campo_modelo')[['valor_oficial_no_bordero']].T

df_resumo_final = df_resumo[['total_disponivel', 'total_devolvido', 'total_utilizado', 'arrecadacao_bruta','total_despesas', 'retencoes', 'receita_liquida', 'consignatários', 'resultado_final', 'complemento_contabil']]
df_resumo_final = df_resumo_final.rename(columns={'consignatários': 'consignatarios'})
df_resumo_final.insert(0, 'id_partida', id_partida)
df_resumo_final = df_resumo_final.astype(object).where(pd.notna(df_resumo_final), None)

registros_resumo = next(df_resumo_final.itertuples(index=False, name=None))

""" sql_resumo = 'INSERT INTO resumo_financeiro_partida (id_partida, total_disponivel, total_devolvido, total_utilizado, arrecadacao_bruta, total_despesas, retencoes, receita_liquida, consignatarios, resultado_final, complemento_contabil) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
cursor.execute(sql_resumo, registros_resumo)
conexao.commit() """

# ============================================================
# 11. ORGANIZAÇÃO DO CONTEXTO DA PARTIDA
# ============================================================

df_contexto = pd.read_excel(selecionado, sheet_name="CONTEXTO", header=3)
df_contexto_final = df_contexto[['Campo do modelo', 'Valor a preencher']]

valores_contexto = (df_contexto_final.set_index('Campo do modelo')['Valor a preencher'].to_dict())

mapa_feriado = {'Sim': True, 'Não': False}
valores_contexto['feriado'] = mapa_feriado[valores_contexto['feriado']]

registro_contexto = (
    id_partida,
    valores_contexto['feriado'],
    valores_contexto['dias_desde_ultimo_jogo_maracana']
)

""" sql_contexto = 'INSERT INTO contexto_partida (id_partida, feriado, dias_desde_ultimo_jogo_maracana) VALUES (%s,%s,%s)'
cursor.execute(sql_contexto, registro_contexto)
conexao.commit() """


# ============================================================
# 12. ORGANIZAÇÃO DOS ATRIBUTOS DA PARTIDA
# ============================================================

df_atributos = pd.read_excel(selecionado, sheet_name="ATRIBUTOS", header=3)
df_atributos = df_atributos[['Campo do modelo', 'Valor (0–10)']]

valores_atributos = (df_atributos.set_index('Campo do modelo')['Valor (0–10)'].to_dict())


registro_atributos = (id_partida, valores_atributos['importancia_partida'], valores_atributos['apelo_adversario'])

""" sql_atributos = 'INSERT INTO atributos_partida (id_partida, importancia_partida, apelo_adversario) VALUES (%s,%s,%s)'
cursor.execute(sql_atributos,registro_atributos)
conexao.commit() """

# ============================================================
# 13. ORGANIZAÇÃO DO DESEMPENHO RECENTE
# ============================================================

df_desempenho = pd.read_excel(selecionado, sheet_name="DESEMPENHO", header=3)
df_desempenho = df_desempenho[['Campo do modelo', 'Valor a preencher']]

valores_desempenho = (df_desempenho.set_index('Campo do modelo')['Valor a preencher'].to_dict())

registro_desempenho = (id_partida, valores_desempenho['posicao_fluminense'], valores_desempenho['pontos_fluminense'], valores_desempenho['vitorias_ultimos_5'], valores_desempenho['empates_ultimos_5'], valores_desempenho['derrotas_ultimos_5'], valores_desempenho['gols_marcados_ultimos_5'], valores_desempenho['gols_sofridos_ultimos_5'])

""" sql_desempenho = 'INSERT INTO desempenho_partida (id_partida, posicao_fluminense, pontos_fluminense, vitorias_ultimos_5, empates_ultimos_5, derrotas_ultimos_5, gols_marcados_ultimos_5, gols_sofridos_ultimos_5) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
cursor.execute(sql_desempenho,registro_desempenho)
conexao.commit() """

# ============================================================
# 14. ENCERRAMENTO DA CONEXÃO
# ============================================================

cursor.close()
conexao.close()


# ============================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÕES
# ============================================================

from pathlib import Path

import pandas as pd




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

    if not lista_arquivos:
        raise FileNotFoundError(f"Nenhum arquivo Excel encontrado em {caminho}")

    return sorted(lista_arquivos)


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





def ler_abas_planilha(caminho):

    df_partida = pd.read_excel(caminho, sheet_name="PARTIDA", header=3)
    df_ingressos = pd.read_excel(caminho, sheet_name="INGRESSOS", header=5)
    df_despesas = pd.read_excel(caminho, sheet_name="DESPESAS", header=5)
    df_resumo = pd.read_excel(caminho, sheet_name="RESUMO", header=4)
    df_contexto = pd.read_excel(caminho, sheet_name="CONTEXTO", header=3)
    df_atributos = pd.read_excel(caminho, sheet_name="ATRIBUTOS", header=3)
    df_desempenho = pd.read_excel(caminho, sheet_name="DESEMPENHO", header=3)

    dados = {
        'partida': df_partida,
        'ingressos': df_ingressos,
        'despesas': df_despesas,
        'resumo': df_resumo,
        'contexto': df_contexto,
        'atributos': df_atributos,
        'desempenho': df_desempenho,
    }
    return dados


# ============================================================
# 3. PREPARAÇÃO DOS ARQUIVOS E CONEXÃO
# ============================================================

lista = listar_arquivos_excel(pasta_interim)

total = len(lista)

    

aprovado = 0
reprovado = 0

# Seleção temporária para os testes
selecionado = lista[0]

abas = ler_abas_planilha(selecionado)

#print(abas['partida'])
#print(abas['ingressos'])
#print(abas['despesas'])
#print(abas['resumo'])
#print(abas['contexto'])
#print(abas['atributos'])
#print(abas['desempenho'])




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
# 5.2. Consultas das dimensões no MySQL
# ------------------------------------------------------------

setores_dict, categorias_dict, planos_dict = (
    obter_ou_criar_referencias_ingressos(cursor, df_ingressos)
)


# ============================================================
# 6. ORGANIZAÇÃO DOS DADOS DA PARTIDA
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





# ============================================================
# 7. CARGA DOS INGRESSOS NO BANCO
# ============================================================

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
# 8. CARGA DAS DESPESAS DA PARTIDA
# ============================================================

""" sql_despesas = "INSERT INTO despesa_partida (id_partida, nome, valor) VALUES (%s, %s, %s)"

cursor.executemany(sql_despesas, registros_despesas)
conexao.commit() """


# ============================================================
# 9. CARGA DO RESUMO FINANCEIRO
# ============================================================

""" sql_resumo = 'INSERT INTO resumo_financeiro_partida (id_partida, total_disponivel, total_devolvido, total_utilizado, arrecadacao_bruta, total_despesas, retencoes, receita_liquida, consignatarios, resultado_final, complemento_contabil) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
cursor.execute(sql_resumo, registros_resumo)
conexao.commit() """

# ============================================================
# 10. CARGA DO CONTEXTO DA PARTIDA
# ============================================================

""" sql_contexto = 'INSERT INTO contexto_partida (id_partida, feriado, dias_desde_ultimo_jogo_maracana) VALUES (%s,%s,%s)'
cursor.execute(sql_contexto, registro_contexto)
conexao.commit() """


# ============================================================
# 11. CARGA DOS ATRIBUTOS DA PARTIDA
# ============================================================

""" sql_atributos = 'INSERT INTO atributos_partida (id_partida, importancia_partida, apelo_adversario) VALUES (%s,%s,%s)'
cursor.execute(sql_atributos,registro_atributos)
conexao.commit() """

# ============================================================
# 12. CARGA DO DESEMPENHO RECENTE
# ============================================================

""" sql_desempenho = 'INSERT INTO desempenho_partida (id_partida, posicao_fluminense, pontos_fluminense, vitorias_ultimos_5, empates_ultimos_5, derrotas_ultimos_5, gols_marcados_ultimos_5, gols_sofridos_ultimos_5) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
cursor.execute(sql_desempenho,registro_desempenho)
conexao.commit() """

# ============================================================
# 13. ENCERRAMENTO DA CONEXÃO
# ============================================================


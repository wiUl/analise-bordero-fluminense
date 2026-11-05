from pathlib import Path
import pandas as pd


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



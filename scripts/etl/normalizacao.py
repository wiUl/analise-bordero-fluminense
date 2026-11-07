import pandas as pd


def normalizar_espacos(valor):
    """Remove espaços nas pontas e reduz qualquer sequência a um espaço simples."""
    if not isinstance(valor, str):
        return valor

    texto_normalizado = " ".join(valor.split())
    return texto_normalizado or None


def normalizar_colunas_textuais(df, colunas):
    """Normaliza apenas as colunas textuais indicadas, sem alterar o DataFrame original."""
    df_normalizado = df.copy()

    for coluna in colunas:
        if coluna in df_normalizado.columns:
            df_normalizado[coluna] = df_normalizado[coluna].map(normalizar_espacos)

    return df_normalizado

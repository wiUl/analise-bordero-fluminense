import argparse
import os
from pathlib import Path
import traceback
from dotenv import load_dotenv
from scripts.etl.leitura_excel import *
from scripts.etl.banco_mysql import *
from scripts.etl.preparacao import *


def ler_planilha_validada(caminho):

    abas_validas, abas_ausentes = verificar_abas_excel(caminho)
    if not abas_validas:
        raise ValueError(f"A planilha tem as seguintes abas faltando: {abas_ausentes}, no arquivo {caminho.name}")

    dados = ler_abas_planilha(caminho)

    return dados

def processar_planilha(caminho, conexao):
    # Lê todas as abas depois de confirmar que o arquivo contém a estrutura esperada.
    dados = ler_planilha_validada(caminho)

    # Organiza os campos da aba PARTIDA e prepara as referências necessárias
    # para localizar ou cadastrar adversário, estádio, competição e temporada.
    dados_partida = organizar_entidades(dados['partida'])
    referencias_partida = preparar_referencias_partida(dados_partida)

    cursor = conexao.cursor()

    try:
        # Mantém as referências, a partida e todas as tabelas-fato na mesma
        # transação: se qualquer etapa falhar, a carga deste arquivo será desfeita.
        conexao.start_transaction()

        # Obtém os IDs das dimensões. Os DataFrames de referências têm uma linha;
        # por isso, iloc[0] extrai o valor que será usado no banco.
        dados_adversario = referencias_partida['adversario'].iloc[0]
        id_adversario = garantir_adversario(
            cursor,
            dados_adversario['nome'],
            dados_adversario['e_classico'],
            dados_adversario['e_clube_g12']
        )

        dados_competicao = referencias_partida['competicao'].iloc[0]
        id_competicao = garantir_competicao(cursor, dados_competicao['nome'])

        dados_temporada = referencias_partida['temporada'].iloc[0]
        id_temporada = garantir_temporada(cursor, dados_temporada['ano'])

        id_competicao_temporada = garantir_competicao_temporada(
            cursor, id_competicao, id_temporada
        )

        dados_estadio = referencias_partida['estadio'].iloc[0]
        id_estadio = garantir_estadio(
            cursor,
            dados_estadio['nome'],
            dados_estadio['cidade'],
            dados_estadio['estado'],
            dados_estadio['pais'],
            dados_estadio['capacidade']
        )

        # Prepara e garante a partida antes de associar os registros das demais abas.
        df_partida = preparar_partida(
            dados_partida,
            id_adversario,
            id_competicao_temporada,
            id_estadio
        )
        id_partida = garantir_partida(cursor, df_partida)

        # Cria ou recupera IDs de setor, categoria e plano de sócio, e então
        # prepara todos os DataFrames no formato das tabelas-fato.
        setores_dict, categorias_dict, planos_dict = garantir_referencias_ingressos(
            cursor, dados['ingressos']
        )
        dataframes_carga = {
            'ingresso_partida': preparar_ingressos(
                dados['ingressos'], id_partida,
                setores_dict, categorias_dict, planos_dict
            ),
            'despesa_partida': preparar_despesas(dados['despesas'], id_partida),
            'resumo_financeiro_partida': preparar_resumo(dados['resumo'], id_partida),
            'contexto_partida': preparar_contexto(dados['contexto'], id_partida),
            'atributos_partida': preparar_atributos(dados['atributos'], id_partida),
            'desempenho_partida': preparar_desempenho(dados['desempenho'], id_partida)
        }

        # Usa as quantidades preparadas como referência para distinguir uma carga
        # completa de uma carga parcial, que precisa ser investigada antes de repetir.
        quantidades_esperadas = {
            tabela: len(df)
            for tabela, df in dataframes_carga.items()
        }
        estado, quantidades_existentes = verificar_estado_carga_partida(
            cursor, id_partida, quantidades_esperadas
        )

        if estado == 'completa':
            # Não repete INSERTs de uma partida que já está carregada.
            conexao.rollback()
            return {
                'arquivo': caminho.name,
                'id_partida': id_partida,
                'estado': 'ignorada; carga já completa',
                'registros_existentes': quantidades_existentes
            }

        if estado == 'parcial':
            # Uma carga incompleta não é corrigida automaticamente para evitar
            # duplicações ou mascarar uma falha anterior.
            raise RuntimeError(
                f"A partida {id_partida} possui carga parcial. "
                f"Registros encontrados: {quantidades_existentes}; "
                f"esperados: {quantidades_esperadas}."
            )

        # A partida ainda não tem registros-fato; insere as abas preparadas.
        registros_inseridos = {
            'ingresso_partida': inserir_ingressos(
                cursor, dataframes_carga['ingresso_partida']
            ),
            'despesa_partida': inserir_despesas(
                cursor, dataframes_carga['despesa_partida']
            ),
            'resumo_financeiro_partida': inserir_resumo(
                cursor, dataframes_carga['resumo_financeiro_partida']
            ),
            'contexto_partida': inserir_contexto(
                cursor, dataframes_carga['contexto_partida']
            ),
            'atributos_partida': inserir_atributos(
                cursor, dataframes_carga['atributos_partida']
            ),
            'desempenho_partida': inserir_desempenho(
                cursor, dataframes_carga['desempenho_partida']
            )
        }

        # Confirma as alterações somente depois que todas as abas foram inseridas.
        conexao.commit()

        return {
            'arquivo': caminho.name,
            'id_partida': id_partida,
            'estado': 'carregada',
            'registros_inseridos': registros_inseridos
        }

    except Exception:
        # Desfaz também dimensões/partida eventualmente criadas nesta tentativa.
        conexao.rollback()
        raise
    finally:
        # Libera o cursor tanto em caso de sucesso quanto de erro.
        cursor.close()


def main():
    # Exige a escolha do escopo para que um argumento incorreto nunca dispare
    # acidentalmente a carga de todas as planilhas.
    parser = argparse.ArgumentParser(
        description="Carrega os dados de uma planilha de borderô no MySQL."
    )
    grupo_execucao = parser.add_mutually_exclusive_group(required=True)
    grupo_execucao.add_argument(
        '--arquivo',
        type=Path,
        help='Processa somente o arquivo Excel informado.'
    )
    grupo_execucao.add_argument(
        '--lote',
        action='store_true',
        help='Processa todos os arquivos Excel de data/interim.'
    )
    argumentos = parser.parse_args()

    # Calcula a raiz do projeto a partir da localização deste arquivo, para que
    # a execução não dependa da pasta atual aberta no terminal.
    pasta_projeto = Path(__file__).resolve().parents[1]
    caminho_env = pasta_projeto / ".env"
    pasta_planilhas = pasta_projeto / "data" / "interim"

    # Carrega as credenciais e interrompe a execução com uma mensagem clara
    # caso alguma variável necessária não esteja configurada.
    load_dotenv(caminho_env)
    credenciais = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    credenciais_ausentes = [
        nome for nome, valor in credenciais.items()
        if valor is None or not valor.strip()
    ]
    if credenciais_ausentes:
        raise ValueError(
            f"Variáveis ausentes ou vazias no arquivo .env: {credenciais_ausentes}"
        )

    # Seleciona um único arquivo ou, somente com --lote explícito, lista a pasta.
    if argumentos.arquivo is not None:
        caminho_arquivo = argumentos.arquivo
        if not caminho_arquivo.is_absolute():
            caminho_arquivo = pasta_projeto.joinpath(caminho_arquivo)
        caminho_arquivo = caminho_arquivo.resolve()

        if not caminho_arquivo.is_file():
            raise FileNotFoundError(
                f"Arquivo Excel não encontrado: {caminho_arquivo}"
            )
        if caminho_arquivo.suffix.lower() != '.xlsx':
            raise ValueError(
                f"O arquivo precisa ter extensão .xlsx: {caminho_arquivo}"
            )

        arquivos = [caminho_arquivo]
        print(f"Arquivo selecionado: {caminho_arquivo.name}")
    else:
        # A função informa se a pasta não contém planilhas Excel.
        arquivos = listar_arquivos_excel(pasta_planilhas)
        print(f"Planilhas encontradas: {len(arquivos)}")

    # Uma conexão é reutilizada durante o lote e fechada ao final da execução.
    conexao = conectar_banco(
        credenciais['host'],
        credenciais['user'],
        credenciais['password'],
        credenciais['database']
    )

    resultados = {
        'carregadas': [],
        'ignoradas': [],
        'com_erro': []
    }

    try:
        # Cada arquivo tem sua própria transação em processar_planilha.
        # Se um deles falhar, registra o erro e segue para o próximo.
        for caminho in arquivos:
            print(f"Processando: {caminho.name}")
            try:
                resultado = processar_planilha(caminho, conexao)

                if resultado['estado'].startswith('ignorada'):
                    resultados['ignoradas'].append(resultado)
                    print(f"Ignorada: {caminho.name} ({resultado['estado']})")
                else:
                    resultados['carregadas'].append(resultado)
                    print(
                        f"Carregada: {caminho.name}; "
                        f"id_partida={resultado['id_partida']}; "
                        f"registros={resultado['registros_inseridos']}"
                    )
            except Exception as erro:
                resultados['com_erro'].append({
                    'arquivo': caminho.name,
                    'erro': str(erro)
                })
                print(f"Erro em {caminho.name}: {erro}")
                # No modo de arquivo único, mostra a linha exata que falhou
                # para facilitar a investigação dos parâmetros enviados ao MySQL.
                if argumentos.arquivo is not None:
                    traceback.print_exc()
    finally:
        # Garante o fechamento mesmo se ocorrer um erro fora do processamento
        # individual dos arquivos.
        conexao.close()

    # Apresenta um resumo final e devolve os resultados para uso programático.
    print(
        "Resumo do lote: "
        f"{len(resultados['carregadas'])} carregadas, "
        f"{len(resultados['ignoradas'])} ignoradas, "
        f"{len(resultados['com_erro'])} com erro."
    )
    return resultados


if __name__ == "__main__":
    resultados = main()
    if resultados['com_erro']:
        raise SystemExit(1)

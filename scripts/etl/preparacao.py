import pandas as pd


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

def validar_colunas_numericas(
    df,
    colunas_numericas,
    colunas_nao_negativas=(),
    colunas_inteiras=()
):
    df_validado = df.copy()

    for coluna in colunas_numericas:
        valores_numericos = pd.to_numeric(df_validado[coluna], errors='coerce')
        valores_invalidos = df_validado[coluna].notna() & valores_numericos.isna()

        if valores_invalidos.any():
            valores = df_validado.loc[valores_invalidos, coluna].unique().tolist()
            raise ValueError(
                f"A coluna {coluna} contém valores não numéricos: {valores}"
            )

        if coluna in colunas_inteiras:
            valores_fracionarios = (
                valores_numericos.notna()
                & (valores_numericos % 1 != 0)
            )

            if valores_fracionarios.any():
                valores = df_validado.loc[
                    valores_fracionarios, coluna
                ].unique().tolist()
                raise ValueError(
                    f"A coluna {coluna} deve conter números inteiros: {valores}"
                )

        if coluna in colunas_nao_negativas:
            valores_negativos = valores_numericos < 0

            if valores_negativos.any():
                valores = df_validado.loc[
                    valores_negativos, coluna
                ].unique().tolist()
                raise ValueError(
                    f"A coluna {coluna} não pode conter valores negativos: {valores}"
                )

        if coluna in colunas_inteiras:
            df_validado[coluna] = valores_numericos.astype('Int64')
        else:
            df_validado[coluna] = valores_numericos

    return df_validado


def preparar_referencias_partida(dados_partida):

    adversario = dados_partida['adversario']
    estadio = dados_partida['estadio']
    competicao = dados_partida['competicao']
    temporada = dados_partida['temporada']

    # COMPETICAO e TEMPORADA possuem campos obrigatórios no modelo.
    nome_competicao = competicao['nome']
    ano_temporada = temporada['ano']

    if pd.isna(nome_competicao) or not isinstance(nome_competicao, str) or not nome_competicao.strip():
        raise ValueError("Nome da competição não pode ser nulo ou vazio")

    ano_numerico = pd.to_numeric(pd.Series([ano_temporada]), errors='coerce').iloc[0]
    if pd.isna(ano_numerico):
        raise ValueError("Ano da temporada não pode ser nulo e deve ser numérico")
    if ano_numerico % 1 != 0:
        raise ValueError(f"Ano da temporada deve ser inteiro: {ano_temporada}")
    if not 1900 <= ano_numerico <= 2200:
        raise ValueError(f"Ano da temporada fora do intervalo permitido: {ano_temporada}")

    df_competicao = pd.DataFrame([{'nome': nome_competicao}])
    df_temporada = pd.DataFrame([{'ano': int(ano_numerico)}])

    # ADVERSARIO exige nome e flags booleanas; não aceita ausência para esses campos.
    nome_adversario = adversario['nome']
    e_classico_adversario = adversario['e_classico']
    e_clube_g12 = adversario['e_clube_g12']

    if pd.isna(nome_adversario) or not isinstance(nome_adversario, str) or not nome_adversario.strip():
        raise ValueError("O nome do adversário não pode ser nulo ou vazio")

    mapeamento = {'Sim': True, 'Não': False}
    flags_adversario = {
        'e_classico': e_classico_adversario,
        'e_clube_g12': e_clube_g12
    }
    flags_convertidas = {}

    for nome_flag, valor_flag in flags_adversario.items():
        if pd.isna(valor_flag):
            raise ValueError(f"A flag {nome_flag} não pode ser nula")
        if isinstance(valor_flag, str):
            valor_flag = valor_flag.strip()
        if valor_flag not in mapeamento:
            raise ValueError(f"Valor inválido para {nome_flag}: {valor_flag}")
        flags_convertidas[nome_flag] = mapeamento[valor_flag]

    df_adversario = pd.DataFrame([{
        'nome': nome_adversario,
        'e_classico': flags_convertidas['e_classico'],
        'e_clube_g12': flags_convertidas['e_clube_g12']
    }])

    # ESTADIO exige nome; localização e capacidade podem ser NULL conforme o modelo.
    nome_estadio = estadio['nome']
    capacidade_estadio = estadio['capacidade']

    if pd.isna(nome_estadio) or not isinstance(nome_estadio, str) or not nome_estadio.strip():
        raise ValueError("O nome do estádio não pode ser nulo ou vazio")

    capacidade_numerica = pd.to_numeric(
        pd.Series([capacidade_estadio]), errors='coerce'
    ).iloc[0]
    if pd.notna(capacidade_estadio) and pd.isna(capacidade_numerica):
        raise ValueError(f"A capacidade do estádio deve ser numérica: {capacidade_estadio}")
    if pd.notna(capacidade_numerica):
        if capacidade_numerica % 1 != 0:
            raise ValueError(f"A capacidade do estádio deve ser inteira: {capacidade_estadio}")
        if capacidade_numerica < 0:
            raise ValueError(f"A capacidade do estádio não pode ser negativa: {capacidade_estadio}")
        capacidade_estadio = int(capacidade_numerica)

    df_estadio = pd.DataFrame([{
        'nome': nome_estadio,
        'cidade': estadio['cidade'],
        'estado': estadio['estado'],
        'pais': estadio['pais'],
        'capacidade': capacidade_estadio
    }])

    # Converte NaN para None nos campos opcionais, preservando NULL no MySQL.
    referencias = {
        'adversario': df_adversario,
        'competicao': df_competicao,
        'temporada': df_temporada,
        'estadio': df_estadio
    }
    return {
        entidade: df.astype(object).where(pd.notna(df), None)
        for entidade, df in referencias.items()
    }


def preparar_partida(dados_partida, id_adversario, id_competicao_temporada, id_estadio):

    # As chaves estrangeiras são resolvidas antes desta etapa e são obrigatórias em PARTIDA.
    ids_obrigatorios = {
        'id_adversario': id_adversario,
        'id_competicao_temporada': id_competicao_temporada,
        'id_estadio': id_estadio
    }
    for nome_id, valor_id in ids_obrigatorios.items():
        if pd.isna(valor_id):
            raise ValueError(f"{nome_id} é obrigatório para preparar a partida")
        id_numerico = pd.to_numeric(pd.Series([valor_id]), errors='coerce').iloc[0]
        if pd.isna(id_numerico) or id_numerico % 1 != 0 or id_numerico <= 0:
            raise ValueError(f"{nome_id} deve ser um número inteiro positivo: {valor_id}")
        ids_obrigatorios[nome_id] = int(id_numerico)

    partida = dados_partida['partida']

    # PARTIDA exige data e as três referências; horário e rodada podem ficar ausentes.
    valor_data = partida['data']
    if pd.isna(valor_data):
        raise ValueError("A data não pode ser nula")

    data_numerica = pd.to_datetime(valor_data, errors='coerce')
    if pd.isna(data_numerica):
        raise ValueError(f"A data da partida é inválida: {valor_data}")

    df_partida = pd.DataFrame([{
        'data': data_numerica.date(),
        'horario': partida['horario'],
        'adversario_id': ids_obrigatorios['id_adversario'],
        'competicao_temporada_id': ids_obrigatorios['id_competicao_temporada'],
        'estadio_id': ids_obrigatorios['id_estadio'],
        'rodada': partida['rodada']
    }])

    return df_partida.astype(object).where(pd.notna(df_partida), None)


def preparar_despesas(df_despesas, id_partida):

    if id_partida is None:
        raise ValueError("id_partida é obrigatório para preparar as despesas")
    
    df_despesas = df_despesas[['nome_original', 'valor']].copy()
    df_despesas = df_despesas.rename(columns={'nome_original': 'nome'})

    if df_despesas['nome'].isna().any():
        raise ValueError('O nome da despesa não pode ser nulo')

    nomes_vazios = df_despesas['nome'].map(
        lambda nome: isinstance(nome, str) and not nome.strip()
    )
    if nomes_vazios.any():
        raise ValueError('O nome da despesa não pode estar vazio')

    df_despesas = validar_colunas_numericas(
        df_despesas,
        colunas_numericas=['valor'],
        colunas_nao_negativas=['valor']
    )

    df_despesas_final = df_despesas.astype(object).where(pd.notna(df_despesas), None)
    df_despesas_final.insert(0, 'id_partida', id_partida)
    
    
    return df_despesas_final

def preparar_ingressos(df_ingressos,id_partida,setores_dict,categorias_dict,planos_dict):
    
    if id_partida is None: #validação do id_partida
        raise ValueError("id_partida é obrigatório para preparar os ingressos")

    colunas_origem = [ #separa as colunas que importam para inserção dentro do dataframe
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

    df_ingressos_carga = df_ingressos[colunas_origem].copy()

    if df_ingressos_carga['descricao_original'].isna().any():
        raise ValueError('A descrição original do ingresso não pode ser nula')

    descricoes_vazias = df_ingressos_carga['descricao_original'].map(
        lambda descricao: isinstance(descricao, str) and not descricao.strip()
    )
    if descricoes_vazias.any():
        raise ValueError('A descrição original do ingresso não pode estar vazia')

    colunas_numericas = [
        'preco',
        'quantidade_disponivel',
        'quantidade_devolvida',
        'quantidade_utilizada',
        'arrecadacao'
    ]
    colunas_inteiras = [
        'quantidade_disponivel',
        'quantidade_devolvida',
        'quantidade_utilizada'
    ]
    df_ingressos_carga = validar_colunas_numericas(
        df_ingressos_carga,
        colunas_numericas=colunas_numericas,
        colunas_nao_negativas=colunas_numericas,
        colunas_inteiras=colunas_inteiras
    )

    mapeamentos = [#relaciona cada coluna textual como setor, categoria do ingresso e plano_socio com o id respectivo de cada um no banco
        ('setor', 'id_setor', setores_dict),
        ('categoria_ingresso', 'id_categoria', categorias_dict),
        ('plano_socio', 'id_plano', planos_dict)
    ]

    #converte os nomes no dataframe de acordo com o id correspondente a partir dos mapeamentos
    for coluna_origem, coluna_id, dicionario in mapeamentos:
        df_ingressos_carga[coluna_id] = (
            df_ingressos_carga[coluna_origem].map(dicionario)
        )

        nomes_nao_encontrados = df_ingressos_carga.loc[
            df_ingressos_carga[coluna_origem].notna()
            & df_ingressos_carga[coluna_id].isna(),
            coluna_origem
        ].unique()

        if len(nomes_nao_encontrados) > 0:
            raise ValueError(
                f"Valores sem correspondência para {coluna_origem}: "
                f"{list(nomes_nao_encontrados)}"
            )

        df_ingressos_carga[coluna_id] = (
            df_ingressos_carga[coluna_id].astype('Int64')
        )

    colunas_finais = [
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

    df_ingressos_final = df_ingressos_carga[colunas_finais].copy()

    df_ingressos_final = df_ingressos_final.astype(object).where(
        pd.notna(df_ingressos_final),
        None
    )

    df_ingressos_final.insert(0, 'id_partida', id_partida)

    return df_ingressos_final

def preparar_resumo(df_resumo, id_partida):

    if id_partida is None:
        raise ValueError("id_partida é obrigatório para preparar o resumo")
        
    df_resumo = df_resumo[['campo_modelo', 'valor_oficial_no_bordero']].copy()
    campos_resumo_obrigatorios = [
        'total_disponivel',
        'total_devolvido',
        'total_utilizado',
        'arrecadacao_bruta',
        'total_despesas',
        'retencoes',
        'receita_liquida',
        'consignatários',
        'resultado_final',
        'complemento_contabil'
    ]
    ocorrencias_campos = df_resumo['campo_modelo'].value_counts()
    campos_ausentes_ou_duplicados = [
        campo for campo in campos_resumo_obrigatorios
        if ocorrencias_campos.get(campo, 0) != 1
    ]
    if campos_ausentes_ou_duplicados:
        raise ValueError(
            "Cada campo oficial do resumo deve aparecer exatamente uma vez. "
            f"Verifique: {campos_ausentes_ou_duplicados}"
        )

    df_resumo = df_resumo.set_index('campo_modelo')[['valor_oficial_no_bordero']].T

    df_resumo_final = df_resumo[[
        'total_disponivel',
        'total_devolvido',
        'total_utilizado',
        'arrecadacao_bruta',
        'total_despesas',
        'retencoes',
        'receita_liquida',
        'consignatários',
        'resultado_final',
        'complemento_contabil'
    ]].copy()
    df_resumo_final = df_resumo_final.rename(columns={'consignatários': 'consignatarios'})

    colunas_totais = [
        'total_disponivel',
        'total_devolvido',
        'total_utilizado'
    ]
    colunas_financeiras = [
        'arrecadacao_bruta',
        'total_despesas',
        'retencoes',
        'receita_liquida',
        'consignatarios',
        'resultado_final',
        'complemento_contabil'
    ]
    df_resumo_final = validar_colunas_numericas(
        df_resumo_final,
        colunas_numericas=colunas_totais + colunas_financeiras,
        colunas_nao_negativas=colunas_totais,
        colunas_inteiras=colunas_totais
    )

    df_resumo_final.insert(0, 'id_partida', id_partida)
    df_resumo_final = df_resumo_final.astype(object).where(pd.notna(df_resumo_final), None)


    return df_resumo_final

def preparar_contexto(df_contexto, id_partida):

    if id_partida is None:
        raise ValueError("id_partida é obrigatório para preparar o contexto")
    
    df_contexto_final = df_contexto[['Campo do modelo', 'Valor a preencher']]
    valores_contexto = df_contexto_final.set_index('Campo do modelo')['Valor a preencher']    

    mapa_feriado = {'Sim': True, 'Não': False}
    feriado = valores_contexto['feriado']

    if pd.isna(feriado):
        feriado = None
    elif feriado in mapa_feriado:
        feriado = mapa_feriado[feriado]
    else:
        raise ValueError(f'Valor inválido para feriado: {feriado}')

    df_contexto_final = pd.DataFrame([{
        'id_partida': id_partida,
        'feriado': feriado,
        'dias_desde_ultimo_jogo_maracana': valores_contexto['dias_desde_ultimo_jogo_maracana']
    }])

    df_contexto_final = validar_colunas_numericas(
        df_contexto_final,
        colunas_numericas=['dias_desde_ultimo_jogo_maracana'],
        colunas_nao_negativas=['dias_desde_ultimo_jogo_maracana'],
        colunas_inteiras=['dias_desde_ultimo_jogo_maracana']
    )
    df_contexto_final = df_contexto_final.astype(object).where(pd.notna(df_contexto_final), None)
    
    return df_contexto_final

def preparar_atributos(df_atributos, id_partida):

    if id_partida is None:
        raise ValueError("id_partida é obrigatório para preparar os atributos")

    df_atributos_final = df_atributos[['Campo do modelo', 'Valor (0–10)']].copy()
    valores_atributos = (df_atributos_final.set_index('Campo do modelo')['Valor (0–10)'].to_dict())

    df_atributos_final = pd.DataFrame([{
        'id_partida': id_partida,
        'importancia_partida': valores_atributos['importancia_partida'],
        'apelo_adversario': valores_atributos['apelo_adversario']
    }])

    df_atributos_final = validar_colunas_numericas(
        df_atributos_final,
        colunas_numericas=['importancia_partida', 'apelo_adversario']
    )
    df_atributos_final = df_atributos_final.astype(object).where(pd.notna(df_atributos_final), None)

    valor_importancia = df_atributos_final['importancia_partida'].item()
    valor_apelo = df_atributos_final['apelo_adversario'].item()


    if valor_importancia is not None:
        if valor_importancia > 10 or valor_importancia < 0:
            raise ValueError(f"A importancia da partida está fora da escala, valor: {valor_importancia}")
        
    if valor_apelo is not None:       
        if valor_apelo > 10 or valor_apelo < 0:
            raise ValueError(f"O apelo do adversario está fora da escala, valor: {valor_apelo}")

    return df_atributos_final


def preparar_desempenho(df_desempenho, id_partida):

    if id_partida is None:
        raise ValueError("id_partida é obrigatório para preparar o desempenho")

    df_desempenho_final = df_desempenho[['Campo do modelo', 'Valor a preencher']].copy()

    valores_desempenho = df_desempenho_final.set_index('Campo do modelo')['Valor a preencher']

    df_desempenho_final = pd.DataFrame([{
        'id_partida': id_partida,
        'posicao_fluminense': valores_desempenho['posicao_fluminense'],
        'pontos_fluminense': valores_desempenho['pontos_fluminense'],
        'vitorias_ultimos_5': valores_desempenho['vitorias_ultimos_5'],
        'empates_ultimos_5': valores_desempenho['empates_ultimos_5'],
        'derrotas_ultimos_5': valores_desempenho['derrotas_ultimos_5'],
        'gols_marcados_ultimos_5': valores_desempenho['gols_marcados_ultimos_5'],
        'gols_sofridos_ultimos_5': valores_desempenho['gols_sofridos_ultimos_5']
    }])

    colunas_inteiras = [
        'posicao_fluminense',
        'pontos_fluminense',
        'vitorias_ultimos_5',
        'empates_ultimos_5',
        'derrotas_ultimos_5',
        'gols_marcados_ultimos_5',
        'gols_sofridos_ultimos_5'
    ]
    df_desempenho_final = validar_colunas_numericas(
        df_desempenho_final,
        colunas_numericas=colunas_inteiras,
        colunas_inteiras=colunas_inteiras
    )
    df_desempenho_final = df_desempenho_final.astype(object).where(pd.notna(df_desempenho_final), None)

    valor_posicao = df_desempenho_final['posicao_fluminense'].item()
    valor_pontos = df_desempenho_final['pontos_fluminense'].item()
    valor_vitorias = df_desempenho_final['vitorias_ultimos_5'].item()
    valor_empates = df_desempenho_final['empates_ultimos_5'].item()
    valor_derrotas = df_desempenho_final['derrotas_ultimos_5'].item()
    valor_gols_marcados = df_desempenho_final['gols_marcados_ultimos_5'].item()
    valor_gols_sofridos = df_desempenho_final['gols_sofridos_ultimos_5'].item()

    if valor_posicao is not None:
        if valor_posicao <= 0:
            raise ValueError('A posição deve ser maior que zero')

    if valor_pontos is not None:
        if valor_pontos < 0:
            raise ValueError('A pontuação não pode ser menor que zero')

    if valor_vitorias is not None:
        if valor_vitorias < 0:
            raise ValueError('O número de vitórias não pode ser menor que zero')
        if valor_vitorias > 5:
            raise ValueError('O número de vitórias não pode ser maior que cinco')

    if valor_empates is not None:
        if valor_empates < 0:
            raise ValueError('O número de empates não pode ser menor que zero')
        if valor_empates > 5:
            raise ValueError('O número de empates não pode ser maior que cinco')

    if valor_derrotas is not None:
        if valor_derrotas < 0:
            raise ValueError('O número de derrotas não pode ser menor que zero')
        if valor_derrotas > 5:
            raise ValueError('O número de derrotas não pode ser maior que cinco')

    if (
        valor_vitorias is not None
        and valor_empates is not None
        and valor_derrotas is not None
        and valor_vitorias + valor_empates + valor_derrotas > 5
    ):
        raise ValueError(
            'A soma de vitórias, empates e derrotas não pode ser maior que cinco'
        )

    if valor_gols_marcados is not None:
        if valor_gols_marcados < 0:
            raise ValueError('O número de gols marcados não pode ser menor que zero')

    if valor_gols_sofridos is not None:
        if valor_gols_sofridos < 0:
            raise ValueError('O número de gols sofridos não pode ser menor que zero')

    return df_desempenho_final

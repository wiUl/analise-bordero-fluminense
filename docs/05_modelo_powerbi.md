# Modelo no Power BI

## Objetivo e escopo

Este documento descreve o modelo dimensional construído no Power BI a partir do banco MySQL local, as decisões de modelagem, as medidas DAX e a primeira página do dashboard (**Resumo Temporada 2026**).

O modelo relacional do banco está documentado em [04_modelagem.md](04_modelagem.md) e o dicionário do banco em [03_dicionario_dados.md](03_dicionario_dados.md). Aqui está a camada analítica, que reorganiza esses dados para consumo no relatório.

Fonte de verdade deste documento: o modelo semântico versionado em `powerbi/Dashboard - Fluminense_Borderô.SemanticModel/definition/` (arquivos TMDL). Em caso de divergência, vale o TMDL.

## Arquitetura da camada Power BI

```text
MySQL local (analise_bordero_fluminense)
   ↓  MySQL.Database("localhost", ...)   — modo Importar
Consultas src_*  (uma por tabela do banco; ocultas no modelo)
   ↓  Power Query (mesclagens à esquerda)
dim_partida        stg_ingresso → map_tipo_ingresso, tmp_descricoes
                         ↓
              dim_ingresso → fato_ingresso        fato_despesa
   ↓
dim_data (tabela calculada em DAX)  +  _Medidas (medidas DAX)
```

- **Conexão:** o Power BI lê o MySQL em `localhost`; os dados são importados. Para atualizar o modelo, o MySQL local precisa estar em execução.
- **Consultas `src_*`:** 14 tabelas espelham as tabelas do banco (adversário, atributos, categoria, competição, competição-temporada, contexto, desempenho, despesa, estádio, partida, plano de sócio, resumo financeiro, setor, temporada). Elas ficam ocultas e servem apenas de insumo; `ingresso_partida` entra por uma consulta própria (`src_ingresso_partida`).
- **Consultas auxiliares (somente Power Query):** `stg_ingresso` (preparação das linhas de ingresso), `map_tipo_ingresso` (de-para de descrições) e `tmp_descricoes` (apoio para localizar descrições sem categoria).
- **Tabela de datas:** não há relação com `src_*`; `dim_data` é calculada em DAX.

## Tabelas do modelo

| Tabela | Tipo | Granularidade | Origem |
| --- | --- | --- | --- |
| `dim_partida` | Dimensão | Uma linha por partida | `src_partida` + adversário, competição, temporada, estádio, atributos, contexto, desempenho e resumo financeiro oficial |
| `dim_ingresso` | Dimensão | Uma linha por combinação única de setor, tipo de ingresso, tipo de público e plano de sócio | `stg_ingresso` (valores distintos) |
| `dim_data` | Dimensão | Uma linha por dia, do início do ano da primeira partida ao fim do ano da última | Calculada (`CALENDAR`) |
| `fato_ingresso` | Fato | Uma linha por linha de ingresso do borderô em cada partida | `stg_ingresso` + chave de `dim_ingresso` |
| `fato_despesa` | Fato | Uma linha por despesa do borderô | `src_despesa_partida` |
| `_Medidas` | Tabela de medidas | — | Medidas DAX |

### Relacionamentos

| De (muitos) | Para (um) |
| --- | --- |
| `fato_ingresso[id_partida]` | `dim_partida[id_partida]` |
| `fato_ingresso[chave_ingresso]` | `dim_ingresso[chave_ingresso]` |
| `fato_despesa[id_partida]` | `dim_partida[id_partida]` |
| `dim_partida[data]` | `dim_data[Date]` |

As duas tabelas fato (ingressos e despesas) se conectam por `dim_partida`, que é a dimensão compartilhada. Por isso, medidas de ingresso e de despesa podem ser combinadas por partida.

## Decisões de modelagem

1. **Duas tabelas fato.** Ingressos e despesas têm granularidades diferentes (linha de ingresso × linha de despesa), então ficam em fatos separadas, ligadas pela partida.
2. **`dim_partida` única e achatada.** Adversário (com `e_classico` e `e_clube_g12`), competição, temporada, estádio, atributos (importância e apelo), contexto (feriado, dias desde o último jogo), desempenho pré-jogo e o resumo financeiro oficial foram trazidos para a mesma dimensão, porque todos têm a granularidade da partida.
3. **Setor, categoria e plano de sócio em uma só dimensão (`dim_ingresso`).** A chave `chave_ingresso` é um índice criado sobre as combinações distintas. Isso evita chaves nulas na fato.
4. **Tratamento de nulos só na camada Power BI.** No banco, setor, categoria e plano seguem `NULL` quando o borderô não informa (regra do projeto). No Power BI, setor sem informação vira `Sem Setor` e plano sem informação vira `Sem Plano`, para que as combinações tenham chave única. A descrição literal do borderô não é usada nas dimensões.
5. **Tipo de ingresso padronizado.** `tipo de ingresso` usa a categoria do banco; quando a categoria é nula, usa o de-para `map_tipo_ingresso`, que reúne 32 descrições originais em 9 tipos: Inteira, Meia, Sócio (inclui a correção de grafia `Socio` → `Sócio`), Sócio Visitante, Ex Sócios, Ingresso Promocional, Camarote Promocional, Cadeira Cativa, Tribuna e Gratuidade por Lei. As três grafias de gratuidade por lei (`Gratuidades por Lei`, `Gratuidades por força da Lei`, `Gratuidades Por Força da Lei`) viram um único tipo.
6. **Tipo de público.** `tipo de publico` = `Gratuidade` quando o preço é nulo; caso contrário, `Pagante`. Com isso, cadeiras cativas, tribuna e gratuidades por lei não entram no público pagante.
7. **Valores oficiais preservados e ocultos.** O resumo financeiro oficial do borderô (`total_utilizado`, `arrecadacao_bruta`, `total_despesas`, `receita_liquida`, entre outros) fica em `dim_partida`, oculto, para conferir os valores calculados a partir das linhas (medidas `Diferença ...`).
8. **Tabela de datas própria.** `dim_data` é criada em DAX (ano, mês e número do mês, trimestre, dia, dia da semana e tipo de dia), com mês e dia da semana em português e ordenação pelo número correspondente. O recurso de data/hora automática está desativado.
9. **Colunas técnicas ocultas.** Chaves (`id_partida`, `chave_ingresso`), `data` e os valores oficiais do resumo ficam ocultos para o relatório usar apenas campos analíticos.

## Dicionário de colunas

### `dim_partida`

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `id_partida` | Inteiro (oculta) | Chave da partida no banco |
| `data` | Data (oculta) | Data da partida; relaciona com `dim_data[Date]` |
| `horario` | Hora | Horário do jogo |
| `rodada` | Texto | Rodada ou fase |
| `nome_adversario` | Texto | Adversário |
| `e_classico` | Booleano | Adversário é clássico |
| `e_clube_g12` | Booleano | Adversário é clube grande do Brasil ou tradicional sul-americano (ver [07](07_metodologia_atributos_partida.md)) |
| `nome_estadio` | Texto | Estádio |
| `capacidade` | Inteiro | Capacidade de referência do estádio |
| `nome_competicao` | Texto | Competição |
| `temporada` | Inteiro | Ano da temporada |
| `importancia_partida` | Decimal | Índice de 0 a 10 |
| `apelo_adversario` | Decimal | Índice de 0 a 10 |
| `feriado` | Booleano | Partida em feriado |
| `dias_desde_ultimo_jogo_maracana` | Inteiro | Intervalo desde o último jogo no Maracanã |
| `posicao_fluminense`, `pontos_fluminense` | Inteiro | Posição e pontos antes da partida |
| `vitorias_ultimos_5`, `empates_ultimos_5`, `derrotas_ultimos_5` | Inteiro | Resultados nos 5 jogos anteriores |
| `gols_marcados_ultimos_5`, `gols_sofridos_ultimos_5` | Inteiro | Gols nos 5 jogos anteriores |
| `Jogo` | Texto (calculada) | `dd/mm` + adversário; ordenada por `data`; usada no eixo dos gráficos por jogo |
| `Classico` | Texto (calculada) | `Sim`/`Não` a partir de `e_classico` |
| `Clubes Grandes` | Texto (calculada) | `Sim`/`Não` a partir de `e_clube_g12` |
| `total_disponivel`, `total_devolvido`, `total_utilizado` | Inteiro (ocultas) | Totais oficiais do borderô |
| `arrecadacao_bruta`, `total_despesas`, `retencoes`, `receita_liquida`, `consignatarios`, `resultado_final`, `complemento_contabil` | Decimal (ocultas) | Valores oficiais do resumo financeiro; usados na conferência. O `complemento_contabil` não é somado à arrecadação (regra do DDL) |

### `dim_ingresso`

| Coluna | Descrição |
| --- | --- |
| `chave_ingresso` (oculta) | Índice criado sobre as combinações distintas |
| `setor` | Setor do estádio; `Sem Setor` quando não informado |
| `tipo de ingresso` | Tipo padronizado (ver decisão 5) |
| `tipo de publico` | `Pagante` ou `Gratuidade` |
| `plano_socio` | Plano de sócio; `Sem Plano` quando não aplicável |

### `fato_ingresso`

`id_partida` e `chave_ingresso` (ocultas), `preco`, `quantidade_disponivel`, `quantidade_devolvida`, `quantidade_utilizada` e `arrecadacao`.

### `fato_despesa`

`id_partida` (oculta), `nome_despesa` (nome original do borderô) e `valor`.

### `dim_data`

`Date` (chave), `Ano`, `Mês nº`, `Mês`, `Trimestre`, `Dia`, `Dia da semana nº`, `Dia da semana` e `Tipo de dia` (`Dia Útil` ou `Fim de semana`).

## Medidas (`_Medidas`)

### Volume e público

| Medida | DAX | Descrição |
| --- | --- | --- |
| `Partidas` | `COUNTROWS(dim_partida)` | Número de partidas |
| `Público Presente` | `SUM(fato_ingresso[quantidade_utilizada])` | Soma da quantidade utilizada |
| `Público Pagante` | `CALCULATE([Público Presente], dim_ingresso[tipo de publico] = "Pagante")` | Presentes com ingresso de preço informado |
| `Gratuidades` | `CALCULATE([Público Presente], dim_ingresso[tipo de publico] = "Gratuidade")` | Presentes sem preço informado |
| `% Gratuidades` | `DIVIDE([Gratuidades], [Público Presente])` | Participação das gratuidades |
| `Público Médio por Jogo` | `AVERAGEX(dim_partida, [Público Presente])` | Média por partida |
| `Ocupação` | `DIVIDE([Público Presente], SUMX(dim_partida, dim_partida[capacidade]))` | Público sobre a capacidade de referência (ver pendências) |

### Financeiro

| Medida | DAX | Descrição |
| --- | --- | --- |
| `Arrecadação` | `SUM(fato_ingresso[arrecadacao])` | Arrecadação das linhas de ingresso |
| `Total Despesas` | `SUM(fato_despesa[valor])` | Soma das despesas do borderô |
| `Receita Líquida` | `[Arrecadação] - [Total Despesas]` | Arrecadação menos despesas |
| `Margem Líquida` | `DIVIDE([Receita Líquida], [Arrecadação])` | Receita líquida sobre arrecadação |
| `Despesa sobre Arrecadação` | `DIVIDE([Total Despesas], [Arrecadação])` | Peso das despesas |
| `Ticket Médio` | `DIVIDE([Arrecadação], [Público Pagante])` | Arrecadação por **pagante** (não por presente) |
| `Receita por Presente` | `DIVIDE([Receita Líquida], [Público Presente])` | Receita líquida por pessoa presente |
| `Arrecadação Média por Jogo` | `AVERAGEX(dim_partida, [Arrecadação])` | Média por partida |
| `Despesa Média por Jogo` | `AVERAGEX(dim_partida, [Total Despesas])` | Média por partida |
| `Receita Líquida Média por Jogo` | `AVERAGEX(dim_partida, [Receita Líquida])` | Média por partida |

### Conferência com os valores oficiais

| Medida | DAX | Resultado esperado |
| --- | --- | --- |
| `Despesas Oficial` | `SUM(dim_partida[total_despesas])` | Total oficial dos borderôs |
| `Diferença Despesas` | `[Total Despesas] - [Despesas Oficial]` | 0 |
| `Diferença Público` | `[Público Presente] - SUM(dim_partida[total_utilizado])` | 0 |
| `Diferença Arrecadação` | `[Arrecadação] - SUM(dim_partida[arrecadacao_bruta])` | 0 |
| `Diferença Receita Líquida` | `[Receita Líquida] - SUM(dim_partida[receita_liquida])` | −R$ 12,00 na temporada 2026 (ver validação) |

## Validação (temporada 2026, 31 partidas)

Totais calculados a partir das planilhas de `data/interim/` e confrontados com os resultados do relatório:

| Indicador | Valor |
| --- | --- |
| Público presente | 868.685 |
| Público pagante | 797.601 |
| Gratuidades | 71.084 (8,18%) |
| Arrecadação | R$ 43.682.279,00 |
| Total de despesas | R$ 30.278.271,37 |
| Receita líquida (arrecadação − despesas) | R$ 13.404.007,63 |
| Ticket médio (arrecadação ÷ pagantes) | R$ 54,77 |

- Público, arrecadação e despesas coincidem com os totais oficiais transcritos dos borderôs em todas as 31 partidas.
- A única diferença na receita líquida é de R$ 12,00, em Fluminense x Flamengo (12/04/2026): o valor oficial é R$ 1.920.535,90 e arrecadação − despesas resulta em R$ 1.920.523,90. A divergência está registrada e não foi corrigida, porque o valor oficial não deve ser substituído por cálculo próprio.
- O total oficial de receita líquida é R$ 13.404.019,63. Descontados os consignatários (R$ 539.658,51), o resultado final oficial é R$ 12.864.397,12.

## Relatório

**Página 1 — Resumo Temporada 2026**

| Visual | Campos |
| --- | --- |
| Cartões | `Ticket Médio`, `Público Presente`, `Arrecadação`, `Total Despesas`, `Receita Líquida` |
| Gráfico de colunas e linha | Eixo: `dim_partida[Jogo]`; colunas: `Público Presente`; linha: `Receita Líquida` |
| Segmentadores | `nome_competicao`, `Classico`, `Clubes Grandes` e `dim_data[Mês]` |

**Página 2 — Tooltip "Público e Receita por Jogo":** cartão por `nome_adversario` com `Público Presente`, `Receita Líquida` e `Ticket Médio`, usado como dica de ferramenta do gráfico por jogo.

Captura da página 1: [dashboard_resumo_temporada_2026.jpg](../images/dashboard_resumo_temporada_2026.jpg).

## Pendências e pontos de atenção

- **Ocupação:** a medida usa `capacidade` do estádio como denominador. A capacidade efetiva varia por partida; validar e documentar o denominador antes de publicar a medida (ver [03_dicionario_dados.md](03_dicionario_dados.md)).
- **Receita líquida × resultado final:** o cartão "Receita Líquida" corresponde à receita líquida do borderô, antes dos consignatários. Se a análise precisar do que o clube efetivamente retém, avaliar uma medida com o resultado final.
- **Ticket médio:** é calculado sobre o público pagante. Deixar isso explícito no rótulo do cartão evita comparação indevida com o público presente.
- **Feriado:** hoje vem de `contexto_partida` e fica em `dim_partida`. Se o projeto passar a ter várias temporadas, avaliar mover o atributo para `dim_data`.
- **Novas temporadas:** `dim_data` acompanha o menor e o maior ano de `dim_partida[data]`. Novos adversários precisam ser classificados quanto a clássico e G12 pelo mesmo critério.
- **Fonte externa de sócios:** a série mensal de sócios ainda não foi integrada ao modelo.
- **Análises ainda não construídas:** preço × demanda, composição por setor e categoria, e relação do público com apelo, importância, desempenho e feriado. Os campos já estão disponíveis em `dim_partida`.

## Arquivos no repositório

Em `powerbi/` estão o `.pbix`, o `.pbit` e o projeto `.pbip` (pastas `.Report` e `.SemanticModel`). O `.pbip` guarda o modelo e o relatório em texto (TMDL e PBIR), o que permite revisar mudanças de medidas e de relatório no Git.

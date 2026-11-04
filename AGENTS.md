
# AGENTS.md — Análise de Borderôs do Fluminense FC

## 1. Objetivo do projeto

Desenvolver uma base de dados relacional a partir dos borderôs oficiais das partidas do Fluminense FC como mandante.

O projeto busca permitir análises sobre:
- Público presente e ingressos comercializados.
- Arrecadação e preço médio dos ingressos.
- Distribuição de ingressos por setor, categoria e plano de sócio.
- Despesas e receitas das partidas.
- Influência de fatores esportivos e contextuais sobre público e arrecadação.

O projeto utiliza Python, pandas, MySQL e Power BI.

## 2. Tecnologias e ambiente

- Python para extração, transformação e carga dos dados.
- pandas para manipulação dos DataFrames.
- openpyxl para leitura de arquivos Excel.
- MySQL Community Server 8.0 como banco de dados.
- mysql-connector-python para conexão com o banco.
- python-dotenv para gerenciamento de variáveis de ambiente.
- Power BI para análise e visualização dos dados.

O banco utilizado é `analise_bordero_fluminense`.

As credenciais de conexão devem ser carregadas do arquivo `.env`. Nunca inserir credenciais diretamente nos scripts ou publicá-las no GitHub.

## 3. Estrutura dos dados de origem

Os PDFs originais estão em `data/raw/`.

As planilhas Excel transcritas e revisadas estão em `data/interim/`.

Cada planilha de partida possui as seguintes abas:

- LEIA-ME
- PARTIDA
- INGRESSOS
- DESPESAS
- RESUMO
- CONTEXTO
- ATRIBUTOS
- DESEMPENHO

### Cabeçalhos das planilhas

Respeitar rigorosamente os parâmetros de leitura definidos:

- PARTIDA: `header=3`
- INGRESSOS: `header=5`
- DESPESAS: `header=5`

A configuração `header=5` para INGRESSOS e DESPESAS foi testada e confirmada pelo responsável pelo projeto. Não sugerir sua alteração sem uma justificativa concreta baseada na estrutura da planilha.

As abas possuem estruturas diferentes. Não presumir que todas podem ser lidas com a mesma configuração.

## 4. Regras de qualidade e tratamento dos dados

### Preservação dos dados originais

- Preservar a descrição original dos borderôs.
- Não corrigir automaticamente nomes, valores ou classificações sem verificar a fonte.
- Não inventar informações ausentes.
- Quando necessário, consultar o PDF original antes de corrigir uma transcrição.

### Tratamento de valores ausentes

A distinção entre `NULL` e zero é fundamental:

- `NULL`: informação ausente, não especificada ou não aplicável.
- `0`: valor explicitamente igual a zero na fonte.

Nunca substituir indiscriminadamente valores ausentes por zero.

Não criar classificações artificiais como "Não informado" para preencher dimensões ausentes.

### Integridade

- Respeitar PKs e FKs.
- Respeitar as restrições UNIQUE e CHECK do banco.
- Não incluir no INSERT colunas geradas automaticamente pelo MySQL.
- Validar os dados antes de realizar cargas.
- Verificar os resultados após cada inserção.

## 5. Modelagem do banco

O banco possui 15 tabelas, organizadas para representar partidas, dimensões de referência, ingressos, despesas, resumos financeiros e informações contextuais e esportivas.

Consultar os documentos existentes em `docs/` e o DDL do projeto antes de propor alterações na modelagem.

Decisões importantes:

- `ingresso_partida.descricao_original` preserva a descrição literal do borderô.
- `id_setor`, `id_categoria` e `id_plano` podem ser NULL.
- `preco` e `arrecadacao` podem ser NULL.
- A tabela `despesa_partida` armazena a despesa associada à partida, com nome e valor.
- Não existe uma tabela `TIPO_DESPESA` na modelagem atual.
- A tabela `RESUMO_FINANCEIRO_PARTIDA` armazena os valores oficiais para conferência dos totais calculados.
- `resumo_financeiro_partida.consignatarios` armazena o valor oficial destinado às instituições consignatárias, descontado da receita líquida quando o resultado é positivo; preservar NULL quando não informado.

As colunas geradas `id_setor_chave`, `id_categoria_chave` e `id_plano_chave` são utilizadas pelo MySQL para permitir restrições de unicidade envolvendo valores NULL. Não devem ser incluídas nos INSERTs.

## 6. Organização do código ETL

O código de leitura e preparação está em:

`scripts/etl/leitura_excel.py`

O ETL deve ser desenvolvido de forma incremental, organizado por etapas:

1. Localização e validação dos arquivos.
2. Leitura das planilhas.
3. Validação das estruturas e dos dados.
4. Transformação e normalização.
5. Recuperação dos IDs das dimensões.
6. Preparação dos registros para inserção.
7. Carga no MySQL.
8. Conferência dos dados carregados.

Cada aba deve ter seu próprio tratamento, respeitando sua estrutura.

Utilizar `copy()` ao preparar DataFrames derivados e preservar os DataFrames originais sempre que possível.

Antes de inserir no MySQL, converter valores ausentes de pandas para `None`, quando apropriado, para que sejam gravados como SQL NULL.

## 7. Cuidados com a carga no banco

O processo de carga deve evitar duplicações.

Não executar novamente uma rotina de INSERT sem antes verificar se os registros já existem.

Priorizar operações incrementais e idempotentes, especialmente para:
- Dimensões.
- Partidas.
- Ingressos.
- Despesas.
- Resumos financeiros.

Não presumir que IDs AUTO_INCREMENT serão iguais entre diferentes execuções ou ambientes. Recuperar IDs por consultas ao banco ou utilizar mecanismos apropriados de integridade.

Sempre conferir a quantidade de registros e os totais após uma carga.

## 8. Estado atual do desenvolvimento

O banco MySQL foi criado e as tabelas foram implementadas.

A conexão Python com o MySQL já foi testada com sucesso.

A leitura e a preparação dos dados da aba INGRESSOS foram desenvolvidas para uma partida.

A carga de 44 registros de ingressos foi executada para `id_partida = 2`, correspondente ao jogo Fluminense x Athletico Paranaense, em 15/03/2026.

A inserção foi confirmada por consultas SELECT, incluindo a preservação de valores NULL.

A carga de 17 registros da aba DESPESAS foi executada para `id_partida = 2` e conferida pela quantidade e pelo total.

### Próxima etapa

Continuar o ETL pela aba RESUMO da mesma partida (`id_partida = 2`), após atualizar o esquema MySQL para incluir `consignatarios`.

Antes da carga, verificar a estrutura real da tabela com:

```sql
DESCRIBE resumo_financeiro_partida;
```

`consignatarios` é um valor oficial da aba RESUMO, distinto de `retencoes`. Deve ser transcrito, não calculado; preservar NULL quando ausente e não tratar automaticamente como zero. `soma_das_linhas`, `diferenca_soma_menos_oficial` e `observacao` são informações de conferência e não integram a tabela relacional atual.

Não desenvolver o INSERT antes de conferir a estrutura real da tabela e verificar se já existe resumo para a partida.

## 9. Como trabalhar com o responsável pelo projeto

O responsável está desenvolvendo o projeto com objetivo de aprender e compreender cada etapa.

Portanto:

- Trabalhar uma etapa por vez.
- Explicar o propósito e a lógica das operações.
- Evitar entregar grandes scripts completos sem necessidade.
- Priorizar orientações para que o responsável escreva e compreenda o próprio código.
- Quando houver dúvidas, solicitar os resultados dos comandos ou trechos de código relevantes.
- Revisar o código escrito pelo responsável e explicar possíveis melhorias.
- Não alterar decisões anteriores sem apresentar justificativa e solicitar concordância.
- Não inventar dados, resultados, funcionalidades ou experiências que não estejam documentados.

Ao modificar arquivos, preservar a estrutura e o estilo já utilizados no projeto.

Antes de alterações relevantes no banco, revisar o DDL e os documentos de modelagem.

## 10. Documentação

Consultar os documentos existentes em `docs/`, especialmente:

- `docs/03_dicionario_dados.md`
- `docs/04_modelagem.md`

A documentação deve refletir a implementação real. Não documentar funcionalidades que ainda não foram implementadas como se estivessem concluídas.


## 11. Idioma e comunicação

- Toda comunicação com o responsável pelo projeto deve ser feita em português brasileiro (pt-BR).
- Explicações, orientações, análises, comentários e recomendações devem ser escritos em português.
- Manter nomes de bibliotecas, funções, métodos, variáveis, comandos, mensagens de erro e termos técnicos em seu idioma original quando necessário.
- Quando apresentar mensagens de erro em inglês, explicar seu significado em português.
- Não alternar para inglês sem solicitação explícita do responsável.
- Utilizar linguagem didática, clara e objetiva, considerando que o objetivo também é aprender as tecnologias utilizadas.

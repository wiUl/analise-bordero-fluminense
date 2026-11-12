
# AGENTS.md — Análise de Borderôs do Fluminense FC

## 1. Objetivo do projeto

Desenvolver uma base de dados relacional e uma camada analítica a partir dos borderôs oficiais das partidas do Fluminense FC como mandante, para entender o público e a arrecadação e identificar o que pode aumentar o público sem prejudicar as receitas.

O projeto busca permitir análises sobre:
- Público presente e ingressos comercializados.
- Arrecadação e preço médio dos ingressos.
- Distribuição de ingressos por setor, categoria e plano de sócio.
- Despesas e receitas das partidas.
- Influência de fatores esportivos e contextuais sobre público e arrecadação.

O projeto utiliza Python, pandas, MySQL e Power BI. A amostra atual é a temporada 2026 (31 partidas como mandante); há a intenção de ampliar para temporadas anteriores.

## 2. Tecnologias e ambiente

- Python para extração, transformação e carga dos dados.
- pandas para manipulação dos DataFrames.
- openpyxl para leitura de arquivos Excel.
- MySQL Community Server 8.0 como banco de dados.
- mysql-connector-python para conexão com o banco.
- python-dotenv para gerenciamento de variáveis de ambiente.
- Power BI para modelagem dimensional, medidas DAX e dashboards. O projeto está versionado em `powerbi/` nos formatos `.pbix`, `.pbit` e `.pbip` (modelo em TMDL e relatório em PBIR).
- As dependências Python estão em `requirements.txt` (UTF-8).

O banco utilizado é `analise_bordero_fluminense`.

As credenciais de conexão devem ser carregadas do arquivo `.env`. Nunca inserir credenciais diretamente nos scripts ou publicá-las no GitHub. O modelo das variáveis está em `.env.example`. O `.gitignore` cobre `.env`, `__pycache__/`, `*.py[cod]`, `**/.pbi/localSettings.json` e `**/.pbi/cache.abf`.

## 3. Estrutura dos dados de origem

Os PDFs originais estão em `data/raw/` (31 borderôs, um por partida). Não manter ali arquivos que não sejam borderôs nem duplicados.

As planilhas Excel transcritas e revisadas estão em `data/interim/` (31 planilhas, uma por partida). `data/processed/` está reservada e não é usada pelo ETL atual.

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

O banco possui 15 tabelas, organizadas para representar partidas, dimensões de referência, ingressos, despesas, resumos financeiros e informações contextuais e esportivas. O DDL vigente é `database/schema_mysql_analise_bordero_fluminense.sql`; não há outro arquivo de DDL.

Consultar os documentos existentes em `docs/` e o DDL do projeto antes de propor alterações na modelagem.

Decisões importantes:

- `ingresso_partida.descricao_original` preserva a descrição literal do borderô.
- `id_setor`, `id_categoria` e `id_plano` podem ser NULL.
- `preco` e `arrecadacao` podem ser NULL.
- A tabela `despesa_partida` armazena a despesa associada à partida, com nome e valor.
- Não existe uma tabela `TIPO_DESPESA` na modelagem atual.
- A tabela `RESUMO_FINANCEIRO_PARTIDA` armazena os valores oficiais para conferência dos totais calculados.
- `resumo_financeiro_partida.consignatarios` armazena o valor oficial destinado às instituições consignatárias, descontado da receita líquida quando o resultado é positivo; preservar NULL quando não informado.

- Na camada Power BI (não no banco), setor e plano sem informação aparecem como `Sem Setor` e `Sem Plano`, apenas para formar chaves únicas na dimensão de ingressos. No banco, o `NULL` é preservado.
- `e_clube_g12` marca os clubes grandes do Brasil e, fora do país, os clubes tradicionais sul-americanos. "G12" é um rótulo do projeto, exibido como "Clubes Grandes" no dashboard. Ver `docs/07_metodologia_atributos_partida.md`.

As colunas geradas `id_setor_chave`, `id_categoria_chave` e `id_plano_chave` são utilizadas pelo MySQL para permitir restrições de unicidade envolvendo valores NULL. Não devem ser incluídas nos INSERTs.

## 6. Organização do código ETL

O código do ETL está em:

- `scripts/main.py` — orquestração; carrega uma planilha por transação.
- `scripts/etl/leitura_excel.py` — localização, validação das abas e leitura.
- `scripts/etl/normalizacao.py` — normalização de espaços e textos.
- `scripts/etl/preparacao.py` — preparação dos registros de cada aba.
- `scripts/etl/banco_mysql.py` — conexão, recuperação e cadastro de referências, inserções e conferência.

Execução, a partir da raiz do repositório e com o `.env` configurado:

- `python -m scripts.main --arquivo "data\interim\NOME.xlsx"` para uma planilha;
- `python -m scripts.main --lote` para todas as planilhas de `data/interim/`.

É obrigatório escolher um dos modos.

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

Sempre conferir a quantidade de registros e os totais após uma carga. O ETL verifica as contagens existentes antes de inserir (carrega se vazio, ignora se completo e avisa se parcial); essa verificação compara contagens, não o conteúdo.

## 8. Estado atual do desenvolvimento

### Concluído

- Coleta dos borderôs de 31 partidas da temporada 2026 (PDFs em `data/raw/`) e transcrição revisada em planilhas (`data/interim/`).
- Banco MySQL criado, com 15 tabelas, e conexão Python testada.
- ETL completo, com tratamento de todas as abas (PARTIDA, INGRESSOS, DESPESAS, RESUMO, CONTEXTO, ATRIBUTOS e DESEMPENHO), execução por arquivo ou em lote e transação por planilha.
- Carga das 31 partidas no MySQL.
- Conferência sistemática: a soma das linhas coincide com os totais oficiais de arrecadação, despesas e público nas 31 partidas. A única divergência é de R$ 12,00 na receita líquida de Fluminense x Flamengo (12/04/2026); ela está registrada e não deve ser "corrigida" sem consultar o PDF.
- Modelo dimensional no Power BI (`dim_partida`, `dim_ingresso`, `dim_data`, `fato_ingresso`, `fato_despesa`, `_Medidas`), documentado em `docs/05_modelo_powerbi.md`.
- Primeira página do dashboard: Resumo Temporada 2026, com página de tooltip.
- Definição de G12 documentada.

### Pendente

- Revisão cruzada das transcrições contra os PDFs.
- Integração de fontes complementares (por exemplo, série de sócios).
- Validação da capacidade do estádio como denominador da ocupação.
- Demais páginas do dashboard e análises de preço × demanda, composição de público e contexto.
- Definição do período da amostra e eventual inclusão de temporadas anteriores.
- Teste de instalação limpa a partir do repositório.

### Indicadores e definições em uso

- **Público presente:** soma de `quantidade_utilizada`.
- **Público pagante:** linhas com preço informado. Linhas com preço `NULL` (cadeiras cativas, tribuna, gratuidades por lei) são gratuidades.
- **Ticket médio:** arrecadação dividida pelo público pagante.
- **Receita líquida:** arrecadação menos despesas, equivalente à receita líquida do borderô, antes dos consignatários.
- Os valores oficiais do resumo financeiro servem para conferir os cálculos; não substituí-los por valores calculados.

### Próxima etapa

Escolher com o responsável a próxima frente, em geral uma destas: validar a ocupação, iniciar as páginas de análise do dashboard ou fazer a revisão cruzada com os PDFs. Antes de alterar o modelo do Power BI, consultar `docs/05_modelo_powerbi.md`.

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

- `docs/03_dicionario_dados.md` — dicionário do banco.
- `docs/04_modelagem.md` — modelagem relacional.
- `docs/05_modelo_powerbi.md` — modelo dimensional, decisões, medidas DAX e relatório.
- `docs/07_metodologia_atributos_partida.md` — critérios de importância, apelo, clássico e G12.
- `database/README.md` — uso do DDL.
- `README.md` — visão geral, fluxo, estrutura do repositório e roadmap; atualizar quando o estado do projeto mudar.

A documentação deve refletir a implementação real. Ao mudar o modelo do Power BI, as medidas ou o banco, atualizar o documento correspondente e o roadmap do README. Não documentar funcionalidades que ainda não foram implementadas como se estivessem concluídas.


## 11. Idioma e comunicação

- Toda comunicação com o responsável pelo projeto deve ser feita em português brasileiro (pt-BR).
- Explicações, orientações, análises, comentários e recomendações devem ser escritos em português.
- Manter nomes de bibliotecas, funções, métodos, variáveis, comandos, mensagens de erro e termos técnicos em seu idioma original quando necessário.
- Quando apresentar mensagens de erro em inglês, explicar seu significado em português.
- Não alternar para inglês sem solicitação explícita do responsável.
- Utilizar linguagem didática, clara e objetiva, considerando que o objetivo também é aprender as tecnologias utilizadas.

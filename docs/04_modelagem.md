# Modelagem de Dados

## Objetivo e escopo

Este documento descreve o modelo lógico relacional do projeto de análise de borderôs do Fluminense FC. O banco principal do projeto é uma instância local do **MySQL 8**, utilizada para armazenar os dados estruturados que serão tratados, analisados em SQL e consumidos pelo Power BI.

O projeto utilizou inicialmente o Supabase com PostgreSQL durante a prototipagem. A decisão atual é adotar MySQL local como banco principal, aproveitando a instalação disponível no ambiente de desenvolvimento. O DDL vigente está em [`database/schema_mysql_analise_bordero_fluminense.sql`](../database/schema_mysql_analise_bordero_fluminense.sql).

O princípio adotado é representar cada conceito de negócio em sua própria entidade quando isso evita dependências indevidas e duplicação, sem criar tabelas artificiais apenas para aumentar o grau de normalização.

## Diagrama entidade-relacionamento

O DER vigente é a imagem exportada do dbdiagram.io:

![Diagrama entidade-relacionamento do projeto](../images/DER%20-%20Fluminense_border%C3%B4.png)

O diagrama deve ser considerado em conjunto com este documento, com o [dicionário de dados](03_dicionario_dados.md) e com o DDL MySQL. O DDL é a implementação efetiva das chaves, restrições e regras de integridade; em caso de alteração do esquema, os três artefatos devem ser revisados em conjunto.

## Estrutura lógica

### PARTIDA

Entidade central, representando cada partida do Fluminense como mandante. Armazena data, horário, rodada/fase e as referências ao adversário, à edição da competição e ao estádio.

A coluna `competicao_temporada_id` referencia `COMPETICAO_TEMPORADA`, não diretamente `COMPETICAO`.

### ADVERSARIO

Registra cada adversário uma única vez, por nome padronizado, incluindo os indicadores `e_classico` e `e_clube_g12`. Esses campos representam classificações do adversário segundo os critérios documentados pelo projeto. O índice `apelo_adversario` não está nesta tabela porque pode variar conforme o contexto histórico de cada partida e é avaliado em `ATRIBUTOS_PARTIDA`.

### COMPETICAO, TEMPORADA e COMPETICAO_TEMPORADA

- `COMPETICAO` identifica a competição por seu nome.
- `TEMPORADA` identifica o ano/temporada.
- `COMPETICAO_TEMPORADA` relaciona uma competição à temporada em que ocorre.

A combinação `(id_competicao, id_temporada)` deve ser única. Essa separação impede misturar a identidade de uma competição com uma edição específica e permite registrar a mesma competição em várias temporadas.

### ESTADIO

Armazena nome e informações de localização, além de uma capacidade de referência. A capacidade efetiva pode variar conforme a configuração da partida; antes de calcular ocupação, a capacidade escolhida como denominador deverá ser validada e documentada.

### SETOR, CATEGORIA_INGRESSO e PLANO_SOCIO

São entidades de referência para padronizar os nomes usados nos borderôs. O plano de sócio é opcional para uma linha de ingresso. Setor e categoria também podem ser `NULL` quando o borderô não especifica essas classificações para determinada linha.

### INGRESSO_PARTIDA

Cada registro corresponde a uma linha de ingresso de uma partida. Quando informados pela fonte, setor, categoria e plano de sócio são relacionados às respectivas entidades de referência. O preço pertence à oferta específica naquela partida, não permanentemente ao setor ou ao plano.

A tabela mantém `descricao_original`, campo obrigatório que preserva a descrição literal apresentada no borderô. Esse campo é importante porque há linhas cuja descrição não permite identificar com segurança um setor ou uma categoria. Nesses casos, `id_setor` e/ou `id_categoria` permanecem `NULL`; não se deve inventar uma classificação para preencher a ausência.

A tabela também registra preço, quantidade disponível, quantidade devolvida, quantidade utilizada e arrecadação. Os valores e a nomenclatura da fonte devem ser preservados antes de qualquer derivação.

Os campos de classificação, preço e arrecadação podem ser nulos quando a informação não é aplicável ou não está disponível no borderô. `NULL` não deve ser convertido automaticamente em zero: zero representa um valor explicitamente informado como zero.

A regra de unicidade considera a partida, os identificadores de setor, categoria e plano e a descrição original. Como os identificadores de classificação podem ser nulos, o DDL MySQL utiliza colunas geradas que substituem esses nulos por um valor sentinela para compor a restrição `UNIQUE`. Essas colunas auxiliares são geradas pelo banco e não devem receber valores diretamente nas operações de carga.

### DESPESA_PARTIDA

Armazena cada linha de despesa apresentada no borderô, mantendo `nome` conforme a nomenclatura da fonte e seu `valor`. Não há uma tabela `TIPO_DESPESA` no modelo atual. Classificações analíticas de despesas poderão ser criadas na camada de transformação caso sejam necessárias.

### RESUMO_FINANCEIRO_PARTIDA

Relação 1:1 com `PARTIDA`, identificada por `id_partida`, para registrar totais consolidados oficiais do borderô: ingressos disponíveis, devolvidos e utilizados; arrecadação bruta; despesas; retenções; receita líquida; resultado final; e complemento contábil, quando informado.

Esta tabela é deliberadamente mantida separada dos detalhes. Sua função é possibilitar reconciliação e auditoria entre os totais oficiais e os valores calculados a partir das linhas de ingresso e despesa. Diferenças devem ser investigadas, não ajustadas automaticamente. `complemento_contabil` não deve ser somado automaticamente à arrecadação de ingressos.

### CONTEXTO_PARTIDA

Armazena circunstâncias objetivas da partida: se a data é feriado segundo o critério adotado e quantos dias se passaram desde o último jogo do Fluminense no Maracanã. Dia da semana e mês podem ser derivados da data. O intervalo desde o jogo anterior é uma variável derivada que deverá seguir uma regra consistente de cálculo.

### ATRIBUTOS_PARTIDA

Armazena os índices avaliativos específicos da partida:

- `importancia_partida`: índice analítico de 0 a 10 para a importância esportiva da partida naquele momento;
- `apelo_adversario`: índice analítico de 0 a 10 para o potencial de interesse associado ao adversário no contexto histórico da partida.

São variáveis construídas pelo projeto, não valores oficiais do borderô. Os critérios de pontuação devem ser estabelecidos antes de analisar público e receita, para reduzir o risco de incorporar o resultado observado à definição dos índices.

### DESEMPENHO_PARTIDA

Armazena o recorte pré-jogo do desempenho do Fluminense: posição e pontos, quando aplicáveis, além dos resultados e gols dos cinco jogos anteriores. As variáveis devem representar apenas informação disponível antes da partida analisada. Em competições ou fases sem tabela por pontos, posição e pontos podem ser `NULL`, não zero.

## Série histórica de sócios

A série mensal de sócios adimplentes e inadimplentes será inicialmente tratada como fonte externa para o Power BI. Ela não integra as tabelas do modelo relacional atual.

## Normalização e integridade

O modelo foi organizado para atender à 3FN, sob as dependências funcionais assumidas: atributos descritivos dependem da chave da entidade a que pertencem; competição e temporada são separadas de sua associação; e dados de partidas, ofertas de ingresso, despesas e resumo oficial têm granularidades distintas.

Não foi identificada, no escopo atual, necessidade de criar relações adicionais apenas para alegar 4FN ou 5FN. A implementação MySQL contempla chaves primárias e estrangeiras, restrições de unicidade e validações de domínio. Entre as regras importantes estão:

- unicidade dos nomes nas entidades de referência;
- unicidade de `(id_competicao, id_temporada)` em `COMPETICAO_TEMPORADA`;
- unicidade das linhas de `INGRESSO_PARTIDA`, inclusive quando os identificadores de setor, categoria ou plano são `NULL`, por meio de colunas geradas;
- preservação de `descricao_original` para distinguir linhas do borderô cuja classificação não está especificada;
- faixas válidas para os índices de 0 a 10 e para indicadores booleanos;
- validações para quantidades não negativas, sem alterar os valores de origem silenciosamente.

A manutenção do resumo financeiro oficial é uma redundância documental intencional para reconciliação, não uma tentativa de substituir as linhas detalhadas.

## Documentos relacionados

- [Dicionário de dados](03_dicionario_dados.md)
- [Metodologia dos atributos da partida](07_metodologia_atributos_partida.md)
- [Imagem do DER](../images/DER%20-%20Fluminense_border%C3%B4.png)
- [DDL MySQL](../database/schema_mysql_analise_bordero_fluminense.sql)

## Próxima etapa

A próxima etapa do desenvolvimento é concluir a implementação do ETL para carregar as informações das planilhas de cada borderô no banco MySQL, mantendo a rastreabilidade da fonte e validando os dados carregados contra os totais oficiais.

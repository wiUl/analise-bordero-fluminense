# Modelagem de Dados

## Objetivo e escopo

Este documento descreve o modelo lógico relacional do projeto de análise de borderôs do Fluminense FC. O modelo será implementado no PostgreSQL e servirá de base para tratamento, análises e consumo pelo Power BI.

O princípio adotado é representar cada conceito de negócio em sua própria entidade quando isso evita dependências indevidas e duplicação, sem criar tabelas artificiais apenas para aumentar o grau de normalização.

## Diagrama entidade-relacionamento

O DER vigente é a imagem exportada do dbdiagram.io:

![Diagrama entidade-relacionamento do projeto](../images/DER%20-%20Fluminense_border%C3%B4.png)

O desenho deve ser considerado em conjunto com este documento e com o [dicionário de dados](03_dicionario_dados.md). O DDL ainda será implementado em `database/schema.sql`; portanto, restrições de unicidade, validações de domínio e demais regras devem ser confirmadas na implementação.

## Estrutura lógica

### PARTIDA

Entidade central, representando cada partida do Fluminense como mandante. Armazena data, horário, rodada/fase e as referências ao adversário, à edição da competição e ao estádio.

A coluna `competicao_temporada_id` referencia `COMPETICAO_TEMPORADA`, não diretamente `COMPETICAO`.

### ADVERSARIO

Registra cada adversário uma única vez, por nome padronizado, incluindo os indicadores `e_classico` e `e_clube_g12`. Esses campos representam classificações do adversário segundo os critérios documentados pelo projeto. O índice `apelo_adversario` não está nesta tabela porque pode variar ao longo do tempo e é avaliado no contexto de cada partida.

### COMPETICAO, TEMPORADA e COMPETICAO_TEMPORADA

- `COMPETICAO` identifica a competição por seu nome.
- `TEMPORADA` identifica o ano/temporada.
- `COMPETICAO_TEMPORADA` relaciona uma competição à temporada em que ocorre.

A combinação `(id_competicao, id_temporada)` deve ser única. Essa separação impede misturar a identidade de uma competição com uma edição específica e permite registrar a mesma competição em várias temporadas.

### ESTADIO

Armazena nome e informações de localização, além de uma capacidade de referência. A capacidade efetiva pode variar conforme a configuração da partida; antes de calcular ocupação, a capacidade escolhida como denominador deverá ser validada e documentada.

### SETOR, CATEGORIA_INGRESSO e PLANO_SOCIO

São entidades de referência para padronizar os nomes usados nos borderôs. O plano de sócio é opcional para uma linha de ingresso; `id_plano` pode ser `NULL` quando não se aplica.

### INGRESSO_PARTIDA

Cada registro corresponde a uma combinação de partida, setor, categoria e, quando aplicável, plano de sócio. O preço pertence à oferta específica naquela partida, não permanentemente ao setor ou ao plano.

A tabela registra preço, quantidade disponível, quantidade devolvida, quantidade utilizada e arrecadação. Os valores e a nomenclatura da fonte devem ser preservados antes de qualquer derivação.

A combinação de negócio `(id_partida, id_setor, id_categoria, id_plano)` não deve gerar duplicidades. Como `id_plano` é opcional, a implementação SQL deve tratar explicitamente a unicidade quando esse campo for `NULL`.

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

Não foi identificada, no escopo atual, necessidade de criar relações adicionais apenas para alegar 4FN ou 5FN. A avaliação final da integridade depende de materializar as regras em `schema.sql`, incluindo:

- chaves primárias e estrangeiras;
- unicidade dos nomes nas entidades de referência;
- unicidade de `(id_competicao, id_temporada)` em `COMPETICAO_TEMPORADA`;
- unicidade da combinação de negócio de `INGRESSO_PARTIDA`, inclusive quando `id_plano` é `NULL`;
- faixas válidas para os índices de 0 a 10 e para indicadores booleanos;
- validações para quantidades não negativas, sem alterar os valores de origem silenciosamente.

A manutenção do resumo financeiro oficial é uma redundância documental intencional para reconciliação, não uma tentativa de substituir as linhas detalhadas.

## Documentos relacionados

- [Dicionário de dados](03_dicionario_dados.md)
- [Metodologia dos atributos da partida](07_metodologia_atributos_partida.md)
- [Imagem do DER](../images/DER%20-%20Fluminense_border%C3%B4.png)

## Próxima etapa

Com a especificação e a documentação alinhadas, a próxima fase é implementar o DDL em `database/schema.sql`, testar as restrições em uma instância PostgreSQL e validar o modelo com um pequeno conjunto de borderôs antes de ampliar a coleta.

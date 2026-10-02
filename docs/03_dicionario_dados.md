# Dicionário de Dados

Este documento descreve as tabelas e os campos definidos para a estruturação dos dados do projeto.

## Convenções

- PK = chave primária.
- FK = chave estrangeira.
- NULL significa que o valor não se aplica ou não está disponível segundo a regra documentada; não significa automaticamente zero.
- Valores monetários serão armazenados com precisão decimal adequada.
- Nomes de despesas devem preservar a nomenclatura apresentada no borderô.

## 1. PARTIDA

Representa o evento esportivo e é a entidade central do modelo.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_partida` | INT | Sim | Interno | Identificador único. PK. |
| `data` | DATE | Sim | Borderô/fonte oficial | Data da partida. |
| `horario` | TIME | Não | Fonte complementar | Horário da partida. |
| `adversario_id` | INT | Sim | Fonte oficial | FK para ADVERSARIO. |
| `competicao_id` | INT | Sim | Fonte oficial | FK para COMPETICAO. |
| `estadio_id` | INT | Sim | Fonte oficial | FK para ESTADIO. |
| `rodada` | VARCHAR | Não | Fonte oficial/complementar | Rodada, fase ou identificação equivalente. |

## 2. ADVERSARIO

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_adversario` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Fonte oficial | Nome padronizado do adversário. |

## 3. COMPETICAO

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_competicao` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Fonte oficial | Nome da competição. |
| `temporada` | INT | Não | Fonte oficial/complementar | Temporada/ano de referência. |

## 4. ESTADIO

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_estadio` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Fonte oficial | Nome do estádio. |
| `cidade` | VARCHAR | Não | Fonte complementar | Cidade. |
| `estado` | VARCHAR | Não | Fonte complementar | Estado/UF. |
| `pais` | VARCHAR | Não | Fonte complementar | País. |
| `capacidade` | INT | Não | Fonte complementar | Capacidade adotada para análises de ocupação. |

## 5. SETOR

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_setor` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Borderô | Nome padronizado do setor. |

## 6. CATEGORIA_INGRESSO

Representa a categoria comercial do ingresso.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_categoria` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Borderô | Categoria, como inteira, meia ou sócio. |

## 7. PLANO_SOCIO

Detalha o plano de sócio quando aplicável.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_plano` | INT | Sim | Interno | Identificador único. PK. |
| `nome` | VARCHAR | Sim | Borderô | Nome do plano/modalidade de sócio. |

Em INGRESSO_PARTIDA, `id_plano` pode ser NULL quando não se aplica.

## 8. INGRESSO_PARTIDA

Representa uma linha de ingresso específica da partida, setor, categoria e, quando aplicável, plano.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_ingresso_partida` | INT | Sim | Interno | Identificador único. PK. |
| `id_partida` | INT | Sim | Borderô | FK para PARTIDA. |
| `id_setor` | INT | Sim | Borderô | FK para SETOR. |
| `id_categoria` | INT | Sim | Borderô | FK para CATEGORIA_INGRESSO. |
| `id_plano` | INT | Não | Borderô | FK para PLANO_SOCIO; NULL quando não aplicável. |
| `preco` | DECIMAL(10,2) | Não | Borderô | Preço unitário da linha. |
| `quantidade_disponivel` | INT | Não | Borderô | Quantidade disponível apresentada. |
| `quantidade_devolvida` | INT | Não | Borderô | Quantidade devolvida apresentada. |
| `quantidade_utilizada` | INT | Não | Borderô | Quantidade utilizada apresentada. |
| `arrecadacao` | DECIMAL(12,2) | Não | Borderô | Arrecadação da linha. |

As definições de disponível, devolvido e utilizado serão preservadas conforme a nomenclatura da fonte, sem interpretações adicionais não validadas.

## 9. DESPESA_PARTIDA

Representa cada linha de despesa apresentada no borderô.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_despesa` | INT | Sim | Interno | Identificador único. PK. |
| `id_partida` | INT | Sim | Borderô | FK para PARTIDA. |
| `nome` | VARCHAR | Sim | Borderô | Nome original da despesa. |
| `valor` | DECIMAL(12,2) | Não | Borderô | Valor da linha. |

Não haverá inicialmente uma tabela TIPO_DESPESA.

## 10. RESUMO_FINANCEIRO_PARTIDA

Tabela 1:1 com PARTIDA para armazenar os valores consolidados oficialmente apresentados no borderô.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_partida` | INT | Sim | Interno | PK e FK para PARTIDA. |
| `total_disponivel` | INT | Não | Borderô | Total oficial disponível. |
| `total_devolvido` | INT | Não | Borderô | Total oficial devolvido. |
| `total_utilizado` | INT | Não | Borderô | Total oficial utilizado. |
| `arrecadacao_bruta` | DECIMAL(14,2) | Não | Borderô | Arrecadação consolidada oficial, conforme nomenclatura. |
| `total_despesas` | DECIMAL(14,2) | Não | Borderô | Total oficial de despesas. |
| `retencoes` | DECIMAL(14,2) | Não | Borderô | Retenções oficiais. |
| `receita_liquida` | DECIMAL(14,2) | Não | Borderô | Receita líquida oficial. |
| `resultado_final` | DECIMAL(14,2) | Não | Borderô | Resultado final oficial. |
| `complemento_contabil` | DECIMAL(14,2) | Não | Borderô | Complemento contábil quando apresentado separadamente. |

O objetivo é comparar os valores oficiais com cálculos independentes feitos a partir do detalhamento. Diferenças devem ser investigadas, não simplesmente ajustadas.

## 11. CONTEXTO_PARTIDA

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_partida` | INT | Sim | Interno | PK e FK para PARTIDA. |
| `feriado` | BOOLEAN | Não | Fonte complementar | Indica se a data é feriado segundo o critério adotado. |
| `dias_desde_ultimo_jogo_maracana` | INT | Não | Derivado | Dias desde o último jogo do Fluminense no Maracanã. |

Dia da semana e mês serão derivados da data.

## 12. ATRIBUTOS_PARTIDA

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_partida` | INT | Sim | Interno | PK e FK para PARTIDA. |
| `importancia_partida` | DECIMAL(4,1) | Não | Metodológico | Índice de 0 a 10. |
| `apelo_adversario` | DECIMAL(4,1) | Não | Metodológico | Índice de 0 a 10. |
| `e_classico` | BOOLEAN | Não | Metodológico | Indica se o confronto é clássico. |
| `e_clube_g12` | BOOLEAN | Não | Metodológico | Indica se o adversário pertence ao G12 definido pelo projeto. |

Esses campos não são dados oficiais do borderô.

## 13. DESEMPENHO_PARTIDA

Representa a situação esportiva do Fluminense antes da partida.

| Campo | Tipo | Obrigatório | Origem | Descrição / regra |
|---|---|---:|---|---|
| `id_partida` | INT | Sim | Interno | PK e FK para PARTIDA. |
| `posicao_fluminense` | INT | Não | Fonte complementar | Posição antes da partida, quando aplicável. NULL quando não se aplica. |
| `pontos_fluminense` | INT | Não | Fonte complementar | Pontos acumulados antes da partida, quando a competição/fase possuir classificação por pontos. NULL em mata-mata sem pontuação acumulada. |
| `vitorias_ultimos_5` | INT | Não | Derivado | Vitórias nos 5 jogos anteriores. |
| `empates_ultimos_5` | INT | Não | Derivado | Empates nos 5 jogos anteriores. |
| `derrotas_ultimos_5` | INT | Não | Derivado | Derrotas nos 5 jogos anteriores. |
| `gols_marcados_ultimos_5` | INT | Não | Derivado | Gols marcados nos 5 jogos anteriores. |
| `gols_sofridos_ultimos_5` | INT | Não | Derivado | Gols sofridos nos 5 jogos anteriores. |

### Regra temporal

Todas as variáveis representam apenas informações disponíveis antes do início da partida. O resultado da própria partida não participa do cálculo.

Em mata-mata sem classificação por pontos, `pontos_fluminense` e `posicao_fluminense` podem ser NULL. NULL significa não se aplica, e não zero.

Fase, jogo de ida/volta e situação do confronto poderão ser representados em outros atributos quando necessários.

## 14. Série histórica de sócios

O Portal da Transparência disponibiliza uma série mensal com informações de sócios adimplentes e inadimplentes.

Inicialmente essa série será tratada como **fonte externa para o Power BI**, sem tabela obrigatória no PostgreSQL. A decisão poderá ser revista se a integração ao banco trouxer benefício analítico.

## Regras gerais de qualidade

1. Preservar os valores do borderô antes das transformações.
2. Identificar claramente valores derivados.
3. Documentar critérios das variáveis metodológicas antes da análise.
4. Não utilizar o resultado da própria partida no desempenho pré-jogo.
5. Não converter NULL automaticamente em zero.
6. Investigar diferenças entre totais calculados e oficiais.
7. Manter o resumo financeiro oficial separado do detalhamento.
8. Preservar a nomenclatura original das despesas.

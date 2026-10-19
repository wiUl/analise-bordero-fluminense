# Metodologia dos Atributos da Partida

## Objetivo

Documentar os critérios para construir atributos analíticos que não estão presentes diretamente nos borderôs.

Índices avaliados por partida e indicadores descritivos do adversário:

- `importancia_partida`: escala de 0 a 10, armazenada em `ATRIBUTOS_PARTIDA`.
- `apelo_adversario`: escala de 0 a 10, armazenada em `ATRIBUTOS_PARTIDA`.
- `e_classico`: indicador binário armazenado em `ADVERSARIO`.
- `e_clube_g12`: indicador binário armazenado em `ADVERSARIO`.

Essa distinção corresponde ao DER: importância e apelo podem ser avaliados no contexto de cada partida; clássico e G12 são classificações do adversário segundo os critérios adotados no projeto.

## Importância da partida

A importância representa a relevância esportiva da partida no momento em que ocorreu.

Serão considerados:

1. competição;
2. fase ou rodada;
3. caráter eliminatório;
4. situação do Fluminense;
5. disputa por título, classificação, vagas ou permanência;
6. proximidade de uma decisão;
7. consequência esportiva objetiva do resultado.

A pontuação deve ser definida antes da análise de público e receita, evitando que o resultado observado influencie a construção da variável.

A escala é analítica e não oficial.

## Apelo do adversário

Representa o interesse potencial associado ao adversário no contexto histórico da partida.

Serão considerados:

- relevância nacional;
- relevância continental;
- tradição;
- tamanho do clube;
- relevância histórica do confronto;
- força esportiva no período;
- condição de clube emergente.

A avaliação deve considerar o período histórico, pois a relevância esportiva de um clube pode mudar.

## Indicadores binários do adversário

### Clássico — `ADVERSARIO.e_classico`

`e_classico = 1` quando o clube adversário estiver classificado como rival de clássico do Fluminense segundo a lista/regra adotada pelo projeto; caso contrário, `0`. A lista de confrontos considerados clássicos deve ser registrada no repositório antes da classificação da amostra.

### G12 — `ADVERSARIO.e_clube_g12`

`e_clube_g12 = 1` quando o adversário pertencer à composição do G12 adotada pelo projeto; caso contrário, `0`. A composição do grupo e o critério temporal devem ser documentados para evitar mudanças implícitas durante a análise.

Esses indicadores são classificações objetivas definidas pelo projeto. O G12 não substitui `apelo_adversario`, que continua sendo um índice de 0 a 10, contextual e específico da partida.

## Controle metodológico

Os critérios definitivos e exemplos de pontuação dos índices, além das listas de referência para os indicadores binários, devem ser estabelecidos antes da aplicação ao conjunto completo de partidas.

As regras devem ser aplicadas de maneira consistente e suas alterações devem ser versionadas no repositório.

# Metodologia dos Atributos da Partida

## Objetivo

Documentar os critérios para construir atributos analíticos que não estão presentes diretamente nos borderôs.

Principais variáveis:

- importancia_partida: escala de 0 a 10.
- apelo_adversario: escala de 0 a 10.
- e_classico: indicador binário.
- e_clube_g12: indicador binário.

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

## Variáveis binárias

### Clássico

e_classico = 1 quando o confronto atender ao critério adotado; caso contrário, 0.

### G12

e_clube_g12 = 1 quando o adversário pertencer ao grupo G12 definido pelo projeto; caso contrário, 0.

G12 é uma variável objetiva complementar e não substitui apelo_adversario.

## Controle metodológico

As regras definitivas e exemplos de pontuação devem ser estabelecidos antes da aplicação ao conjunto completo de partidas.

As regras devem ser aplicadas de maneira consistente e suas alterações devem ser versionadas no repositório.

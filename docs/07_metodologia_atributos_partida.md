# Metodologia dos Atributos da Partida

## Objetivo

Documentar os critérios para construir atributos analíticos que não estão presentes diretamente nos borderôs.

Atributos e indicadores considerados:

- `importancia_partida`: escala de 0 a 10, armazenada em `ATRIBUTOS_PARTIDA`.
- `apelo_adversario`: escala de 0 a 10, armazenada em `ATRIBUTOS_PARTIDA`.
- `e_classico`: indicador binário armazenado em `ADVERSARIO`.
- `e_clube_g12`: indicador binário armazenado em `ADVERSARIO`.

Importância e apelo são avaliados no contexto de cada partida. Os indicadores de clássico e G12 são classificações do adversário segundo os critérios adotados no projeto, não notas de atração.

As escalas são metodológicas e analíticas, não oficiais. Devem ser aplicadas com critérios consistentes antes de investigar relações com público, ocupação ou receita.

## 1. Importância da partida — `importancia_partida`

### Definição

Mede a relevância esportiva da partida para a competição e para a situação do Fluminense naquele momento.

A avaliação parte da **competição e da fase/rodada**, mas esses fatores não determinam sozinhos a nota. O contexto esportivo pode elevar significativamente a importância.

Considere informações conhecidas antes do início da partida, como:

1. competição;
2. fase ou rodada;
3. caráter eliminatório;
4. situação do Fluminense na competição;
5. disputa por título, classificação, vagas ou permanência;
6. proximidade de uma decisão;
7. consequência esportiva provável do resultado.

### Escala de referência

| Nota | Critério | Exemplo ilustrativo |
|---:|---|---|
| **0** | Amistoso ou jogo-treino sem consequência esportiva relevante. | Amistoso de pré-temporada contra equipe regional. |
| **1** | Partida oficial de importância muito baixa, sem objetivo imediato relevante. | Rodada inicial do Carioca com classificação já assegurada e sem disputa significativa. |
| **2** | Alguma relevância competitiva, mas pouco impacto provável na classificação ou no objetivo da equipe. | Fase inicial do Carioca sem pressão pela classificação. |
| **3** | Jogo regular com consequências limitadas, ainda dentro da disputa por pontos ou classificação. | Rodada intermediária do Brasileirão contra equipe do meio da tabela, sem disputa direta importante. |
| **4** | Importância normal de uma partida de campeonato, sem consequência excepcional. | Jogo comum do Brasileirão em rodada sem impacto extraordinário. |
| **5** | Contribui de maneira relevante para um objetivo esportivo concreto. | Vitória necessária para manter o Fluminense próximo da zona de classificação à Libertadores. |
| **6** | Impacto importante em disputa direta por classificação, liderança, vaga ou permanência. | Confronto contra concorrente direto na luta contra o rebaixamento, com poucos pontos de diferença. |
| **7** | Alto impacto na competição ou em fase eliminatória importante. | Jogo de volta de oitavas de final da Libertadores com a classificação em aberto. |
| **8** | Muito decisiva para um objetivo relevante, com pouca margem para recuperação. | Semifinal de Copa do Brasil ou última rodada em que uma vitória garante vaga continental. |
| **9** | Pode praticamente definir um objetivo esportivo excepcionalmente importante. | Última rodada do Brasileirão em que vencer garante a permanência, sem depender de outros resultados. |
| **10** | Decisão máxima ou consequência esportiva extraordinária, com o principal objetivo diretamente em jogo. | Final da Libertadores de 2023 entre Fluminense e Boca Juniors, valendo o título continental. |

Os exemplos servem como referências de calibração; não substituem a análise da situação real de cada partida.

### Regras de aplicação

- **Competição e fase são a referência inicial.** Uma final não recebe automaticamente nota 10.
- **O contexto pode elevar bastante a nota.** Uma rodada comum pode chegar a 9 ou 10 se decidir diretamente um título, uma classificação excepcional ou a permanência.
- **Avaliação pré-jogo.** Não aumente a nota devido ao resultado, aos gols ou à emoção observada depois da partida.
- **Separação do apelo.** O tamanho ou a fama do adversário não aumenta diretamente a importância; esse fator é avaliado em `apelo_adversario`.
- **Notas extremas justificadas.** Notas 0, 1, 9 e 10 devem ter justificativa clara.
- **Comparação entre jogos semelhantes.** Compare partidas da mesma competição, fase e contexto para reduzir diferenças arbitrárias.

## 2. Apelo do adversário — `apelo_adversario`

### Definição

Mede o potencial de atração associado ao adversário, considerando **história, popularidade e relevância atual na temporada**. Não mede a importância esportiva da partida nem apenas a qualidade técnica da equipe.

A avaliação deve refletir o apelo do adversário **no momento da partida, considerando a temporada em curso**. O apelo pode mudar entre temporadas e ao longo de uma temporada quando houver mudança relevante de contexto.

### Escala de referência

| Nota | Critério | Exemplo ilustrativo |
|---:|---|---|
| **0** | Apelo praticamente inexistente para o público geral. | Clube fictício de expressão local mínima, sem histórico relevante ou torcida expressiva. |
| **1** | Apelo muito baixo e reconhecimento restrito à região. | Pequeno clube regional pouco conhecido nacionalmente. |
| **2** | Apelo baixo, mas com alguma identidade regional ou presença nacional ocasional. | Clube de pouca torcida e pouca exposição, vindo de divisão inferior. |
| **3** | Apelo modesto, conhecido principalmente por quem acompanha o futebol brasileiro. | Clube tradicional de seu estado, mas com alcance nacional limitado. |
| **4** | Apelo regional ou nacional moderado, com torcida reconhecível e alguma história competitiva. | Clube de tradição estadual e presença ocasional em competições nacionais. |
| **5** | Apelo intermediário, com história ou torcida relevante, sem grande destaque nacional naquele momento. | Clube tradicional de uma capital brasileira, com torcida expressiva regionalmente. |
| **6** | Apelo considerável, com reconhecimento nacional, torcida significativa ou relevância recente. | Clube que disputa frequentemente a Série A ou ganhou destaque nacional recente. |
| **7** | Apelo alto, com grande torcida, tradição nacional ou presença frequente em disputas importantes. | Clube tradicional da Série A com torcida nacionalmente conhecida. |
| **8** | Apelo muito alto, combinando tradição, torcida expressiva e grande exposição nacional ou internacional. | Grande clube brasileiro em temporada de destaque, mesmo fora de um clássico local. |
| **9** | Apelo excepcional, com reconhecimento nacional/internacional e relevância histórica ou atual muito elevada. | River Plate ou Boca Juniors em temporada de destaque continental. |
| **10** | Apelo máximo no universo analisado, com enorme reconhecimento, capacidade de mobilização e relevância histórica ou atual. Vários clubes podem atingir essa nota. | Boca Juniors na final da Libertadores de 2023 contra o Fluminense. |

Os exemplos são referências de calibração, não um ranking definitivo e imutável de clubes. Clubes como Flamengo, Palmeiras, Vasco e Botafogo podem receber notas altas, assim como River Plate, Boca Juniors, Peñarol e Olimpia em contextos continentais; a nota concreta deve refletir a avaliação do período definido.

### Regras de aplicação

- **História, popularidade e relevância atual.** Considere os três elementos, sem reduzir a avaliação a apenas um deles.
- **Avaliação contextual.** Não use apenas a divisão disputada nem apenas o tamanho histórico da torcida.
- **Indicadores separados.** `e_classico` e `e_clube_g12` não determinam automaticamente a nota de apelo.
- **Não confundir com a fase do jogo.** O fato de uma partida ser uma final pertence à importância; não atribua apelo 10 apenas porque o jogo é uma decisão.
- **Notas extremas justificadas.** Notas 0, 1, 9 e 10 devem ter justificativa clara.
- **Consistência temporal.** Avalie o adversário com base no contexto disponível antes da partida. Uma mudança relevante durante a temporada pode influenciar partidas posteriores, sem alterar automaticamente as notas já atribuídas.

## 3. Como os atributos funcionam em conjunto

Os atributos são independentes e podem assumir valores muito diferentes na mesma partida.

| Situação | `importancia_partida` | `apelo_adversario` | Interpretação |
|---|---:|---:|---|
| Grande clube brasileiro em rodada comum do Brasileirão | 4 | 8 | Jogo regular contra adversário de grande apelo. |
| Clube de pouca expressão em partida decisiva contra o rebaixamento | 9 | 2 | Importância esportiva muito alta, apesar do baixo apelo do adversário. |
| Boca Juniors na fase de grupos da Libertadores, sem decisão imediata | 4–6 | 9–10 | A importância depende da situação no grupo; o apelo pode continuar muito alto. |
| Fluminense x Boca Juniors, final da Libertadores de 2023 | 10 | 10 | Decisão continental histórica contra adversário de enorme reconhecimento. |

Esses exemplos não constituem pontuações oficiais. Para partidas reais, atribua a nota conforme o contexto pré-jogo e registre a justificativa quando possível.

## 4. Registro e consistência

Quando possível, registre uma justificativa curta para cada nota na planilha de transcrição. Por exemplo:

- `justificativa_importancia`: "Final única da Libertadores, valendo o título continental."
- `justificativa_apelo`: "Boca Juniors: enorme tradição e reconhecimento continental."

As justificativas podem permanecer na planilha e na documentação metodológica; não é obrigatório criar novas colunas no PostgreSQL nesta etapa.

Regras gerais:

1. Defina as notas usando informações disponíveis antes do início da partida.
2. Justifique notas extremas (0, 1, 9 e 10).
3. Compare jogos e adversários semelhantes para calibrar notas.
4. Não use o resultado da partida como critério retroativo.
5. Documente e versione qualquer alteração futura da metodologia.
6. Não altere notas históricas automaticamente quando a escala mudar; se uma revisão for necessária, registre o motivo e aplique a regra de forma consistente à amostra afetada.

## 5. Indicadores binários do adversário

### Clássico — `ADVERSARIO.e_classico`

`e_classico = 1` quando o clube adversário estiver classificado como rival de clássico do Fluminense segundo a lista/regra adotada pelo projeto; caso contrário, `0`. A lista de confrontos considerados clássicos deve ser registrada no repositório antes da classificação da amostra.

### G12 — `ADVERSARIO.e_clube_g12`

`e_clube_g12 = 1` quando o adversário pertencer à composição do G12 adotada pelo projeto; caso contrário, `0`. A composição do grupo e o critério temporal devem ser documentados para evitar mudanças implícitas durante a análise.

Esses indicadores são classificações objetivas definidas pelo projeto. O G12 não substitui `apelo_adversario`, que continua sendo um índice de 0 a 10, contextual e específico da partida.

# Análise de Borderôs do Fluminense FC

Projeto de análise de dados voltado ao estudo da relação entre **preços de ingressos, público, arrecadação e contexto das partidas do Fluminense FC**, utilizando dados de borderôs de jogos realizados como mandante.

O projeto busca construir uma base de dados estruturada a partir dos borderôs e integrá-la posteriormente a outras fontes de informação, permitindo análises exploratórias e estatísticas sobre a **demanda por ingressos, ocupação e desempenho financeiro das partidas**.

> **Status:** O banco MySQL local, o pipeline ETL e o modelo dimensional no Power BI estão implementados. Os dados de 31 partidas da temporada 2026 foram carregados e a primeira página do dashboard (Resumo Temporada 2026) foi construída. A revisão cruzada das transcrições e as análises aprofundadas seguem em desenvolvimento.

### Resumo do projeto

| | |
| --- | --- |
| **Pergunta** | Como preço, contexto da partida e perfil do jogo se relacionam com público, ocupação e receita de bilheteria do Fluminense? |
| **Fonte** | Borderôs de jogos do Fluminense como mandante, divulgados publicamente pelo clube (PDFs) no [Portal da Transparência do Fluminense](https://transparenciafluminense.com.br/public/lista/124/arenas/operacao-de-jogos/borderos). Amostra inicial: temporada **2026**. |
| **Já existe** | Modelagem relacional (DER), dicionário de dados, metodologia dos atributos, banco MySQL local e pipeline ETL para as planilhas de borderô. Os dados de 31 partidas foram carregados. Modelo dimensional no Power BI (`dim_partida`, `dim_ingresso`, `dim_data`, `fato_ingresso`, `fato_despesa`) e a página-resumo do dashboard. |
| **Em andamento / pendente** | Revisão cruzada das transcrições, conclusão do inventário, integração de fontes complementares, demais páginas do dashboard e análises de demanda, receita e contexto. |
| **Tecnologias** | MySQL local, SQL, Python, Excel e Power BI. |

A coleta e a transcrição da temporada 2026 continuam em andamento; algumas partidas ainda não possuem borderô disponível. Existe uma primeira página de dashboard (resumo da temporada 2026); as análises de preço × demanda e de contexto ainda não foram produzidas.

---

## 🎯 Objetivo

Investigar como diferentes fatores relacionados às partidas podem estar associados ao comportamento do público e à arrecadação de bilheteria.

Entre os fatores analisados ou previstos estão:

* preço dos ingressos;
* quantidade de ingressos disponíveis;
* ingressos devolvidos;
* ingressos utilizados;
* arrecadação;
* setores do estádio;
* categorias de ingresso;
* planos de sócio;
* adversário;
* competição;
* fase ou rodada da competição;
* importância esportiva da partida;
* apelo do adversário;
* desempenho recente do Fluminense;
* posição das equipes;
* dia e horário da partida;
* ocorrência de feriado;
* intervalo desde o último jogo no Maracanã;
* características do confronto, como clássico;
* relevância histórica/esportiva do adversário, representada por critérios como pertencimento ao G12.

O projeto também pretende investigar diferentes faixas de preço e seus possíveis efeitos sobre **público, ocupação e receita**, considerando diferentes contextos de partida.

> Variáveis como importância da partida e apelo do adversário serão construídas por meio de critérios metodológicos próprios, documentados no projeto.

---

## 📊 Fonte dos dados

A principal fonte de dados será constituída pelos **borderôs das partidas do Fluminense FC**, disponibilizados publicamente pelo clube no [Portal da Transparência do Fluminense](https://transparenciafluminense.com.br/public/lista/124/arenas/operacao-de-jogos/borderos).

Os borderôs contêm informações financeiras e de bilheteria das partidas, incluindo dados relacionados a:

* setores;
* categorias de ingresso;
* planos de sócio;
* preços;
* quantidade de ingressos disponíveis;
* ingressos devolvidos;
* ingressos utilizados;
* arrecadação;
* despesas relacionadas à operação da partida;
* retenções;
* resultado financeiro.

Os documentos serão utilizados como **fonte primária para a construção da base de dados**.

Informações que não estejam disponíveis nos borderôs poderão ser obtidas em fontes complementares, de acordo com a metodologia definida para cada variável.

---

## 🗄️ Arquitetura dos dados

Os dados não serão armazenados diretamente no formato dos PDFs.

A arquitetura atual transforma as informações transcritas dos borderôs em uma estrutura relacional utilizando **MySQL em ambiente local**. O banco é acessado pelos scripts Python e pelo Power BI, sem necessidade de hospedagem na nuvem para o escopo atual. O modelo havia sido inicialmente criado no Supabase com PostgreSQL; o banco principal do projeto é atualmente MySQL.

Fluxo de dados do projeto:

```text
Borderôs
   ↓
Extração e padronização
   ↓
Modelagem dos dados
   ↓
Planilhas Excel (interim)
   ↓
ETL e validações com Python
   ↓
MySQL local
   ↓
Modelo dimensional no Power BI (Power Query + DAX)
   ↓
Consultas SQL e integração com fontes complementares
   ↓
Análises
   ↓
Power BI
```

As etapas de leitura, preparação, carga no MySQL e modelagem no Power BI estão implementadas. Análises complementares e as demais páginas do dashboard ainda estão previstas.

Os PDFs originais são preservados em `data/raw/`. As transcrições revisadas em Excel ficam em `data/interim/` e funcionam como etapa intermediária para validação e carga. Os dados estruturados são armazenados no MySQL local. A pasta `data/processed/` está reservada; o ETL atual não grava cópias transformadas nela. O Supabase/PostgreSQL foi utilizado na etapa inicial de modelagem/prototipagem, mas não é a plataforma principal do projeto.

### Execução do ETL

Execute os comandos a partir da raiz do repositório, com o ambiente Python configurado e as variáveis `DB_HOST`, `DB_USER`, `DB_PASSWORD` e `DB_NAME` definidas no arquivo `.env`.

Para carregar uma planilha específica:

```powershell
python -m scripts.main --arquivo "data\interim\NOME-DA-PLANILHA.xlsx"
```

Para processar todas as planilhas Excel em `data/interim/`:

```powershell
python -m scripts.main --lote
```

É obrigatório escolher um dos modos. Cada planilha é processada em uma transação própria: em caso de erro, suas alterações são revertidas; no modo de lote, o processamento segue para os arquivos seguintes e apresenta um resumo ao final.

Antes de inserir, o ETL verifica as quantidades existentes nas tabelas de dados da partida. Se todas estiverem vazias, carrega os dados; se as quantidades coincidirem com as esperadas, ignora a planilha; nos demais casos, informa uma carga parcial. Essa verificação compara contagens, não o conteúdo dos registros.

Antes de consultar ou cadastrar setores, categorias e planos de sócio, o ETL remove espaços no início e no fim e reduz sequências de espaços a um único espaço. Assim, valores como `Sul`, ` Sul ` e `Sul  ` usam a mesma chave; o espaço simples entre palavras, como em `Leste Inferior`, é mantido. O texto de `descricao_original` continua literal. O ETL também verifica os cadastros existentes e interrompe a carga se encontrar IDs diferentes cujos nomes colidam após essa normalização, para que a duplicidade seja corrigida explicitamente no banco.

---

## 🧩 Modelagem dos dados

A documentação detalhada está em [docs/04_modelagem.md](docs/04_modelagem.md) e o dicionário completo em [docs/03_dicionario_dados.md](docs/03_dicionario_dados.md).

![Diagrama da modelagem de dados](images/DER%20-%20Fluminense_border%C3%B4.png)

A modelagem busca separar entidades e eventos que possuem significados diferentes, evitando tanto a duplicação desnecessária de informações quanto uma normalização excessiva.

A estrutura lógica representada no DER contempla:

```text
PARTIDA
├── ADVERSARIO
├── COMPETICAO_TEMPORADA
│   ├── COMPETICAO
│   └── TEMPORADA
├── ESTADIO
├── INGRESSO_PARTIDA
│   ├── SETOR
│   ├── CATEGORIA_INGRESSO
│   └── PLANO_SOCIO
├── DESPESA_PARTIDA
├── RESUMO_FINANCEIRO_PARTIDA
├── CONTEXTO_PARTIDA
├── ATRIBUTOS_PARTIDA
└── DESEMPENHO_PARTIDA
```

A série histórica mensal de sócios adimplentes e inadimplentes será inicialmente usada como fonte externa para o Power BI; ela não corresponde a uma tabela desse modelo relacional.

A edição da competição é representada por `COMPETICAO_TEMPORADA`, que associa uma competição a uma temporada. Assim, `PARTIDA` referencia essa associação, em vez de armazenar a competição e o ano como atributos independentes.

### Partida

A entidade `PARTIDA` representa o evento esportivo e funciona como elemento central do modelo.

Entre seus principais atributos estão:

* data;
* horário;
* adversário;
* edição da competição (`competicao_temporada_id`);
* estádio;
* rodada/fase.

A competição e o ano/temporada são mantidos em entidades próprias: `COMPETICAO` registra a competição, `TEMPORADA` registra o ano e `COMPETICAO_TEMPORADA` representa a participação daquela competição naquela temporada.

### Ingressos

As informações de bilheteria são estruturadas em diferentes níveis:

* **setor** — localização do ingresso no estádio;
* **categoria** — inteira, meia ou sócio;
* **plano de sócio** — detalhamento da categoria de sócio;
* **ingresso por partida** — combinação entre partida, setor, categoria e, quando aplicável, plano de sócio.

A tabela `INGRESSO_PARTIDA` concentra informações específicas daquela oferta de ingresso na partida, como:

* descrição original da linha do borderô (`descricao_original`);
* setor, quando informado;
* categoria do ingresso, quando informada;
* plano de sócio, quando aplicável;
* preço;
* quantidade disponível;
* quantidade devolvida;
* quantidade utilizada;
* arrecadação.

**Tratamento de classificações ausentes:** alguns itens dos borderôs, como ingressos promocionais, camarotes promocionais, cadeiras cativas, tribuna e gratuidades por lei, podem não apresentar setor ou categoria. Por isso, `id_setor` e `id_categoria` aceitam `NULL` em `INGRESSO_PARTIDA`. A descrição original é obrigatória e preserva o texto do documento, sem criar setores ou categorias artificiais.

O campo `id_plano` também aceita `NULL` quando não há plano de sócio associado. Preço e arrecadação permanecem nulos quando o borderô não informa esses valores; zero continua sendo tratado como valor informado, distinto de ausência.

A restrição de unicidade considera a partida, as chaves técnicas das classificações (com `NULL` representado por zero apenas nessas colunas geradas) e a descrição original. Isso permite preservar linhas distintas mesmo quando setor ou categoria não estão especificados.

Essa estrutura permite analisar, por exemplo, como diferentes preços e categorias se comportam dentro de cada setor, sem descartar itens cuja classificação não esteja explícita no documento.

### Despesas

As despesas são armazenadas diretamente em `DESPESA_PARTIDA`.

Cada registro representa uma linha de despesa apresentada no borderô, preservando sua nomenclatura original:

```text
id_despesa
id_partida
nome
valor
```

Não será criada inicialmente uma entidade separada de `TIPO_DESPESA`, pois isso acrescentaria uma camada de normalização sem necessidade para a estrutura atual.

Caso análises futuras exijam agrupamentos das despesas, classificações poderão ser criadas posteriormente na camada de transformação ou análise.

---

## 📐 Modelo analítico no Power BI

O Power BI consome o MySQL e reorganiza o modelo relacional em um modelo dimensional:

| Tabela | Papel |
| --- | --- |
| `dim_partida` | Partida com adversário, competição, temporada, estádio, contexto, atributos e desempenho |
| `dim_ingresso` | Tipo de ingresso (setor, categoria e plano de sócio) |
| `dim_data` | Tabela de datas |
| `fato_ingresso` | Ingressos por partida e tipo de ingresso |
| `fato_despesa` | Despesas por partida |
| `_Medidas` | Medidas DAX |

Definições usadas nos indicadores:

* **Público presente:** soma da quantidade utilizada;
* **Público pagante:** ingressos com preço informado (linhas sem preço são gratuidades);
* **Ticket médio:** arrecadação ÷ público pagante;
* **Receita líquida:** arrecadação − despesas.

> Documentação completa das decisões de modelagem, das colunas e das medidas: [docs/05_modelo_powerbi.md](docs/05_modelo_powerbi.md).

---

## 📊 Dashboard

Primeira página: **Resumo Temporada 2026** (31 jogos como mandante).

![Dashboard – Resumo Temporada 2026](images/dashboard_resumo_temporada_2026.jpg)

---

## 🌐 Contexto da partida

O contexto representa condições circunstanciais da realização da partida.

A estrutura atual contempla:

```text
CONTEXTO_PARTIDA

- id_partida
- feriado
- dias_desde_ultimo_jogo_maracana
```

Variáveis como dia da semana e mês não precisam necessariamente ser armazenadas, pois podem ser derivadas diretamente da data da partida.

Informações climáticas, como temperatura e precipitação, foram inicialmente consideradas, mas foram retiradas do escopo devido à dificuldade de obter dados históricos consistentes para partidas mais antigas.

---

## ⭐ Atributos da partida

Os atributos da partida representam características utilizadas para avaliar o potencial de interesse e relevância do confronto.

A estrutura atual contempla:

```text
ATRIBUTOS_PARTIDA

- id_partida
- importancia_partida
- apelo_adversario
```

Os indicadores `e_classico` e `e_clube_g12` ficam em `ADVERSARIO`, conforme o DER. Eles descrevem o adversário segundo os critérios definidos pelo projeto; não são índices de avaliação específicos de cada partida. Já `apelo_adversario` permanece em `ATRIBUTOS_PARTIDA`, pois pode variar conforme o período histórico e o contexto da partida.

### Importância da partida

`importancia_partida` será representada por uma escala analítica de **0 a 10**. Ela mede a relevância esportiva da partida para a competição e para a situação do Fluminense naquele momento.

A avaliação parte da **competição e da fase/rodada**, mas esses fatores não determinam a nota sozinhos: o contexto esportivo pode elevar significativamente a importância. A pontuação deve considerar informações conhecidas antes do início do jogo, sem usar o resultado final ou o quanto a partida acabou sendo emocionante.

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

**Regras de aplicação:**

- A competição e a fase definem a referência inicial; uma final não recebe automaticamente nota 10.
- O contexto pode elevar bastante a nota: uma rodada comum pode chegar a 9 ou 10 se decidir diretamente um título, uma classificação excepcional ou a permanência.
- Avalie o cenário conhecido antes da partida. Não aumente a nota devido ao resultado, aos gols ou à emoção observada depois.
- O tamanho ou a fama do adversário não aumenta diretamente a importância; esse fator é avaliado em `apelo_adversario`.
- Use notas extremas com justificativa clara e compare jogos semelhantes para manter a escala consistente.

### Apelo do adversário

`apelo_adversario` também utiliza uma escala analítica de **0 a 10**. Mede o potencial de atração associado ao adversário, considerando **história, popularidade e relevância atual na temporada**. Não mede a importância esportiva da partida nem apenas a qualidade técnica da equipe.

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

Os exemplos são referências de calibração, não um ranking definitivo e imutável de clubes.

**Regras de aplicação:**

- Avalie o apelo do adversário **no momento da partida, considerando a temporada em curso**. O apelo pode mudar entre temporadas e ao longo de uma temporada quando houver mudança relevante de contexto.
- História e popularidade importam, mas a relevância atual também deve pesar.
- Não use apenas a divisão disputada nem apenas a torcida histórica.
- `e_classico` e `e_clube_g12` são indicadores separados e não determinam automaticamente a nota de apelo.
- A condição de final pertence à importância da partida; não atribua apelo 10 apenas porque o jogo é uma decisão.
- Justifique notas extremas e aplique o mesmo critério a adversários e períodos comparáveis.

### Aplicação conjunta dos atributos

Os dois atributos são independentes. Exemplos ilustrativos:

| Situação | `importancia_partida` | `apelo_adversario` | Interpretação |
|---|---:|---:|---|
| Grande clube brasileiro em rodada comum do Brasileirão | 4 | 8 | Jogo regular contra adversário de grande apelo. |
| Clube de pouca expressão em partida decisiva contra o rebaixamento | 9 | 2 | Importância esportiva muito alta, apesar do baixo apelo do adversário. |
| Boca Juniors na fase de grupos da Libertadores, sem decisão imediata | 4–6 | 9–10 | A importância depende da situação no grupo; o apelo do adversário pode continuar muito alto. |
| Fluminense x Boca Juniors, final da Libertadores de 2023 | 10 | 10 | Decisão continental histórica contra adversário de enorme reconhecimento. |

### Registro e consistência

Quando possível, registrar uma justificativa curta para cada nota na planilha de transcrição, por exemplo:

- `justificativa_importancia`: "Final única da Libertadores, valendo o título continental."
- `justificativa_apelo`: "Boca Juniors: enorme tradição e reconhecimento continental."

As justificativas podem permanecer na planilha e na documentação metodológica; não é obrigatório criar novas colunas no banco nesta etapa.

A pontuação deve ser definida com base em informações disponíveis antes do início da partida. Notas extremas (0, 1, 9 e 10) devem ter justificativa clara. Mudanças futuras nos critérios devem ser documentadas e versionadas; notas históricas não devem ser alteradas retroativamente sem uma regra explícita.

### Indicadores do adversário

Os campos `e_classico` e `e_clube_g12` pertencem à entidade `ADVERSARIO`, conforme o DER. O critério exato para considerar um adversário clássico deve ser documentado e aplicado de forma consistente.

**Definição de G12 no projeto:** o indicador `e_clube_g12` marca os **clubes grandes do Brasil** e, fora do país, os **clubes tradicionais sul-americanos**. Portanto, o nome "G12" é um rótulo do projeto e não se restringe aos 12 grandes brasileiros. No dashboard, o indicador aparece como "Clubes Grandes". Nas 31 partidas de 2026, estão marcados: Atlético Mineiro, Botafogo, Corinthians, Flamengo, Grêmio, Internacional, Palmeiras, Santos, São Paulo e Vasco (Brasil) e Bolívar (América do Sul).

Valor de ambos os indicadores:

```text
0 = não
1 = sim
```

O G12 funciona como uma classificação objetiva complementar e não substitui a avaliação contextual de `apelo_adversario`.

---

---

## ⚽ Desempenho da partida

O desempenho esportivo será tratado separadamente dos atributos de importância e apelo.

A estrutura inicial considera informações como:

* posição do Fluminense antes da partida;
* pontos do Fluminense;
* resultados recentes;
* vitórias nos últimos jogos;
* empates nos últimos jogos;
* derrotas nos últimos jogos;
* gols marcados recentemente;
* gols sofridos recentemente.

Essa estrutura poderá ser refinada posteriormente para incorporar também informações equivalentes do adversário.

A separação entre desempenho e importância permite distinguir, por exemplo:

> **como o Fluminense estava jogando**

de:

> **o quanto aquela partida era importante naquele momento**.

---

## 👥 Sócio-torcedor

O Portal da Transparência disponibiliza uma série histórica mensal de sócios adimplentes e inadimplentes. Neste momento, essa série será tratada como **fonte externa para o Power BI**, sem uma tabela obrigatória no banco.

A decisão poderá ser revista posteriormente caso a integração ao banco traga benefício analítico.

Além disso, os próprios borderôs permitirão analisar a participação de diferentes categorias de sócios nos ingressos.

---

## 📈 Análises planejadas

### Demanda

* relação entre preço e público;
* taxa de utilização dos ingressos disponíveis;
* taxa de ocupação do estádio;
* composição do público por categoria;
* comportamento da demanda por setor;
* participação dos sócios no público;
* comportamento da demanda em diferentes contextos de partida.

### Receita

* preço médio dos ingressos;
* arrecadação por partida;
* receita por espectador;
* receita por setor;
* composição da arrecadação por categoria;
* relação entre preço, público e receita;
* impacto das despesas no resultado financeiro.

### Contexto e atributos da partida

* público × adversário;
* público × apelo do adversário;
* público × clube do G12;
* público × clássico;
* público × importância da partida;
* público × desempenho recente;
* público × posição na tabela;
* público × dia e horário;
* público × feriado;
* público × intervalo desde o último jogo no Maracanã.

A separação entre **importância da partida** e **apelo do adversário** permitirá investigar situações distintas, como:

```text
Alto apelo + baixa importância
```

versus:

```text
Baixo apelo + alta importância
```

permitindo avaliar se o comportamento do público está mais associado às características do adversário, à relevância esportiva da partida ou à combinação desses fatores.

---

## 💰 Análise de preços

Em uma etapa posterior, poderão ser utilizados modelos estatísticos para investigar a associação entre preço e demanda, controlando outros fatores relevantes.

Também poderá ser estimada a **elasticidade-preço da demanda** e simulados diferentes cenários de preço.

A análise poderá considerar diferentes níveis de:

* preço;
* setor;
* categoria;
* plano de sócio;
* importância da partida;
* apelo do adversário;
* desempenho esportivo;
* competição;
* demais fatores disponíveis.

> As análises estatísticas serão interpretadas como relações observadas nos dados. Associação entre variáveis não será automaticamente interpretada como causalidade.

---

## 🛠️ Tecnologias utilizadas e previstas

* **Python e pandas** — leitura, validação, transformação e preparação dos dados para carga
* **openpyxl** — leitura das planilhas Excel
* **MySQL e mysql-connector-python** — armazenamento local e acesso ao banco pelo ETL
* **python-dotenv** — carregamento das credenciais de conexão a partir do `.env`
* **SQL** — consultas e conferência dos dados
* **Excel** — transcrição e revisão dos borderôs
* **Git/GitHub** — versionamento e documentação
* **dbdiagram.io** — modelagem e documentação do banco de dados
* **Power BI** — modelagem dimensional, medidas DAX e dashboards

As ferramentas poderão ser ajustadas conforme o desenvolvimento do projeto.

---

## 📁 Estrutura do repositório

```text
analise-bordero-fluminense/
│
├── README.md
├── AGENTS.md
├── requirements.txt
├── .env.example
│
├── docs/
│   ├── 03_dicionario_dados.md        (existe)
│   ├── 04_modelagem.md               (existe)
│   ├── 05_modelo_powerbi.md          (existe)
│   ├── 07_metodologia_atributos_partida.md   (existe)
│   └── ...                           (demais documentos serão criados conforme as etapas avançarem)
│
├── images/
│   ├── DER - Fluminense_borderô.png  (existe)
│   └── dashboard_resumo_temporada_2026.jpg
│
├── database/
│   ├── schema_mysql_analise_bordero_fluminense.sql
│   ├── schema_mysql_revisado.sql
│   └── README.md
│
├── scripts/
│   ├── main.py                       (orquestração do ETL)
│   └── etl/
│       ├── leitura_excel.py          (localização, validação e leitura)
│       ├── preparacao.py             (organização e preparação dos dados)
│       └── banco_mysql.py            (conexão, referências e inserções)
│
├── data/
│   ├── raw/          (PDFs originais dos borderôs)
│   ├── interim/      (planilhas Excel de transcrição por partida)
│   └── processed/    (reservada; o ETL ainda não gera arquivos aqui)
│
└── powerbi/
    └── Dashboard - Fluminense Borderô.pbix
```

---

## 📚 Documentação

A documentação detalhada do projeto fica em `docs/` e será ampliada ao longo do desenvolvimento:

- [Dicionário de dados](docs/03_dicionario_dados.md)
- [Modelagem de dados](docs/04_modelagem.md)
- [Modelo no Power BI](docs/05_modelo_powerbi.md)
- [Metodologia dos atributos da partida](docs/07_metodologia_atributos_partida.md)

O diagrama da modelagem (DER) está em [`images/DER - Fluminense_borderô.png`](images/DER%20-%20Fluminense_border%C3%B4.png).

## 🗺️ Roadmap

* [x] Definição inicial do problema
* [x] Identificação dos borderôs como fonte primária
* [x] Análise inicial da estrutura dos borderôs
* [x] Revisão inicial das entidades do modelo
* [x] Definição inicial das estruturas de contexto e atributos da partida
* [x] Definição do desempenho pré-jogo
* [x] Definição do armazenamento do resumo financeiro oficial
* [x] Definição inicial do tratamento da série histórica de sócios
* [x] Definição do modelo conceitual
* [x] Definição e documentação do modelo lógico (DER)
* [x] Definição da metodologia de `importancia_partida` (escala 0–10 documentada)
* [x] Definição da metodologia de `apelo_adversario` (escala 0–10 documentada)
* [x] Definição do G12 utilizado na análise (clubes grandes do Brasil e clubes tradicionais sul-americanos)
* [x] Criação do dicionário de dados
* [x] Definição do MySQL local como banco principal do projeto
* [x] Configuração do ambiente MySQL local e conexão Python com o banco
* [x] Adaptação do DDL para MySQL e revisão de `INGRESSO_PARTIDA` para preservar descrições originais e aceitar setor/categoria não informados
* [ ] Teste de instalação limpa e validação das restrições do DDL revisado
* [x] Organização inicial dos PDFs originais (`data/raw/`) e das transcrições Excel (`data/interim/`)
* [x] Conclusão do inventário das partidas e dos borderôs disponíveis da temporada 2026
* [ ] Revisão cruzada das transcrições com os PDFs originais
* [x] Implementação do ETL modularizado para ler, preparar e carregar as abas das planilhas no MySQL
* [x] Implementação da execução de uma planilha isolada ou de um lote explícito
* [x] Carga dos dados de 31 partidas disponíveis até o momento
* [x] Conferência sistemática das quantidades e dos totais oficiais de todas as 31 partidas (soma das linhas = totais oficiais de arrecadação, despesas e público)
* [ ] Integração com fontes complementares
* [x] Implementação do tratamento e da transformação dos dados necessários à carga ETL
* [ ] Análise exploratória
* [ ] Modelagem estatística
* [x] Desenvolvimento do modelo no Power BI
* [x] Primeira página do dashboard (Resumo Temporada 2026)
* [ ] Páginas de análise do dashboard (demanda, receita, contexto)
* [x] Documentação do modelo dimensional e das medidas ([docs/05_modelo_powerbi.md](docs/05_modelo_powerbi.md))
* [ ] Documentação dos resultados
* [ ] Publicação do projeto como portfólio

---

## 🔎 Rastreabilidade

A documentação do projeto será construída progressivamente neste repositório.

Cada etapa será registrada para manter a rastreabilidade entre:

```text
fonte
  ↓
coleta
  ↓
tratamento
  ↓
modelagem
  ↓
atributos derivados
  ↓
análise
  ↓
visualização
```

Especial atenção será dada às variáveis construídas pelo projeto, como `importancia_partida` e `apelo_adversario`.

Essas variáveis não representam informações oficiais presentes nos borderôs. São **índices analíticos construídos a partir de critérios definidos e documentados**, que deverão ser aplicados de maneira consistente ao conjunto de dados.

O objetivo é que o projeto não seja apenas um dashboard final, mas um exemplo completo de um **pipeline de análise de dados**, desde a obtenção dos dados até a geração e interpretação dos insights.

---

## ⚠️ Status dos resultados

Este projeto encontra-se em fase de desenvolvimento. O modelo conceitual e lógico está documentado no DER, no documento de modelagem e no dicionário de dados. Os PDFs originais são preservados em `data/raw/`, e as planilhas transcritas e revisadas ficam em `data/interim/`. O pipeline ETL carrega os dados no MySQL local; os dados de 31 partidas disponíveis até o momento já foram inseridos. Algumas partidas permanecem pendentes porque seus borderôs ainda não foram disponibilizados.

Os critérios e exemplos de pontuação para `importancia_partida` e `apelo_adversario` estão documentados em [Metodologia dos atributos da partida](docs/07_metodologia_atributos_partida.md). A conferência sistemática dos dados carregados, a conclusão do inventário e a revisão das transcrições permanecem pendentes. O período da amostra ainda precisa ser definido antes das análises completas. A primeira página do dashboard foi produzida; as análises e conclusões ainda não foram finalizadas.

Resultados apresentados futuramente serão baseados nos dados coletados e na metodologia documentada neste repositório.

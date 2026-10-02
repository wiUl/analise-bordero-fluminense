# Análise de Borderôs do Fluminense FC

Projeto de análise de dados voltado ao estudo da relação entre **preços de ingressos, público, arrecadação e contexto das partidas do Fluminense FC**, utilizando dados de borderôs de jogos realizados como mandante.

O projeto busca construir uma base de dados estruturada a partir dos borderôs e integrá-la posteriormente a outras fontes de informação, permitindo análises exploratórias e estatísticas sobre a demanda por ingressos e o desempenho financeiro das partidas.

> **Status:** Em desenvolvimento

---

## 🎯 Objetivo

Investigar como diferentes fatores relacionados às partidas podem estar associados ao comportamento do público e à arrecadação de bilheteria.

Entre os fatores que poderão ser analisados estão:

* preço dos ingressos;
* quantidade de ingressos disponíveis, devolvidos e utilizados;
* arrecadação;
* categorias e setores dos ingressos;
* adversário;
* competição;
* importância da partida;
* desempenho recente do Fluminense;
* posição das equipes;
* dia e horário da partida;
* intervalo desde o último jogo no estádio;
* condições climáticas;
* outros fatores que possam influenciar a demanda.

O projeto também pretende avaliar diferentes faixas de preço e seus possíveis efeitos sobre **público, ocupação e receita**, considerando diferentes contextos de partida.

---

## 📊 Fonte dos dados

A principal fonte de dados será constituída pelos **borderôs das partidas do Fluminense FC**, disponibilizados publicamente pelo clube.

Os borderôs contêm informações financeiras e de bilheteria das partidas, incluindo dados relacionados a:

* ingressos;
* setores;
* categorias;
* preços;
* ingressos utilizados;
* ingressos devolvidos;
* arrecadação;
* despesas relacionadas à operação da partida;
* retenções;
* resultado financeiro.

Os documentos serão utilizados como **fonte primária para a construção da base de dados**.

---

## 🗄️ Arquitetura dos dados

Os dados não serão armazenados diretamente no formato dos PDFs.

A proposta é transformar as informações dos borderôs em uma estrutura relacional utilizando **PostgreSQL**, permitindo posteriormente sua utilização em ferramentas de Business Intelligence.

Fluxo planejado:

```text
Borderôs
   ↓
Extração e padronização
   ↓
Modelagem dos dados
   ↓
PostgreSQL
   ↓
Integração com outras fontes
   ↓
Análises
   ↓
Power BI
```

A estrutura definitiva do banco será definida durante a etapa de modelagem.

---

## 🧩 Modelagem

A modelagem será realizada considerando a separação entre diferentes entidades e eventos.

Uma estrutura inicial prevista é:

```text
PARTIDAS
    │
    ├──────< INGRESSOS
    │
    └──────< DESPESAS
```

Essa estrutura poderá ser modificada conforme a análise de novos borderôs e a identificação de novos requisitos para as análises.

Posteriormente, poderá ser desenvolvido um **modelo dimensional específico para o Power BI**, caso seja adequado às necessidades analíticas do projeto.

---

## 🔎 Dados complementares

Além dos borderôs, poderão ser incorporadas informações provenientes de outras fontes para contextualizar as partidas.

Exemplos:

* desempenho do Fluminense;
* desempenho do adversário;
* classificação no campeonato;
* resultados recentes;
* competição e rodada;
* data e horário;
* calendário;
* clima;
* informações relacionadas ao programa de sócio-torcedor;
* características do adversário.

Essas informações serão relacionadas à partida por meio de chaves e identificadores definidos durante a modelagem.

---

## 📈 Análises planejadas

Entre as análises previstas estão:

### Demanda

* relação entre preço e público;
* taxa de ocupação do estádio;
* utilização dos ingressos disponíveis;
* composição do público por categoria;
* comportamento da demanda por setor.

### Receita

* preço médio dos ingressos;
* arrecadação por partida;
* receita por espectador;
* receita por setor;
* composição da arrecadação por categoria.

### Contexto da partida

* público × adversário;
* público × desempenho recente;
* público × posição na tabela;
* público × importância da partida;
* público × dia e horário;
* público × intervalo desde a última partida.

### Análise de preços

Em uma etapa posterior, poderão ser utilizados modelos estatísticos para investigar a associação entre preço e demanda, controlando outros fatores relevantes.

Também poderá ser estimada a **elasticidade-preço da demanda** e simulados diferentes cenários de preço.

> As análises estatísticas serão interpretadas como relações observadas nos dados. Associação entre variáveis não será automaticamente interpretada como causalidade.

---

## 🛠️ Tecnologias planejadas

* **Python** — extração, tratamento e preparação dos dados
* **PostgreSQL** — armazenamento e gerenciamento dos dados
* **SQL** — consultas e transformação dos dados
* **Power BI** — análise e visualização
* **Git/GitHub** — versionamento e documentação
* **dbdiagram.io** — modelagem e documentação do banco de dados

As ferramentas poderão ser ajustadas conforme o desenvolvimento do projeto.

---

## 📁 Estrutura planejada do repositório

```text
analise-borderos-fluminense/
│
├── README.md
│
├── docs/
│   ├── 01_objetivo.md
│   ├── 02_fontes_dados.md
│   ├── 03_modelagem.md
│   ├── 04_dicionario_dados.md
│   ├── 05_metodologia_coleta.md
│   ├── 06_tratamento_dados.md
│   └── 07_metodologia_analise.md
│
├── database/
│   ├── schema.sql
│   └── seeds.sql
│
├── scripts/
│   ├── extraction/
│   └── transformation/
│
├── data/
│   ├── raw/
│   └── processed/
│
└── powerbi/
    └── ...
```

A estrutura poderá evoluir conforme novas etapas forem implementadas.

---

## 🗺️ Roadmap

* [x] Definição inicial do problema
* [x] Identificação dos borderôs como fonte primária
* [x] Análise inicial da estrutura dos borderôs
* [ ] Definição do modelo conceitual
* [ ] Definição do modelo lógico
* [ ] Criação do dicionário de dados
* [ ] Configuração do PostgreSQL
* [ ] Desenvolvimento da estrutura do banco
* [ ] Desenvolvimento da extração dos borderôs
* [ ] Validação dos dados extraídos
* [ ] Coleta dos borderôs
* [ ] Integração com fontes complementares
* [ ] Tratamento e transformação dos dados
* [ ] Análise exploratória
* [ ] Modelagem estatística
* [ ] Desenvolvimento do modelo no Power BI
* [ ] Construção do dashboard
* [ ] Documentação dos resultados
* [ ] Publicação do projeto como portfólio

---

## 📚 Documentação

A documentação do projeto será construída progressivamente neste repositório.

Cada etapa será registrada para manter a rastreabilidade entre:

**fonte → coleta → tratamento → modelagem → análise → visualização**

O objetivo é que o projeto não seja apenas um dashboard final, mas um exemplo completo de um **pipeline de análise de dados**, desde a obtenção dos dados até a geração dos insights.

---

## ⚠️ Status dos resultados

Este projeto encontra-se em fase de desenvolvimento. As análises, conclusões e visualizações ainda não foram finalizadas.

Resultados apresentados futuramente serão baseados nos dados coletados e na metodologia documentada neste repositório.

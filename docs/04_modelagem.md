# Modelagem de Dados

## Objetivo

Organizar os dados dos borderôs em uma estrutura relacional adequada ao PostgreSQL e ao posterior consumo pelo Power BI.

O princípio adotado é separar conceitos realmente distintos sem criar entidades apenas por normalização.

## Estrutura conceitual

```
PARTIDA
│
├── ADVERSARIO
├── COMPETICAO
├── ESTADIO
│
├── INGRESSO_PARTIDA
│   ├── SETOR
│   ├── CATEGORIA_INGRESSO
│   └── PLANO_SOCIO
│
├── DESPESA_PARTIDA
├── RESUMO_FINANCEIRO_PARTIDA
├── CONTEXTO_PARTIDA
├── ATRIBUTOS_PARTIDA
└── DESEMPENHO_PARTIDA

Série histórica de sócios
└── Fonte externa mensal
```

## Decisões de modelagem

### Ingressos

O preço pertence à oferta específica de ingresso naquela partida, setor, categoria e plano, quando aplicável. Não pertence permanentemente ao setor ou ao plano.

### Despesas

As despesas permanecem diretamente em DESPESA_PARTIDA e preservam os nomes apresentados no borderô. Não há uma dimensão TIPO_DESPESA no modelo atual.

### Resumo financeiro

RESUMO_FINANCEIRO_PARTIDA é uma relação 1:1 com PARTIDA e guarda os valores consolidados oficiais.

Ela não substitui os detalhes. Sua função é permitir reconciliação:

```
Detalhamento
    ↓
cálculo independente
    ↓
comparação
    ↓
resumo oficial do borderô
```

### Contexto x atributos

CONTEXTO_PARTIDA representa circunstâncias objetivas, como feriado e intervalo desde o último jogo no Maracanã.

ATRIBUTOS_PARTIDA representa características e índices analíticos, como importância e apelo do adversário.

### Desempenho pré-jogo

DESEMPENHO_PARTIDA representa a situação conhecida antes do jogo. Em competições com classificação por pontos, posição e pontos podem ser preenchidos. Em mata-mata sem classificação por pontos, podem ser NULL.

## Diagrama

O diagrama visual está em [../images/modelo_dados.svg](../images/modelo_dados.svg).

O dicionário completo está em [03_dicionario_dados.md](03_dicionario_dados.md).

## Próxima etapa

Depois desta etapa será definida a modelagem lógica e o DDL do PostgreSQL, incluindo tipos, chaves, restrições e índices.

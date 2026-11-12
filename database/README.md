# Database

Esquema relacional do projeto em **MySQL 8** (instância local).

## Arquivo

- [`schema_mysql_analise_bordero_fluminense.sql`](schema_mysql_analise_bordero_fluminense.sql) — DDL vigente: cria o banco `analise_bordero_fluminense` e as 15 tabelas, com chaves, restrições (`UNIQUE` e `CHECK`) e índices.

## Como usar

Execute o script em um servidor MySQL 8 com banco novo ou vazio. O script usa `CREATE DATABASE IF NOT EXISTS` e `CREATE TABLE`, então não apaga nem altera tabelas existentes.

Depois de criar o esquema, configure o `.env` (modelo em `.env.example`) e carregue as planilhas com o ETL (`python -m scripts.main --lote`). Os detalhes estão no [README principal](../README.md).

## Tabelas

- **Dimensões de referência:** `adversario`, `competicao`, `temporada`, `competicao_temporada`, `estadio`, `setor`, `categoria_ingresso`, `plano_socio`.
- **Partida:** `partida`.
- **Dados da partida:** `ingresso_partida`, `despesa_partida`, `resumo_financeiro_partida`, `contexto_partida`, `atributos_partida`, `desempenho_partida`.

## Documentação relacionada

- [Modelagem de dados](../docs/04_modelagem.md)
- [Dicionário de dados](../docs/03_dicionario_dados.md)
- Diagrama entidade-relacionamento: [`images/DER - Fluminense_borderô.png`](../images/DER%20-%20Fluminense_border%C3%B4.png)

O DDL é a implementação efetiva das regras de integridade; ao alterar o esquema, revise o DDL, o DER, a modelagem e o dicionário em conjunto.

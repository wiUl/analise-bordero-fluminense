-- Análise de Borderôs do Fluminense FC
-- DDL para MySQL Community Server 8.0.43.
-- Esquema revisado: descricao_original preservada e setor/categoria opcionais.
-- Executar em banco novo/vazio. Não apaga tabelas nem dados existentes.

CREATE DATABASE IF NOT EXISTS analise_bordero_fluminense
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE analise_bordero_fluminense;

CREATE TABLE adversario (
  id_adversario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  e_classico TINYINT(1) NOT NULL DEFAULT 0,
  e_clube_g12 TINYINT(1) NOT NULL DEFAULT 0,
  CONSTRAINT uq_adversario_nome UNIQUE (nome),
  CONSTRAINT chk_adversario_classico CHECK (e_classico IN (0,1)),
  CONSTRAINT chk_adversario_g12 CHECK (e_clube_g12 IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE competicao (
  id_competicao INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  CONSTRAINT uq_competicao_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE temporada (
  id_temporada INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  ano INT NOT NULL,
  CONSTRAINT uq_temporada_ano UNIQUE (ano),
  CONSTRAINT chk_temporada_ano CHECK (ano BETWEEN 1900 AND 2200)
) ENGINE=InnoDB;

CREATE TABLE competicao_temporada (
  id_competicao_temporada INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_competicao INT NOT NULL,
  id_temporada INT NOT NULL,
  CONSTRAINT uq_competicao_temporada UNIQUE (id_competicao,id_temporada),
  KEY idx_ct_temporada (id_temporada),
  CONSTRAINT fk_ct_competicao FOREIGN KEY (id_competicao) REFERENCES competicao(id_competicao),
  CONSTRAINT fk_ct_temporada FOREIGN KEY (id_temporada) REFERENCES temporada(id_temporada)
) ENGINE=InnoDB;

CREATE TABLE estadio (
  id_estadio INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  cidade VARCHAR(255),
  estado VARCHAR(255),
  pais VARCHAR(255),
  capacidade INT,
  CONSTRAINT uq_estadio_nome UNIQUE (nome),
  CONSTRAINT chk_estadio_capacidade CHECK (capacidade IS NULL OR capacidade >= 0)
) ENGINE=InnoDB;

CREATE TABLE setor (
  id_setor INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  CONSTRAINT uq_setor_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE categoria_ingresso (
  id_categoria INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  CONSTRAINT uq_categoria_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE plano_socio (
  id_plano INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  CONSTRAINT uq_plano_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE partida (
  id_partida INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  data DATE NOT NULL,
  horario TIME,
  adversario_id INT NOT NULL,
  competicao_temporada_id INT NOT NULL,
  estadio_id INT NOT NULL,
  rodada VARCHAR(255),
  KEY idx_partida_adversario (adversario_id),
  KEY idx_partida_ct (competicao_temporada_id),
  KEY idx_partida_estadio (estadio_id),
  KEY idx_partida_data (data),
  CONSTRAINT fk_partida_adversario FOREIGN KEY (adversario_id) REFERENCES adversario(id_adversario),
  CONSTRAINT fk_partida_ct FOREIGN KEY (competicao_temporada_id) REFERENCES competicao_temporada(id_competicao_temporada),
  CONSTRAINT fk_partida_estadio FOREIGN KEY (estadio_id) REFERENCES estadio(id_estadio)
) ENGINE=InnoDB;

CREATE TABLE ingresso_partida (
  id_ingresso_partida INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_partida INT NOT NULL,
  descricao_original VARCHAR(255) NOT NULL,
  id_setor INT NULL,
  id_categoria INT NULL,
  id_plano INT NULL,
  -- 0 representa NULL apenas nas chaves técnicas; IDs reais devem ser positivos.
  id_setor_chave INT GENERATED ALWAYS AS (IFNULL(id_setor,0)) STORED,
  id_categoria_chave INT GENERATED ALWAYS AS (IFNULL(id_categoria,0)) STORED,
  id_plano_chave INT GENERATED ALWAYS AS (IFNULL(id_plano,0)) STORED,
  preco DECIMAL(10,2),
  quantidade_disponivel INT,
  quantidade_devolvida INT,
  quantidade_utilizada INT,
  arrecadacao DECIMAL(12,2),
  CONSTRAINT uq_ingresso_composicao UNIQUE
    (id_partida,id_setor_chave,id_categoria_chave,id_plano_chave,descricao_original),
  KEY idx_ingresso_setor (id_setor),
  KEY idx_ingresso_categoria (id_categoria),
  KEY idx_ingresso_plano (id_plano),
  CONSTRAINT chk_ingresso_setor CHECK (id_setor IS NULL OR id_setor > 0),
  CONSTRAINT chk_ingresso_categoria CHECK (id_categoria IS NULL OR id_categoria > 0),
  CONSTRAINT chk_ingresso_plano CHECK (id_plano IS NULL OR id_plano > 0),
  CONSTRAINT chk_ingresso_preco CHECK (preco IS NULL OR preco >= 0),
  CONSTRAINT chk_ingresso_disponivel CHECK (quantidade_disponivel IS NULL OR quantidade_disponivel >= 0),
  CONSTRAINT chk_ingresso_devolvida CHECK (quantidade_devolvida IS NULL OR quantidade_devolvida >= 0),
  CONSTRAINT chk_ingresso_utilizada CHECK (quantidade_utilizada IS NULL OR quantidade_utilizada >= 0),
  CONSTRAINT chk_ingresso_arrecadacao CHECK (arrecadacao IS NULL OR arrecadacao >= 0),
  CONSTRAINT fk_ingresso_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida),
  CONSTRAINT fk_ingresso_setor FOREIGN KEY (id_setor) REFERENCES setor(id_setor),
  CONSTRAINT fk_ingresso_categoria FOREIGN KEY (id_categoria) REFERENCES categoria_ingresso(id_categoria),
  CONSTRAINT fk_ingresso_plano FOREIGN KEY (id_plano) REFERENCES plano_socio(id_plano)
) ENGINE=InnoDB;

CREATE TABLE despesa_partida (
  id_despesa INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_partida INT NOT NULL,
  nome VARCHAR(255) NOT NULL,
  valor DECIMAL(12,2),
  KEY idx_despesa_partida (id_partida),
  CONSTRAINT chk_despesa_valor CHECK (valor IS NULL OR valor >= 0),
  CONSTRAINT fk_despesa_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida)
) ENGINE=InnoDB;

CREATE TABLE resumo_financeiro_partida (
  id_partida INT NOT NULL PRIMARY KEY,
  total_disponivel INT,
  total_devolvido INT,
  total_utilizado INT,
  arrecadacao_bruta DECIMAL(14,2),
  total_despesas DECIMAL(14,2),
  retencoes DECIMAL(14,2),
  receita_liquida DECIMAL(14,2),
  consignatarios DECIMAL(14,2),
  resultado_final DECIMAL(14,2),
  complemento_contabil DECIMAL(14,2),
  CONSTRAINT chk_resumo_disponivel CHECK (total_disponivel IS NULL OR total_disponivel >= 0),
  CONSTRAINT chk_resumo_devolvido CHECK (total_devolvido IS NULL OR total_devolvido >= 0),
  CONSTRAINT chk_resumo_utilizado CHECK (total_utilizado IS NULL OR total_utilizado >= 0),
  CONSTRAINT fk_resumo_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida)
) ENGINE=InnoDB;

CREATE TABLE contexto_partida (
  id_partida INT NOT NULL PRIMARY KEY,
  feriado TINYINT(1),
  dias_desde_ultimo_jogo_maracana INT,
  CONSTRAINT chk_contexto_feriado CHECK (feriado IS NULL OR feriado IN (0,1)),
  CONSTRAINT chk_contexto_dias CHECK (dias_desde_ultimo_jogo_maracana IS NULL OR dias_desde_ultimo_jogo_maracana >= 0),
  CONSTRAINT fk_contexto_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida)
) ENGINE=InnoDB;

CREATE TABLE atributos_partida (
  id_partida INT NOT NULL PRIMARY KEY,
  importancia_partida DECIMAL(3,1),
  apelo_adversario DECIMAL(3,1),
  CONSTRAINT chk_atributos_importancia CHECK (importancia_partida IS NULL OR importancia_partida BETWEEN 0 AND 10),
  CONSTRAINT chk_atributos_apelo CHECK (apelo_adversario IS NULL OR apelo_adversario BETWEEN 0 AND 10),
  CONSTRAINT fk_atributos_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida)
) ENGINE=InnoDB;

CREATE TABLE desempenho_partida (
  id_partida INT NOT NULL PRIMARY KEY,
  posicao_fluminense INT,
  pontos_fluminense INT,
  vitorias_ultimos_5 INT,
  empates_ultimos_5 INT,
  derrotas_ultimos_5 INT,
  gols_marcados_ultimos_5 INT,
  gols_sofridos_ultimos_5 INT,
  CONSTRAINT chk_desempenho_posicao CHECK (posicao_fluminense IS NULL OR posicao_fluminense > 0),
  CONSTRAINT chk_desempenho_pontos CHECK (pontos_fluminense IS NULL OR pontos_fluminense >= 0),
  CONSTRAINT chk_desempenho_vitorias CHECK (vitorias_ultimos_5 IS NULL OR vitorias_ultimos_5 BETWEEN 0 AND 5),
  CONSTRAINT chk_desempenho_empates CHECK (empates_ultimos_5 IS NULL OR empates_ultimos_5 BETWEEN 0 AND 5),
  CONSTRAINT chk_desempenho_derrotas CHECK (derrotas_ultimos_5 IS NULL OR derrotas_ultimos_5 BETWEEN 0 AND 5),
  CONSTRAINT chk_desempenho_soma_resultados CHECK (
    vitorias_ultimos_5 IS NULL OR empates_ultimos_5 IS NULL OR derrotas_ultimos_5 IS NULL
    OR vitorias_ultimos_5 + empates_ultimos_5 + derrotas_ultimos_5 <= 5
  ),
  CONSTRAINT chk_desempenho_gols_marcados CHECK (gols_marcados_ultimos_5 IS NULL OR gols_marcados_ultimos_5 >= 0),
  CONSTRAINT chk_desempenho_gols_sofridos CHECK (gols_sofridos_ultimos_5 IS NULL OR gols_sofridos_ultimos_5 >= 0),
  CONSTRAINT fk_desempenho_partida FOREIGN KEY (id_partida) REFERENCES partida(id_partida)
) ENGINE=InnoDB;

-- Observações:
-- * NULL representa dado não disponível ou não aplicável; não substituir por zero.
-- * descricao_original preserva o texto da linha do borderô, inclusive quando
--   setor ou categoria não estiverem informados no documento.
-- * id_setor e id_categoria são opcionais em ingresso_partida porque alguns
--   itens do borderô não apresentam essas classificações.
-- * A reconciliação entre detalhes e resumo oficial será feita no ETL.
-- * consignatarios registra o valor oficial destinado às instituições consignatárias;
--   não calcular nem substituir NULL por zero.
-- * O complemento_contabil não deve ser somado automaticamente à arrecadação.
-- * Divergências devem ser auditadas, preservando os valores originais do borderô.

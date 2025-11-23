-- ==========================================
-- Script 03: Criar Tabelas no Schema SIS
-- ==========================================

SET search_path TO sis;

-- ==========================================
-- Tabela Principal: tickets (Estrutura idêntica ao DTIC)
-- ==========================================
CREATE TABLE tickets (
    -- Identificadores
    id SERIAL PRIMARY KEY,
    glpi_id INTEGER UNIQUE NOT NULL,
    
    -- Conteúdo
    titulo VARCHAR(500) NOT NULL,
    descricao TEXT,
    descricao_md TEXT,
    
    -- Classificação
    status VARCHAR(50) NOT NULL,
    status_id INTEGER,
    prioridade VARCHAR(20),
    prioridade_id INTEGER,
    tipo VARCHAR(50),
    tipo_id INTEGER,
    
    -- Impacto e Urgência (GLPI nativo: 1-5)
    impact INTEGER CHECK (impact BETWEEN 1 AND 5),
    urgency INTEGER CHECK (urgency BETWEEN 1 AND 5),
    
    -- Entidades (Nomes enriquecidos + IDs originais)
    categoria VARCHAR(255),
    categoria_id INTEGER,
    entidade VARCHAR(255),
    entidade_id INTEGER,
    tecnico VARCHAR(255),
    tecnico_id INTEGER,
    grupo VARCHAR(255),
    grupo_id INTEGER,
    grupo_nivel VARCHAR(10),
    requerente VARCHAR(255),
    requerente_id INTEGER,
    ultimo_atualizador VARCHAR(255),
    ultimo_atualizador_id INTEGER,
    
    -- Localização e Ativos
    localizacao VARCHAR(255),
    localizacao_id INTEGER,
    item_relacionado_tipo VARCHAR(100),
    item_relacionado_id INTEGER,
    
    -- SLA/OLA
    sla_ttr_id INTEGER,
    sla_tto_id INTEGER,
    ola_ttr_id INTEGER,
    ola_tto_id INTEGER,
    tempo_para_resolver INTEGER,
    tempo_para_atribuir INTEGER,
    
    -- Tempos de Interação (em segundos)
    tempo_primeira_interacao INTEGER,
    tempo_acao_total INTEGER,
    
    -- Tipo de Requisição
    tipo_requisicao VARCHAR(50),
    tipo_requisicao_id INTEGER,
    
    -- Validação e Satisfação
    status_validacao VARCHAR(50),
    percentual_validacao INTEGER,
    
    -- Fornecedor (opcional)
    fornecedor VARCHAR(255),
    fornecedor_id INTEGER,
    
    -- Custos (opcional)
    custo_tempo DECIMAL(10,2),
    custo_fixo DECIMAL(10,2),
    custo_material DECIMAL(10,2),
    
    -- Timestamps (com timezone)
    criado_em TIMESTAMPTZ NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL,
    solucionado_em TIMESTAMPTZ,
    fechado_em TIMESTAMPTZ,
    
    -- Metadados
    url VARCHAR(500),
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Controle de Sincronização
    ticket_hash VARCHAR(32),
    sincronizado_em TIMESTAMPTZ DEFAULT NOW(),
    versao INTEGER DEFAULT 1
);

-- Índices otimizados
CREATE UNIQUE INDEX idx_sis_tickets_glpi_id ON tickets(glpi_id);
CREATE INDEX idx_sis_tickets_status ON tickets(status);
CREATE INDEX idx_sis_tickets_atualizado_em ON tickets(atualizado_em DESC);
CREATE INDEX idx_sis_tickets_criado_em ON tickets(criado_em DESC);
CREATE INDEX idx_sis_tickets_tecnico ON tickets(tecnico) WHERE tecnico IS NOT NULL;
CREATE INDEX idx_sis_tickets_grupo ON tickets(grupo) WHERE grupo IS NOT NULL;
CREATE INDEX idx_sis_tickets_categoria ON tickets(categoria) WHERE categoria IS NOT NULL;
CREATE INDEX idx_sis_tickets_hash ON tickets(ticket_hash);
CREATE INDEX idx_sis_tickets_prioridade ON tickets(prioridade);

-- Full-Text Search (PostgreSQL nativo em português)
CREATE INDEX idx_sis_tickets_fts ON tickets 
    USING GIN(to_tsvector('portuguese', 
        coalesce(titulo, '') || ' ' || coalesce(descricao_md, '')));

-- Comentários para documentação
COMMENT ON TABLE tickets IS 'Tickets SIS sincronizados do GLPI';
COMMENT ON COLUMN tickets.glpi_id IS 'ID original do ticket no GLPI';
COMMENT ON COLUMN tickets.impact IS 'Impacto: 1=Muito Baixo, 2=Baixo, 3=Médio, 4=Alto, 5=Muito Alto';
COMMENT ON COLUMN tickets.urgency IS 'Urgência: 1=Muito Baixa, 2=Baixa, 3=Média, 4=Alta, 5=Muito Alta';
COMMENT ON COLUMN tickets.ticket_hash IS 'MD5 hash para detectar mudanças';

-- ==========================================
-- Tabela: sync_meta (Metadados de Sincronização)
-- ==========================================
CREATE TABLE sync_meta (
    chave VARCHAR(50) PRIMARY KEY,
    valor TEXT,
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE sync_meta IS 'Metadados de sincronização SIS (last_sync_time, etc.)';

-- Inserir valor inicial
INSERT INTO sync_meta (chave, valor) 
VALUES ('last_sync_time', '2024-01-01T00:00:00Z');

-- ==========================================
-- Tabela: sync_history (Histórico de Sincronizações)
-- ==========================================
CREATE TABLE sync_history (
    id SERIAL PRIMARY KEY,
    tipo_sync VARCHAR(20) NOT NULL,
    tickets_novos INTEGER DEFAULT 0,
    tickets_atualizados INTEGER DEFAULT 0,
    tickets_sem_mudanca INTEGER DEFAULT 0,
    tickets_total INTEGER DEFAULT 0,
    erros INTEGER DEFAULT 0,
    duracao_segundos DECIMAL(10,2),
    iniciado_em TIMESTAMPTZ NOT NULL,
    finalizado_em TIMESTAMPTZ,
    sucesso BOOLEAN,
    observacoes TEXT
);

CREATE INDEX idx_sis_sync_history_iniciado ON sync_history(iniciado_em DESC);

COMMENT ON TABLE sync_history IS 'Histórico de execuções de sincronização SIS';
COMMENT ON COLUMN sync_history.tipo_sync IS 'FULL, INCREMENTAL, STARTUP_CHECK';

-- ==========================================
-- Tabela: sync_errors (Log de Erros)
-- ==========================================
CREATE TABLE sync_errors (
    id SERIAL PRIMARY KEY,
    glpi_id INTEGER,
    tipo_erro VARCHAR(100),
    mensagem_erro TEXT,
    stack_trace TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sis_sync_errors_criado ON sync_errors(criado_em DESC);
CREATE INDEX idx_sis_sync_errors_glpi_id ON sync_errors(glpi_id);

COMMENT ON TABLE sync_errors IS 'Log de erros durante sincronização SIS';

-- Confirmar criação
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'sis';
    
    RAISE NOTICE 'Schema SIS: % tabelas criadas', table_count;
END $$;

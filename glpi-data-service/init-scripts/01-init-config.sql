-- ==========================================
-- Script 01: Configuração Inicial e Schemas
-- ==========================================

-- Configurar timezone para América/São Paulo
ALTER DATABASE glpi_data SET timezone TO 'America/Sao_Paulo';

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- Busca de similaridade/fuzzy search
CREATE EXTENSION IF NOT EXISTS unaccent;     -- Remover acentos para busca

-- Criar schemas separados para DTIC e SIS
CREATE SCHEMA IF NOT EXISTS dtic;
CREATE SCHEMA IF NOT EXISTS sis;

-- Configurar search_path padrão
ALTER DATABASE glpi_data SET search_path TO dtic, sis, public;

-- Confirmar criação
DO $$
BEGIN
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'Timezone: %', current_setting('timezone');
    RAISE NOTICE 'Schemas criados: dtic, sis';
    RAISE NOTICE 'Extensões: pg_trgm, unaccent';
END $$;

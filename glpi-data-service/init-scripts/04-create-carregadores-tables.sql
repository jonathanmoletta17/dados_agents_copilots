-- Create carregadores table for SIS schema
CREATE TABLE IF NOT EXISTS sis.carregadores (
    id INTEGER PRIMARY KEY,  -- GLPI ID
    name VARCHAR(255),
    locations_id INTEGER,
    location_name VARCHAR(255),
    users_id INTEGER,
    user_name VARCHAR(255),
    is_deleted INTEGER DEFAULT 0,
    date_mod TIMESTAMP WITH TIME ZONE,
    date_creation TIMESTAMP WITH TIME ZONE,
    sincronizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create carregador_tickets link table
CREATE TABLE IF NOT EXISTS sis.carregador_tickets (
    id SERIAL PRIMARY KEY,
    tickets_id INTEGER NOT NULL,  -- Link to tickets.glpi_id
    items_id INTEGER NOT NULL,    -- Link to carregadores.id
    itemtype VARCHAR(100) DEFAULT 'PluginGenericobjectCarregador',
    sincronizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tickets_id, items_id)  -- Prevent duplicates
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_carregador_tickets_ticket ON sis.carregador_tickets(tickets_id);
CREATE INDEX IF NOT EXISTS idx_carregador_tickets_item ON sis.carregador_tickets(items_id);
CREATE INDEX IF NOT EXISTS idx_carregadores_deleted ON sis.carregadores(is_deleted);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE sis.carregadores TO glpi_user;
GRANT ALL PRIVILEGES ON TABLE sis.carregador_tickets TO glpi_user;
GRANT ALL PRIVILEGES ON SEQUENCE sis.carregador_tickets_id_seq TO glpi_user;

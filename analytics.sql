CREATE SCHEMA IF NOT EXISTS analytics;

-- Tabela para rastrear eventos anônimos do site (Funil)
CREATE TABLE analytics.web_events (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Um ID de sessão anônima
    event_name VARCHAR(100) NOT NULL, -- Ex: 'visitou_site', 'iniciou_cadastro'
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE SET NULL, -- Vincula ao usuário se ele completar
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para custos de marketing (CAC)
CREATE TABLE analytics.marketing_costs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL, -- Ex: 'Google Ads', 'Facebook Ads'
    cost NUMERIC(10, 2) NOT NULL,
    clicks INTEGER,
    date DATE NOT NULL UNIQUE, -- Custo diário
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
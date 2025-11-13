-- === Tabelas de Gamificação (Missões) ===

-- A definição da Missão
CREATE TABLE consumers.missions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    points_reward INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de junção (Quem completou qual missão)
CREATE TABLE consumers.user_missions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    mission_id INTEGER REFERENCES consumers.missions(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, mission_id) -- Impede que o usuário complete a mesma missão duas vezes
);

-- === Tabelas de B2B (Campanhas) ===

-- A definição da Campanha B2B
CREATE TABLE companies.campaigns (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES companies.companies_client(id) ON DELETE CASCADE, -- Campanha de uma empresa
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de junção (Qual colaborador participou de qual campanha)
CREATE TABLE companies.user_campaign_participation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES companies.campaigns(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, campaign_id)
);
-- Tabela para armazenar o histórico de MEV Score
CREATE TABLE consumers.user_mev_score (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    score INTEGER NOT NULL, -- O score de risco (ex: 0-100)
    risk_level VARCHAR(50), -- Ex: 'Baixo', 'Médio', 'Alto'
    calculated_at DATE NOT NULL, -- Data que o score foi calculado
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, calculated_at) -- Um score por usuário por dia
);
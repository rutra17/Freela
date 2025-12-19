-- ARQUIVO: interactions.sql
-- OBJETIVO: Tabela fato de interações para Gamificação (Regras de Negócio B2C/B2B)
-- DEPENDÊNCIAS: consumers.user, companies.companies_client, providers.partner

CREATE SCHEMA IF NOT EXISTS consumers;

-- 1. Tabela de Interações (Fato)
CREATE TABLE IF NOT EXISTS consumers.user_interaction (
    id SERIAL PRIMARY KEY,
    
    -- Quem interagiu?
    user_id INTEGER NOT NULL REFERENCES consumers.user(id) ON DELETE CASCADE,
    
    -- Onde? (Pode ser nulo se for um treino em casa ou outdoor)
    company_id INTEGER REFERENCES companies.companies_client(id) ON DELETE SET NULL,
    partner_id INTEGER REFERENCES providers.partner(id) ON DELETE SET NULL,
    partner_schedule_id INTEGER, -- Caso queira ligar com a agenda (opcional)
    
    -- O quê?
    type VARCHAR(50) NOT NULL, -- Ex: 'check-in', 'class_booking', 'social_share', 'evaluation'
    status VARCHAR(50) NOT NULL DEFAULT 'CONCLUIDO', -- Ex: 'CONCLUIDO', 'CANCELADO', 'NO-SHOW'
    
    -- O "Cérebro" da Gamificação (JSONB)
    -- Guarda: friends_ids (array), workout_type (string), rating (int), morning_bonus (bool)
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Quando?
    interaction_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Índices de Performance (Obrigatórios para o Dashboard não travar)

-- Índice GIN: Permite buscar "quem treinou Boxe" dentro do JSON instantaneamente
CREATE INDEX IF NOT EXISTS "IDX_interaction_metadata" ON consumers.user_interaction USING GIN (metadata);

-- Índices B-Tree: Para filtros rápidos de data e chaves estrangeiras
CREATE INDEX IF NOT EXISTS "IDX_interaction_user" ON consumers.user_interaction(user_id);
CREATE INDEX IF NOT EXISTS "IDX_interaction_partner" ON consumers.user_interaction(partner_id);
CREATE INDEX IF NOT EXISTS "IDX_interaction_company" ON consumers.user_interaction(company_id);
CREATE INDEX IF NOT EXISTS "IDX_interaction_date" ON consumers.user_interaction(interaction_timestamp);
CREATE INDEX IF NOT EXISTS "IDX_interaction_type" ON consumers.user_interaction(type);

-- Comentário técnico:
-- A coluna 'metadata' suporta as queries de:
-- 1. Consistência (Distinct Date)
-- 2. Hábito (Extract Hour)
-- 3. Diversidade (Distinct workout_type no JSON)
-- 4. Social (Array length friends_ids no JSON)
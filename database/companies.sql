-- SCRIPT CORRIGIDO: Adicionado prefixo 'companies.' em tudo

CREATE SCHEMA IF NOT EXISTS companies;


-- 1. Tabela companies.plan (Tabela Mestra de Planos/Assinaturas)
CREATE TABLE companies.companies_plan (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela companies.client (Clientes/Empresas)
CREATE TABLE companies.companies_client (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES companies.companies_plan(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela companies.indicator (Definição dos Indicadores)
CREATE TABLE companies.companies_indicator (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    unit VARCHAR(20), -- Ex: %, R$, Unidade
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela companies.client_collaborator (Junção N:N de Clientes e Usuários)
CREATE TABLE companies.companies_client_collaborator (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES companies.companies_client(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    role VARCHAR(50), 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (client_id, user_id)
);

-- 5. Tabela companies.billet (Boletos/Faturamento)
CREATE TABLE companies.companies_billet (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES companies.companies_client(id) ON DELETE RESTRICT,
    value NUMERIC(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL, -- Ex: 'PENDENTE', 'PAGO', 'ATRASADO'
    billet_url VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabela companies.indicator_consolidation (Valores dos Indicadores por Cliente e Período)
CREATE TABLE companies.companies_indicator_consolidation (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES companies.companies_indicator(id) ON DELETE RESTRICT,
    client_id INTEGER REFERENCES companies.companies_client(id) ON DELETE CASCADE,
    consolidation_date DATE NOT NULL,
    value NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (indicator_id, client_id, consolidation_date)
);

-- 7. Tabela companies.client_token (Tokens de Acesso/API)
CREATE TABLE companies.companies_client_token (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES companies.companies_client(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Tabela companies.user_affiliation (Afiliações de Usuários)
CREATE TABLE companies.companies_user_affiliation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    affiliate_id INTEGER REFERENCES consumers.user(id)  ON DELETE SET NULL, 
    affiliation_type VARCHAR(50), 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, affiliate_id)
);
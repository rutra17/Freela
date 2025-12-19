-- 1. Cria o Schema 'policies' para organizar as tabelas
CREATE SCHEMA IF NOT EXISTS policies;

--------------------------------------------------------------------------------
-- TABELAS DE ESTRUTURA E PERMISSÃO
--------------------------------------------------------------------------------

-- Tabela: policies.owner_rule
-- Armazena os papéis (regras) de acesso do sistema (Ex: Admin, Assistente)
CREATE TABLE policies.owner_rule (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(100) NOT NULL UNIQUE,
    level           INTEGER NOT NULL,
    allows_register BOOLEAN NOT NULL DEFAULT FALSE,
    allows_edit     BOOLEAN NOT NULL DEFAULT FALSE,
    allows_remove   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela: policies.owner
-- Armazena os usuários do sistema (administradores/colaboradores)
CREATE TABLE policies.owner (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(255) NOT NULL,
    registry_code   VARCHAR(14), -- Assumindo CPF ou CNPJ
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    password        VARCHAR(255) NOT NULL, -- O ideal é usar um campo TEXT para o hash
    occupation      VARCHAR(100),
    owner_rule_id   INTEGER NOT NULL,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira para owner_rule
    CONSTRAINT fk_owner_rule
        FOREIGN KEY (owner_rule_id)
        REFERENCES policies.owner_rule (id)
        ON DELETE RESTRICT
);

-- Tabela: policies.owner_route
-- Permissões de rota/endpoint por regra de acesso
CREATE TABLE policies.owner_route (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    route           VARCHAR(255) NOT NULL,
    owner_rule_id   INTEGER NOT NULL,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira para owner_rule
    CONSTRAINT fk_owner_route_rule
        FOREIGN KEY (owner_rule_id)
        REFERENCES policies.owner_rule (id)
        ON DELETE CASCADE,
        
    -- Garante que uma mesma regra não tenha a mesma rota cadastrada mais de uma vez
    UNIQUE (route, owner_rule_id)
);

--------------------------------------------------------------------------------
-- TABELAS DE LOGS E EVENTOS
--------------------------------------------------------------------------------

-- Tabela: policies.login_log
-- Registro de acessos ao sistema
CREATE TABLE policies.login_log (
    id                      SERIAL PRIMARY KEY,
    auth_token           TEXT, -- Assumindo o token JWT
    user_id                 INTEGER, -- Assumindo que se refere ao policies.owner.id
    client_collaborator_id  INTEGER, -- Mantido, mas sem FK, pois a tabela de referência não foi fornecida
    partner_employee_id     INTEGER, -- Mantido, mas sem FK, pois a tabela de referência não foi fornecida
    audit                   TEXT,
    created_at              TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITHOUT TIME ZONE,

    -- Chave Estrangeira para owner
    CONSTRAINT fk_login_owner
        FOREIGN KEY (user_id)
        REFERENCES policies.owner (id)
        ON DELETE SET NULL
);


-- Tabela: policies.log
-- Logs de sistema/erros
CREATE TABLE policies.log (
    id              SERIAL PRIMARY KEY,
    level           VARCHAR(50) NOT NULL, -- Ex: Critical, Warning
    message         TEXT NOT NULL,
    http_message    TEXT,
    source          VARCHAR(100),
    code            INTEGER, -- HTTP Status Code ou Código de Erro
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Tabela: policies.recovery_account
-- Armazena códigos de recuperação de conta
CREATE TABLE policies.recovery_account (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    code            VARCHAR(10) NOT NULL UNIQUE,
    reference       VARCHAR(255) NOT NULL, -- Email ou registry_code usado para recuperação
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE
);

--------------------------------------------------------------------------------
-- TABELAS DE DADOS GERAIS
--------------------------------------------------------------------------------

-- Tabela: policies.support
-- Tickets de suporte
CREATE TABLE policies.support (
    id                      SERIAL PRIMARY KEY,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    status                  VARCHAR(50) NOT NULL, -- Ex: CL (Closed), OP (Open)
    title                   VARCHAR(255) NOT NULL,
    text                    TEXT NOT NULL,
    answer                  TEXT,
    user_id                 INTEGER, -- Cliente/Usuário que abriu o ticket (FK indefinida)
    partner_employee_id     INTEGER, -- Colaborador de parceiro (FK indefinida)
    client_collaborator_id  INTEGER, -- Colaborador de cliente (FK indefinida)
    owner_id                INTEGER, -- Colaborador interno que respondeu

    created_at              TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira para o staff que respondeu
    CONSTRAINT fk_support_owner
        FOREIGN KEY (owner_id)
        REFERENCES policies.owner (id)
        ON DELETE SET NULL
);

-- Tabela: policies.document
-- Documentos armazenados
CREATE TABLE policies.document (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(255) NOT NULL,
    type            INTEGER,
    audit           VARCHAR(50),
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela: policies.settings
-- Configurações do sistema (chave-valor)
CREATE TABLE policies.settings (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    key             VARCHAR(100) NOT NULL UNIQUE,
    value           TEXT,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE
);
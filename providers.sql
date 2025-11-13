-- 1. Cria o Schema 'providers' para organizar as tabelas
CREATE SCHEMA IF NOT EXISTS providers;

--------------------------------------------------------------------------------
-- TABELAS DE ESTRUTURA E REGRAS
--------------------------------------------------------------------------------

-- Tabela: providers.partner_rule
-- Define os papéis/cargos para os colaboradores do Parceiro
CREATE TABLE providers.partner_rule (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(100) NOT NULL UNIQUE,
    level           INTEGER NOT NULL,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela: providers.partner
-- Dados principais do Parceiro (Academia, Prestador de Serviço, etc.)
CREATE TABLE providers.partner (
    id                      SERIAL PRIMARY KEY,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    name                    VARCHAR(255) NOT NULL,
    registry_code           VARCHAR(20) UNIQUE, -- CNPJ ou CPF
    email                   VARCHAR(255) NOT NULL UNIQUE,
    phone                   VARCHAR(20),
    type                    CHAR(1), -- J (Jurídica) ou F (Física)
    about                   TEXT,
    service_value           NUMERIC(10, 2) DEFAULT 0.00,
    schedule_cancel_value   NUMERIC(10, 2),
    schedule_previous_days  INTEGER,
    schedule_cancel_timeout INTEGER,
    schedule_cancel_tolerance INTEGER,
    
    -- Campos extras para integração/auditoria
    audit                   TEXT,
    partner_id_ref          INTEGER, -- Se for sub-unidade, referência ao parceiro principal
    wallet_id               VARCHAR(36), -- UUID
    wallet_email            VARCHAR(255),
    api_key                 VARCHAR(36), -- UUID
    type_model              VARCHAR(50),
    verified                BOOLEAN NOT NULL DEFAULT FALSE,
    transfer_rate           NUMERIC(5, 2),
    external_code           VARCHAR(50),
    
    created_at              TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela: providers.partner_employee
-- Colaboradores/funcionários do Parceiro
CREATE TABLE providers.partner_employee (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(255) NOT NULL,
    registry_code   VARCHAR(14),
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    password        TEXT NOT NULL,
    partner_id      INTEGER NOT NULL,
    partner_rule_id INTEGER NOT NULL,
    audit           TEXT,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_employee_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE, -- Se o parceiro for deletado, os funcionários também
    
    CONSTRAINT fk_employee_rule
        FOREIGN KEY (partner_rule_id)
        REFERENCES providers.partner_rule (id)
        ON DELETE RESTRICT -- Não deleta a regra se ela estiver em uso
);

--------------------------------------------------------------------------------
-- TABELAS DE DETALHES DO PARCEIRO
--------------------------------------------------------------------------------

-- Tabela: providers.partner_address
-- Endereços do Parceiro
CREATE TABLE providers.partner_address (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    country         VARCHAR(100),
    state           VARCHAR(100),
    city            VARCHAR(100),
    district        VARCHAR(100),
    street          VARCHAR(255),
    number          VARCHAR(50),
    zip_code        VARCHAR(20),
    latitude        NUMERIC(10, 8),
    longitude       NUMERIC(10, 8),
    complement      VARCHAR(255),
    partner_id      INTEGER NOT NULL,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira
    CONSTRAINT fk_address_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE
);

-- Tabela: providers.partner_social_network
-- Redes Sociais do Parceiro
CREATE TABLE providers.partner_social_network (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    social_network  INTEGER, -- Assumindo que é um código para o tipo de rede
    url             VARCHAR(500) NOT NULL,
    partner_id      INTEGER NOT NULL,
    audit           TEXT,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira
    CONSTRAINT fk_social_network_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE
);

-- Tabela: providers.partner_activity
-- Atividades/Serviços oferecidos pelo Parceiro
CREATE TABLE providers.partner_activity (
    id              SERIAL PRIMARY KEY,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    partner_id      INTEGER NOT NULL,
    created_at      TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chave Estrangeira
    CONSTRAINT fk_activity_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE
);

-- Tabela: providers.partner_schedule
-- Agendamentos, aulas ou horários específicos para atividades
CREATE TABLE providers.partner_schedule (
    id                      SERIAL PRIMARY KEY,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    weekday                 INTEGER, -- 0=Domingo, 1=Segunda, etc.
    hour                    INTEGER,
    minute                  INTEGER,
    duration                INTEGER, -- Duração em minutos
    slot_limit                   INTEGER, -- Limite de vagas
    description             TEXT,
    start_date              DATE,
    recurrent               BOOLEAN NOT NULL DEFAULT FALSE,
    value                   NUMERIC(10, 2), -- Valor da sessão/aula
    canceled_at             TIMESTAMP WITHOUT TIME ZONE,
    class_opening_time      INTEGER,
    checkin_tolerance_time  INTEGER,
    cancellation_timeout    INTEGER,
    
    partner_id              INTEGER NOT NULL,
    partner_activity_id     INTEGER NOT NULL,
    partner_employee_id     INTEGER,
    
    created_at              TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITHOUT TIME ZONE,
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_schedule_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE,
        
    CONSTRAINT fk_schedule_activity
        FOREIGN KEY (partner_activity_id)
        REFERENCES providers.partner_activity (id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_schedule_employee
        FOREIGN KEY (partner_employee_id)
        REFERENCES providers.partner_employee (id)
        ON DELETE SET NULL
);

-- Tabela: providers.category
-- Necessária para completar a tabela N:N (assumindo que existe)
CREATE TABLE providers.category (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela: providers.partner_category
-- Tabela de ligação N:N entre Parceiros e Categorias
CREATE TABLE providers.partner_category (
    partner_id      INTEGER NOT NULL,
    category_id     INTEGER NOT NULL,
    
    -- Chave Primária Composta
    PRIMARY KEY (partner_id, category_id),
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_pc_partner
        FOREIGN KEY (partner_id)
        REFERENCES providers.partner (id)
        ON DELETE CASCADE,
        
    CONSTRAINT fk_pc_category
        FOREIGN KEY (category_id)
        REFERENCES providers.category (id)
        ON DELETE RESTRICT
);
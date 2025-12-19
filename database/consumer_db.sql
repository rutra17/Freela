--
-- SCRIPT SQL UNIFICADO PARA O ESQUEMA 'CONSUMERS'
-- Consolida Usuários, Saúde, Treinamento e Transações
--

-- 1. Cria o Schema 'consumers' para organizar as tabelas
CREATE SCHEMA IF NOT EXISTS consumers;

--------------------------------------------------------------------------------
-- TABELAS DE REFERÊNCIA GERAL (BASE)
--------------------------------------------------------------------------------

-- Tabela: consumers.rank (Níveis/Patentes do Usuário)
CREATE TABLE consumers.rank (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(100) UNIQUE NOT NULL,
    points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.gpaq (Perguntas Mestra do Questionário GPAQ)
CREATE TABLE consumers.gpaq (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    "order" INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer_type INTEGER,
    answer_false_jump_order INTEGER,
    form INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE ("order", form)
);

-- Tabela: consumers.user_exercise (Catálogo de Exercícios)
CREATE TABLE consumers.user_exercise (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(255) UNIQUE NOT NULL,
    media_url VARCHAR(255),
    note TEXT,
    audit TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.health_playlist
CREATE TABLE consumers.health_playlist (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.health_point (Métricas ou Pontos de Dados de Saúde)
CREATE TABLE consumers.health_point (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    unit VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.health_question (Perguntas de Avaliação/Quiz)
CREATE TABLE consumers.health_question (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


--------------------------------------------------------------------------------
-- TABELAS DE USUÁRIO (A BASE DE TUDO)
--------------------------------------------------------------------------------

-- Tabela: consumers.user (Tabela Principal de Usuários)
CREATE TABLE consumers.user (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(255) NOT NULL,
    registry_code VARCHAR(50) UNIQUE, -- CPF
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password VARCHAR(255) NOT NULL, -- Deve ser um hash
    occupation VARCHAR(100),
    sector VARCHAR(100),
    weight NUMERIC(5, 2),
    height NUMERIC(5, 2),
    diabetic BOOLEAN DEFAULT FALSE,
    hypertensive BOOLEAN DEFAULT FALSE,
    birth_date DATE,
    gender CHAR(1), -- Ex: 'M', 'F', 'O'
    zip_code VARCHAR(20),
    address VARCHAR(255),
    address_number VARCHAR(20),
    fcm_token VARCHAR(255),
    rank_id INTEGER REFERENCES consumers.rank(id) ON DELETE SET NULL, -- FK Resolvida
    external_id VARCHAR(100),
    health_level INTEGER,
    user_type VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_card (Meios de Pagamento do Usuário)
CREATE TABLE consumers.user_card (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    number_mask VARCHAR(50),
    hash VARCHAR(255), -- Hash do cartão ou do token de pagamento
    holder VARCHAR(255),
    type INTEGER,
    flag INTEGER,
    acquirer INTEGER,
    holder_email VARCHAR(255),
    holder_phone VARCHAR(50),
    holder_address VARCHAR(255),
    holder_address_number VARCHAR(20),
    holder_zip_code VARCHAR(20),
    holder_registry_code VARCHAR(50),
    temp_hash VARCHAR(255),
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


--------------------------------------------------------------------------------
-- TABELAS DE INTERAÇÃO E GESTÃO (COM FKs RESOLVIDAS)
--------------------------------------------------------------------------------

-- Tabela: consumers.user_partner_link (Vínculo Usuário-Parceiro)
CREATE TABLE consumers.user_partner_link (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_code VARCHAR(50),
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    -- Parceiro é um usuário (owner/employee) no esquema 'policies' ou 'providers', mas a FK aponta para consumers.user para manter a consistência neste schema.
    partner_id INTEGER REFERENCES consumers.user(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, partner_id)
);

-- Tabela: consumers.user_gpaq (Questionário GPAQ)
CREATE TABLE consumers.user_gpaq (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    gpaq_id INTEGER REFERENCES consumers.gpaq(id) ON DELETE RESTRICT, -- FK Resolvida
    answer_bit INTEGER,
    answer_day INTEGER,
    answer_time INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, gpaq_id)
);

-- Tabela: consumers.health_answer (Respostas dos Usuários às Perguntas de Saúde)
CREATE TABLE consumers.health_answer (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES consumers.health_question(id) ON DELETE RESTRICT,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE, -- FK Resolvida
    answer_value TEXT,
    answered_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_health_playlist (Acompanhamento do Usuário em Playlists)
CREATE TABLE consumers.user_health_playlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE, -- FK Resolvida
    health_playlist_id INTEGER REFERENCES consumers.health_playlist(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    start_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, health_playlist_id)
);

-- Tabela: consumers.user_health_point (Registro dos Dados de Saúde do Usuário)
CREATE TABLE consumers.user_health_point (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE, -- FK Resolvida
    health_point_id INTEGER REFERENCES consumers.health_point(id) ON DELETE RESTRICT,
    value NUMERIC(10, 2) NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_health_form (Submissões de Formulários de Saúde)
CREATE TABLE consumers.user_health_form (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE, -- FK Resolvida
    form_template_id INTEGER, -- FK implícita
    submission_data JSONB,
    submitted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_health_stamp (Conquistas/Carimbos/Badges do Usuário)
CREATE TABLE consumers.user_health_stamp (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE, -- FK Resolvida
    stamp_id INTEGER NOT NULL, -- FK implícita
    achieved_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, stamp_id)
);

-- Tabela: consumers.user_health_feedback (Feedback do Usuário)
CREATE TABLE consumers.user_health_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    rating INTEGER,
    comments TEXT,
    feedback_type VARCHAR(50),
    related_entity_id INTEGER,
    submitted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_training_book (Caderno de Treinos - Livro)
CREATE TABLE consumers.user_training_book (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(255) NOT NULL,
    partner_id INTEGER REFERENCES consumers.user(id) ON DELETE SET NULL, -- O instrutor que prescreveu (FK Resolvida)
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,     -- O usuário proprietário (FK Resolvida)
    note TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, name)
);

-- Tabela: consumers.user_training_sheet (Ficha de Treino - Folha)
CREATE TABLE consumers.user_training_sheet (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    goal INTEGER,
    goal_completed INTEGER DEFAULT 0,
    started_at DATE,
    ended_at DATE,
    note TEXT,
    user_training_book_id INTEGER REFERENCES consumers.user_training_book(id) ON DELETE CASCADE,
    external_code VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_training (Sessão de Treino - Divisão A, B, C)
CREATE TABLE consumers.user_training (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(50) NOT NULL,
    note TEXT,
    user_training_sheet_id INTEGER REFERENCES consumers.user_training_sheet(id) ON DELETE CASCADE,
    trained_at TIMESTAMP WITHOUT TIME ZONE,
    "order" INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_training_sheet_id, name),
    UNIQUE (user_training_sheet_id, "order")
);

-- Tabela: consumers.user_training_exercise (Detalhes dos Exercícios da Sessão)
CREATE TABLE consumers.user_training_exercise (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    session VARCHAR(50),
    session_completed BOOLEAN NOT NULL DEFAULT FALSE,
    repetition VARCHAR(50),
    rest_time VARCHAR(50),
    ended_at TIMESTAMP WITHOUT TIME ZONE,
    note TEXT,
    user_training_id INTEGER REFERENCES consumers.user_training(id) ON DELETE CASCADE,
    user_exercise_id INTEGER REFERENCES consumers.user_exercise(id) ON DELETE RESTRICT, -- FK Resolvida
    "order" INTEGER,
    external_code VARCHAR(100),
    charge INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_training_id, user_exercise_id, "order")
);


--------------------------------------------------------------------------------
-- TABELAS DE TRANSAÇÃO E LOGÍSTICA
--------------------------------------------------------------------------------

-- Tabela: consumers.user_time (Log de Uso/Check-in)
CREATE TABLE consumers.user_time (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES consumers.user_card(id) ON DELETE SET NULL,
    partner_id INTEGER REFERENCES providers.partner(id) ON DELETE RESTRICT, -- O parceiro/local onde ocorreu o evento (FK Resolvida)
    type VARCHAR(20),
    status VARCHAR(20),
    canceled_at TIMESTAMP WITHOUT TIME ZONE,
    finished_at TIMESTAMP WITHOUT TIME ZONE,
    partner_schedule_id INTEGER, -- FK implícita
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.user_scheduling (Agendamento de Serviços)
CREATE TABLE consumers.user_scheduling (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES consumers.user_card(id) ON DELETE SET NULL,
    partner_schedule_id INTEGER, -- FK implícita
    scheduled_at DATE NOT NULL,
    hour VARCHAR(5),
    minute VARCHAR(5),
    full_time VARCHAR(10),
    status VARCHAR(20),
    canceled_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, scheduled_at, hour, minute)
);

-- Tabela: consumers.user_appointment (Agendamentos de Consultas)
CREATE TABLE consumers.user_appointment (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE CASCADE,
    partner_id INTEGER REFERENCES consumers.user(id) ON DELETE RESTRICT, -- O profissional agendado (FK Resolvida)
    description VARCHAR(255),
    details TEXT,
    external_code VARCHAR(100),
    appointment_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    canceled_at TIMESTAMP WITHOUT TIME ZONE,
    hour VARCHAR(5),
    minute VARCHAR(5),
    full_time VARCHAR(10),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: consumers.payment (Transações de Pagamento)
CREATE TABLE consumers.payment (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    card_mask VARCHAR(50),
    amount_due NUMERIC(10, 2) NOT NULL,
    amount_hour NUMERIC(10, 2),
    hours NUMERIC(5, 2),
    card_id INTEGER REFERENCES consumers.user_card(id) ON DELETE SET NULL,
    partner_id INTEGER REFERENCES consumers.user(id) ON DELETE RESTRICT,  -- FK Resolvida
    user_time_id INTEGER REFERENCES consumers.user_time(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reference VARCHAR(255),
    user_scheduling_id INTEGER REFERENCES consumers.user_scheduling(id) ON DELETE SET NULL,
    external_id VARCHAR(100),
    billing_type VARCHAR(50),
    user_name VARCHAR(255),
    transferred_value NUMERIC(10, 2) DEFAULT 0.0,
    value_obtained NUMERIC(10, 2) DEFAULT 0.0,
    payment_type VARCHAR(50)
);

-- Tabela: consumers.refunds (Estornos/Reembolsos)
CREATE TABLE consumers.refunds (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    payment_id INTEGER REFERENCES consumers.payment(id) ON DELETE RESTRICT,
    user_id INTEGER REFERENCES consumers.user(id) ON DELETE SET NULL, -- FK Resolvida
    refund_date TIMESTAMP WITHOUT TIME ZONE,
    refund_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
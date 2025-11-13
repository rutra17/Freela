-- SCRIPT CORRIGIDO: Adicionado prefixo 'communities.' em tudo

CREATE SCHEMA IF NOT EXISTS communities;
-- 1. Tabela de USUÁRIOS importadaa para as FKs funcionarem)
--

--
-- 2. Tabela communities.tag (Tabela mestre)
--
CREATE TABLE communities.communities_tag (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--
-- 3. Tabela communities.social_group (Tabela mestre)
--
CREATE TABLE communities.communities_social_group (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    privacy VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    details TEXT,
    user_id INTEGER REFERENCES consumers.user(id),             
    partner_employee_id INTEGER REFERENCES consumers.user(id), 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--
-- 4. Tabela communities.social_event
--
CREATE TABLE communities.communities_social_event (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(255) NOT NULL,
    responsible_name VARCHAR(255),
    type VARCHAR(50),
    privacy VARCHAR(50),
    value NUMERIC(10, 2) DEFAULT 0.00,
    scheduled_date DATE,
    scheduled_time TIME WITHOUT TIME ZONE,
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    street VARCHAR(255),
    number VARCHAR(20),
    zip_code VARCHAR(20),
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    complement VARCHAR(255),
    details TEXT,
    image_url VARCHAR(255),
    user_id INTEGER REFERENCES consumers.user(id),
    partner_employee_id INTEGER REFERENCES consumers.user(id),
    group_id INTEGER REFERENCES communities.communities_social_group(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--
-- 5. Tabela communities.publication
--
CREATE TABLE communities.communities_publication (
    id SERIAL PRIMARY KEY,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    responsible_name VARCHAR(255),
    type VARCHAR(50),
    privacy VARCHAR(50),
    text TEXT,
    content_url VARCHAR(255),
    user_id INTEGER REFERENCES consumers.user(id),
    partner_employee_id INTEGER REFERENCES consumers.user(id),
    group_id INTEGER REFERENCES communities.communities_social_group(id) ON DELETE SET NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--
-- 6. Tabela communities.publication_tag (Tabela de Junção N:N)
--
CREATE TABLE communities.communities_publication_tag (
    publication_id INTEGER REFERENCES communities.communities_publication(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES communities.communities_tag(id) ON DELETE CASCADE,
    PRIMARY KEY (publication_id, tag_id)
);
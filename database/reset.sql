--botão de reset

-- ARQUIVO: 0_reset_database.sql
-- OBJETIVO: Limpar completamente o banco de dados.

SET client_min_messages TO WARNING;

-- Derruba todos os schemas na ordem correta de dependência
DROP SCHEMA IF EXISTS consumers CASCADE;
DROP SCHEMA IF EXISTS providers CASCADE;
DROP SCHEMA IF EXISTS companies CASCADE;
DROP SCHEMA IF EXISTS communities CASCADE;
DROP SCHEMA IF EXISTS analytics CASCADE;
DROP SCHEMA IF EXISTS policies CASCADE;

-- Limpa tabelas órfãs no public (se houver)
DROP TABLE IF EXISTS public.alembic_version CASCADE;
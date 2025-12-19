--validador das 9 tabelas

-- ARQUIVO: 11_verify_structure.sql
-- OBJETIVO: Validar se todos os 6 schemas e as tabelas críticas dos 9 arquivos existem.

WITH schema_check AS (
    SELECT 
        table_schema, 
        COUNT(*) as tables_count 
    FROM information_schema.tables 
    WHERE table_schema IN ('consumers', 'providers', 'companies', 'communities', 'analytics', 'policies')
    GROUP BY table_schema
)
SELECT * FROM schema_check
ORDER BY table_schema;

-- Verificação de Integridade das Tabelas Críticas (Cross-Schema)
-- Se retornar erro aqui, alguma conexão falhou.
SELECT 'consumers.user_interaction (NOVA)' as check_item, count(*) FROM information_schema.tables WHERE table_schema='consumers' AND table_name='user_interaction'
UNION ALL
SELECT 'providers.partner (BASE)', count(*) FROM information_schema.tables WHERE table_schema='providers' AND table_name='partner'
UNION ALL
SELECT 'companies.companies_client (B2B)', count(*) FROM information_schema.tables WHERE table_schema='companies' AND table_name='companies_client'
UNION ALL
SELECT 'consumers.user_scheduling (CONEXAO)', count(*) FROM information_schema.tables WHERE table_schema='consumers' AND table_name='user_scheduling';

-- Verificação do Índice JSONB (Fundamental para o BI)
SELECT 
    tablename as tabela, 
    indexname as indice, 
    indexdef as definicao
FROM pg_indexes 
WHERE indexname = 'IDX_interaction_metadata';
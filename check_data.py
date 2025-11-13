# check_data.py (Versão Final com Hard Wins)
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERRO: Não foi possível encontrar a DATABASE_URL no arquivo .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# Tabelas principais
tables_to_check = [
    "consumers.user",
    "providers.partner",
    "consumers.user_scheduling",
    "consumers.payment",
    "companies.companies_client",
    "companies.companies_client_collaborator",
    # Easy Wins
    "consumers.user_health_point",
    "consumers.user_health_feedback",
    # Hard Wins
    "analytics.web_events",
    "analytics.marketing_costs",
    "consumers.missions",
    "consumers.user_missions",
    "companies.campaigns",
    "companies.user_campaign_participation",
    "consumers.user_mev_score"
]

# Colunas "Easy Win"
columns_to_check = {
    "consumers.user_time": "finished_at",
    "consumers.payment": "transferred_value"
}

print("--- Verificando contagem de linhas nas tabelas ---")
all_good = True
try:
    with engine.connect() as conn:
        for table in tables_to_check:
            try:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                count = count_result[0]
                
                if count > 0:
                    print(f"✅ [SUCESSO] {table}: {count} linhas.")
                else:
                    print(f"❌ [FALHA] {table}: 0 linhas. O script de popular falhou.")
                    all_good = False
            except Exception as e:
                print(f"🔥 [ERRO SQL] {table}: {e}")
                all_good = False
        
        print("\n--- Verificando colunas dos 'Easy Wins' ---")
        
        for table, column in columns_to_check.items():
            try:
                count_result = conn.execute(
                    text(f"SELECT COUNT({column}) FROM {table} WHERE {column} IS NOT NULL")
                ).fetchone()
                count = count_result[0]
                
                if count > 0:
                    print(f"✅ [SUCESSO] {table}.{column} está populada ({count} linhas).")
                else:
                    print(f"❌ [FALHA] {table}.{column} está vazia (0 linhas).")
                    all_good = False
            except Exception as e:
                print(f"🔥 [ERRO SQL] {table}.{column}: {e}")
                all_good = False

    if all_good:
        print("\n[PROJETO CONCLUÍDO!] O banco está 100% populado (incluindo Easy e Hard Wins).")
    else:
        print("\n[PROBLEMA] Algumas tabelas dos Hard Wins estão vazias.")

except Exception as e:
    print(f"\n[ERRO CRÍTICO] Não foi possível conectar ao banco: {e}")
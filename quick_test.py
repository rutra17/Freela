# quick_test.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega a DATABASE_URL (com o usuário bi_reader) do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERRO: Não foi possível encontrar a DATABASE_URL no arquivo .env")
    exit()

print(f"Conectando com o usuário: {DATABASE_URL.split('@')[0]}...") # Mostra o usuário

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("\n--- Testando bi.dau_by_day (limite 5) ---")
        result_dau = conn.execute(text("SELECT * FROM bi.dau_by_day LIMIT 5")).fetchall()
        print(result_dau)
        
        print("\n--- Testando bi.checkins_per_day (limite 5) ---")
        result_checkins = conn.execute(text("SELECT * FROM bi.checkins_per_day LIMIT 5")).fetchall()
        print(result_checkins)

        print("\n--- Testando bi.revenue_monthly (limite 5) ---")
        result_revenue = conn.execute(text("SELECT * FROM bi.revenue_monthly LIMIT 5")).fetchall()
        print(result_revenue)

        print("\n--- Testando bi.user_funnel (limite 5) ---")
        result_funnel = conn.execute(text("SELECT * FROM bi.user_funnel LIMIT 5")).fetchall()
        print(result_funnel)
        
    print("\n[SUCESSO] Teste concluído. O usuário bi_reader tem permissão de leitura!")

except Exception as e:
    print(f"\n[ERRO] O teste falhou: {e}")
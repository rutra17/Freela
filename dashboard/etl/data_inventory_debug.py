# etl/data_inventory_debug.py
import os, json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()  # carrega .env local

DATABASE_URL = os.getenv("DATABASE_URL")
print("DEBUG: DATABASE_URL =", ("SET" if DATABASE_URL else "NOT SET"))

if not DATABASE_URL:
    raise SystemExit("ERROR: DATABASE_URL is not set. Coloque no .env ou exporte.")

# Criar engine (timeout curto)
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})

out = []
try:
    with engine.connect() as conn:
        # 1) informação básica do servidor
        ver = conn.execute(text("SELECT version()")).fetchone()
        print("DEBUG: Postgres version:", ver[0])

        # 2) listar schemas/tables visíveis para este usuário
        q = text("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog','information_schema')
            ORDER BY table_schema, table_name;
        """)
        # Linha 32 - NOVA
        # --- INÍCIO DA CORREÇÃO ---
        result = conn.execute(q)
        keys = result.keys()
        tables = [dict(zip(keys, r)) for r in result]
        # --- FIM DA CORREÇÃO ---
        print(f"DEBUG: found {len(tables)} tables (visible to this user).")

        for t in tables:
            s = t['table_schema']
            name = t['table_name']
            row_count = None
            sample = None
            try:
                row_count = conn.execute(text(f"SELECT count(*) FROM {s}.{name}")).scalar()
                
                # --- INÍCIO DA CORREÇÃO DE SAMPLE ---
                sample_result = conn.execute(text(f"SELECT * FROM {s}.{name} LIMIT 3"))
                sample_keys = sample_result.keys()
                sample = [dict(zip(sample_keys, r)) for r in sample_result]
                # --- FIM DA CORREÇÃO DE SAMPLE ---
                
            except Exception as e:
                sample = f"ERROR reading table: {str(e)}"
            out.append({"schema": s, "table": name, "row_count": row_count, "sample": sample})
except SQLAlchemyError as e:
    raise SystemExit("DB ERROR: " + str(e))

with open("data_inventory_debug.json", "w", encoding="utf-8") as f:
    json.dump(out, f, default=str, indent=2)

print("Wrote data_inventory_debug.json with", len(out), "entries.")

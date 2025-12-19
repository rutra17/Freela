import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
import subprocess
import time

# --- CONFIGURAÇÕES ---
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = "abcde"           # <--- Sua senha
DB_NAME = "banco"           # Nome do banco

# Pasta onde estão TODOS os 11 arquivos SQL
SQL_FOLDER = "database"

# Ordem EXATA de execução (11 arquivos)
SQL_FILES_ORDER = [
    "reset.sql",             # 1. Limpa schemas (se existirem)
    "policies.sql",          # 2. Permissões
    "providers.sql",         # 3. Parceiros
    "consumer_db.sql",       # 4. Usuários
    "companies.sql",         # 5. Empresas
    "communities.sql",       # 6. Comunidades
    "analytics.sql",         # 7. Analytics
    "interactions.sql",      # 8. Interações (User + Partner)
    "gamification_b2b.sql",  # 9. Missões
    "scores.sql",            # 10. Scores
    "validador.sql"          # 11. Validação final
]

def drop_and_create_db():
    print(f"\n--- 1. REINICIANDO BANCO DE DADOS: {DB_NAME} ---")
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Derruba conexões ativas
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{DB_NAME}'
            AND pid <> pg_backend_pid();
        """)
        
        # O Python faz o Hard Reset (Drop Database)
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        print(f"-> Banco '{DB_NAME}' deletado (Hard Reset).")
        
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"-> Banco '{DB_NAME}' criado do zero.")
        
        cur.close()
        conn.close()
        time.sleep(1) 
    except Exception as e:
        print(f"ERRO CRÍTICO AO RESETAR BANCO: {e}")
        sys.exit(1)

def run_sql_files():
    print(f"\n--- 2. EXECUTANDO 11 ARQUIVOS SQL ---")
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        conn.autocommit = True
        cur = conn.cursor()

        for filename in SQL_FILES_ORDER:
            file_path = os.path.join(SQL_FOLDER, filename)
            
            if os.path.exists(file_path):
                print(f"-> Executando: {filename}...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    try:
                        cur.execute(sql_content)
                        # Se for o validador, tenta mostrar o resultado (opcional)
                        if filename == "validador.sql":
                            print("   [Validador rodou com sucesso - verifique logs se necessário]")
                    except Exception as sql_error:
                        print(f"   [AVISO] Erro em {filename}: {sql_error}")
                        # Não para o script no reset.sql, mas para nos outros
                        if filename != "reset.sql": 
                             raise sql_error
            else:
                print(f"ERRO: Arquivo {filename} não encontrado em '{SQL_FOLDER}'!")
                sys.exit(1)
        
        print("-> Todos os arquivos SQL processados.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERRO FATAL AO RODAR SQL: {e}")
        sys.exit(1)

def run_fake_data_generator():
    print(f"\n--- 3. POPULANDO DADOS FAKES ---")
    script_name = "generate_fake_data.py"
    
    if not os.path.exists(script_name):
        print(f"ERRO: {script_name} não encontrado na raiz.")
        return

    try:
        process = subprocess.Popen(
            ["python", script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='latin-1'
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
    except Exception as e:
        print(f"Erro no gerador: {e}")

if __name__ == "__main__":
    drop_and_create_db()
    run_sql_files()
    run_fake_data_generator()
    print("\n=== AMBIENTE PRONTO! ===")
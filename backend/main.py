# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (DATABASE_URL) do arquivo .env
print("Carregando .env...")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERRO: DATABASE_URL não encontrada no .env")
    raise SystemExit("ERRO: DATABASE_URL não encontrada no .env")

try:
    # Cria a "engine" de conexão com o banco
    # O 'bi_reader' será usado para todas as consultas
    engine = create_engine(DATABASE_URL)
    print("Conexão com o banco de dados (engine) criada com sucesso.")
except Exception as e:
    print(f"ERRO ao criar a engine: {e}")
    raise SystemExit

app = FastAPI(title="BI Backend MVP")
print("Aplicação FastAPI iniciada.")

@app.get("/")
def read_root():
    return {"message": "API de BI está no ar. Acesse /docs para ver os endpoints."}

# Endpoint para /bi/dau
@app.get("/bi/dau")
def get_dau(days: int = 30):
    """
    Retorna o DAU (Usuários Ativos por Dia) dos últimos N dias.
    Consulta 'consumers.user_time' (check-ins) para definir atividade.
    """
    params = {"days": days}
    
    # SQL modificado para usar a tabela real 'consumers.user_time'
    # DAU = Contagem de usuários ÚNICOS por dia
    sql = """
        SELECT 
            DATE(created_at) as day, 
            COUNT(DISTINCT user_id) as dau
        FROM consumers.user_time
        WHERE created_at >= (CURRENT_DATE - INTERVAL '1 day' * :days)
        GROUP BY day 
        ORDER BY day DESC
    """
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        print(f"ERRO no endpoint /bi/dau: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/checkins")
def get_checkins(partner_id: int = None, days: int = 30):
    """
    Retorna o número de checkins por dia dos últimos N dias.
    Consulta 'consumers.user_time' diretamente (agora com partner_id).
    """
    params = {"days": days}
    
    sql = """
        SELECT 
            DATE(created_at) as day, 
            COUNT(id) as total_checkins 
        FROM consumers.user_time
    """
    
    # Agora podemos filtrar diretamente, é mais rápido
    where_clauses = ["type = 'CHECKIN'"]
    
    if partner_id:
        where_clauses.append("partner_id = :partner_id")
        params["partner_id"] = partner_id
    
    sql += " WHERE " + " AND ".join(where_clauses)
    sql += " GROUP BY day ORDER BY day DESC LIMIT :days"
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        print(f"ERRO no endpoint /bi/checkins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# [SUBSTITUA AS FUNÇÕES get_revenue E get_reservations NO SEU main.py]

# Endpoint para /bi/revenue
# [SUBSTITUA A FUNÇÃO get_revenue NO SEU main.py]

@app.get("/bi/revenue")
def get_revenue(partner_id: int = None, days: int = 30):
    """
    Retorna o faturamento (revenue) por dia dos últimos N dias.
    Consulta 'consumers.payment' e faz JOIN para encontrar o partner_id.
    """
    params = {"days": days}
    
    # SQL base
    sql = """
        SELECT 
            DATE(p.created_at) as day, 
            SUM(p.amount_due) as total_revenue 
        FROM consumers.payment p
    """
    
    where_clauses = ["p.status = 'PAID'"]
    
    # CORREÇÃO: Se houver filtro de parceiro, precisamos
    # fazer o JOIN para encontrá-lo, assim como na query de reservas.
    if partner_id:
        # JOIN: payment -> user_scheduling -> partner_schedule
        sql += """
            JOIN consumers.user_scheduling s ON p.user_scheduling_id = s.id
            JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id
        """
        where_clauses.append("ps.partner_id = :partner_id")
        params["partner_id"] = partner_id
    
    # Adiciona a cláusula WHERE ao SQL
    sql += " WHERE " + " AND ".join(where_clauses)
        
    # Agrupamento, Ordenação e Limite
    sql += " GROUP BY day ORDER BY day DESC LIMIT :days"
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            # Formata a saída
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [float(r[1]) for r in rows]
            }
    except Exception as e:
        print(f"ERRO no endpoint /bi/revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para /bi/reservations
@app.get("/bi/reservations")
def get_reservations(partner_id: int = None, days: int = 30):
    """
    Retorna o número de reservas por dia dos últimos N dias.
    Consulta 'consumers.user_scheduling' e faz JOIN com 'providers.partner_schedule'.
    """
    params = {"days": days}
    
    # SQL modificado para usar as tabelas reais
    #
    sql = """
        SELECT 
            DATE(s.created_at) as day, 
            COUNT(s.id) as total_reservations
        FROM consumers.user_scheduling s
    """
    
    where_clauses = []
    
    # Para filtrar por partner_id, precisamos unir as tabelas
    # s.partner_schedule_id -> ps.id
    # ps.partner_id
    if partner_id:
        sql += " JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id"
        where_clauses.append("ps.partner_id = :partner_id")
        params["partner_id"] = partner_id
    
    # Adiciona a cláusula WHERE ao SQL
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
        
    # Agrupamento, Ordenação e Limite
    sql += " GROUP BY day ORDER BY day DESC LIMIT :days"
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        print(f"ERRO no endpoint /bi/reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

print("Endpoints definidos. Servidor pronto para iniciar.")
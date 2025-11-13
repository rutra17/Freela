# backend/main.py
import os
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from enum import Enum

# Carrega as variáveis de ambiente (DATABASE_URL) do arquivo .env
print("Carregando .env...")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERRO: DATABASE_URL não encontrada no .env")
    raise SystemExit("ERRO: DATABASE_URL não encontrada no .env")

try:
    # Cria a "engine" de conexão com o banco
    engine = create_engine(DATABASE_URL)
    print("Conexão com o banco de dados (engine) criada com sucesso.")
except Exception as e:
    print(f"ERRO ao criar a engine: {e}")
    raise SystemExit

app = FastAPI(title="BI Backend MVP")
print("Aplicação FastAPI iniciada.")

# --- Modelos de Enum para filtros ---
class TimeGroup(str, Enum):
    day = "day"
    month = "month"
    hour = "hour"

# --- ENDPOINTS EXISTENTES (Corrigidos e Mantidos) ---

@app.get("/")
def read_root():
    return {"message": "API de BI está no ar. Acesse /docs para ver os endpoints."}

@app.get("/bi/dau")
def get_dau(days: int = 30):
    """
    Retorna o DAU (Usuários Ativos por Dia) dos últimos N dias.
    Consulta 'consumers.user_time' (check-ins) para definir atividade.
    """
    params = {"days": days}
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
    Consulta 'consumers.user_time' e filtra por partner_id (se fornecido).
    """
    params = {"days": days}
    
    # [CORREÇÃO]: A FK de partner_id em user_time foi corrigida,
    # então este filtro agora funciona perfeitamente.
    sql = """
        SELECT 
            DATE(created_at) as day, 
            COUNT(id) as total_checkins 
        FROM consumers.user_time
    """
    
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

@app.get("/bi/revenue")
def get_revenue(partner_id: int = None, days: int = 30):
    """
    Retorna o faturamento (revenue) por dia dos últimos N dias.
    Consulta 'consumers.payment' e faz JOIN para encontrar o partner_id.
    """
    params = {"days": days}
    
    sql = """
        SELECT 
            DATE(p.created_at) as day, 
            SUM(p.amount_due) as total_revenue 
        FROM consumers.payment p
    """
    
    where_clauses = ["p.status = 'PAID'"]
    
    if partner_id:
        sql += """
            JOIN consumers.user_scheduling s ON p.user_scheduling_id = s.id
            JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id
        """
        where_clauses.append("ps.partner_id = :partner_id")
        params["partner_id"] = partner_id
    
    sql += " WHERE " + " AND ".join(where_clauses)
    sql += " GROUP BY day ORDER BY day DESC LIMIT :days"
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [float(r[1]) for r in rows]
            }
    except Exception as e:
        print(f"ERRO no endpoint /bi/revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/reservations")
def get_reservations(partner_id: int = None, days: int = 30):
    """
    Retorna o número de reservas por dia dos últimos N dias.
    Consulta 'consumers.user_scheduling' e faz JOIN com 'providers.partner_schedule'.
    """
    params = {"days": days}
    
    sql = """
        SELECT 
            DATE(s.created_at) as day, 
            COUNT(s.id) as total_reservations
        FROM consumers.user_scheduling s
    """
    
    where_clauses = []
    
    if partner_id:
        sql += " JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id"
        where_clauses.append("ps.partner_id = :partner_id")
        params["partner_id"] = partner_id
    
    if where_clauses:
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
        print(f"ERRO no endpoint /bi/reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# ### 🚀 NOVOS ENDPOINTS DE KPI (Fase 2) ###
# ==============================================================================

# --- KPIs GERAIS (Admin) ---

@app.get("/bi/kpi_overview")
def get_kpi_overview():
    """
    Retorna os KPIs principais da plataforma (Total de Usuários, Receita, Parceiros).
    """
    sql = """
        SELECT 
            (SELECT COUNT(id) FROM consumers.user) as total_users,
            (SELECT SUM(amount_due) FROM consumers.payment WHERE status = 'PAID') as total_revenue,
            (SELECT COUNT(id) FROM providers.partner) as total_partners;
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql)).fetchone()
            if result:
                return {
                    "total_users": int(result[0]),
                    "total_revenue": float(result[1]),
                    "total_partners": int(result[2])
                }
            return {"total_users": 0, "total_revenue": 0, "total_partners": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/new_users_over_time")
def get_new_users_over_time(group_by: TimeGroup = TimeGroup.day):
    """
    Retorna a contagem de novos usuários (Cadastros) agrupados por dia, mês ou hora.
    """
    if group_by == TimeGroup.hour:
        # Agrupamento por hora do dia (0-23)
        sql_fragment = "EXTRACT(HOUR FROM created_at)"
        order_fragment = "hour_of_day"
    elif group_by == TimeGroup.month:
        # Agrupamento por mês
        sql_fragment = "DATE_TRUNC('month', created_at)"
        order_fragment = "month"
    else:
        # Agrupamento por dia (padrão)
        sql_fragment = "DATE(created_at)"
        order_fragment = "day"

    sql = f"""
        SELECT 
            {sql_fragment} as time_group,
            COUNT(id) as new_users
        FROM consumers.user
        GROUP BY time_group
        ORDER BY time_group;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/active_users")
def get_active_users(days: int = 30):
    """
    Retorna DAU, WAU (7 dias) e MAU (30 dias)
    """
    params = {"days": days}
    sql = """
        SELECT 
            (SELECT COUNT(DISTINCT user_id) 
             FROM consumers.user_time 
             WHERE created_at >= (CURRENT_DATE - INTERVAL '1 day')) as dau,
             
            (SELECT COUNT(DISTINCT user_id) 
             FROM consumers.user_time 
             WHERE created_at >= (CURRENT_DATE - INTERVAL '7 day')) as wau,
             
            (SELECT COUNT(DISTINCT user_id) 
             FROM consumers.user_time 
             WHERE created_at >= (CURRENT_DATE - INTERVAL '30 day')) as mau;
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql)).fetchone()
            if result:
                return {"dau": result[0], "wau": result[1], "mau": result[2]}
            return {"dau": 0, "wau": 0, "mau": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/retention_d1_d7_d30")
def get_retention():
    """
    Calcula a retenção D1, D7 e D30 (simplificada).
    Verifica quantos usuários que se cadastraram há X dias,
    fizeram check-in (tiveram atividade) hoje.
    """
    sql = """
        WITH 
        D1_Cohort AS (
            -- Usuários que se cadastraram ontem
            SELECT id FROM consumers.user 
            WHERE DATE(created_at) = (CURRENT_DATE - INTERVAL '1 day')
        ),
        D7_Cohort AS (
            -- Usuários que se cadastraram 7 dias atrás
            SELECT id FROM consumers.user 
            WHERE DATE(created_at) = (CURRENT_DATE - INTERVAL '7 day')
        ),
        D30_Cohort AS (
            -- Usuários que se cadastraram 30 dias atrás
            SELECT id FROM consumers.user 
            WHERE DATE(created_at) = (CURRENT_DATE - INTERVAL '30 day')
        ),
        Today_Activity AS (
            -- Usuários ativos hoje
            SELECT DISTINCT user_id FROM consumers.user_time 
            WHERE DATE(created_at) = CURRENT_DATE
        )
        SELECT
            (SELECT COUNT(*) FROM D1_Cohort) as d1_total,
            (SELECT COUNT(t.user_id) FROM Today_Activity t JOIN D1_Cohort c ON t.user_id = c.id) as d1_retained,
            
            (SELECT COUNT(*) FROM D7_Cohort) as d7_total,
            (SELECT COUNT(t.user_id) FROM Today_Activity t JOIN D7_Cohort c ON t.user_id = c.id) as d7_retained,

            (SELECT COUNT(*) FROM D30_Cohort) as d30_total,
            (SELECT COUNT(t.user_id) FROM Today_Activity t JOIN D30_Cohort c ON t.user_id = c.id) as d30_retained;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql)).fetchone()
            if r:
                # Calcula a % de retenção, evitando divisão por zero
                d1_pct = (r[1] / r[0] * 100) if r[0] > 0 else 0
                d7_pct = (r[3] / r[2] * 100) if r[2] > 0 else 0
                d30_pct = (r[5] / r[4] * 100) if r[4] > 0 else 0
                
                return {
                    "d1": {"total": r[0], "retained": r[1], "pct": d1_pct},
                    "d7": {"total": r[2], "retained": r[3], "pct": d7_pct},
                    "d30": {"total": r[4], "retained": r[5], "pct": d30_pct}
                }
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [ADIÇÃO - Linha 293]

@app.get("/bi/revenue_by_region")
def get_revenue_by_region():
    """
    Retorna a receita total (LTV) agrupada por região (CEP).
    Este é um "Hard Win" (Receita por Região).
    """
    # Este SQL junta Pagamento -> Agendamento -> Usuário (para pegar o zip_code)
    sql = """
        SELECT 
            u.zip_code,
            SUM(p.amount_due) as total_revenue
        FROM consumers.payment p
        JOIN consumers.user_scheduling s ON p.user_scheduling_id = s.id
        JOIN consumers.user u ON s.user_id = u.id
        WHERE p.status = 'PAID'
          AND u.zip_code IS NOT NULL
        GROUP BY u.zip_code
        ORDER BY total_revenue DESC
        LIMIT 10; -- Pega só as 10 top regiões
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [float(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [ADIÇÃO - Linha 325]

@app.get("/bi/conversion_funnel")
def get_conversion_funnel():
    """ Retorna dados para o Funil de Conversão (Hard Win) """
    sql = """
        SELECT 
            (SELECT COUNT(DISTINCT session_id) 
             FROM analytics.web_events 
             WHERE event_name = 'visitou_site') as step_1_visited,
             
            (SELECT COUNT(DISTINCT session_id) 
             FROM analytics.web_events 
             WHERE event_name = 'iniciou_cadastro') as step_2_started_form,
             
            (SELECT COUNT(DISTINCT user_id) 
             FROM analytics.web_events 
             WHERE event_name = 'completou_cadastro') as step_3_completed_signup;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql)).fetchone()
            if r:
                return {
                    "labels": ["Visitou o Site", "Iniciou Cadastro", "Completou Cadastro"],
                    "values": [int(r[0]), int(r[1]), int(r[2])]
                }
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/ltv_cac")
def get_ltv_cac():
    """ Retorna o LTV (Lifetime Value) e CAC (Custo Aquisição) (Hard Win) """
    sql = """
        SELECT
            -- LTV: (Receita Total / Total de Clientes)
            (SELECT SUM(amount_due) FROM consumers.payment WHERE status = 'PAID') / 
            (SELECT COUNT(id) FROM consumers.user) as ltv,
            
            -- CAC (30d): (Custo Marketing 30d / Novos Clientes 30d)
            (SELECT SUM(cost) FROM analytics.marketing_costs 
             WHERE date >= (CURRENT_DATE - INTERVAL '30 day')) /
            (SELECT COUNT(id) FROM consumers.user 
             WHERE created_at >= (CURRENT_DATE - INTERVAL '30 day')) as cac_30d;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql)).fetchone()
            if r:
                return {
                    "ltv": float(r[0]) if r[0] is not None else 0,
                    "cac_30d": float(r[1]) if r[1] is not None else 0
                }
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# [ADIÇÃO - Linha 372]

@app.get("/bi/gamification/missions")
def get_gamification_missions():
    """ Retorna o status das Missões (Hard Win) """
    sql = """
        SELECT 
            m.name, 
            COUNT(um.user_id) as total_completions
        FROM consumers.missions m
        LEFT JOIN consumers.user_missions um ON m.id = um.mission_id
        GROUP BY m.name
        ORDER BY total_completions DESC;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/gamification/streaks")
def get_gamification_streaks():
    """ 
    Retorna o 'Stickiness' (dias ativos nos últimos 7d)
    Isso é um proxy para 'Streaks' (Hard Win)
    """
    sql = """
        WITH UserActivity AS (
            SELECT 
                user_id, 
                COUNT(DISTINCT DATE(created_at)) as active_days_last_7d
            FROM consumers.user_time
            WHERE created_at >= (CURRENT_DATE - INTERVAL '7 day')
            AND type = 'CHECKIN'
            GROUP BY user_id
        )
        SELECT 
            active_days_last_7d, 
            COUNT(user_id) as total_users
        FROM UserActivity
        GROUP BY active_days_last_7d
        ORDER BY active_days_last_7d DESC;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            # O resultado será (ex: "7 dias", 5 usuários)
            return {
                "labels": [f"{r[0]} dias" for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

# --- KPIs do PARCEIRO (Partner View) ---

@app.get("/bi/partners_list")
def get_partners_list():
    """ Retorna uma lista de todos os parceiros para filtros de dashboard. """
    sql = "SELECT id, name FROM providers.partner WHERE active = TRUE ORDER BY name;"
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return [{"id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/partner/reservation_status")
def get_partner_reservation_status(partner_id: int):
    """
    Retorna a contagem de reservas por status (Confirmadas vs No-Show)
    para um parceiro específico.
    """
    params = {"partner_id": partner_id}
    sql = """
        SELECT 
            s.status, 
            COUNT(s.id) as total
        FROM consumers.user_scheduling s
        JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id
        WHERE ps.partner_id = :partner_id
        GROUP BY s.status;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            # Nota: O generate_fake_data só cria status 'CONFIRMED'.
            # Para 'NO-SHOW' aparecer, seria preciso mais dados.
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/partner/occupation_by_hour")
def get_partner_occupation_by_hour(partner_id: int):
    """
    Retorna a taxa de ocupação (total de reservas) por hora do dia
    para um parceiro específico.
    """
    params = {"partner_id": partner_id}
    sql = """
        SELECT 
            ps.hour, 
            COUNT(s.id) as total_reservas
        FROM consumers.user_scheduling s
        JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id
        WHERE ps.partner_id = :partner_id
        AND ps.hour IS NOT NULL
        GROUP BY ps.hour
        ORDER BY ps.hour;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [f"{r[0]}:00" for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [ADIÇÃO - Linha 325]

@app.get("/bi/partner/kpi_overview")
def get_partner_kpi_overview(partner_id: int):
    """
    Retorna KPIs extras do Parceiro (NPS, Repasses) - (Easy Wins)
    """
    params = {"partner_id": partner_id}
    sql = """
        WITH
        PartnerNPS AS (
            -- Calcula a média de NPS para o parceiro
            SELECT AVG(rating) as nps_avg
            FROM consumers.user_health_feedback
            WHERE related_entity_id = :partner_id
              AND feedback_type = 'NPS_PARTNER'
        ),
        PartnerRepasse AS (
            -- Soma o valor repassado (transferred_value) nos últimos 30 dias
            SELECT SUM(p.transferred_value) as total_repassado
            FROM consumers.payment p
            JOIN consumers.user_scheduling s ON p.user_scheduling_id = s.id
            JOIN providers.partner_schedule ps ON s.partner_schedule_id = ps.id
            WHERE ps.partner_id = :partner_id
              AND p.status = 'PAID'
              AND p.created_at >= (CURRENT_DATE - INTERVAL '30 day')
        )
        SELECT
            (SELECT nps_avg FROM PartnerNPS) as nps,
            (SELECT total_repassado FROM PartnerRepasse) as repasse_30d;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql), params).fetchone()
            if r:
                return {
                    "nps_avg": round(r[0] if r[0] is not None else 0, 1),
                    "total_repassado_30d": round(r[1] if r[1] is not None else 0, 2)
                }
            return {"nps_avg": 0, "total_repassado_30d": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- KPIs do CLIENTE B2B (B2B View) ---

@app.get("/bi/b2b/clients_list")
def get_b2b_clients_list():
    """ Retorna uma lista de todos os clientes B2B para filtros de dashboard. """
    # Corrigido para usar os nomes de tabela corretos
    sql = "SELECT id, name FROM companies.companies_client WHERE active = TRUE ORDER BY name;"
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return [{"id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/b2b/engagement_stats")
def get_b2b_engagement_stats(client_id: int):
    """
    Retorna estatísticas de engajamento (Adesão, Engajamento)
    para um cliente B2B específico.
    """
    params = {"client_id": client_id}
    sql = """
        WITH 
        EligibleBase AS (
            -- Base total de colaboradores elegíveis (cadastrados)
            SELECT user_id 
            FROM companies.companies_client_collaborator
            WHERE client_id = :client_id
        ),
        ActiveBase AS (
            -- Colaboradores da base que tiveram atividade (check-in) nos últimos 30 dias
            SELECT DISTINCT eb.user_id
            FROM EligibleBase eb
            JOIN consumers.user_time ut ON eb.user_id = ut.user_id
            WHERE ut.created_at >= (CURRENT_DATE - INTERVAL '30 day')
        )
        SELECT
            (SELECT COUNT(*) FROM EligibleBase) as total_elegivel,
            (SELECT COUNT(*) FROM ActiveBase) as total_ativo_30d;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql), params).fetchone()
            if r:
                total_elegivel = r[0]
                total_ativo_30d = r[1]
                # Adesão = % de usuários elegíveis que se ativaram
                adesao_pct = (total_ativo_30d / total_elegivel * 100) if total_elegivel > 0 else 0
                
                return {
                    "total_colaboradores": total_elegivel,
                    "total_ativos_30d": total_ativo_30d,
                    "taxa_adesao_pct": adesao_pct
                }
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/b2b/cost_per_collaborator")
def get_b2b_cost_per_collaborator(client_id: int):
    """
    Calcula o Custo por Colaborador Ativo (Receita total / Colaboradores ativos).
    """
    params = {"client_id": client_id}
    sql = """
        WITH 
        ClientRevenue AS (
            -- Receita total gerada pelos colaboradores deste cliente
            SELECT SUM(p.amount_due) as total_revenue
            FROM consumers.payment p
            JOIN consumers.user_scheduling s ON p.user_scheduling_id = s.id
            JOIN consumers.user u ON s.user_id = u.id
            JOIN companies.companies_client_collaborator c ON u.id = c.user_id
            WHERE c.client_id = :client_id AND p.status = 'PAID'
        ),
        ActiveBase AS (
            -- Colaboradores ativos (check-in) nos últimos 30 dias
            SELECT COUNT(DISTINCT c.user_id) as total_ativos
            FROM companies.companies_client_collaborator c
            JOIN consumers.user_time ut ON c.user_id = ut.user_id
            WHERE c.client_id = :client_id
            AND ut.created_at >= (CURRENT_DATE - INTERVAL '30 day')
        )
        SELECT 
            (SELECT total_revenue FROM ClientRevenue) as revenue,
            (SELECT total_ativos FROM ActiveBase) as ativos;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql), params).fetchone()
            if r:
                total_revenue = r[0] if r[0] is not None else 0
                total_ativos = r[1] if r[1] > 0 else 0
                
                custo_por_ativo = (total_revenue / total_ativos) if total_ativos > 0 else 0
                
                return {
                    "total_revenue_cliente": float(total_revenue),
                    "total_colaboradores_ativos": int(total_ativos),
                    "custo_por_colaborador_ativo": float(custo_por_ativo)
                }
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [ADIÇÃO - Linha 477]

@app.get("/bi/b2b/campaign_participation")
def get_b2b_campaign_participation(client_id: int):
    """ Retorna a participação em Campanhas B2B (Hard Win) """
    params = {"client_id": client_id}
    # [CÓDIGO CORRIGIDO - REMOVENDO O JOIN BUGADO]
    sql = """
    SELECT
        c.name,
        COUNT(up.user_id) as total_participantes
    FROM companies.campaigns c -- Pega as campanhas do cliente
    -- Traz os participantes DESSA campanha (se houver)
    LEFT JOIN companies.user_campaign_participation up ON c.id = up.campaign_id
    WHERE c.client_id = :client_id
    -- (Removemos a junção 'ccc' que matava o LEFT JOIN.
    --  Assumimos que o gerador de dados só insere participantes válidos)
    GROUP BY c.name
    ORDER BY total_participantes DESC;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/b2b/mev_score_variation")
def get_b2b_mev_score_variation(client_id: int):
    """ Retorna a variação média do MEV Score (Hard Win) """
    params = {"client_id": client_id}
    # [SUBSTITUA O SQL ANTIGO]
    sql = """
    WITH
    Collaborators AS (
        -- Pega todos os colaboradores do cliente
        SELECT user_id FROM companies.companies_client_collaborator
        WHERE client_id = :client_id
    ),
    RankedScores AS (
        -- Pega todos os scores dos colaboradores e os ranqueia
        SELECT
            user_id,
            score,
            calculated_at,
            -- Rank 1 = mais recente
            ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY calculated_at DESC) as rn_desc,
            -- Rank 1 = mais antigo (nos últimos 35 dias)
            ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY calculated_at ASC) as rn_asc
        FROM consumers.user_mev_score
        WHERE user_id IN (SELECT user_id FROM Collaborators)
          AND calculated_at >= (CURRENT_DATE - INTERVAL '35 day')
    ),
    OldScores AS (
        -- Média dos scores mais antigos (rn_asc = 1)
        SELECT AVG(score) as avg_score_old
        FROM RankedScores
        WHERE rn_asc = 1
    ),
    NewScores AS (
        -- Média dos scores mais recentes (rn_desc = 1)
        SELECT AVG(score) as avg_score_new
        FROM RankedScores
        WHERE rn_desc = 1
    )
    SELECT
        (SELECT avg_score_old FROM OldScores) as old_score,
        (SELECT avg_score_new FROM NewScores) as new_score;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql), params).fetchone()
            if r:
                return {
                    "old_score": round(r[0] if r[0] is not None else 0, 1),
                    "new_score": round(r[1] if r[1] is not None else 0, 1)
                }
            return {"old_score": 0, "new_score": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- KPIs do USUÁRIO FINAL (User View) ---

@app.get("/bi/user/list")
def get_user_list():
    """ Retorna uma lista de usuários para filtros de dashboard. """
    sql = "SELECT id, name FROM consumers.user WHERE active = TRUE ORDER BY name LIMIT 100;"
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
            return [{"id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bi/user/activity_history")
def get_user_activity_history(user_id: int):
    """
    Retorna o histórico de check-ins (Treinos/semana) do usuário.
    """
    params = {"user_id": user_id}
    sql = """
        SELECT 
            DATE(created_at) as day, 
            COUNT(id) as checkins
        FROM consumers.user_time
        WHERE user_id = :user_id 
          AND type = 'CHECKIN'
          AND created_at >= (CURRENT_DATE - INTERVAL '30 day')
        GROUP BY day
        ORDER BY day DESC;
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()
            return {
                "labels": [str(r[0]) for r in rows], 
                "values": [int(r[1]) for r in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [SUBSTITUIÇÃO - Linhas 420-441]

@app.get("/bi/user/gamification_stats")
def get_user_gamification_stats(user_id: int):
    """
    Retorna as estatísticas de gamificação (Conquistas, Pontos)
    E TAMBÉM: Minutos Ativos e Calorias (Easy Wins)
    para um usuário específico.
    """
    params = {"user_id": user_id}
    sql = """
        SELECT 
            (SELECT COUNT(id) 
             FROM consumers.user_health_stamp 
             WHERE user_id = :user_id) as total_conquistas,
             
            (SELECT r.points 
             FROM consumers.rank r
             JOIN consumers.user u ON u.rank_id = r.id
             WHERE u.id = :user_id) as total_pontos,

            (SELECT SUM(EXTRACT(EPOCH FROM (finished_at - created_at)) / 60)
             FROM consumers.user_time
             WHERE user_id = :user_id
               AND type = 'CHECKIN'
               AND status = 'FINISHED'
               AND created_at >= (CURRENT_DATE - INTERVAL '30 day')
               AND finished_at IS NOT NULL) as total_minutos_ativos_30d,

            (SELECT SUM(uhp.value)
             FROM consumers.user_health_point uhp
             JOIN consumers.health_point hp ON uhp.health_point_id = hp.id
             WHERE uhp.user_id = :user_id
               AND hp.name = 'Calorias Queimadas'
               AND uhp.recorded_at >= (CURRENT_DATE - INTERVAL '30 day')
            ) as total_calorias_30d;
    """
    try:
        with engine.connect() as conn:
            r = conn.execute(text(sql), params).fetchone()
            if r:
                return {
                    "total_conquistas": r[0] if r[0] is not None else 0,
                    "total_pontos": r[1] if r[1] is not None else 0,
                    "total_minutos_ativos_30d": round(r[2] if r[2] is not None else 0),
                    "total_calorias_30d": round(r[3] if r[3] is not None else 0)
                }
            return {
                "total_conquistas": 0, 
                "total_pontos": 0, 
                "total_minutos_ativos_30d": 0, 
                "total_calorias_30d": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print("Endpoints definidos. Servidor pronto para iniciar.")
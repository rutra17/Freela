# [SUBSTITUA TODO O ARQUIVO generate_fake_data.py]

import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# --- 1. Configuração do Banco de Dados ---
load_dotenv() 
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise SystemExit("ERROR: DATABASE_URL is not set. Coloque no .env ou exporte.")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    raise SystemExit

fake = Faker("pt_BR")
print("Conectado ao banco de dados. Iniciando a população...")

# --- 2. Funções de População (em ordem de dependência) ---

#
# [COPIE E SUBSTITUA A FUNÇÃO 'populate_users' INTEIRA]
# (Desde a linha 'def' até o 'return')
#
# [SUBSTITUA A FUNÇÃO 'populate_users' INTEIRA]

def populate_users(n=100, rank_ids_list=None): # <-- MUDANÇA 1: parâmetro
    if not rank_ids_list:
        print("Erro: Lista de IDs de Rank está vazia. Abortando populate_users.")
        return [], []
        
    print(f"Populando {n} registros em consumers.user (COM ZIP_CODE, RANK e INATIVOS)...")
    ids = []
    
    for _ in range(n):
        email = fake.email() 
        try:
            cursor.execute("""
                INSERT INTO consumers.user (name, email, password, created_at, active, zip_code, rank_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, (
                fake.name(),
                email,
                'hash_de_senha_segura', 
                fake.date_time_between(start_date='-2y', end_date='now'),
                True,
                fake.postcode(),
                random.choice(rank_ids_list) # <-- MUDANÇA 2: Escolhe um rank aleatório
            ))
            
            new_id = cursor.fetchone()
            if new_id:
                ids.append(new_id[0])
                if len(ids) == 1: 
                    # Apenas para debug, mostra o primeiro rank atribuído
                    print(f"-> [DIAGNÓSTICO RANK] Primeiro usuário (ID {new_id[0]}) criado.")
                    
        except Exception as e:
            print(f"Erro ao inserir usuário: {e}")
            conn.rollback()
    
    conn.commit()
    
    # O resto da função (marcar inativos) continua igual...
    num_inactive = int(len(ids) * 0.4)
    if num_inactive > 0 and len(ids) >= num_inactive:
        inactive_ids = random.sample(ids, k=num_inactive)
        
        if inactive_ids:
            inactive_tuple = tuple(inactive_ids)
            if len(inactive_tuple) == 1:
                cursor.execute(
                    f"UPDATE consumers.user SET active = FALSE WHERE id = {inactive_tuple[0]}"
                )
            else:
                 cursor.execute(
                    f"UPDATE consumers.user SET active = FALSE WHERE id IN {inactive_tuple}"
                )
            conn.commit()
            print(f"-> {len(inactive_ids)} usuários marcados como inativos.")

        active_user_ids = list(set(ids) - set(inactive_ids))
        print(f"-> {len(ids)} usuários criados no total ({len(active_user_ids)} ativos, {len(inactive_ids)} inativos).")
        return ids, active_user_ids
    
    print(f"-> {len(ids)} usuários criados no total (todos ativos).")
    return ids, ids

def populate_partners_and_schedules(n=10):
    print(f"Populando {n} parceiros (providers.partner) e seus horários...")
    partner_ids = []
    schedule_ids = []

    for _ in range(n):
        try:
            # 1. Criar o Parceiro
            cursor.execute("""
                INSERT INTO providers.partner (name, email, registry_code, active, verified)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id;
            """, (
                fake.company(),
                fake.unique.email(),
                fake.numerify('##############'), # Gera 14 dígitos numéricos
                True,
                True
            ))
            partner_result = cursor.fetchone()
            if not partner_result:
                conn.rollback()
                continue
            
            partner_id = partner_result[0]
            partner_ids.append(partner_id)

            # 2. Criar uma Atividade para o Parceiro
            cursor.execute("""
                INSERT INTO providers.partner_activity (name, partner_id, active)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, ("Aula de Teste", partner_id, True))
            activity_id = cursor.fetchone()[0]

            # [SUBSTITUIÇÃO - Linhas 95-108]

            # 3. Criar MÚLTIPLOS Horários (Schedule) para a Atividade (FIX P/ GRÁFICO DE HORA)
            for _ in range(random.randint(3, 6)): # Cria de 3 a 6 horários por parceiro
                cursor.execute("""
                    INSERT INTO providers.partner_schedule (partner_id, partner_activity_id, active, recurrent, value, hour)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
                    partner_id,
                    activity_id,
                    True,
                    True,
                    random.uniform(20.0, 50.0),
                    random.randint(8, 20) # Hora aleatória
                ))
                schedule_ids.append(cursor.fetchone()[0])
            
        except Exception as e:
            print(f"Erro ao criar parceiro/horário: {e}")
            conn.rollback()
        else:
            conn.commit()
            
    print(f"-> {len(partner_ids)} parceiros e {len(schedule_ids)} horários criados.")
    return partner_ids, schedule_ids

# [SUBSTITUA APENAS A FUNÇÃO populate_facts NO SEU generate_fake_data.py]

# [SUBSTITUA APENAS A FUNÇÃO populate_facts NO SEU generate_fake_data.py]

# [SUBSTITUA A FUNÇÃO 'populate_facts' INTEIRA (começa linha 166)]

def populate_facts(n=500, user_ids=[], schedule_ids=[], master_data={}):
    print(f"Populando {n} fatos (reservas, pagamentos, check-ins, NPS, calorias)...")
    if not user_ids or not schedule_ids:
        print("Faltando IDs de usuários ou horários. Pulando fatos.")
        return

    # Pega o ID de "Calorias Queimadas" que pré-populamos (Easy Win)
    calories_id = master_data.get("calories_id")

    # Precisamos saber qual parceiro é dono de qual schedule
    # Criar um mapa: {schedule_id: partner_id}
    try:
        # CORREÇÃO: Força a query a pegar APENAS horários que tenham a hora preenchida
        cursor.execute("SELECT id, partner_id FROM providers.partner_schedule WHERE hour IS NOT NULL")
        schedule_to_partner_map = {row[0]: row[1] for row in cursor.fetchall()}
        if not schedule_to_partner_map:
            print("ERRO: Nenhum schedule encontrado no mapa. Verifique se 'populate_partners_and_schedules' rodou.")
            return
    except Exception as e:
        print(f"ERRO ao criar mapa schedule->partner: {e}")
        return

    reservations_created = 0
    payments_created = 0
    checkins_created = 0
    nps_created = 0
    calories_created = 0
    stamps_created = 0 # <-- MUDANÇA 1: Adicionado o contador de Stamps

    for _ in range(n):
        try:
            # --- 1. Criar Reserva (consumers.user_scheduling) ---
            user_id = random.choice(user_ids)
            schedule_id = random.choice(list(schedule_to_partner_map.keys()))
            
            data_agendamento = fake.date_time_between(start_date="-90d", end_date="now")
            
            cursor.execute("""
                INSERT INTO consumers.user_scheduling
                (user_id, partner_schedule_id, scheduled_at, status, active, hour, minute, full_time, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, scheduled_at, hour, minute) DO NOTHING
                RETURNING id, created_at;
            """, (
                user_id, schedule_id, data_agendamento.date(), random.choice(['CONFIRMED', 'CONFIRMED', 'CONFIRMED', 'CANCELED', 'NO-SHOW']), True,
                data_agendamento.strftime("%H"), data_agendamento.strftime("%M"),
                data_agendamento.strftime("%H:%M"), data_agendamento
            ))
            schedule_result = cursor.fetchone()
            
            if not schedule_result:
                conn.rollback() 
                continue
            
            reservation_id, reservation_created_at = schedule_result
            reservations_created += 1
            
            # --- 2. Criar Pagamento (COM REPASSES - Easy Win) ---
            if random.random() < 0.7:
                # Lógica de Repasse
                amount_due = round(random.uniform(20.0, 50.0), 2)
                value_obtained = round(amount_due * 0.8, 2) # Plataforma fica com 80%
                transferred_value = round(amount_due - value_obtained, 2) # Parceiro recebe 20%
                
                cursor.execute("""
                    INSERT INTO consumers.payment
                    (user_scheduling_id, status, amount_due, payment_type, active, created_at, 
                     value_obtained, transferred_value) -- NOVAS COLUNAS
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) -- NOVOS VALORES
                """, (
                    reservation_id, 'PAID', amount_due, 'CREDIT_CARD', True, reservation_created_at,
                    value_obtained, transferred_value # NOVOS VALORES
                ))
                payments_created += 1

            # --- 3. Criar Check-in (COM MINUTOS ATIVOS - Easy Win) ---
            if random.random() < 0.5:
                partner_id_real = schedule_to_partner_map.get(schedule_id)
                
                if partner_id_real:
                    # Lógica de Minutos Ativos
                    checkin_start = reservation_created_at + timedelta(minutes=random.randint(-5, 5))
                    checkin_end = checkin_start + timedelta(minutes=random.randint(30, 90)) # Duração do treino
                    
                    cursor.execute("""
                        INSERT INTO consumers.user_time
                        (user_id, partner_id, type, status, active, created_at, finished_at) -- NOVA COLUNA
                        VALUES (%s, %s, %s, %s, %s, %s, %s) -- NOVO VALOR
                    """, (
                        user_id, partner_id_real, 'CHECKIN', 'FINISHED', True,
                        checkin_start, checkin_end # NOVO VALOR
                    ))
                    checkins_created += 1
                    
                    # --- 4. Criar NPS (Easy Win) ---
                    if random.random() < 0.3: # 30% de chance de deixar feedback
                        cursor.execute("""
                            INSERT INTO consumers.user_health_feedback
                            (user_id, rating, feedback_type, related_entity_id, submitted_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            user_id, 
                            random.randint(0, 10), # Nota NPS
                            'NPS_PARTNER', 
                            partner_id_real, # Linka com o parceiro
                            checkin_end + timedelta(minutes=random.randint(5, 60))
                        ))
                        nps_created += 1
                        
                    # --- 5. Criar CALORIAS (Easy Win) ---
                    if calories_id: # Só insere se o ID mestre de 'Calorias' foi encontrado
                        cursor.execute("""
                            INSERT INTO consumers.user_health_point
                            (user_id, health_point_id, value, recorded_at)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            user_id,
                            calories_id,
                            random.randint(150, 500), # Calorias queimadas
                            checkin_end
                        ))
                        calories_created += 1

                    # --- 6. Criar STAMP (Conquista) ---
                    # [MUDANÇA 2: Adicionado o bloco de STAMPS]
                    if random.random() < 0.1: # 10% de chance de ganhar um stamp
                        cursor.execute("""
                            INSERT INTO consumers.user_health_stamp
                            (user_id, stamp_id, achieved_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (user_id, stamp_id) DO NOTHING
                        """, (
                            user_id,
                            random.randint(1, 5), # ID do stamp (1 a 5)
                            checkin_end + timedelta(minutes=1)
                        ))
                        stamps_created += 1
                    # [FIM DA MUDANÇA 2]

        except Exception as e:
            print(f"Erro ao inserir fato (desfazendo): {e}")
            conn.rollback()
        else:
            conn.commit()
            
    print(f"-> Fatos criados: {reservations_created} reservas, {payments_created} pagamentos, {checkins_created} check-ins.")
    # [MUDANÇA 3: Adicionado 'stamps_created' ao print]
    print(f"-> Easy Wins: {nps_created} feedbacks (NPS), {calories_created} registros (Calorias), {stamps_created} conquistas (Stamps).")

# [FIM DA SUBSTITUIÇÃO]

def populate_plans():
    """Cria os planos B2B (ex: Básico, Pro)"""
    print("Populando 3 planos em companies.companies_plan...")
    plan_ids = []
    plans = [
        ("Essencial", "Plano básico para pequenas empresas", 99.90),
        ("Profissional", "Plano intermediário com suporte completo", 249.90),
        ("Enterprise", "Plano corporativo personalizado", 499.90)
    ]
    try:
        for name, desc, price in plans:
            cursor.execute("""
                INSERT INTO companies.companies_plan (name, description, price, active)
                VALUES (%s, %s, %s, %s)
                -- ON CONFLICT removido para ser compatível com o SQL
                RETURNING id;
            """, (name, desc, price, True))
            plan_id = cursor.fetchone()[0]
            plan_ids.append(plan_id)
        conn.commit()
    except Exception as e:
        print(f"Erro ao popular planos: {e}")
        conn.rollback()
    print(f"-> {len(plan_ids)} planos criados.")
    return plan_ids

def populate_b2b_clients(n=10, plan_ids=[]):
    """Cria os clientes B2B (empresas)"""
    if not plan_ids:
        print("Sem plan_ids, pulando criação de clientes B2B.")
        return []
    
    print(f"Populando {n} clientes B2B em companies.companies_client...")
    client_ids = []
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO companies.companies_client (plan_id, name, cnpj, active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cnpj) DO NOTHING
                RETURNING id;
            """, (
                random.choice(plan_ids),
                fake.company(),
                fake.unique.cnpj(),
                True
            ))
            result = cursor.fetchone()
            if result:
                client_ids.append(result[0])
            conn.commit()
        except Exception as e:
            # O psycopg2 pode gerar um erro se o CNPJ único já existir
            conn.rollback() 
    print(f"-> {len(client_ids)} clientes B2B criados.")
    return client_ids

#
# [COPIE E SUBSTITUA A FUNÇÃO 'populate_b2b_collaborators' INTEIRA]
#
def populate_b2b_collaborators(client_ids, user_ids):
    """
    [VERSÃO REESCRITA - 11/NOV]
    Liga os usuários (colaboradores) aos clientes (empresas).
    Esta versão remove o 'ON CONFLICT' para ser compatível com o banco.
    """
    print(f"Populando {len(user_ids)} colaboradores B2B...")
    
    # Mapeia usuários para clientes (Round-Robin)
    count = 0
    num_clients = len(client_ids)
    
    if num_clients == 0:
        print("-> [ERRO] Nenhum client_id encontrado para ligar colaboradores. Abortando.")
        return

    try:
        for i, user_id in enumerate(user_ids):
            client_id_to_assign = client_ids[i % num_clients] # Round-Robin
            
            # --- A CORREÇÃO CRÍTICA ---
            # O 'ON CONFLICT' FOI REMOVIDO DAQUI
            cursor.execute("""
                INSERT INTO companies.companies_client_collaborator (client_id, user_id, role)
                VALUES (%s, %s, %s);
            """, (
                client_id_to_assign,
                user_id,
                random.choice(["Analista", "Operacional", "Gestor"])
            ))
            count += 1
        
        # Faz o commit de todos os 100 colaboradores de uma vez
        conn.commit() 
        print(f"-> {count} colaboradores B2B ligados aos clientes.")
        
    except Exception as e:
        print(f"-> [ERRO CRÍTICO EM populate_b2b_collaborators]: {e}")
        conn.rollback()
#
# [FIM DO BLOCO DE SUBSTITUIÇÃO]
#
    print(f"-> {count} colaboradores B2B ligados (distribuição garantida).")

# [SUBSTITUA A FUNÇÃO 'populate_master_data' INTEIRA]

# [SUBSTITUA A FUNÇÃO 'populate_master_data' INTEIRA]

def populate_master_data():
    """Popula tabelas mestras (health_point e rank) com dados fixos."""
    print("Populando dados mestres (health_point, rank)...")
    master_ids = {} # Dicionário para guardar os IDs
    rank_ids = [] # Lista para guardar os IDs dos Ranks

    try:
        # --- 1. Garantir 'Calorias' ---
        cursor.execute("""
            INSERT INTO consumers.health_point (name, unit)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id;
        """, ("Calorias Queimadas", "kcal"))
        
        result_cal = cursor.fetchone()
        if result_cal:
            print(f"-> 'Calorias Queimadas' (ID: {result_cal[0]}) garantido.")
            master_ids['calories_id'] = result_cal[0]
        else:
            cursor.execute("SELECT id FROM consumers.health_point WHERE name = %s", ("Calorias Queimadas",))
            result_cal = cursor.fetchone()
            if result_cal:
                 print(f"-> 'Calorias Queimadas' (ID: {result_cal[0]}) já existia.")
                 master_ids['calories_id'] = result_cal[0]

        # --- 2. Garantir 'Ranks' (A CORREÇÃO) ---
        ranks = [
            ("Iniciante", 0),
            ("Bronze", 500),
            ("Prata", 1500),
            ("Ouro", 3000)
        ]
        
        for name, points in ranks:
            cursor.execute("""
                INSERT INTO consumers.rank (name, points)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id;
            """, (name, points))
            
            result_rank = cursor.fetchone()
            rank_id = None
            if result_rank:
                rank_id = result_rank[0]
                print(f"-> Rank '{name}' (ID: {rank_id}) garantido.")
            else:
                cursor.execute("SELECT id FROM consumers.rank WHERE name = %s", (name,))
                result_rank = cursor.fetchone()
                if result_rank:
                    rank_id = result_rank[0]
                    print(f"-> Rank '{name}' (ID: {rank_id}) já existia.")
            
            if rank_id:
                rank_ids.append(rank_id)

        # Adiciona a lista de IDs de rank ao dicionário mestre
        master_ids['rank_ids'] = rank_ids
        conn.commit()
        
        if 'calories_id' not in master_ids:
             print("ERRO CRÍTICO: Não foi possível obter o calories_id.")
             return {} # Falha
        if not rank_ids:
            print("ERRO CRÍTICO: Não foi possível obter os rank_ids.")
            return {} # Falha

        print(f"-> Dados mestres carregados: {master_ids}")
        return master_ids

    except Exception as e:
        print(f"Erro ao popular dados mestres: {e}")
        conn.rollback()
    
    return {}

def populate_web_events_and_costs(user_ids=[]):
    """Popula o funil de conversão e os custos de marketing."""
    print("Populando 'Hard Wins' (Funil e CAC)...")
    
    # --- 1. Funil de Conversão ---
    # Vamos criar 500 sessões anônimas
    funnel_count = 0
    for _ in range(500):
        try:
            session_id = fake.uuid4()
            # 100% visitaram o site
            cursor.execute(
                "INSERT INTO analytics.web_events (session_id, event_name, created_at) VALUES (%s, %s, %s)",
                (session_id, 'visitou_site', fake.date_time_between(start_date="-30d", end_date="now"))
            )
            
            # 60% iniciaram o cadastro
            if random.random() < 0.6:
                cursor.execute(
                    "INSERT INTO analytics.web_events (session_id, event_name, created_at) VALUES (%s, %s, %s)",
                    (session_id, 'iniciou_cadastro', fake.date_time_between(start_date="-30d", end_date="now"))
                )
                
            funnel_count += 1
        except Exception as e:
            conn.rollback()
        else:
            conn.commit()
            
    # Vincula 30% dos usuários cadastrados a uma sessão de funil
    for user_id in random.sample(user_ids, k=int(len(user_ids) * 0.3)):
        try:
            cursor.execute(
                "INSERT INTO analytics.web_events (session_id, event_name, user_id, created_at) VALUES (%s, %s, %s, %s)",
                (fake.uuid4(), 'completou_cadastro', user_id, fake.date_time_between(start_date="-30d", end_date="now"))
            )
            conn.commit()
        except Exception:
            conn.rollback()

    print(f"-> {funnel_count} eventos de funil criados.")

    # --- 2. Custos de Marketing (CAC) ---
    cost_count = 0
    for i in range(30): # 30 dias de custos
        try:
            cost_date = datetime.now().date() - timedelta(days=i)
            cursor.execute(
                "INSERT INTO analytics.marketing_costs (source, cost, clicks, date) VALUES (%s, %s, %s, %s) ON CONFLICT (date) DO NOTHING",
                ('Google Ads', random.uniform(50.0, 200.0), random.randint(100, 500), cost_date)
            )
            cursor.execute(
                "INSERT INTO analytics.marketing_costs (source, cost, clicks, date) VALUES (%s, %s, %s, %s) ON CONFLICT (date) DO NOTHING",
                ('Facebook Ads', random.uniform(40.0, 150.0), random.randint(150, 600), cost_date)
            )
            cost_count += 2
            conn.commit()
        except Exception:
            conn.rollback()
            
    print(f"-> {cost_count} registros de Custo de Aquisição (CAC) criados.")

#
# [COLE ESTE CÓDIGO INTEIRO NO LUGAR DA FUNÇÃO 'populate_missions_and_campaigns' ANTIGA]
#
def populate_missions_and_campaigns(user_ids=[], active_user_ids=[], client_ids=[]):
    """
    [VERSÃO REESCRITA DO ZERO - 11/NOV]
    Popula missões (Gamificação) e campanhas (B2B).
    Esta versão é standalone e busca seus próprios dados para garantir a execução.
    """
    print("\n--- INICIANDO populate_missions_and_campaigns (VERSÃO REESCRITA) ---")
    
    # --- PARTE 1: MISSÕES (Gamificação) ---
    mission_ids = []
    try:
        print("-> [ETAPA 1/5] Criando missões mestras...")
        cursor.execute("INSERT INTO consumers.missions (name, points_reward) VALUES ('Primeiro Check-in', 50) RETURNING id")
        res_m1 = cursor.fetchone()
        if res_m1: mission_ids.append(res_m1[0])
        
        cursor.execute("INSERT INTO consumers.missions (name, points_reward) VALUES ('Treino de Fim de Semana', 100) RETURNING id")
        res_m2 = cursor.fetchone()
        if res_m2: mission_ids.append(res_m2[0])
        
        conn.commit()
        print("-> [ETAPA 1/5] Missões mestras criadas ou já existentes.")

        # Atribuir missões a 50% dos usuários
        if mission_ids: # Só continua se houver missões para atribuir
            print("-> [ETAPA 2/5] Atribuindo missões a usuários...")
            # Usa a lista user_ids (que sabemos que funciona)
            users_to_assign = random.sample(user_ids, k=int(len(user_ids) * 0.5))
            count_m = 0
            for user_id in users_to_assign:
                try:
                    cursor.execute("INSERT INTO consumers.user_missions (user_id, mission_id) VALUES (%s, %s) ON CONFLICT (user_id, mission_id) DO NOTHING", 
                                   (user_id, random.choice(mission_ids)))
                    count_m += 1
                except Exception:
                    conn.rollback() # Erro em um, rola pra trás só ele
            conn.commit() # Commita todos de uma vez
            print(f"-> [ETAPA 2/5] {count_m} missões atribuídas.")
        else:
            print("-> [ETAPA 2/5] Nenhuma missão mestre encontrada ou criada para atribuir.")

    except Exception as e: 
        print(f"-> [ERRO ETAPA 1/2] Erro ao popular missões: {e}")
        conn.rollback()
        
    # --- PARTE 2: CAMPANHAS B2B (O Ponto Crítico) ---
    try:
        # ETAPA 3: Buscar colaboradores B2B *DIRETO DO BANCO*
        # Esta é a nova abordagem. Ignora os parâmetros.
        print("-> [ETAPA 3/5] Buscando colaboradores B2B (ativos) direto do banco...")
        
        # Pega o ID de TODOS os usuários que estão na tabela de colaboração E estão ativos (active=true)
        sql_get_collaborators = """
            SELECT ccc.user_id, ccc.client_id
            FROM companies.companies_client_collaborator ccc
            JOIN consumers.user u ON ccc.user_id = u.id
            WHERE u.active = TRUE; 
        """
        cursor.execute(sql_get_collaborators)
        all_active_collaborators = cursor.fetchall() # Lista de tuplas (user_id, client_id)
        
        if not all_active_collaborators:
            print("-> [ERRO CRÍTICO ETAPA 3/5] Nenhum colaborador B2B (ativo) encontrado no banco.")
            print("-> Causa provável: 'populate_b2b_collaborators' falhou ou todos os colaboradores estão inativos.")
            print("--- ABORTANDO populate_missions_and_campaigns ---")
            return # ABORTA A FUNÇÃO
        
        print(f"-> [DIAGNÓSTICO ETAPA 3/5] SUCESSO! Encontrados {len(all_active_collaborators)} colaboradores B2B ativos.")

        # ETAPA 4: Criar Campanhas B2B Mestras (uma para cada cliente)
        print("-> [ETAPA 4/5] Criando campanhas B2B mestras...")
        
        # Pega a lista de IDs de clientes *distintos* dos colaboradores que encontramos
        client_ids_from_collaborators = list(set([row[1] for row in all_active_collaborators]))
        
        campaign_map = {} # Dicionário {client_id: campaign_id}
        count_c = 0
        for client_id in client_ids_from_collaborators:
            # ON CONFLICT garante que não vai duplicar
            cursor.execute("INSERT INTO companies.campaigns (client_id, name) VALUES (%s, %s) RETURNING id", 
                           (client_id, 'Campanha de Saúde Trimestral'))
            res_c = cursor.fetchone()
            if res_c:
                campaign_map[client_id] = res_c[0]
                count_c += 1
        
        conn.commit()
        print(f"-> [ETAPA 4/5] {count_c} campanhas B2B criadas.")

        # ETAPA 5: Atribuir campanhas aos colaboradores
        print("-> [ETAPA 5/5] Atribuindo campanhas aos colaboradores...")
        count_p = 0
        for user_id, client_id in all_active_collaborators:
            if random.random() < 0.7: # 70% de chance
                campaign_id_to_join = campaign_map.get(client_id)
                if campaign_id_to_join:
                    cursor.execute(
                        """
                        INSERT INTO companies.user_campaign_participation (user_id, campaign_id) 
                        VALUES (%s, %s) 
                        ON CONFLICT (user_id, campaign_id) DO NOTHING
                        """, 
                        (user_id, campaign_id_to_join)
                    )
                    count_p += 1
        
        conn.commit()
        print(f"-> [ETAPA 5/5] SUCESSO! {count_p} participações em campanhas B2B registradas.")

    except Exception as e: 
        print(f"-> [ERRO ETAPA 3/4/5] Erro ao popular campanhas B2B: {e}")
        conn.rollback()
        
    print("--- FINALIZANDO populate_missions_and_campaigns (VERSÃO REESCRITA) ---")
#
# [FIM DO BLOCO DE CÓDIGO PARA COPIAR]
#

def populate_mev_scores(user_ids=[]):
    """Popula scores de risco (MEV Score) para os usuários."""
    print("Populando 'Hard Wins' (MEV Scores)...")
    count = 0
    for user_id in user_ids:
        try:
            # Um score para 30 dias atrás
            score_30d = random.randint(20, 80)
            cursor.execute(
                "INSERT INTO consumers.user_mev_score (user_id, score, risk_level, calculated_at) VALUES (%s, %s, %s, %s)",
                (user_id, score_30d, 'Médio', datetime.now().date() - timedelta(days=30))
            )
            # Um score para hoje
            score_hoje = score_30d + random.randint(-10, 10)
            cursor.execute(
                "INSERT INTO consumers.user_mev_score (user_id, score, risk_level, calculated_at) VALUES (%s, %s, %s, %s)",
                (user_id, score_hoje, 'Baixo' if score_hoje < 50 else 'Médio', datetime.now().date())
            )
            count += 2
            conn.commit()
        except Exception:
            conn.rollback()
    print(f"-> {count} registros de MEV Score criados.")

# [SUBSTITUIÇÃO - Bloco 'try...finally' no final do arquivo]
# --- 3. Execução em ordem lógica ---
try:
    # 0. Popula dados mestres (Easy Wins)
    master_data = populate_master_data()
    
    # 1. Criar usuários (retorna DUAS listas)
    all_user_ids, active_user_ids = populate_users(100, rank_ids_list=master_data['rank_ids'])
    partner_ids, schedule_ids = populate_partners_and_schedules(20)
    
    # 2. Criar o mundo B2B (usa TODOS os usuários)
    plan_ids = populate_plans()
    client_ids = populate_b2b_clients(30, plan_ids)
    populate_b2b_collaborators(client_ids, all_user_ids)
    
    # 3. Gerar fatos (usa APENAS usuários ATIVOS)
    populate_facts(2000, active_user_ids, schedule_ids, master_data)
    
    # 4. Popula "Hard Wins" (usa TODAS as listas)
    populate_web_events_and_costs(all_user_ids)
    # [LINHA 577 - A CORREÇÃO]
    populate_missions_and_campaigns(user_ids=all_user_ids, active_user_ids=active_user_ids, client_ids=client_ids)
    populate_mev_scores(all_user_ids)
    
except Exception as e:
    print(f"Um erro crítico ocorreu durante a população: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("\nBanco populado com sucesso (COM DADOS VARIADOS) e conexão fechada!")
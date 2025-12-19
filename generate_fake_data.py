import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

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

def populate_users(n=100, rank_ids_list=None): 
    if not rank_ids_list:
        print("Erro: Lista de IDs de Rank está vazia. Abortando populate_users.")
        return [], []
        
    print(f"Populando {n} registros em consumers.user (COM IDENTIDADE COERENTE)...")
    ids = []
    
    # MAPA LÓGICO DE SETORES E PROFISSÕES
    job_map = {
        'Tecnologia': ['Desenvolvedor Full Stack', 'DevOps Engineer', 'Analista de Dados', 'Tech Lead', 'QA Tester', 'Product Owner'],
        'Saúde': ['Enfermeiro(a)', 'Médico(a) Plantonista', 'Fisioterapeuta', 'Nutricionista', 'Técnico em Radiologia', 'Farmacêutico'],
        'Educação': ['Professor de Matemática', 'Coordenador Pedagógico', 'Bibliotecário', 'Pesquisador', 'Assistente Docente'],
        'Varejo': ['Gerente de Loja', 'Vendedor Sênior', 'Supervisor de Estoque', 'Caixa', 'Representante Comercial'],
        'Finanças': ['Analista Financeiro', 'Contador', 'Auditor Fiscal', 'Trader', 'Gerente de Contas'],
        'Engenharia': ['Engenheiro Civil', 'Engenheiro Eletricista', 'Arquiteto', 'Mestre de Obras', 'Projetista CAD'],
        'Serviços': ['Consultor de RH', 'Assistente Administrativo', 'Recepcionista', 'Motorista', 'Segurança']
    }
    tipos_usuario = ['FREE', 'PREMIUM', 'B2B_CORPORATE', 'B2B_GOLD'] 

    # --- [ADICIONAR ISSO AQUI] ---
    # CEPs fixos para criar aglomeração nos gráficos de região (Recife, SP, RJ, DF, BH)
    strategic_zips = [
        "50000-000", "01310-100", "22041-001", "70040-010", "30140-071"
    ]
    # -----------------------------
    
    # Função auxiliar para remover acentos do email
    import unicodedata
    def slugify(text):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return text.lower().replace(' ', '.')

    for i in range(n):
        # 1. IDENTIDADE COERENTE
        genero = random.choice(['M', 'F'])
        
        if genero == 'M':
            nome_real = fake.first_name_male() + " " + fake.last_name()
        else:
            nome_real = fake.first_name_female() + " " + fake.last_name()
            
        # Email baseado no nome
        email = f"{slugify(nome_real)}@{fake.free_email_domain()}"

        # --- [ADICIONAR ISSO AQUI] ---
        # Lógica BI: 70% de chance de cair num CEP estratégico para o gráfico ficar denso
        if random.random() < 0.7:
            zip_code_bi = random.choice(strategic_zips)
        else:
            zip_code_bi = fake.postcode()
        # -----------------------------

        # Resto dos dados
        peso = round(random.uniform(50.0, 110.0), 2)
        altura = round(random.uniform(1.50, 1.95), 2)
        nascimento = fake.date_of_birth(minimum_age=18, maximum_age=65)
        
        setor = random.choice(list(job_map.keys()))
        profissao = random.choice(job_map[setor])
        
        is_diabetic = random.choice([True, False, False, False])
        is_hypertensive = random.choice([True, False, False, False])

        registry_code = fake.unique.cpf()
        phone = fake.phone_number()
        address = fake.street_name()
        address_number = str(fake.building_number())
        fcm_token = fake.sha256()
        external_id = fake.uuid4()
        health_level = random.randint(1, 100)
        user_type = random.choice(tipos_usuario)

        try:
            cursor.execute("""
                INSERT INTO consumers.user (
                    name, email, password, created_at, active, zip_code, rank_id,
                    occupation, sector, weight, height, diabetic, hypertensive, birth_date, gender,
                    registry_code, phone, address, address_number, fcm_token, external_id, health_level, user_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, (
                nome_real, # Nome corrigido
                email,     # Email corrigido
                'hash_de_senha_segura', 
                fake.date_time_between(start_date='-2y', end_date='now'),
                True,
                zip_code_bi,
                random.choice(rank_ids_list),
                profissao,
                setor,
                peso,
                altura,
                is_diabetic,
                is_hypertensive,
                nascimento,
                genero,    # Gênero corrigido
                registry_code,
                phone,
                address,
                address_number,
                fcm_token,
                external_id,
                health_level,
                user_type
            ))
            
            new_id = cursor.fetchone()
            if new_id:
                ids.append(new_id[0])

                # --- PRINT DE DIAGNÓSTICO ATUALIZADO ---
                if len(ids) == 1: 
                    print(f"-> [DIAGNÓSTICO FINAL] Usuário 1: Tipo '{user_type}', Saúde Lvl {health_level}, CPF {registry_code}")
                if len(ids) == 50:
                    print(f"-> [DIAGNÓSTICO FINAL] Usuário 50: Tipo '{user_type}', Saúde Lvl {health_level}, Tel {phone}")
                
        except Exception as e:
            print(f"Erro ao inserir usuário: {e}")
            conn.rollback()
    
    conn.commit()
    
    # Lógica de Inativos
    num_inactive = int(len(ids) * 0.2) # Reduzi para 20% inativos para ter mais dados nos gráficos
    if num_inactive > 0 and len(ids) >= num_inactive:
        inactive_ids = random.sample(ids, k=num_inactive)
        if inactive_ids:
            inactive_tuple = tuple(inactive_ids)
            if len(inactive_tuple) == 1:
                cursor.execute(f"UPDATE consumers.user SET active = FALSE WHERE id = {inactive_tuple[0]}")
            else:
                 cursor.execute(f"UPDATE consumers.user SET active = FALSE WHERE id IN {inactive_tuple}")
            conn.commit()

        active_user_ids = list(set(ids) - set(inactive_ids))
        print(f"-> {len(ids)} usuários criados ({len(active_user_ids)} ativos). Identidades Corrigidas.")
        return ids, active_user_ids
    
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


def populate_b2b_collaborators(client_ids, user_ids):
    """
    [VERSÃO COM DIVERSIDADE DE TAMANHO]
    Distribui colaboradores de forma DESIGUAL entre as empresas.
    Algumas terão muitos funcionários, outras poucos.
    """
    print(f"Populando colaboradores B2B de forma assimétrica para {len(client_ids)} clientes...")
    
    # Embaralha os usuários para não pegar sempre os mesmos perfis
    available_users = user_ids[:]
    random.shuffle(available_users)
    
    total_users = len(available_users)
    count = 0
    
    # Diagnóstico prévio
    print(f"-> Total de usuários disponíveis: {total_users}")
    
    # Distribuição de pesos aleatórios para cada empresa (tamanho da empresa)
    # Ex: Empresa A tem peso 5 (grande), Empresa B tem peso 1 (pequena)
    client_weights = {cid: random.randint(1, 10) for cid in client_ids}
    total_weight = sum(client_weights.values())
    
    try:
        current_idx = 0
        
        for client_id in client_ids:
            # Calcula quantos usuários essa empresa vai ter baseada no peso
            weight = client_weights[client_id]
            # A fórmula mágica da desigualdade:
            num_employees = int((weight / total_weight) * total_users)
            
            # Garante mínimo de 5 funcionários para não quebrar gráficos
            num_employees = max(5, num_employees)
            
            # Pega a fatia de usuários
            end_idx = min(current_idx + num_employees, total_users)
            company_staff = available_users[current_idx:end_idx]
            current_idx = end_idx
            
            if not company_staff:
                continue

            # Inserção no banco
            insert_buffer = []
            for uid in company_staff:
                insert_buffer.append((client_id, uid, random.choice(["Analista", "Operacional", "Gestor"])))
                
            cursor.executemany("""
                INSERT INTO companies.companies_client_collaborator (client_id, user_id, role)
                VALUES (%s, %s, %s);
            """, insert_buffer)
            
            count += len(insert_buffer)
            
            # --- DIAGNÓSTICO NO TERMINAL ---
            print(f"   -> Cliente ID {client_id}: Recebeu {len(company_staff)} colaboradores.")

        conn.commit()
        print(f"-> {count} colaboradores B2B distribuídos com tamanhos variados.")
        
    except Exception as e:
        print(f"-> [ERRO CRÍTICO EM populate_b2b_collaborators]: {e}")
        conn.rollback()


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
    [VERSÃO CORRIGIDA PARA DASHBOARD PROFISSIONAL]
    Gera múltiplas campanhas por cliente para enriquecer os gráficos.
    """
    print("\n--- INICIANDO populate_missions_and_campaigns (VERSÃO GRÁFICA RICA) ---")
    
    # --- PARTE 1: MISSÕES (Gamificação - Mantida igual) ---
    mission_ids = []
    try:
        print("-> [ETAPA 1/5] Criando missões mestras...")
        # Usa ON CONFLICT para evitar erros se rodar 2 vezes
        cursor.execute("INSERT INTO consumers.missions (name, points_reward) VALUES ('Primeiro Check-in', 50) ON CONFLICT (name) DO NOTHING")
        cursor.execute("SELECT id FROM consumers.missions WHERE name = 'Primeiro Check-in'")
        res_m1 = cursor.fetchone()
        if res_m1: mission_ids.append(res_m1[0])
        
        cursor.execute("INSERT INTO consumers.missions (name, points_reward) VALUES ('Treino de Fim de Semana', 100) ON CONFLICT (name) DO NOTHING")
        cursor.execute("SELECT id FROM consumers.missions WHERE name = 'Treino de Fim de Semana'")
        res_m2 = cursor.fetchone()
        if res_m2: mission_ids.append(res_m2[0])
        
        conn.commit()

        # Atribuir missões a 50% dos usuários
        if mission_ids and user_ids:
            print("-> [ETAPA 2/5] Atribuindo missões a usuários...")
            users_to_assign = random.sample(user_ids, k=int(len(user_ids) * 0.5))
            count_m = 0
            for user_id in users_to_assign:
                try:
                    cursor.execute("INSERT INTO consumers.user_missions (user_id, mission_id) VALUES (%s, %s) ON CONFLICT (user_id, mission_id) DO NOTHING", 
                                   (user_id, random.choice(mission_ids)))
                    count_m += 1
                except Exception:
                    conn.rollback()
            conn.commit()
            print(f"-> [ETAPA 2/5] {count_m} missões atribuídas.")
    except Exception as e: 
        print(f"-> [ERRO ETAPA 1/2] Erro ao popular missões: {e}")
        conn.rollback()
        
    # --- PARTE 2: CAMPANHAS B2B (AQUI ESTÁ A MÁGICA GRÁFICA) ---
    try:
        print("-> [ETAPA 3/5] Buscando colaboradores B2B...")
        
        # Busca colaboradores ativos e seus clientes
        sql_get_collaborators = """
            SELECT ccc.user_id, ccc.client_id
            FROM companies.companies_client_collaborator ccc
            JOIN consumers.user u ON ccc.user_id = u.id
            WHERE u.active = TRUE; 
        """
        cursor.execute(sql_get_collaborators)
        all_active_collaborators = cursor.fetchall() # Lista de (user_id, client_id)
        
        if not all_active_collaborators:
            print("-> [AVISO] Nenhum colaborador B2B encontrado. Populando campanhas vazias apenas para constar.")
            client_ids_from_collaborators = client_ids # Usa a lista passada se não achar no banco
        else:
            client_ids_from_collaborators = list(set([row[1] for row in all_active_collaborators]))
            print(f"-> [DIAGNÓSTICO] Encontrados {len(all_active_collaborators)} colaboradores em {len(client_ids_from_collaborators)} empresas.")

        # MAPA DE COLABORADORES POR EMPRESA (Para agilizar a atribuição)
        # { client_id: [user_id, user_id, ...] }
        company_users_map = {}
        for uid, cid in all_active_collaborators:
            if cid not in company_users_map: company_users_map[cid] = []
            company_users_map[cid].append(uid)

        # ETAPA 4: Criar Múltiplas Campanhas Variadas
        print("-> [ETAPA 4/5] Criando campanhas B2B variadas...")
        
        campanhas_temas = [
            "Outubro Rosa", "Novembro Azul", "Desafio Verão 2025", 
            "Semana da Hidratação", "Mindfulness no Trabalho", 
            "Corrida Virtual", "Jornada do Sono", "Coma Bem"
        ]
        
        campaign_map = [] # Lista de tuplas (campaign_id, client_id, theme_name)
        count_c = 0

        for client_id in client_ids_from_collaborators:
            # MAGIA: Cada empresa escolhe aleatoriamente 2 ou 3 temas diferentes
            num_campaigns = random.randint(2, 3)
            selected_themes = random.sample(campanhas_temas, k=num_campaigns)
            
            for theme in selected_themes:
                try:
                    # Inserção sem ON CONFLICT no nome para permitir que empresas diferentes tenham campanhas com mesmo nome
                    cursor.execute("INSERT INTO companies.campaigns (client_id, name) VALUES (%s, %s) RETURNING id", 
                                   (client_id, theme))
                    res_c = cursor.fetchone()
                    if res_c:
                        campaign_map.append((res_c[0], client_id, theme))
                        count_c += 1
                except Exception:
                    conn.rollback()
        
        conn.commit()
        print(f"-> [ETAPA 4/5] {count_c} campanhas criadas (Média de 2-3 por empresa).")

        # ETAPA 5: Atribuir campanhas aos colaboradores
        print("-> [ETAPA 5/5] Povoando campanhas com adesão variável...")
        
        count_p = 0
        for camp_id, client_id, theme in campaign_map:
            # Pega os usuários desta empresa
            employees = company_users_map.get(client_id, [])
            
            if not employees: continue

            # Define uma "taxa de sucesso" aleatória para ESSA campanha específica
            # Ex: "Outubro Rosa" pode ter 80% de adesão, "Corrida" apenas 20%
            adherence_rate = random.uniform(0.15, 0.90)
            
            # Sorteia quais funcionários participam
            num_participants = int(len(employees) * adherence_rate)
            participantes = random.sample(employees, k=num_participants)
            
            insert_buffer = []
            for user_id in participantes:
                insert_buffer.append((user_id, camp_id))
            
            if insert_buffer:
                try:
                    cursor.executemany(
                        "INSERT INTO companies.user_campaign_participation (user_id, campaign_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        insert_buffer
                    )
                    count_p += len(insert_buffer)
                    conn.commit()
                except Exception as e:
                    print(f"Erro no lote de participação: {e}")
                    conn.rollback()

        print(f"-> [ETAPA 5/5] SUCESSO! {count_p} participações registradas em diversas campanhas.")

    except Exception as e: 
        print(f"-> [ERRO ETAPA 3/4/5] Erro ao popular campanhas B2B: {e}")
        conn.rollback()
        
    print("--- FINALIZANDO populate_missions_and_campaigns (VERSÃO RICA) ---")

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

# --- NOVA FUNÇÃO: Gamificação e Interações (JSONB) ---
def populate_interactions(n_interactions, user_ids, partner_ids, company_ids):
    print(f"\n--- Populando {n_interactions} interações com CULTURA CORPORATIVA ---")
    
    if not user_ids or not partner_ids:
        print("AVISO: Sem usuários ou parceiros.")
        return

    # 1. Mapear quem trabalha onde (Para definir cultura da empresa)
    # Precisamos saber quais usuários pertencem a qual empresa para aplicar a taxa de engajamento dela
    cursor.execute("SELECT client_id, user_id FROM companies.companies_client_collaborator")
    rows = cursor.fetchall()
    
    company_staff_map = {} # {client_id: [user_id, user_id...]}
    user_to_company = {}   # {user_id: client_id}
    
    for cid, uid in rows:
        if cid not in company_staff_map: company_staff_map[cid] = []
        company_staff_map[cid].append(uid)
        user_to_company[uid] = cid

    # 2. Definir o "Fator Fitness" de cada empresa (Diversidade de Engajamento)
    # Algumas empresas terão 90% de adesão, outras 20%
    gym_goers_pool = []
    
    print("-> Definindo Culturas Corporativas (Diagnóstico):")
    
    # Se houver usuários sem empresa (B2C), eles entram com 50% de chance
    users_with_company = set(user_to_company.keys())
    users_b2c = list(set(user_ids) - users_with_company)
    gym_goers_pool.extend(random.sample(users_b2c, k=int(len(users_b2c) * 0.5)))

    # Para usuários B2B, respeitamos a cultura da empresa
    for cid, staff in company_staff_map.items():
        # Fator Fitness: Aleatório entre 20% (0.2) e 95% (0.95)
        fitness_factor = random.uniform(0.20, 0.95) 
        
        qty_active = int(len(staff) * fitness_factor)
        active_users = random.sample(staff, k=qty_active)
        
        gym_goers_pool.extend(active_users)
        
        # PRINT DE DIAGNÓSTICO (O que você pediu para ver se funcionou)
        print(f"   -> Empresa {cid}: {len(staff)} func. | Fator Fitness: {fitness_factor:.2f} | Ativos Reais: {qty_active}")

    # Garante que temos gente suficiente
    if not gym_goers_pool:
        gym_goers_pool = user_ids # Fallback

    print(f"-> Base de 'Gym Goers' definida: {len(gym_goers_pool)} usuários únicos vão gerar treinos.")

    sql = """
        INSERT INTO consumers.user_interaction 
        (user_id, partner_id, company_id, type, status, metadata, interaction_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    interactions_buffer = []
    
    # Modalidades para variar a "Diversidade"
    modalities_list = ['Yoga', 'Pilates', 'Boxe', 'Natação', 'Spinning', 'Crossfit', 'Jiu-Jitsu', 'Dança', 'Beach Tennis']
    
    for _ in range(n_interactions):
        user = random.choice(gym_goers_pool)
        partner = random.choice(partner_ids)
        company = random.choice(company_ids) if company_ids else None
        
        # --- A MUDANÇA MÁGICA NOS PESOS ---
        # Aumentamos muito a chance de MORNING_HABIT (Manhã) e SOCIAL_WORKOUT
        # Antes: weights=[20, 15, 20, 15, 30]
        scenario = random.choices(
            ['MORNING_HABIT', 'SOCIAL_WORKOUT', 'HIGH_RATING', 'DIVERSITY', 'NORMAL'],
            weights=[35, 25, 10, 20, 10] # Foco total em Manhã (35%) e Social (25%)
        )[0]

        # Base da data (últimos 30 dias para encher o gráfico)
        base_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        metadata = {}
        interaction_type = 'check-in'

        # 1. Regra do Hábito (Forçando Manhã)
        if scenario == 'MORNING_HABIT':
            hour = random.randint(6, 9) # Entre 06h e 09h
            base_date = base_date.replace(hour=hour, minute=random.randint(0, 59))
            metadata['workout_type'] = 'Musculação'

        # 2. Regra Social (Amigos)
        elif scenario == 'SOCIAL_WORKOUT':
            friends = random.sample(user_ids, k=random.randint(1, 3)) # 1 a 3 amigos
            metadata['friend_ids'] = friends
            metadata['workout_type'] = 'Futevôlei' 
            base_date = base_date.replace(hour=19)

        # 3. Regra de Qualidade
        elif scenario == 'HIGH_RATING':
            metadata['rating'] = 5
            metadata['comment'] = random.choice(["Top demais!", "Estrutura incrível", "Amei a aula"])
            base_date = base_date.replace(hour=12)

        # 4. Regra de Diversidade (Várias modalidades)
        elif scenario == 'DIVERSITY':
            metadata['workout_type'] = random.choice(modalities_list)
            base_date = base_date.replace(hour=18)

        # 5. Normal (Noite ou tarde)
        else:
            metadata['workout_type'] = 'Esteira'
            base_date = base_date.replace(hour=random.randint(15, 22))

        # --- [INÍCIO DA CORREÇÃO BI - INSERIR AQUI] ---
        # O problema: Só o cenário 'HIGH_RATING' dava nota 5. A média ficava em 10%.
        # A solução: Injetamos notas 5 nos outros cenários, mas variando por Parceiro.
        if 'rating' not in metadata:
            # Usamos o ID do parceiro para definir a "Qualidade Fixa" dele.
            # (partner % 5) gera números de 0 a 4. 
            # Multiplicamos para criar faixas de qualidade: 40%, 55%, 70%, 85%, 100% (teórico)
            
            fator_qualidade = 0.40 + ((partner % 5) * 0.15) 
            
            # Adiciona um pouco de "sorte" aleatória para variar dia a dia
            if random.random() < fator_qualidade:
                metadata['rating'] = 5
        # --- [FIM DA CORREÇÃO BI] ---

        metadata_json = json.dumps(metadata)
        interactions_buffer.append((user, partner, company, interaction_type, 'CONCLUIDO', metadata_json, base_date))

        if len(interactions_buffer) >= 500:
            cursor.executemany(sql, interactions_buffer)
            conn.commit()
            interactions_buffer = []

    if interactions_buffer:
        cursor.executemany(sql, interactions_buffer)
        conn.commit()
    
    print(f"-> {n_interactions} interações criadas com sucesso (Distribuição ajustada).")


def populate_strategic_retention_and_missions(user_ids, partner_ids):
    """
    Função 'Cirúrgica' final - VERSÃO CORRIGIDA (SEM ON CONFLICT): 
    1. Garante Retenção (D1/D7/D30).
    2. Garante Gráfico de Receita por Região (Força pagamentos em CEPs chave).
    3. Garante Gráfico de Missões (Verifica existência antes de inserir).
    """
    print("--- INICIANDO CORREÇÃO CIRÚRGICA DE DADOS (Retenção, Receita e Missões) ---")
    
    today = datetime.now().date()
    
    # --- PARTE 1: RETENÇÃO (D1, D7, D30) ---
    # Essa parte estava certa, mas rodava rollback por causa do erro nas missões.
    cohorts = [
        (today - timedelta(days=1), 15), 
        (today - timedelta(days=7), 12), 
        (today - timedelta(days=30), 20)
    ]
    
    for date_val, qtd in cohorts:
        target_users = random.sample(user_ids, k=min(qtd, len(user_ids)))
        if target_users:
            tuple_users = tuple(target_users)
            ids_str = str(tuple_users) if len(tuple_users) > 1 else f"({tuple_users[0]})"
            
            # Força a data de criação para cair na coorte correta
            cursor.execute(f"UPDATE consumers.user SET created_at = '{date_val} 10:00:00' WHERE id IN {ids_str}")
            
            # Faz 60% deles voltarem hoje (Retenção)
            retained_users = random.sample(target_users, k=int(len(target_users) * 0.6))
            for r_user in retained_users:
                cursor.execute("""
                    INSERT INTO consumers.user_time (user_id, partner_id, type, status, active, created_at, finished_at)
                    VALUES (%s, %s, 'CHECKIN', 'FINISHED', TRUE, NOW(), NOW() + INTERVAL '1 hour')
                """, (r_user, random.choice(partner_ids)))

    # --- PARTE 2: CORREÇÃO DO GRÁFICO "RECEITA POR REGIÃO" ---
    print("-> Injetando pagamentos estratégicos para o gráfico de Região...")
    
    strategic_zips = ["50000-000", "01310-100", "22041-001", "70040-010", "30140-071"]
    vip_users = random.sample(user_ids, k=min(60, len(user_ids))) 
    
    # Pega um ID de schedule qualquer para vincular
    cursor.execute("SELECT id FROM providers.partner_schedule LIMIT 1")
    res_schedule = cursor.fetchone()
    
    if res_schedule:
        schedule_id_base = res_schedule[0]
        
        for i, uid in enumerate(vip_users):
            chosen_zip = strategic_zips[i % len(strategic_zips)]
            # 1. Atualiza CEP
            cursor.execute("UPDATE consumers.user SET zip_code = %s WHERE id = %s", (chosen_zip, uid))
            
            # 2. Cria Agendamento
            cursor.execute("""
                INSERT INTO consumers.user_scheduling (user_id, partner_schedule_id, scheduled_at, status, active) 
                VALUES (%s, %s, NOW(), 'CONFIRMED', TRUE) RETURNING id
            """, (uid, schedule_id_base))
            sched_id = cursor.fetchone()[0]
            
            # 3. Cria Pagamento Alto (R$ 180 a R$ 450)
            val_pagamento = random.uniform(180.0, 450.0) 
            cursor.execute("""
                INSERT INTO consumers.payment 
                (user_scheduling_id, status, amount_due, payment_type, active, created_at, value_obtained, transferred_value)
                VALUES (%s, 'PAID', %s, 'CREDIT_CARD', TRUE, NOW(), %s, %s)
            """, (sched_id, val_pagamento, val_pagamento*0.8, val_pagamento*0.2))

    # --- PARTE 3: CORREÇÃO DO GRÁFICO "MISSÕES" (SEM ON CONFLICT) ---
    print("-> Forçando população de Missões (Modo Seguro)...")
    
    missoes_def = [
        ("Primeiro Treino", 50), ("Semana de Foco", 100), ("Guerreiro da Manhã", 150),
        ("Mestre do Yoga", 200), ("Maratonista", 300)
    ]
    
    mission_db_ids = []
    
    for nome, pts in missoes_def:
        # Tenta buscar primeiro (Evita erro ON CONFLICT se não houver Unique Key)
        cursor.execute("SELECT id FROM consumers.missions WHERE name = %s", (nome,))
        res = cursor.fetchone()
        
        if res:
            mission_db_ids.append(res[0])
        else:
            # Se não existe, insere
            cursor.execute("INSERT INTO consumers.missions (name, points_reward) VALUES (%s, %s) RETURNING id", (nome, pts))
            mid = cursor.fetchone()
            if mid: mission_db_ids.append(mid[0])
            
    # Distribui missões para 70% dos usuários
    if mission_db_ids:
        users_for_missions = random.sample(user_ids, k=int(len(user_ids) * 0.7))
        for uid in users_for_missions:
            missions_to_give = random.sample(mission_db_ids, k=random.randint(1, 2))
            for mid in missions_to_give:
                # Aqui usamos SELECT para evitar duplicidade na tabela de ligação N:N
                cursor.execute("SELECT id FROM consumers.user_missions WHERE user_id = %s AND mission_id = %s", (uid, mid))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO consumers.user_missions (user_id, mission_id) 
                        VALUES (%s, %s)
                    """, (uid, mid))

    conn.commit()
    print("-> [SUCESSO] Correção cirúrgica aplicada: Retenção salva, Regiões populadas e Missões corrigidas.")

# [SUBSTITUIÇÃO - Bloco 'try...finally' no final do arquivo]
# --- 3. Execução em ordem lógica ---
try:
    # 0. Popula dados mestres (Easy Wins)
    master_data = populate_master_data()
    
    # 1. AUMENTO DE VOLUME: De 100 para 600 usuários.
    # Isso garante que cada empresa tenha ~40 funcionários, permitindo variação estatística.
    all_user_ids, active_user_ids = populate_users(600, rank_ids_list=master_data['rank_ids'])
    partner_ids, schedule_ids = populate_partners_and_schedules(25)
    
    # 2. REDUÇÃO DE CLIENTES B2B: De 30 para 15.
    # Menos clientes + Mais usuários = Gráficos mais ricos e variados.
    plan_ids = populate_plans()
    client_ids = populate_b2b_clients(15, plan_ids)
    populate_b2b_collaborators(client_ids, all_user_ids)
    
    # --- FINANCEIRO E AGENDA ---
    # Aumentamos para 8000 fatos para cobrir os novos usuários
    populate_facts(12000, all_user_ids, schedule_ids, master_data) 

    # --- NOVO: Popular Interações Gamificadas ---
    # Aumentamos para 6000 interações para garantir que o gráfico de "Engajamento" 
    # (Ativos vs Inativos) tenha dados reais de atividade.
    populate_interactions(10000, active_user_ids, partner_ids, client_ids)
    
    # 4. Popula "Hard Wins"
    populate_web_events_and_costs(all_user_ids)
    
    # Ao ter mais usuários, a chance de uma campanha ficar vazia cai para quase zero.
    populate_missions_and_campaigns(user_ids=all_user_ids, active_user_ids=active_user_ids, client_ids=client_ids)
    populate_mev_scores(all_user_ids)
    
    # 4. Popula "Hard Wins" (usa TODAS as listas)
    populate_web_events_and_costs(all_user_ids)
    # [LINHA 577 - A CORREÇÃO]
    populate_missions_and_campaigns(user_ids=all_user_ids, active_user_ids=active_user_ids, client_ids=client_ids)
    populate_mev_scores(all_user_ids)
    populate_strategic_retention_and_missions(all_user_ids, partner_ids)
    
except Exception as e:
    print(f"Um erro crítico ocorreu durante a população: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("\nBanco populado com sucesso (COM DADOS VARIADOS) e conexão fechada!")
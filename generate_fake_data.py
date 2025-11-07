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

def populate_users(n=50):
    print(f"Populando {n} registros em consumers.user...")
    ids = []
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO consumers.user (name, email, password, created_at, active) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id;
            """, (
                fake.name(), 
                fake.unique.email(), 
                "senha_fake_hash_123", 
                fake.date_time_between(start_date="-2y", end_date="now"),
                True
            ))
            result = cursor.fetchone()
            if result:
                ids.append(result[0])
        except Exception as e:
            conn.rollback()
        else:
            conn.commit()
    
    print(f"-> {len(ids)} novos usuários inseridos.")
    return ids

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
                fake.cnpj(),
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

            # 3. Criar um Horário (Schedule) para a Atividade
            cursor.execute("""
                INSERT INTO providers.partner_schedule (partner_id, partner_activity_id, active, recurrent, value)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                partner_id,
                activity_id,
                True,
                True,
                random.uniform(20.0, 50.0)
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

def populate_facts(n=500, user_ids=[], schedule_ids=[]):
    print(f"Populando {n} fatos (reservas, pagamentos, check-ins)...")
    if not user_ids or not schedule_ids:
        print("Faltando IDs de usuários ou horários. Pulando fatos.")
        return

    # Precisamos saber qual parceiro é dono de qual schedule
    # Criar um mapa: {schedule_id: partner_id}
    try:
        cursor.execute("SELECT id, partner_id FROM providers.partner_schedule")
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
                user_id, schedule_id, data_agendamento.date(), 'CONFIRMED', True,
                data_agendamento.strftime("%H"), data_agendamento.strftime("%M"),
                data_agendamento.strftime("%H:%M"), data_agendamento
            ))
            schedule_result = cursor.fetchone()
            
            if not schedule_result:
                conn.rollback() 
                continue
            
            reservation_id, reservation_created_at = schedule_result
            reservations_created += 1
            
            # --- 2. Criar Pagamento (consumers.payment) ---
            # CORREÇÃO: Removido "user_id" e "partner_id" do INSERT
            if random.random() < 0.7:
                cursor.execute("""
                    INSERT INTO consumers.payment
                    (user_scheduling_id, status, amount_due, payment_type, active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    reservation_id, # Link para a reserva
                    'PAID', random.uniform(20.0, 50.0), 'CREDIT_CARD', True, reservation_created_at
                ))
                payments_created += 1

            # --- 3. Criar Check-in (consumers.user_time) ---
            # CORREÇÃO: Removido "partner_id" do INSERT (que causaria FK violation)
            if random.random() < 0.8:
                cursor.execute("""
                    INSERT INTO consumers.user_time
                    (user_id, type, status, active, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id, 
                    'CHECKIN', 'FINISHED', True,
                    reservation_created_at + timedelta(minutes=random.randint(-5, 5))
                ))
                checkins_created += 1

        except Exception as e:
            print(f"Erro ao inserir fato (desfazendo): {e}") # Agora vai mostrar o erro real
            conn.rollback()
        else:
            conn.commit() # Salva a transação (reserva + pagamento + checkin)
            
    print(f"-> Fatos criados: {reservations_created} reservas, {payments_created} pagamentos, {checkins_created} check-ins.")


# --- 3. Execução em ordem lógica ---
try:
    # Removemos o código de 'companies' pois não é usado nos dashboards atuais
    user_ids = populate_users(100)
    partner_ids, schedule_ids = populate_partners_and_schedules(20)
    
    # Gerar muitos fatos para termos dados nos gráficos
    populate_facts(2000, user_ids, schedule_ids) 
    
except Exception as e:
    print(f"Um erro crítico ocorreu durante a população: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("\nBanco populado com sucesso e conexão fechada!")
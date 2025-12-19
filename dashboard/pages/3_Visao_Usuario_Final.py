# pages/3_Visao_Usuario_Final.py

import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# URL base da sua API
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Visão Usuário Final", page_icon="🏃", layout="wide")
st.title("🏃 Dashboard de Visão do Usuário Final")

# --- Funções de API ---
@st.cache_data(ttl=600)
def get_user_list():
    try:
        res = requests.get(f"{API_URL}/bi/user/list")
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar lista de usuários: {e}")
        return []
    
@st.cache_data(ttl=0)
def get_my_profile(user_id):
    """ Busca o perfil completo do usuário logado """
    try:
        res = requests.get(f"{API_URL}/bi/user/profile", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_user_activity(user_id):
    try:
        res = requests.get(f"{API_URL}/bi/user/activity_history", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_user_gamification(user_id):
    try:
        res = requests.get(f"{API_URL}/bi/user/gamification_stats", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return {}

# --- NOVAS FUNÇÕES (Gamificação Comportamental) ---
@st.cache_data(ttl=60)
def get_user_consistency(user_id):
    try:
        res = requests.get(f"{API_URL}/bi/user/consistency", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_user_habit(user_id):
    try:
        res = requests.get(f"{API_URL}/bi/user/habit", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_user_social_stats(user_id):
    try:
        # Nota: Este endpoint retorna Diversidade e Social
        res = requests.get(f"{API_URL}/bi/user/gamification_stats", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except: return {}

# --- Interface do Dashboard ---

users = get_user_list()

if not users:
    st.error("Não foi possível carregar os usuários. Verifique se a API está rodando.")
    st.stop()

# Dropdown para selecionar o usuário
user_names = {u['name']: u['id'] for u in users}
selected_name = st.selectbox("Selecione um Usuário:", list(user_names.keys()))
selected_id = user_names[selected_name]

st.markdown(f"### Métricas para: **{selected_name}** (ID: {selected_id})")

# --- Carregar dados do usuário selecionado ---
activity_data = get_user_activity(selected_id)
gamification_data = get_user_gamification(selected_id)

# --- KPIs em colunas ---
col1, col2, col3 = st.columns(3)

if activity_data and 'values' in activity_data:
    total_checkins = sum(activity_data['values'])
    media_semanal = (total_checkins / 4.28) # 30 dias / 7 dias
else:
    total_checkins = 0
    media_semanal = 0

with col1:
    st.metric(label="Treinos (Últimos 30d)", value=f"{total_checkins}")

with col2:
    st.metric(label="Média de Treinos/Semana", value=f"{media_semanal:.1f}")
    
with col3:
    val_minutos = gamification_data.get("total_minutos_ativos_30d", 0)
    st.metric(label="Minutos Ativos (30d)", value=f"{val_minutos} min")

# Nova métrica de Calorias
    st.subheader("Métricas de Saúde")
    val_calorias = gamification_data.get("total_calorias_30d", 0)
    st.metric(label="Calorias Queimadas (30d)", value=f"{val_calorias} kcal")
    
    st.divider() # Adiciona um novo separador
    st.subheader("Métricas de Gamificação") # Título para a seção antiga

st.divider()
col4, col5 = st.columns(2)

with col4:
    val = gamification_data.get("total_pontos", 0)
    st.metric(label="Total de Pontos (Rank)", value=f"{val}")

with col5:
    val = gamification_data.get("total_conquistas", 0)
    st.metric(label="Total de Conquistas (Stamps)", value=f"{val}")


# --- ADIÇÃO: Análise de Comportamento (DNA do Usuário) ---
st.divider()
st.subheader("🧬 DNA do Usuário (Comportamento)")

# Busca os dados novos
consistency = get_user_consistency(selected_id)
habit = get_user_habit(selected_id)
social = get_user_social_stats(selected_id)

c1, c2, c3, c4 = st.columns(4)

with c1:
    # Consistência (Dias treinados nos últimos 7d)
    days = consistency.get("days_trained_last_7d", 0)
    badge = consistency.get("consistency_badge", "Sem Dados")
    st.metric("Consistência (7d)", f"{days} dias", help=badge)
    if days >= 3:
        st.success(f"🏅 {badge}")
    else:
        st.warning(f"⚠️ {badge}")

with c2:
    # Hábito (Turno preferido)
    turno = habit.get("favorite_time", "Indefinido")
    total_turno = habit.get("sessions", 0)
    emoji_turno = "🌅" if turno == "Manhã" else "🌃" if turno == "Noite" else "☀️"
    st.metric("Hábito (Turno)", f"{emoji_turno} {turno}", f"{total_turno} treinos")

with c3:
    # Diversidade (Modalidades diferentes)
    unique_sports = social.get("unique_modalities", 0)
    st.metric("Diversidade", f"{unique_sports} Modalidades")

with c4:
    # Social (Treinos com amigos)
    social_count = social.get("social_workouts", 0)
    st.metric("Treinos Sociais", f"{social_count}", "Com amigos")

# --- Gráficos ---
st.subheader("Histórico de Atividade (Check-ins nos últimos 30 dias)")

if activity_data and total_checkins > 0:
    df_activity = pd.DataFrame(activity_data)
    # Criar um range de datas completo para os últimos 30 dias
    all_dates = pd.date_range(start=pd.to_datetime('today') - pd.Timedelta(days=29), end=pd.to_datetime('today'))
    df_dates = pd.DataFrame(all_dates, columns=['date'])
    df_dates['labels'] = df_dates['date'].dt.strftime('%Y-%m-%d')
    
    # Juntar com os dados reais
    df_activity = pd.merge(df_dates, df_activity, on="labels", how="left").fillna(0)
    
    fig = px.bar(df_activity, x="labels", y="values", 
                 title="Check-ins por Dia", 
                 labels={"labels": "Data", "values": "Check-ins (1=Sim, 0=Não)"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Este usuário não possui check-ins nos últimos 30 dias.")

st.divider()
st.subheader("📋 Meu Passaporte de Saúde")

# Busca os dados detalhados
my_profile = get_my_profile(selected_id)

if my_profile:
    p_info = my_profile.get("personal_info", {})
    h_stats = my_profile.get("health_stats", {})
    loc = my_profile.get("location", {})
    
    # Cartão de Identificação Visual
    with st.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c1:
            # Avatar genérico baseado no gênero
            gender = p_info.get('gender', 'O')
            avatar = "👨" if gender == 'M' else "👩" if gender == 'F' else "👤"
            st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{avatar}</h1>", unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"### {p_info.get('name')}")
            st.caption(f"Membro desde: {my_profile.get('system_data', {}).get('created_at', '')[:10]}")
            st.write(f"📧 {p_info.get('email')}")
            st.write(f"🏠 {loc.get('full_address')}")
            
        with c3:
            # Score de Saúde em destaque
            lvl = h_stats.get('health_level', 0)
            st.metric("Health Score", f"{lvl}/100")
            if lvl > 80: st.success("Excelente!")
            elif lvl > 50: st.warning("Pode melhorar")
            else: st.error("Atenção")

    # Dados Biométricos
    st.markdown("#### 🩺 Biometria Atual")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Peso", f"{h_stats.get('weight')} kg")
    b2.metric("Altura", f"{h_stats.get('height')} m")
    
    # Cálculo simples de IMC no front para exibir na hora
    try:
        imc = h_stats.get('weight') / (h_stats.get('height') ** 2)
        b3.metric("IMC", f"{imc:.1f}")
    except:
        b3.metric("IMC", "--")
        
    b4.write(f"**Diabético:** {'Sim' if h_stats.get('is_diabetic') else 'Não'}")
    b4.write(f"**Hipertenso:** {'Sim' if h_stats.get('is_hypertensive') else 'Não'}")

else:
    st.warning("Perfil detalhado não carregado.")
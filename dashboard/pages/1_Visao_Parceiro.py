# pages/1_Visao_Parceiro.py
# (O Streamlit trata arquivos "pages/X_Nome.py" como páginas)
# Renomeie seu arquivo para "pages/1_Visao_Parceiro.py"
# Se não quiser usar a pasta 'pages', apenas renomeie para "1_Visao_Parceiro.py"

import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# URL base da sua API
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Visão do Parceiro", page_icon="🏢", layout="wide")
st.title("🏢 Dashboard de Visão do Parceiro")

# --- Funções de API ---
@st.cache_data(ttl=600) # Cache de 10 minutos
def get_partners_list():
    try:
        res = requests.get(f"{API_URL}/bi/partners_list")
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar lista de parceiros: {e}")
        return []

# --- COLE ISSO JUNTO COM AS OUTRAS FUNÇÕES DE API ---

@st.cache_data(ttl=600)
def get_user_list():
    """ Busca lista de usuários para o dropdown """
    try:
        res = requests.get(f"{API_URL}/bi/user/list")
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return []

@st.cache_data(ttl=0) # TTL 0 para não fazer cache e pegar dados frescos
def get_user_profile_data(user_id):
    """ Busca o perfil COMPLETO (24 colunas) """
    try:
        res = requests.get(f"{API_URL}/bi/user/profile", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return {}

@st.cache_data(ttl=60)
def get_partner_efficiency(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/partner/efficiency", params={"partner_id": partner_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

# --- ADIÇÃO: Função para buscar Eficiência e Qualidade (Parte 3) ---
@st.cache_data(ttl=60)
def get_partner_efficiency(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/partner/efficiency", params={"partner_id": partner_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60) # Cache de 1 minuto
def get_partner_revenue(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/revenue", params={"partner_id": partner_id, "days": 30})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_partner_checkins(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/checkins", params={"partner_id": partner_id, "days": 30})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_reservation_status(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/partner/reservation_status", params={"partner_id": partner_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_occupation_by_hour(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/partner/occupation_by_hour", params={"partner_id": partner_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_partner_kpi_overview(partner_id):
    try:
        res = requests.get(f"{API_URL}/bi/partner/kpi_overview", params={"partner_id": partner_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return {} # Retorna dict vazio em caso de erro

# --- Interface do Dashboard ---

partners = get_partners_list()

if not partners:
    st.error("Não foi possível carregar os parceiros. Verifique se a API está rodando.")
    st.stop()

# Dropdown para selecionar o parceiro
partner_names = {p['name']: p['id'] for p in partners}
selected_name = st.selectbox("Selecione um Parceiro:", list(partner_names.keys()))
selected_id = partner_names[selected_name]

st.markdown(f"### Métricas para: **{selected_name}** (ID: {selected_id})")

# --- Carregar dados do parceiro selecionado ---
revenue_data = get_partner_revenue(selected_id)
checkin_data = get_partner_checkins(selected_id)
status_data = get_reservation_status(selected_id)
occupation_data = get_occupation_by_hour(selected_id)

# Carregar dados dos KPIs extras (NPS, Repasses)
kpi_data = get_partner_kpi_overview(selected_id)

# --- KPIs em colunas ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if revenue_data and 'values' in revenue_data:
        total_revenue = sum(revenue_data['values'])
        st.metric(label="Receita Total (Últimos 30d)", value=f"R$ {total_revenue:,.2f}")
    else:
        st.metric(label="Receita Total (Últimos 30d)", value="R$ 0,00")

with col2:
    if checkin_data and 'values' in checkin_data:
        total_checkins = sum(checkin_data['values'])
        st.metric(label="Check-ins (Últimos 30d)", value=f"{total_checkins}")
    else:
        st.metric(label="Check-ins (Últimos 30d)", value="0")

with col3:
    val_nps = kpi_data.get("nps_avg", 0)
    st.metric(label="NPS (Média 0-10)", value=f"{val_nps:.1f} ⭐")

with col4:
    val_repasses = kpi_data.get("total_repassado_30d", 0)
    st.metric(label="Repasses (Últimos 30d)", value=f"R$ {val_repasses:,.2f}")

# ... (mantenha o código anterior até a linha st.divider())

st.divider()

# --- ADIÇÃO CORRIGIDA: KPIs de Qualidade & Eficiência ---
# Busca os dados novos usando a variável CORRETA (selected_id)
efficiency_data = get_partner_efficiency(selected_id)
    
st.subheader("🌟 Qualidade & Eficiência Operacional")

if efficiency_data:
    k1, k2, k3 = st.columns(3)
    
    # KPI 1: Classificação (Ex: Alta Performance)
    k1.metric("Classificação", efficiency_data.get("efficiency_label", "N/A"))
    
    # KPI 2: Score de Qualidade (Barra de progresso)
    score = efficiency_data.get("quality_score_percent", 0)
    k2.metric("Score de Qualidade (5★)", f"{score}%")
    k2.progress(int(score)) # Streamlit pede int ou float entre 0 e 100
    
    # KPI 3: Volume Total
    k3.metric("Volume Total Check-ins", efficiency_data.get("total_volume", 0))

else:
    # Mensagem amigável se não houver dados (ou se o backend não tiver rodado)
    st.info("Aguardando dados de eficiência... (Verifique se o generate_fake_data.py rodou as interações)")
    
st.divider()

# ... (restante do código com os gráficos de Receita, etc.)

# --- Gráficos ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Receita por Dia")
    if revenue_data:
        df_revenue = pd.DataFrame(revenue_data)
        fig = px.line(df_revenue, x="labels", y="values", title="Receita (R$) por Dia", labels={"labels": "Data", "values": "Receita"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de receita para exibir.")

with col4:
    st.subheader("Check-ins por Dia")
    if checkin_data:
        df_checkin = pd.DataFrame(checkin_data)
        fig = px.bar(df_checkin, x="labels", y="values", title="Check-ins por Dia", labels={"labels": "Data", "values": "Total de Check-ins"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de check-in para exibir.")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Reservas por Status")
    if status_data and 'values' in status_data and sum(status_data['values']) > 0:
        df_status = pd.DataFrame(status_data)
        fig = px.pie(df_status, names="labels", values="values", title="Status de Reservas (Total)", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de status de reserva para exibir.")
        
with col6:
    st.subheader("Ocupação por Hora do Dia")
    if occupation_data and 'values' in occupation_data and sum(occupation_data['values']) > 0:
        df_occupation = pd.DataFrame(occupation_data)
        fig = px.bar(df_occupation, x="labels", y="values", title="Total de Reservas por Hora", labels={"labels": "Hora", "values": "Nº de Reservas"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de ocupação por hora para exibir.")

# --- COLE ISSO NO FINAL DO ARQUIVO 1_Visao_Parceiro.py ---

st.divider()
st.markdown("### 🧬 Raio-X do Aluno (Ficha Técnica)")

# 1. Carregar lista de usuários para o Parceiro selecionar
users_list = get_user_list()
if users_list:
    u_names = {u['name']: u['id'] for u in users_list}
    # Cria uma chave única no selectbox para não conflitar com outros dashboards
    selected_user_name = st.selectbox("Selecione um Aluno para Análise:", list(u_names.keys()), key="partner_user_select")
    selected_user_id = u_names[selected_user_name]

    # 2. Buscar o Perfil Rico
    profile = get_user_profile_data(selected_user_id)

    if profile:
        # Extrair dados do JSON aninhado
        p_info = profile.get("personal_info", {})
        h_stats = profile.get("health_stats", {})
        sys_data = profile.get("system_data", {})
        loc = profile.get("location", {})

        # Layout em Cards
        c1, c2, c3 = st.columns(3)

        with c1:
            st.info("**Dados Pessoais**")
            st.write(f"👤 **Nome:** {p_info.get('name')}")
            st.write(f"📧 **Email:** {p_info.get('email')}")
            st.write(f"📞 **Tel:** {p_info.get('phone')}")
            st.write(f"🆔 **CPF:** {p_info.get('cpf')}")
            st.write(f"🎂 **Nasc:** {p_info.get('birth_date')} ({p_info.get('gender')})")

        with c2:
            st.success("**Perfil de Saúde**")
            st.write(f"⚖️ **Peso:** {h_stats.get('weight')} kg")
            st.write(f"📏 **Altura:** {h_stats.get('height')} m")
            
            # Tags visuais para condições
            diab = "Sim" if h_stats.get('is_diabetic') else "Não"
            hiper = "Sim" if h_stats.get('is_hypertensive') else "Não"
            
            st.write(f"🍬 **Diabético:** {diab}")
            st.write(f"🧂 **Hipertenso:** {hiper}")
            
            # Barra de Nível de Saúde
            lvl = h_stats.get('health_level', 0)
            st.write(f"🛡️ **Nível de Saúde:** {lvl}/100")
            st.progress(lvl)

        with c3:
            st.warning("**Sistema & Endereço**")
            st.write(f"📍 **CEP:** {loc.get('zip_code')}")
            st.write(f"🏠 **Endereço:** {loc.get('full_address')}")
            st.write(f"🏆 **Rank ID:** {sys_data.get('rank_id')}")
            st.write(f"🔑 **Token FCM:** {sys_data.get('fcm_token')[:10]}...") # Mostra só o começo
            st.write(f"📅 **Criado em:** {sys_data.get('created_at')}")

    else:
        st.error("Não foi possível carregar o perfil deste usuário.")
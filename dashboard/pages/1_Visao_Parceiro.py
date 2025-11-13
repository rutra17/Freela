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

st.divider()

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
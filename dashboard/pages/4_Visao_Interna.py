# pages/4_Visao_Interna.py
import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# URL base da sua API
API_URL = "http://127.0.0.1:8000" # Cuidado com o typo, se o seu for 127.0.0.1

st.set_page_config(page_title="Visão Interna (Admin)", page_icon="🔑", layout="wide")
st.title("🔑 Dashboard de Visão Interna (Admin)")
st.markdown("KPIs estratégicos para a gestão da plataforma.")

# --- Funções de API (Chamando todos os Hard Wins) ---

@st.cache_data(ttl=60)
def get_ltv_cac():
    try:
        res = requests.get(f"{API_URL}/bi/ltv_cac")
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_conversion_funnel():
    try:
        res = requests.get(f"{API_URL}/bi/conversion_funnel")
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_revenue_by_region():
    try:
        res = requests.get(f"{API_URL}/bi/revenue_by_region")
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60) 
def get_gamification_missions():
    try:
        res = requests.get(f"{API_URL}/bi/gamification/missions")
        res.raise_for_status()
        return res.json()
    except: return {}

@st.cache_data(ttl=60)
def get_gamification_streaks():
    try:
        res = requests.get(f"{API_URL}/bi/gamification/streaks")
        res.raise_for_status()
        return res.json()
    except: return {}

# --- Carregar Todos os Dados ---
ltv_data = get_ltv_cac()
funnel_data = get_conversion_funnel()
region_data = get_revenue_by_region()
mission_data = get_gamification_missions()
streaks_data = get_gamification_streaks()

# --- KPIs Principais (LTV/CAC) ---
st.subheader("Métricas de Vendas e Aquisição")
col1, col2 = st.columns(2)
with col1:
    ltv = ltv_data.get("ltv", 0)
    st.metric(label="Lifetime Value (LTV) Total", value=f"R$ {ltv:,.2f}")
with col2:
    cac = ltv_data.get("cac_30d", 0)
    st.metric(label="Custo por Aquisição (CAC) 30d", value=f"R$ {cac:,.2f}")

st.divider()

# --- Gráficos (Funil, Região, Gamificação) ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Funil de Conversão (Últimos 30d)")
    if funnel_data and 'values' in funnel_data:
        df_funnel = pd.DataFrame(funnel_data)
        fig_funnel = px.funnel(df_funnel, x='values', y='labels', title="Funil de Novos Usuários")
        st.plotly_chart(fig_funnel, use_container_width=True)
    else:
        st.warning("Sem dados de funil.")

with col4:
    st.subheader("Top 10 Receita por Região (CEP)")
    if region_data and 'values' in region_data:
        df_region = pd.DataFrame(region_data)
        fig_region = px.bar(df_region, x='labels', y='values', title="Receita por Região")
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.warning("Sem dados de região.")

st.divider()
col5, col6 = st.columns(2)

with col5:
    st.subheader("Missões Mais Completadas")
    if mission_data and 'values' in mission_data:
        df_mission = pd.DataFrame(mission_data)
        fig_mission = px.pie(df_mission, names='labels', values='values', title="Conclusão de Missões", hole=0.3)
        st.plotly_chart(fig_mission, use_container_width=True)
    else:
        st.warning("Sem dados de missões.")
        
with col6:
    st.subheader("Engajamento (Streaks) 7d")
    if streaks_data and 'values' in streaks_data:
        df_streaks = pd.DataFrame(streaks_data)
        fig_streaks = px.bar(df_streaks, x='labels', y='values', title="Nº de Usuários por Dias Ativos (Últimos 7d)")
        fig_streaks.update_xaxes(categoryorder='array', categoryarray=sorted(df_streaks['labels'], reverse=True))
        st.plotly_chart(fig_streaks, use_container_width=True)
    else:
        st.warning("Sem dados de streaks.")
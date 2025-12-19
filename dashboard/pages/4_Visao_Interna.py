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

@st.cache_data(ttl=600)
def get_user_list_admin():
    try:
        res = requests.get(f"{API_URL}/bi/user/list")
        res.raise_for_status()
        return res.json()
    except: return []

@st.cache_data(ttl=0)
def get_full_user_audit(user_id):
    try:
        res = requests.get(f"{API_URL}/bi/user/profile", params={"user_id": user_id})
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
def get_retention_metrics():
    try:
        res = requests.get(f"{API_URL}/bi/retention_d1_d7_d30")
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

# --- ADIÇÃO: KPIs de Retenção (Coortes) ---
retention = get_retention_metrics()

st.markdown("### 🔄 Retenção de Usuários (Churn Analysis)")
r1, r2, r3 = st.columns(3)

if retention:
    with r1:
        d1 = retention.get("d1", {})
        val = d1.get("pct", 0)
        st.metric("Retenção D1 (Voltou dia seguinte)", f"{val:.1f}%", f"{d1.get('retained')}/{d1.get('total')}")
        
    with r2:
        d7 = retention.get("d7", {})
        val = d7.get("pct", 0)
        st.metric("Retenção D7 (Voltou após 1 sem)", f"{val:.1f}%", f"{d7.get('retained')}/{d7.get('total')}")
        
    with r3:
        d30 = retention.get("d30", {})
        val = d30.get("pct", 0)
        st.metric("Retenção D30 (Mês completo)", f"{val:.1f}%", f"{d30.get('retained')}/{d30.get('total')}")
else:
    st.info("Dados de retenção insuficientes para cálculo de coorte.")

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
        # ADICIONEI: text_auto=True para mostrar o valor na barra
        fig_region = px.bar(df_region, x='labels', y='values', title="Receita por Região", text_auto=True)
        # ADICIONEI: Update layout para remover gaps excessivos
        fig_region.update_layout(bargap=0.2)
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

st.divider()
st.markdown("### 🕵️ Ferramenta de Auditoria Individual")
st.info("Utilize esta seção para validar dados cadastrais, tokens e integridade de registros de qualquer usuário.")

# Seleção de usuário para auditar
users_audit = get_user_list_admin()
if users_audit:
    u_map = {u['name']: u['id'] for u in users_audit}
    audit_name = st.selectbox("Pesquisar Usuário (Nome):", list(u_map.keys()), key="audit_select")
    audit_id = u_map[audit_name]
    
    # Busca dados brutos
    raw_data = get_full_user_audit(audit_id)
    
    if raw_data:
        t1, t2 = st.tabs(["Visualização Amigável", "JSON Bruto (Debug)"])
        
        with t1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Identificação**")
                st.code(f"""
ID Interno: {raw_data.get('id')}
ID Externo: {raw_data.get('system_data', {}).get('external_id')}
CPF: {raw_data.get('personal_info', {}).get('cpf')}
Token FCM: {raw_data.get('system_data', {}).get('fcm_token')}
                """)
            with col_b:
                st.write("**Status & Conta**")
                st.write(f"Status: {raw_data.get('status')}")
                st.write(f"Tipo: {raw_data.get('professional_info', {}).get('user_type')}")
                st.write(f"Último Update: {raw_data.get('system_data', {}).get('updated_at')}")
                
        with t2:
            st.json(raw_data)
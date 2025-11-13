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
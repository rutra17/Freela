# dashboard/pages/2_Visao_B2B.py
# [VERSÃO TOTALMENTE CORRIGIDA E BLINDADA]

import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# URL base da sua API
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Visão Cliente B2B", page_icon="💼", layout="wide")
st.title("💼 Dashboard de Visão do Cliente B2B")

# --- Funções de API (BLINDADAS) ---

@st.cache_data(ttl=600)
def get_b2b_clients_list():
    """
    Busca a lista de clientes B2B.
    GARANTIA: Sempre retorna uma lista (list).
    """
    try:
        res = requests.get(f"{API_URL}/bi/b2b/clients_list")
        res.raise_for_status()
        data = res.json()
        # GARANTIA: Se a API não retornar uma lista, retorna uma lista vazia.
        if not isinstance(data, list):
            return []
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar lista de clientes: {e}")
        return []

@st.cache_data(ttl=60)
def get_b2b_engagement_stats(client_id):
    """
    Busca dados de engajamento para um cliente.
    GARANTIA: Sempre retorna um dicionário (dict).
    """
    try:
        res = requests.get(f"{API_URL}/bi/b2b/engagement_stats", params={"client_id": client_id})
        res.raise_for_status()
        data = res.json()
        # [CORREÇÃO DEFINITIVA DO BUG]
        # GARANTIA: Se a API retornar uma lista (ex: []), força um dict vazio.
        if not isinstance(data, dict):
            return {} 
        return data
    except requests.exceptions.RequestException as e:
        # GARANTIA: Em caso de erro de API, retorna um dict vazio.
        st.error(f"API Error (engagement): {e}")
        return {}

@st.cache_data(ttl=60)
def get_b2b_cost_per_collaborator(client_id):
    """
    Busca dados de custo por colaborador.
    GARANTIA: Sempre retorna um dicionário (dict).
    """
    try:
        res = requests.get(f"{API_URL}/bi/b2b/cost_per_collaborator", params={"client_id": client_id})
        res.raise_for_status()
        data = res.json()
        # [CORREÇÃO DEFINITIVA DO BUG]
        # GARANTIA: Se a API retornar uma lista (ex: []), força um dict vazio.
        if not isinstance(data, dict):
            return {}
        return data
    except requests.exceptions.RequestException as e:
        # GARANTIA: Em caso de erro de API, retorna um dict vazio.
        st.error(f"API Error (cost): {e}")
        return {}
# [ADIÇÃO - Linha 91]

@st.cache_data(ttl=60)
def get_b2b_campaign_participation(client_id):
    """ Busca dados de participação em campanhas (Hard Win) """
    try:
        res = requests.get(f"{API_URL}/bi/b2b/campaign_participation", params={"client_id": client_id})
        res.raise_for_status()
        data = res.json()
        if not isinstance(data, dict): return {}
        return data
    except requests.exceptions.RequestException:
        return {}

@st.cache_data(ttl=60)
def get_b2b_mev_score_variation(client_id):
    """ Busca dados de variação do MEV Score (Hard Win) """
    try:
        res = requests.get(f"{API_URL}/bi/b2b/mev_score_variation", params={"client_id": client_id})
        res.raise_for_status()
        data = res.json()
        if not isinstance(data, dict): return {}
        return data
    except requests.exceptions.RequestException:
        return {}

# --- Interface do Dashboard ---

clients = get_b2b_clients_list()

if not clients:
    st.error("Não foi possível carregar os clientes B2B. Verifique se a API está rodando.")
    st.warning("Lembrete: Se nenhum cliente aparecer, rode o script 'generate_fake_data.py' (com as correções B2B) para popular o banco.")
    # Vamos continuar mesmo sem clientes, para o layout aparecer
    clients = [{"id": 0, "name": "Nenhum cliente B2B encontrado"}]

# Dropdown para selecionar o cliente
client_names = {c['name']: c['id'] for c in clients}
selected_name = st.selectbox("Selecione um Cliente B2B:", list(client_names.keys()))
selected_id = client_names[selected_name]

st.markdown(f"### Métricas para: **{selected_name}** (ID: {selected_id})")

# --- Carregar dados do cliente selecionado ---
# [BLOCO DE BLINDAGEM NUCLEAR]
# Vamos chamar as funções, que podem estar retornando lixo (listas)
engagement_data_raw = get_b2b_engagement_stats(selected_id)
cost_data_raw = get_b2b_cost_per_collaborator(selected_id)
# Carrega dados dos Hard Wins
campaign_data_raw = get_b2b_campaign_participation(selected_id)
mev_score_data_raw = get_b2b_mev_score_variation(selected_id)

# Agora, vamos FORÇAR essas variáveis a serem dicionários
# não importa o que a função "fantasma" retornou.
engagement_data = engagement_data_raw if isinstance(engagement_data_raw, dict) else {}
cost_data = cost_data_raw if isinstance(cost_data_raw, dict) else {}
campaign_data = campaign_data_raw if isinstance(campaign_data_raw, dict) else {}
mev_score_data = mev_score_data_raw if isinstance(mev_score_data_raw, dict) else {}
# [FIM DO BLOCO DE BLINDAGEM]


# --- KPIs em colunas ---
col1, col2, col3 = st.columns(3)

with col1:
    # Este .get() agora é 100% seguro.
    val = engagement_data.get("taxa_adesao_pct", 0)
    st.metric(label="Taxa de Adesão (Ativos 30d)", value=f"{val:.1f} %")

with col2:
    val = engagement_data.get("total_colaboradores", 0)
    st.metric(label="Total de Colaboradores (Base Elegível)", value=f"{val}")

with col3:
    val = engagement_data.get("total_ativos_30d", 0)
    st.metric(label="Colaboradores Ativos (Últimos 30d)", value=f"{val}")

st.divider()
col4, col5, col6 = st.columns(3)

with col4:
    val = cost_data.get("custo_por_colaborador_ativo", 0)
    st.metric(label="Custo por Colaborador Ativo", value=f"R$ {val:,.2f}")

with col5:
    val = cost_data.get("total_revenue_cliente", 0)
    st.metric(label="Receita Total Gerada pelo Cliente", value=f"R$ {val:,.2f}")
    
with col6:
    # Carrega dados do MEV Score
    old_score = mev_score_data.get("old_score", 0)
    new_score = mev_score_data.get("new_score", 0)
    delta = new_score - old_score

    st.metric(
        label="Variação de Risco (MEV Score)", 
        value=f"{new_score:.1f}", 
        delta=f"{delta:.1f} (vs {old_score:.1f} em 30d)",
        delta_color="inverse" # "inverse" = verde se o risco (score) diminuir
    )

# --- Gráficos ---
st.subheader("Engajamento da Base")

# Usamos as variáveis 'limpas' e seguras
total_elegivel = engagement_data.get("total_colaboradores", 0)
total_ativos = engagement_data.get("total_ativos_30d", 0)
total_inativos = total_elegivel - total_ativos

if total_elegivel > 0:
    df_engagement = pd.DataFrame({
        "Status": ["Ativos (30d)", "Inativos"],
        "Total": [total_ativos, total_inativos]
    })
    fig = px.pie(df_engagement, names="Status", values="Total", 
                 title="Colaboradores Ativos vs. Inativos", 
                 hole=0.3,
                 color_discrete_map={"Ativos (30d)": "green", "Inativos": "lightgray"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Não há dados de engajamento para este cliente ou a base de colaboradores está zerada.")

# [ADIÇÃO - Fim do Arquivo]

st.divider()
st.subheader("Participação em Campanhas de Saúde")

# Usa a variável 'campaign_data' que carregamos
if campaign_data and 'values' in campaign_data and sum(campaign_data['values']) > 0:
    df_campaigns = pd.DataFrame(campaign_data)
    fig_campaign = px.bar(
        df_campaigns, 
        x="labels", 
        y="values", 
        title="Participantes por Campanha Ativa",
        labels={"labels": "Campanha", "values": "Nº de Participantes"}
    )
    st.plotly_chart(fig_campaign, use_container_width=True)
else:
    st.warning("Nenhuma campanha ou participante encontrado para este cliente.")
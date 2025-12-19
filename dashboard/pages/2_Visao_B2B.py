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

# --- COLE ISSO JUNTO COM AS OUTRAS FUNÇÕES DE API ---

@st.cache_data(ttl=600)
def get_all_users_list():
    """ Busca lista global de usuários (simulando base de colaboradores) """
    try:
        res = requests.get(f"{API_URL}/bi/user/list")
        res.raise_for_status()
        return res.json()
    except: return []

@st.cache_data(ttl=0)
def get_collaborator_profile(user_id):
    """ Busca perfil rico (Endpoint novo) """
    try:
        res = requests.get(f"{API_URL}/bi/user/profile", params={"user_id": user_id})
        res.raise_for_status()
        return res.json()
    except: return {}

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
    
# --- ADIÇÃO: Função para buscar ROI Corporativo (Parte 3) ---
@st.cache_data(ttl=60)
def get_company_roi(client_id):
    try:
        res = requests.get(f"{API_URL}/bi/b2b/roi", params={"client_id": client_id})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return None

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

st.divider()

# --- ADIÇÃO: Análise de ROI (Retorno sobre Investimento) ---
roi_data = get_company_roi(selected_id)

st.subheader("📈 Análise de ROI Corporativo")

if roi_data:
    r1, r2, r3 = st.columns(3)
    
    # Taxa de Adoção Real
    r1.metric("Taxa de Adoção Real", roi_data.get("adoption_rate", "0%"))
    
    # Status do ROI (Positivo/Atenção)
    status_roi = roi_data.get("roi_status", "N/A")
    emoji = "✅" if status_roi == "Positivo" else "⚠️"
        
    r2.metric("Status do ROI", f"{emoji} {status_roi}")
    
    # Usuários "Heavy Users" (que treinam > 4x mês)
    r3.metric("Usuários Ativos (>4 treinos/mês)", roi_data.get("active_users", 0))

else:
    st.warning("Dados de ROI insuficientes para análise.")
    
st.divider()

# --- Gráficos ---
st.subheader("Engajamento da Base")

# Usamos as variáveis 'limpas' e seguras
total_elegivel = engagement_data.get("total_colaboradores", 0)
total_ativos = engagement_data.get("total_ativos_30d", 0)

# [CORREÇÃO VISUAL E MATEMÁTICA]
# 1. Garante que inativos nunca seja negativo (max(0, ...))
total_inativos = max(0, total_elegivel - total_ativos)

if total_elegivel > 0:
    df_engagement = pd.DataFrame({
        "Status": ["Ativos (30d)", "Inativos"],
        "Total": [total_ativos, total_inativos]
    })
    
    # 2. Paleta de cores corporativa profissional (Azul Profundo para Ativos, Cinza Claro para Inativos)
    # Isso remove aquele azul padrão "brinquedo" do Streamlit.
    fig = px.pie(
        df_engagement, 
        names="Status", 
        values="Total", 
        title="Colaboradores Ativos vs. Inativos", 
        hole=0.5, # Buraco maior fica mais elegante (Donut Chart)
        color="Status",
        color_discrete_map={
            "Ativos (30d)": "#2E86C1",  # Azul Corporativo Forte
            "Inativos": "#D5D8DC"       # Cinza Suave
        }
    )
    
    # Ajuste de Layout para tirar poluição visual
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(showlegend=False) # Legenda interna é mais limpa

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

# --- COLE ISSO NO FINAL DO ARQUIVO 2_Visao_B2B.py ---

st.divider()
st.markdown("### 👔 Detalhes do Colaborador (Auditoria)")

# Lista de usuários para simular a busca de um colaborador
collab_list = get_all_users_list()

if collab_list:
    c_names = {u['name']: u['id'] for u in collab_list}
    # Selectbox com chave única
    sel_collab_name = st.selectbox("Buscar Colaborador:", list(c_names.keys()), key="b2b_user_select")
    sel_collab_id = c_names[sel_collab_name]

    # Busca perfil
    profile = get_collaborator_profile(sel_collab_id)

    if profile:
        prof_info = profile.get("professional_info", {})
        h_stats = profile.get("health_stats", {})
        sys_data = profile.get("system_data", {})

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 💼 Dados Corporativos")
            st.write(f"**Cargo:** {prof_info.get('occupation')}")
            st.write(f"**Setor:** {prof_info.get('sector')}")
            st.write(f"**Tipo de Conta:** {prof_info.get('user_type')}")
            
            status = profile.get("status")
            if status == "Ativo":
                st.success(f"Status: {status}")
            else:
                st.error(f"Status: {status}")

        with col2:
            st.markdown("#### 🏥 Risco & Saúde")
            
            # 1. CÁLCULO DO IMC E DEFINIÇÃO DE CORES
            peso = h_stats.get('weight', 0) or 0
            altura = h_stats.get('height', 0) or 0
            imc_val = 0
            imc_cat = "N/A"
            cor_imc = "grey" # Default

            if altura > 0:
                imc_val = peso / (altura ** 2)
                
                if imc_val < 18.5: 
                    imc_cat = "Abaixo do Peso"
                    cor_imc = "orange" # Atenção
                elif imc_val < 25: 
                    imc_cat = "Peso Normal"
                    cor_imc = "green" # Ideal
                elif imc_val < 30: 
                    imc_cat = "Sobrepeso"
                    cor_imc = "orange" # Atenção
                else: 
                    imc_cat = "Obesidade"
                    cor_imc = "red" # Perigo

            # 2. NOVA LÓGICA DE RISCO (Doenças + IMC)
            tem_doenca = h_stats.get('is_hypertensive') or h_stats.get('is_diabetic')
            
            if tem_doenca or imc_val >= 30:
                risco = "ALTO"
                cor_risco = "red"
                motivo_risco = "(Doença Crônica ou Obesidade)"
            elif imc_val >= 25:
                risco = "MÉDIO"
                cor_risco = "orange"
                motivo_risco = "(Sobrepeso)"
            else:
                risco = "BAIXO"
                cor_risco = "green"
                motivo_risco = ""

            # 3. EXIBIÇÃO VISUAL
            st.markdown(f"**Risco:** :{cor_risco}[{risco}] {motivo_risco}")
            
            # Exibe Doenças se houver
            if tem_doenca:
                if h_stats.get('is_hypertensive'): st.caption("⚠️ Hipertensão Detectada")
                if h_stats.get('is_diabetic'): st.caption("⚠️ Diabetes Detectada")

            # Exibe IMC Colorido
            st.write("---")
            st.markdown(f"**IMC:** {imc_val:.1f}")
            st.markdown(f"**Classificação:** :{cor_imc}[{imc_cat}]")
            st.caption(f"Dados: {peso}kg / {altura}m")
            
            # --- LÓGICA DE CÁLCULO IMC ---
            peso = h_stats.get('weight', 0) or 0
            altura = h_stats.get('height', 0) or 0
            imc_val = 0
            imc_msg = "N/A"
            
            if altura > 0:
                imc_val = peso / (altura ** 2)
                if imc_val < 18.5: imc_msg = "Abaixo do Peso"
                elif imc_val < 25: imc_msg = "Peso Normal"
                elif imc_val < 30: imc_msg = "Sobrepeso"
                else: imc_msg = "Obesidade"
            # -----------------------------

            st.markdown(f"**Classificação de Risco:** :{cor_risco}[{risco}]")
            st.metric("IMC Calculado", f"{imc_val:.1f}", imc_msg)
            st.write(f"Score de Saúde: {h_stats.get('health_level')}")

        with col3:
            st.markdown("#### 🔐 Auditoria")
            st.write(f"**ID Interno:** {profile.get('id')}")
            st.write(f"**ID Externo:** {sys_data.get('external_id')}")
            st.write(f"**Última Atualização:** {sys_data.get('updated_at')}")

    else:
        st.warning("Dados do colaborador indisponíveis.")
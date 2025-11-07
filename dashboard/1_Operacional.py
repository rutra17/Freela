# dashboard/app.py
import streamlit as st
import requests

# -- Configuração da Página --
st.set_page_config(
    page_title="BI Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Conexão com a API (FastAPI) ---
# A API que você criou no Passo 6 e está rodando
API_BASE_URL = "http://127.0.0.1:8000"

st.title("BI MVP - Dashboard Operacional 📊")

# --- Barra Lateral (Inputs) ---
st.sidebar.header("Filtros")
partner_id = st.sidebar.text_input("ID do Parceiro (Opcional)", help="Insira um ID numérico, ex: 1")

# --- Gráfico 1: Check-ins ---
st.header("Check-ins por Dia")

if st.button("Carregar Check-ins"):
    # Prepara os parâmetros para enviar à API
    params = {}
    if partner_id:
        try:
            params["partner_id"] = int(partner_id)
        except ValueError:
            st.error("Por favor, insira um ID de parceiro numérico.")
    
    try:
        # Chama o endpoint /bi/checkins da sua API
        response = requests.get(f"{API_BASE_URL}/bi/checkins", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["values"]:
                st.line_chart({"Check-ins": data["values"]}, use_container_width=True)
                st.dataframe(data) # Mostra os dados brutos
            else:
                st.warning("Nenhum dado de check-in encontrado para este filtro.")
        else:
            st.error(f"Erro ao carregar da API: {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error(f"Erro de Conexão: Não foi possível conectar à API em {API_BASE_URL}. O servidor FastAPI (Passo 6) está rodando?")
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu: {e}")

# --- Gráfico 2: DAU (Usuários Ativos) ---
st.header("Usuários Ativos por Dia (DAU)")

if st.button("Carregar DAU"):
    try:
        # Chama o endpoint /bi/dau da sua API
        response = requests.get(f"{API_BASE_URL}/bi/dau")
        
        if response.status_code == 200:
            data = response.json()
            if data["values"]:
                st.line_chart({"DAU": data["values"]}, use_container_width=True)
                st.dataframe(data)
            else:
                st.warning("Nenhum dado de DAU encontrado.")
        else:
            st.error(f"Erro ao carregar da API: {response.text}")

    except requests.exceptions.ConnectionError:
        st.error(f"Erro de Conexão: Não foi possível conectar à API em {API_BASE_URL}. O servidor FastAPI (Passo 6) está rodando?")
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu: {e}")
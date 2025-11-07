# dashboard/pages/2_💰_Dashboard_Executivo.py
import streamlit as st
import requests

# -- Configuração da Página --
# Isso define o título que aparece na aba do navegador
st.set_page_config(
    page_title="Dashboard Executivo",
    page_icon="💰",
    layout="wide"
)

# --- Conexão com a API (FastAPI) ---
API_BASE_URL = "http://127.0.0.1:8000"

st.title("BI MVP - Dashboard Executivo 💰")

# --- Barra Lateral (Inputs) ---
st.sidebar.header("Filtros")
partner_id = st.sidebar.text_input("ID do Parceiro (Opcional)", help="Insira um ID numérico, ex: 1")

# --- Gráfico 1: Faturamento (Revenue) ---
st.header("Faturamento por Dia (R$)")

if st.button("Carregar Faturamento"):
    params = {}
    if partner_id:
        try:
            params["partner_id"] = int(partner_id)
        except ValueError:
            st.error("Por favor, insira um ID de parceiro numérico.")
    
    try:
        # Chama o NOVO endpoint /bi/revenue
        response = requests.get(f"{API_BASE_URL}/bi/revenue", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["values"]:
                st.line_chart({"Faturamento (R$)": data["values"]}, use_container_width=True)
                st.dataframe(data)
            else:
                st.warning("Nenhum dado de faturamento encontrado para este filtro.")
        else:
            st.error(f"Erro ao carregar da API: {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error(f"Erro de Conexão: Não foi possível conectar à API em {API_BASE_URL}. O servidor FastAPI está rodando?")
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu: {e}")

# --- Gráfico 2: Reservas (Reservations) ---
st.header("Reservas por Dia")

if st.button("Carregar Reservas"):
    params = {}
    if partner_id:
        try:
            params["partner_id"] = int(partner_id)
        except ValueError:
            st.error("Por favor, insira um ID de parceiro numérico.")

    try:
        # Chama o NOVO endpoint /bi/reservations
        response = requests.get(f"{API_BASE_URL}/bi/reservations", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["values"]:
                st.line_chart({"Reservas": data["values"]}, use_container_width=True)
                st.dataframe(data)
            else:
                st.warning("Nenhum dado de reservas encontrado para este filtro.")
        else:
            st.error(f"Erro ao carregar da API: {response.text}")

    except requests.exceptions.ConnectionError:
        st.error(f"Erro de Conexão: Não foi possível conectar à API em {API_BASE_URL}. O servidor FastAPI está rodando?")
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu: {e}")
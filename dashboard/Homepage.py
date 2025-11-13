# Homepage.py
import streamlit as st

st.set_page_config(
    page_title="Dashboard BI - Homepage",
    page_icon="🏠",
    layout="wide"
)

st.title("Central de Dashboards BI 📊")
st.sidebar.success("Selecione um dashboard acima.")

st.markdown(
    """
    ### Bem-vindo à plataforma de Business Intelligence.

    Este é o projeto de BI para demonstrar a análise de dados e KPIs 
    da plataforma.

    **Use o menu na barra lateral à esquerda para navegar entre as 
    diferentes visões (Personas):**

    1.  **Visão Parceiro:**
        * Análise de receita, reservas e ocupação para um Parceiro específico.

    2.  **Visão Cliente B2B:**
        * Análise de engajamento, adesão e custo por colaborador para clientes corporativos.

    3.  **Visão Usuário Final:**
        * Análise de atividade e gamificação para um usuário individual.

    ---

    **Como usar:**
    1.  Certifique-se de que o **Backend (API FastAPI)** esteja rodando.
        * (No terminal, rode: `uvicorn main:app --reload`)
    2.  Selecione uma das páginas no menu ao lado.

    """
)
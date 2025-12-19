# Homepage.py
import streamlit as st

st.set_page_config(
    page_title="GymGo Intelligence",
    page_icon="💪",
    layout="wide"
)

# Cabeçalho Principal
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>GymGo Intelligence 💪</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Plataforma Central de Analytics & Business Intelligence</h3>", unsafe_allow_html=True)

st.divider()

# Bloco de Explicação
st.markdown("""
Bem-vindo ao **MVP de BI da GymGo**. Esta aplicação centraliza dados de **milhares de interações**, 
transações financeiras e métricas de saúde para fornecer insights acionáveis para todas as pontas do ecossistema.
""")

st.write("") # Espaçamento

# Cards de Navegação (Layout em Colunas)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🏢 Parceiros")
    st.info("Para Academias e Personal Trainers.")
    st.markdown("""
    * Analise Receita Diária
    * Controle de Check-ins
    * Raio-X dos Alunos
    * Métricas de Ocupação
    """)

with col2:
    st.markdown("### 💼 Clientes B2B")
    st.success("Para Empresas Contratantes.")
    st.markdown("""
    * ROI Corporativo
    * Engajamento dos Times
    * Custo por Vida Ativa
    * Auditoria de Colaboradores
    """)

with col3:
    st.markdown("### 🏃 Usuário Final")
    st.warning("Para o Aluno/Atleta.")
    st.markdown("""
    * Passaporte de Saúde
    * Histórico de Treinos
    * Gamificação & Badges
    * Análise de Consistência
    """)

with col4:
    st.markdown("### 🔑 Admin/Interno")
    st.error("Para Gestão da Plataforma.")
    st.markdown("""
    * LTV & CAC
    * Funil de Conversão
    * Receita por Região
    * **Ferramenta de Auditoria**
    """)

st.divider()

# Rodapé Técnico
with st.expander("🛠️ Status do Sistema & Arquitetura"):
    st.markdown("""
    * **Backend:** FastAPI (Python) rodando em `127.0.0.1:8000`
    * **Database:** PostgreSQL (Schema Unificado)
    * **Dados:** Gerador Sintético v2.0 (Faker + Logica de Negócio)
    * **Front:** Streamlit Single-Page App
    """)
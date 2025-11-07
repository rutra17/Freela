# Projeto BI MVP - Dashboard Operacional e Executivo

Este projeto é um MVP (Minimum Viable Product) de uma plataforma de Business Intelligence. Ele consiste em um backend (API) construído com FastAPI que lê dados de um banco PostgreSQL e um frontend (Dashboard) construído com Streamlit para visualização.

O projeto também inclui scripts para "povoar" o banco de dados com dados falsos (`generate_fake_data.py`) para fins de demonstração.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, FastAPI
* **Frontend:** Streamlit
* **Banco de Dados:** PostgreSQL
* **Conexão com BD:** SQLAlchemy
* **Geração de Dados:** Faker
* **Ambiente:** .venv (Gerenciamento de pacotes via `requirements.txt`)

---

## 🚀 Como Rodar o Projeto

Siga este guia passo a passo para configurar e executar o projeto em sua máquina local.

### Pré-requisitos

* [Git](https://git-scm.com/downloads)
* [Python](https://www.python.org/downloads/) (Este projeto foi desenvolvido com a versão 3.11)
* [PostgreSQL](https://www.postgresql.org/download/) (Um servidor de banco de dados rodando localmente)
* (Opcional) [pgAdmin](https://www.pgadmin.org/download/) para gerenciar seu banco de dados visualmente.

---

### ⚙️ Instruções de Instalação

#### 1. Clonar o Repositório (O Código)

Primeiro, obtenha o código-fonte do GitHub:

```bash
git clone [https://github.com/rutra17/Freela.git](https://github.com/rutra17/Freela.git)
cd Freela
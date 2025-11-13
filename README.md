# BI MVP Project - Operational & Executive Dashboard 📊

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🧠 Overview

This repository contains a **Minimum Viable Product (MVP)** for a **Business Intelligence Platform**.  
The system is composed of:

- **Backend**: REST API built with **FastAPI** that consumes data from **PostgreSQL**.
- **Frontend**: Interactive **Streamlit** dashboard for data visualization.
- **Data Generation**: Script to populate the database with synthetic data (`generate_fake_data.py`).

---

## 🛠️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend** | FastAPI, Python |
| **Frontend** | Streamlit |
| **Database** | PostgreSQL |
| **ORM / Driver** | SQLAlchemy, Psycopg2 |
| **Data Generator** | Faker |
| **Visualization** | Plotly |
| **Environment** | `.venv` + `requirements.txt` |

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have the following installed:

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- (Optional) [pgAdmin](https://www.pgadmin.org/) for visual DB management

### 2. Clone the Repository

```bash
git clone https://github.com/rutra17/FREELA.git
cd FREELA
```

### 3. Create a PostgreSQL Database

Use `psql` or pgAdmin to create an empty database:

```sql
CREATE DATABASE mydb;
```

### 4. Environment Variables

Create a `.env` file in the project root:

```ini
# .env
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/mydb
```

> ⚠️ This file must **NOT** be committed to GitHub.

### 5. Virtual Environment Setup

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧩 Database Setup

Run the SQL scripts in the following order to create all schemas and tables:

1. `consumer_db.sql` — Creates the `consumers` schema
2. `providers.sql` — Creates the `providers` schema
3. `companies.sql` — Creates the `companies` schema
4. `communities.sql` — Creates the `communities` schema
5. `policies.sql` — Creates the `policies` schema
6. `analytics.sql` — Creates the `analytics` schema
7. `gamification_b2b.sql` — Adds tables to `consumers` and `companies`
8. `scores.sql` — Adds `user_mev_score` table to `consumers`

> 💡 Tip: Execute each `.sql` file via pgAdmin’s Query Tool or `psql`.

---

## ▶️ Running the Application

You’ll need **three terminals** open:

### Terminal 1 — Populate the Database

```bash
python generate_fake_data.py
```

Wait until you see messages like *“Populating 100 records...”* and *“Database populated successfully...”*.

### Terminal 2 — Run the Backend (FastAPI)

```bash
uvicorn main:app --reload
```

The API should be available at:
```
http://127.0.0.1:8000
```

### Terminal 3 — Run the Frontend (Streamlit)

```bash
streamlit run Homepage.py
```

---

## 🌐 Accessing the Dashboard

Once Streamlit launches, it should automatically open in your browser.  
If not, navigate manually to:

```
http://localhost:8501
```

---

## 📁 Project Structure

```
FREELA/
│
├── .venv/                   # Virtual environment (ignored)
├── backend/                 # Optional backend folder
├── dashboard/               # Optional Streamlit folder
├── etl/                     # ETL scripts
│
├── .env                     # Environment variables (ignored)
├── .gitignore               # Git ignore file
├── Homepage.py              # Main Streamlit app
├── 1_Visao_Parceiro.py      # Dashboard page 1
├── 2_Visao_B2B.py           # Dashboard page 2
├── 3_Visao_Usuario_Final.py # Dashboard page 3
├── 4_Visao_Interna.py       # Dashboard page 4
│
├── main.py                  # FastAPI main app
├── generate_fake_data.py    # Database population script
│
├── requirements.txt         # Dependencies
├── README.md                # This file
│
└── *.sql                    # SQL schema creation scripts
```

---

## 💡 Best Practices

- Never commit `.env` or sensitive credentials.
- Keep `requirements.txt` updated after installing new dependencies.
- If you encounter `relation already exists` errors, modify SQL scripts to include `IF NOT EXISTS`.
- Use virtual environments for dependency isolation.

---

## 🧾 License

### MIT License

```
Copyright (c) 2025 Artur Tabosa Rodrigues Reis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

> 🧩 Developed by **Artur Tabosa Rodrigues Reis** — 2025
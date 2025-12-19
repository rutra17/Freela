# 📊 GymGo - Business Intelligence Platform (MVP)

![Project Status](https://img.shields.io/badge/Status-MVP%20Complete-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal)

## 🧠 Overview

This repository contains a **Minimum Viable Product (MVP)** for a **Business Intelligence Platform** focused on the fitness industry (Gyms & Corporate Wellness). The system simulates a real-world environment with distinct company cultures, user behaviors, and financial transactions.

**The system is composed of:**

* **Backend:** REST API built with **FastAPI** & **SQLAlchemy**.
* **Frontend:** Interactive **Streamlit** dashboards for different personas (B2B Clients, Partners, End-Users).
* **Data Engine:** Sophisticated Python scripts (`Faker`) to populate the **PostgreSQL** database with realistic, diverse, and interconnected data (Simulating retention, churn, and gamification).

---

## 🛠️ Tech Stack

| Layer              | Technology                        |
| :----------------- | :-------------------------------- |
| **Backend**        | Python, FastAPI, Pydantic         |
| **Frontend**       | Streamlit, Plotly Express, Pandas |
| **Database**       | PostgreSQL                        |
| **ORM / Driver**   | SQLAlchemy, Psycopg2              |
| **ETL / Data Gen** | Faker, Python Scripts             |
| **Environment**    | Dotenv, Venv                      |

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have the following installed:

* Git
* Python 3.10+
* PostgreSQL (Local or Cloud)
* (Optional) VS Code (Recommended)

### 2. Clone the Repository

```bash
git clone https://github.com/rutra17/FREELA.git
cd FREELA
```

### 3. Setup Environment Variables

Create a `.env` file in the project root:

```ini
# .env
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/gymgo_db
```

*⚠️ Note: Replace `YOUR_USER`, `YOUR_PASSWORD`, and `gymgo_db` with your local postgres credentials.*

### 4. Virtual Environment Setup

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧩 Database & Data Generation

Instead of running SQL files manually, use the automated scripts included in the project.

**Step 1: Create Schemas & Tables**
This script drops existing schemas and recreates the entire structure (Consumers, Providers, Companies, Analytics, etc.).

```bash
python reset_database.py
```

**Step 2: Populate with Synthetic Data**
This script generates users, companies with specific cultures, transactions, and gamification history.

```bash
python generate_fake_data.py
```

*Wait until you see the message: "Banco populado com sucesso!"*

---

## ▶️ Running the Application

You will need **two terminals** open (or run in background):

### Terminal 1 — Backend (API)

```bash
uvicorn backend.main:app --reload
```

*Access API Docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### Terminal 2 — Frontend (Dashboards)

```bash
streamlit run dashboard/Homepage.py
```

*The dashboard will open automatically at: [http://localhost:8501](http://localhost:8501)*

---

## 📂 Project Structure

```text
FREELA/
│
├── backend/                 # API Logic
│   └── main.py              # FastAPI Entry point
│
├── dashboard/               # Frontend Application
│   ├── Homepage.py          # Main Streamlit Navigation
│   └── pages/
│       ├── 1_Visao_Parceiro.py      # Gym/Partner KPIs
│       ├── 2_Visao_B2B.py           # Corporate Clients (ROI & Health)
│       ├── 3_Visao_Usuario_Final.py # User Gamification & Stats
│       └── 4_Visao_Interna.py       # Admin/Internal View
│
├── database/                # SQL Schemas
│   ├── analytics.sql
│   ├── companies.sql
│   ├── consumer_db.sql
│   ├── ... (other schemas)
│
├── generate_fake_data.py    # Main Data Generator (The "Brain")
├── reset_database.py        # Database Reset Automation
├── requirements.txt         # Project Dependencies
├── .env                     # Credentials (Not tracked by Git)
└── README.md                # Project Documentation
```

---

## 💡 Key Features

* **B2B Dashboard:** Calculates the "Fitness Factor" of companies, showing ROI based on employee health improvements and engagement.
* **Gamification Engine:** Tracks user streaks, "Morning Person" habits, and social workouts to generate badges and rewards.
* **Financial Analytics:** Tracks LTV (Lifetime Value), CAC (Customer Acquisition Cost), and Revenue by Region (Zip Code).
* **Diverse Data Simulation:** The data generator creates "Gym Goers" vs "Sedentary" profiles to ensure realistic graphs, avoiding flat 100% metrics.

---

## 🧾 License

**MIT License**

Copyright (c) 2025 **Artur Tabosa Rodrigues Reis**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

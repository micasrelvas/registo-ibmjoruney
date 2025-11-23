import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials
import time

# --- Configuração da página ---
st.set_page_config(page_title="IBM Journey powered by Timestamp - Open Day", layout="wide")

# --- ALERTA DE HIBERNAÇÃO ---
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="text-align:center; padding:50px;">
        <h2>⚡ A app está a acordar...</h2>
        <p> Pode demorar alguns segundos. Obrigada pela paciência!</p>
        <p>⏳ Por favor, aguarde enquanto carregamos os dados das inscrições.</p>
    </div>
    """, unsafe_allow_html=True)
time.sleep(2)
loading_placeholder.empty()

# --- CSS personalizado ---
st.markdown("""
<style>
.stApp { background-color: #00274c; color: #ffffff; font-family: 'Arial', sans-serif; }
h1,h2,h3 { color: #00bfff; text-align:center; }
.stButton>button { background-color: #00bfff; color: #ffffff; font-weight: bold; }
.stDataFrame th { background-color: #1f1f1f; color: #ffffff; }
.stDataFrame td { background-color: #2c2c2c; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# --- Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

def carregar_registos():
    data = sheet.get_all_records()
    if len(data) == 0:
        return []
    return data

def guardar_registo(nome, apelido, email, equipa, datahora):
    sheet.append_row([nome, apelido, email, equipa, datahora])

def apagar_registo(email):
    registos = sheet.get_all_records()
    for i, reg in enumerate(registos, start=2):
        if reg["Email"] == email:
            sheet.delete_rows(i)
            return reg
    return None

def enviar_email(destinatario, assunto, mensagem):
    EMAIL_REMETENTE = st.secrets["EMAIL_REMETENTE"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
            server.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
    except Exception as e:
        st.warning(f"Não foi possível enviar email para {destinatario}: {e}")

# --- Informação do evento sempre visível ---
st.markdown("""
**Estás pronto para levar a tua experiência com Inteligência Artificial a outro nível?**

📅 **2 de dezembro | 🕙 10h – 17h30 | 📍 Edifício Lumnia (junto à Gare do Oriente)**

Junta-te a nós para um dia exclusivo nos escritórios da IBM, onde vais descobrir o futuro do AI e pôr mãos à obra!
""", unsafe_allow_html=True)

# --- Tabs ---
tabs = ["About IBM", "OpenDay Enroll", "Challenge", "Requirements Checklist", 
        "Judging Criteria", "Technology", "OpenDay Unenroll"]
selected_tab = st.radio("📌 Navegação", tabs, horizontal=True)

# -------------------------------
# 1) About IBM
# -------------------------------
if selected_tab == "About IBM":
    st.markdown("""
    **IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing. IBM's cutting-edge technology and research continue to drive advancements in multiple sectors:**

    • **AI and Machine Learning** – Leading the charge in AI development with powerful tools and models.  
    • **Cloud Solutions** – Providing scalable and flexible cloud services.  
    • **Quantum Computing** – Pushing the boundaries of computing with revolutionary quantum technologies.  
    • **Research and Development** – Continuously advancing technology with extensive research and high-quality datasets.  
    • **Open-Source Commitment** – Promoting collaboration and innovation through major open-source contributions.
    """, unsafe_allow_html=True)

# -------------------------------
# 2) OpenDay Enroll
# -------------------------------
elif selected_tab == "OpenDay Enroll":
    with st.expander("📝 Inscrição no Open Day - 2 de dezembro", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("👤 Nome")
            apelido = st.text_input("👤 Apelido")
        with col2:
            email = st.text_input("📧 Email")
            equipa = st.text_input("👥 Nome da Equipa")
        if equipa:
            equipa = equipa.strip().lower().replace("  "," ").title()
        if st.button("✅ Confirmar Inscrição"):
            if not all([nome, apelido, email, equipa]):
                st.warning("Todos os campos são obrigatórios.")
            else:
                df = carregar_registos()
                count_equipa = sum(1 for r in df if r["Nome da Equipa"].strip().lower() == equipa.lower())
                if count_equipa >= 2:
                    st.error(f"⚠️ A equipa '{equipa}' já atingiu o limite de 2 alunos.")
                elif email in [r["Email"] for r in df]:
                    st.warning(f"⚠️ {nome}, o teu email já está registado.")
                else:
                    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    guardar_registo(nome, apelido, email, equipa, datahora)
                    st.success(f"{nome}, o teu registo está confirmado!")
                    assunto = "Confirmação de inscrição no IBM Journey | 02/12"
                    mensagem = f"""Olá {nome},

O teu registo foi confirmado!

Nome da Equipa: {equipa}

Se quiseres cancelar a tua inscrição, acede a este link: {st.secrets['APP_URL']}
"""
                    enviar_email(email, assunto, mensagem)

# -------------------------------
# 3) Challenge
# -------------------------------
elif selected_tab == "Challenge":
    st.markdown("""
    # 🏁 The Challenge
    **Your challenge:** Design an AI agent powered by IBM watsonx Orchestrate that helps people and businesses achieve more with less effort.

    ### What’s Expected?
    - **Ideate with watsonx Orchestrate:** Design a solution concept with orchestration features, integrations, and digital skills.  
    - **Focus on Real-World Impact:** Address challenges in HR, sales, customer service, finance, or procurement.  
    - **Innovate for the Future of Work:** Enhance human potential and productivity.  
    - **Reference IBM Technology:** Explain how watsonx Orchestrate’s features, skills, integrations, or workflows would be leveraged.

    ### Inspiration & Use Cases
    - **Customer Service:** Faster responses, automate ticket handling.  
    - **Finance:** Streamline approvals, reporting, risk analysis.  
    - **HR:** Simplify onboarding, manage requests.  
    - **Procurement:** Automate supplier management, purchase orders, cycles.  
    - **Sales:** Support CRM updates, scheduling, lead follow-up.
    """, unsafe_allow_html=True)

# -------------------------------
# 4) Requirements Checklist
# -------------------------------
elif selected_tab == "Requirements Checklist":
    st.markdown("""
    # 📋 Requirements Checklist

    ### 1 — Enroll in the tab "OpenDay Enrollment"
    Complete your registration to participate.

    ### 2 — Create your IBM ID
    You must have an IBMid to access your IBM Cloud services.  
    Create your IBMid using the same email address used to register.
    👉 [Create your IBMid (3 min, free)](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776&target=https%3A%2F%2Flogin.ibm.com%2Foidc%2Fendpoint%2Fdefault%2Fauthorize%3FqsId%3Dd3536a32-17e1-4fcc-81df-f6df78fc6467%26client_id%3Dv18LoginProdCI)

    ### 3 — Request Your Cloud Account
    Follow the "Request your hackathon IBM Cloud account" instructions in the workshop guide. Includes:
    - watsonx Orchestrate  
    - Optional: watsonx.ai, NLU, Speech-to-Text, others  
    🔹 Access enabled at workshop start.  
    🔹 Some services support Orchestrate built-in functionality.
    """, unsafe_allow_html=True)

# -------------------------------
# 5) Judging Criteria
# -------------------------------
elif selected_tab == "Judging Criteria":
    st.markdown("""
    # 🏆 Judging Criteria

    **1️⃣ Application of Technology**  
    How effectively the chosen model(s) are integrated into the solution.

    **2️⃣ Presentation**  
    The clarity and effectiveness of the project presentation.

    **3️⃣ Business Value**  
    The impact and practical value, considering how well it fits into business areas.

    **4️⃣ Originality**  
    The uniqueness & creativity of the solution, highlighting approaches and ability to demonstrate behaviors.
    """, unsafe_allow_html=True)

# -------------------------------
# 6) Technology
# -------------------------------
elif selected_tab == "Technology":
    st.markdown("""
    # 🧩 Technology
    ### Explore Before the Hackathon
    Familiarize yourself with **watsonx Orchestrate**:

    - [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
    - [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
    - [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
    - [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
    """, unsafe_allow_html=True)

# -------------------------------
# 7) OpenDay Unenroll
# -------------------------------
elif selected_tab == "OpenDay Unenroll":
    with st.expander("❌ Cancelamento de Inscrição"):
        email_cancel = st.text_input("📧 Email para cancelar inscrição")
        if st.button("Cancelar Inscrição"):
            if not email_cancel:
                st.warning("O campo Email é obrigatório.")
            else:
                registro = apagar_registo(email_cancel)
                if registro is None:
                    st.info(f"⚠️ Não encontrei nenhum registo com este email.") 
                else:
                    st.info(f"🛑 A tua inscrição foi cancelada!")
                    assunto = "Cancelamento de inscrição no IBM Journey | 02/12"
                    mensagem = f"""Olá {registro['Nome']},

A tua inscrição foi cancelada.

Nome da Equipa: {registro['Nome da Equipa']}

Se quiseres voltar a inscrever-te, acede a este link: {st.secrets['APP_URL']}
"""
                    enviar_email(email_cancel, assunto, mensagem)


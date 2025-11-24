import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials
import time

# --- Configuração da página ---
st.set_page_config(page_title="🚀 IBM Journey powered by Timestamp - Open Day", layout="wide")

st.markdown("""
<style>
/* Fundo geral da app */
.stApp {
    background-color: #cce6ff;  /* azul claro */
    color: black;
    font-family: 'Arial', sans-serif;
}

/* Títulos da app */
h1, h2, h3 {
    color: #003366;  /* azul escuro */
    text-align: center;
    background-color: #cce6ff;
    padding: 10px;
    border-radius: 8px;
}

/* Botões */
.stButton>button {
    background-color: #0059b3;  /* azul médio */
    color: white;
    font-weight: bold;
}

/* DataFrames */
.stDataFrame th { background-color: #e6f2ff; color: black; }
.stDataFrame td { background-color: #ffffff; color: black; }
/* Expander fechado */
[data-baseweb="expander"] > div > div:first-child {
    background-color: #00274c !important; /* azul escuro IBM */
    color: white !important;               /* texto branco */
    font-weight: bold;
}

/* Expander aberto */
[data-baseweb="expander"][open] > div > div:first-child {
    background-color: #99ccff !important; /* azul claro */
    color: #003366 !important;            /* texto azul escuro */
    font-weight: bold;
}

/* Hover sobre cabeçalho (qualquer estado) */
[data-baseweb="expander"] > div > div:first-child:hover {
    background-color: #3399ff !important; 
    color: black !important;
}



/* Campos de input */
div.stTextInput>div>div>input {
    background-color: white !important;
    color: black !important;
}

/* Labels dos inputs */
div.stTextInput>label {
    color: black !important;
    font-weight: normal;
}
</style>
""", unsafe_allow_html=True)


# --- ALERTA DE HIBERNAÇÃO ---
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="text-align:center; padding:50px;">
        <h2>⚡ The app is waking up...</h2>
        <p>It may take a few seconds. Thank you for your patience!</p>
        <p>⏳ Please wait while we load the data.</p>
    </div>
    """, unsafe_allow_html=True)
time.sleep(2)
loading_placeholder.empty()

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

# --- Nome da App ---
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - December 2nd | Edifício Lumnia</p>", unsafe_allow_html=True)

# --- Informação do evento sempre visível ---
st.markdown("""
**Are you ready to take your experience with Artificial Intelligence to the next level?**

📅 **December 2nd | 🕙 10h – 17h30 | 📍 Edifício Lumnia (next to Gare do Oriente station)**

Join us for an exclusive day at IBM's offices, where you'll discover the future of AI and get hands-on experience!
""", unsafe_allow_html=True)

# -------------------------------
# 1️⃣ About IBM
# -------------------------------
with st.expander("1️⃣ About IBM", expanded=True):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing. IBM's cutting-edge technology and research continue to drive advancements in multiple sectors:

• **AI and Machine Learning** – Leading the charge in AI development with powerful tools and models.  
• **Cloud Solutions** – Providing scalable and flexible cloud services.  
• **Quantum Computing** – Pushing the boundaries of computing with revolutionary quantum technologies.  
• **Research and Development** – Continuously advancing technology with extensive research and high-quality datasets.  
• **Open-Source Commitment** – Promoting collaboration and innovation through major open-source contributions.
""", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ OpenDay Enroll
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Name")
        apelido = st.text_input("👤 Surname")
    with col2:
        email = st.text_input("📧 Email")
        equipa = st.text_input("👥 Team's Name")
    if equipa:
        equipa = equipa.strip().lower().replace("  "," ").title()
    if st.button("✅ Confirm enrollment"):
        if not all([nome, apelido, email, equipa]):
            st.warning("All fields are required.")
        else:
            df = carregar_registos()
            count_equipa = sum(1 for r in df if r["Nome da Equipa"].strip().lower() == equipa.lower())
            if count_equipa >= 2:
                st.error(f"⚠️ The team '{equipa}' has already reached the limit of 2 students.")
            elif email in [r["Email"] for r in df]:
                st.warning(f"⚠️ {nome}, your email is already registered.")
            else:
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(nome, apelido, email, equipa, datahora)
                st.success(f"{nome}, your enrollment is confirmed!")
                assunto = "Confirmação de inscrição no IBM Journey | 02/12"
                mensagem = f"""Olá {nome},

O teu registo foi confirmado!

Nome da Equipa: {equipa}

Se quiseres cancelar a tua inscrição, acede a este link: {st.secrets['APP_URL']}
"""
                enviar_email(email, assunto, mensagem)

# -------------------------------
# 3️⃣ Challenge
# -------------------------------
with st.expander("3️⃣ Challenge", expanded=True):
    st.markdown("""
**The Challenge:** Design an AI agent powered by IBM watsonx Orchestrate that helps people and businesses achieve more with less effort.

**What’s Expected?**
- Ideate with watsonx Orchestrate: Design a solution concept with orchestration features, integrations, and digital skills.  
- Focus on Real-World Impact: Address challenges in HR, sales, customer service, finance, or procurement.  
- Innovate for the Future of Work: Enhance human potential and productivity.  
- Reference IBM Technology: Explain how watsonx Orchestrate’s features, skills, integrations, or workflows would be leveraged.

**Inspiration & Use Cases**
- [Customer Service](https://www.ibm.com/products/watsonx-orchestrate/ai-agent-for-customer-service): Faster responses, automate ticket handling.  
- [Finance](https://www.ibm.com/products/watsonx-orchestrate/ai-agent-for-finance): Streamline approvals, reporting, risk analysis.  
- [HR](https://www.ibm.com/products/watsonx-orchestrate/ai-agent-for-hr): Simplify onboarding, manage requests.  
- [Procurement](https://www.ibm.com/products/watsonx-orchestrate/ai-agent-for-procurement): Automate supplier management, purchase orders, cycles.  
- [Sales](https://www.ibm.com/products/watsonx-orchestrate/ai-agent-for-sales): Support CRM updates, scheduling, lead follow-up.
""", unsafe_allow_html=True)

# -------------------------------
# 4️⃣ Requirements Checklist
# -------------------------------
with st.expander("4️⃣ Requirements Checklist", expanded=True):
    st.markdown("""
✅ Enroll in the tab "OpenDay Enroll"  
✅ Create your IBM ID: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)  
✅ Request Your Cloud Account: Follow the workshop guide to set up watsonx Orchestrate and optional services.
""", unsafe_allow_html=True)

# -------------------------------
# 5️⃣ Judging Criteria
# -------------------------------
with st.expander("5️⃣ Judging Criteria", expanded=True):
    st.markdown("""
**👉 Application of Technology**: How effectively the chosen model(s) are integrated into the solution.  
**👉 Presentation**: The clarity and effectiveness of the project presentation.  
**👉 Business Value**: The impact and practical value.  
**👉 Originality**: The uniqueness & creativity of the solution.
""", unsafe_allow_html=True)

# -------------------------------
# 6️⃣ Technology
# -------------------------------
with st.expander("6️⃣ Technology", expanded=True):
    st.markdown("""
**Explore Before the OpenDay:** Familiarize with watsonx Orchestrate.

- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""", unsafe_allow_html=True)

# -------------------------------
# 7️⃣ OpenDay Unenroll
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll", expanded=True):
    email_cancel = st.text_input("📧 Email to unenroll")
    if st.button("OpenDay Unenroll"):
        if not email_cancel:
            st.warning("The Email field is required.")
        else:
            registro = apagar_registo(email_cancel)
            if registro is None:
                st.info(f"⚠️ No records found with this email address.") 
            else:
                st.info(f"🛑 Your enrollment has been canceled!")
                assunto = "Cancelamento de inscrição no IBM Journey | 02/12"
                mensagem = f"""Olá {registro['Nome']},

A tua inscrição foi cancelada.

Nome da Equipa: {registro['Nome da Equipa']}

Se quiseres voltar a inscrever-te, acede a este link: {st.secrets['APP_URL']}
"""
                enviar_email(email_cancel, assunto, mensagem)


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
/* Fonte IBM Plex Sans */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

/* Fundo geral da app */
.stApp {
    background-color: #cce6ff;  /* azul claro */
    color: black;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Títulos da app */
h1, h2, h3 {
    color: #003366;  /* azul escuro */
    text-align: center;
    background-color: #cce6ff;
    padding: 10px;
    border-radius: 8px;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Botões */
.stButton>button {
    background-color: #0059b3;  /* azul médio */
    color: white;
    font-weight: bold;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* DataFrames */
.stDataFrame th { background-color: #e6f2ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame td { background-color: #ffffff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }

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
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Labels dos inputs */
div.stTextInput>label {
    color: black !important;
    font-weight: normal;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
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

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

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
with st.expander("1️⃣ About IBM", expanded=False):
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
if st.session_state.update_clicked:
    # Apagar registro antigo
    apagar_registo(email)

    # Validar equipe se escolher Challenge
    if modo == "Attend Open Day + Participate in the Challenge":
        if not equipa:
            st.warning("Please enter a Team Name to join the Challenge.")
            st.stop()
        # Limite de 2 estudantes por equipe
        count_equipa = sum(
            1 for r in df if r["Nome da Equipa"].strip().lower() == equipa.lower()
        )
        if count_equipa >= 2:
            st.error(f"⚠️ The team '{equipa}' has already reached the limit of 2 students.")
            st.stop()
    else:
        equipa = "—"

    # Guardar novo registro
    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_registo(
        nome,
        apelido,
        email,
        "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
        equipa,
        datahora
    )

    # Variável com o modo atual
    novo_modo = "Open Day + Challenge" if modo == "Attend Open Day + Participate in the Challenge" else "Open Day only"

    # Mensagem de sucesso no app
    st.success(f"✅ Your registration has been successfully changed to '{novo_modo}' mode!")

    # E-mail automático
    assunto = "IBM Journey registration updated | 02/12"
    mensagem = f"""Olá {nome},

Your registration has been updated.

Current mode: {novo_modo}
Team Name: {equipa}

Thank you!
"""
    enviar_email(email, assunto, mensagem)


# -------------------------------
# 3️⃣ Challenge
# -------------------------------
with st.expander("3️⃣ Challenge", expanded=False):
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
with st.expander("4️⃣ Requirements Checklist", expanded=False):
    st.markdown("""
✅ Enroll in the tab "OpenDay Enroll"  
✅ Create your IBM ID: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)  
""", unsafe_allow_html=True)
#✅ Request Your Cloud Account: Follow the workshop guide to set up watsonx Orchestrate and optional services.

# -------------------------------
# 5️⃣ Judging Criteria
# -------------------------------
with st.expander("5️⃣ Judging Criteria", expanded=False):
    st.markdown("""
**👉 Application of Technology**: How effectively the chosen model(s) are integrated into the solution.  
**👉 Presentation**: The clarity and effectiveness of the project presentation.  
**👉 Business Value**: The impact and practical value.  
**👉 Originality**: The uniqueness & creativity of the solution.
""", unsafe_allow_html=True)

# -------------------------------
# 6️⃣ Technology
# -------------------------------
with st.expander("6️⃣ Technology", expanded=False):
    st.markdown("""
**Explore Before the OpenDay:** Familiarize with watsonx Orchestrate.

- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""", unsafe_allow_html=True)

# -------------------------------
# 7️⃣ OpenDay Unenroll / Update
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll / Update Mode", expanded=False):
    email_cancel = st.text_input("📧 Enter your email to cancel or update registration")

    if st.button("Search Registration"):
        if not email_cancel:
            st.warning("The Email field is required.")
        else:
            # Buscar registro
            registos = carregar_registos()
            registro = next((r for r in registos if r["Email"].strip().lower() == email_cancel.strip().lower()), None)
            
            if registro is None:
                st.info(f"⚠️ No registration found with this email.")
            else:
                modo_atual = "Open Day + Challenge" if registro["Participa Challenge"].strip().lower() == "sim" else "Open Day only"
                st.success(f"✅ Registration found! Current mode: {modo_atual}")

                # Opções
                opcao = st.radio("Choose an action:", ["Cancel registration", "Update mode"])

                if opcao == "Cancel registration":
                    if st.button("Confirm Cancellation"):
                        apagar_registo(email_cancel)
                        st.info("🛑 Your registration has been canceled!")
                        assunto = "Cancellation of IBM Journey registration | 02/12"
                        mensagem = f"""Olá {registro['Nome']},

Your registration has been canceled.

Previous mode: {modo_atual}

If you wish to register again, please use the enrollment form: {st.secrets['APP_URL']}
"""
                        enviar_email(email_cancel, assunto, mensagem)

                elif opcao == "Update mode":
                    novo_modo = st.radio("Select new mode:", ["Open Day only", "Open Day + Challenge"])
                    
                    if st.button("Confirm Mode Update"):
                        if novo_modo == modo_atual:
                            st.info("⚠️ The selected mode is the same as current mode. No changes made.")
                        else:
                            # Atualizar registro no Sheet
                            for i, r in enumerate(registos, start=2):
                                if r["Email"].strip().lower() == email_cancel.strip().lower():
                                    # Atualizar "Participa Challenge" e "Nome da Equipa" se necessário
                                    if novo_modo == "Open Day only":
                                        sheet.update(f"D{i}", "Não")      # Coluna "Participa Challenge"
                                        sheet.update(f"E{i}", "—")        # Coluna "Nome da Equipa"
                                    else:
                                        sheet.update(f"D{i}", "Sim")      # Coluna "Participa Challenge"
                                        # Se quiseres, pode pedir para atualizar "Nome da Equipa" aqui
                                    break
                            
                            st.success(f"✅ Your registration has been successfully changed to '{novo_modo}' mode!")
                            assunto = "IBM Journey Registration Mode Updated | 02/12"
                            mensagem = f"""Olá {registro['Nome']},

Your registration has been updated.

Previous mode: {modo_atual}
New mode: {novo_modo}

If you wish to make further changes, please use the enrollment form: {st.secrets['APP_URL']}
"""
                            enviar_email(email_cancel, assunto, mensagem)


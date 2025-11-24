import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials
import time

# --- Configuração da página ---
st.set_page_config(page_title="🚀 IBM Journey powered by Timestamp - Open Day", layout="wide")

# --- Inicializar session_state ---
if "update_clicked" not in st.session_state:
    st.session_state.update_clicked = False
if "update_email" not in st.session_state:
    st.session_state.update_email = ""
if "update_nome" not in st.session_state:
    st.session_state.update_nome = ""
if "update_apelido" not in st.session_state:
    st.session_state.update_apelido = ""
if "update_equipe" not in st.session_state:
    st.session_state.update_equipe = ""

# --- Estilo CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

.stApp { background-color: #cce6ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
h1, h2, h3 { color: #003366; text-align: center; background-color: #cce6ff; padding: 10px; border-radius: 8px; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stButton>button { background-color: #0059b3; color: white; font-weight: bold; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame th { background-color: #e6f2ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame td { background-color: #ffffff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
[data-baseweb="expander"] > div > div:first-child { background-color: #00274c !important; color: white !important; font-weight: bold; }
[data-baseweb="expander"][open] > div > div:first-child { background-color: #99ccff !important; color: #003366 !important; font-weight: bold; }
[data-baseweb="expander"] > div > div:first-child:hover { background-color: #3399ff !important; color: black !important; }
div.stTextInput>div>div>input { background-color: white !important; color: black !important; font-family: 'IBM Plex Sans', Arial, sans-serif; }
div.stTextInput>label { color: black !important; font-weight: normal; font-family: 'IBM Plex Sans', Arial, sans-serif; }
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
    return data if data else []

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

def apagar_registo(email):
    registos = sheet.get_all_records()
    for i, reg in enumerate(registos, start=2):
        if reg["Email"].strip().lower() == email.strip().lower():
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

# --- Cabeçalho ---
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - December 2nd | Edifício Lumnia</p>", unsafe_allow_html=True)

st.markdown("""
**Are you ready to take your experience with Artificial Intelligence to the next level?**

📅 **December 2nd | 🕙 10h – 17h30 | 📍 Edifício Lumnia**

Join us for an exclusive day at IBM's offices, where you'll discover the future of AI and get hands-on experience!
""", unsafe_allow_html=True)

# -------------------------------
# 1️⃣ About IBM
# -------------------------------
with st.expander("1️⃣ About IBM", expanded=False):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing.
""", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ OpenDay Enroll
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=False):
    st.markdown("### Choose your participation mode:")
    modo = st.radio(
        "Select one option:",
        ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"]
    )

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Name", key="enroll_nome")
        apelido = st.text_input("👤 Surname", key="enroll_apelido")
    with col2:
        email = st.text_input("📧 Email", key="enroll_email")

    equipa = ""
    if modo == "Attend Open Day + Participate in the Challenge":
        equipa = st.text_input("👥 Team Name (required for Challenge)", key="enroll_equipe")
        if equipa:
            equipa = equipa.strip().lower().replace("  "," ").title()

    if st.button("✅ Confirm enrollment"):
        if not all([nome, apelido, email]):
            st.warning("All fields except team name are required.")
        else:
            df = carregar_registos()
            registro_existente = next((r for r in df if r["Email"].strip().lower() == email.strip().lower()), None)

            if registro_existente:
                modo_atual = "Open Day + Challenge" if registro_existente["Participa Challenge"].strip().lower() == "sim" else "Open Day only"
                st.info(f"⚠️ Your email is already registered for '{modo_atual}' mode.")
                if st.confirm("Do you want to update to the new selected mode?"):
                    apagar_registo(email)
                    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    guardar_registo(
                        nome,
                        apelido,
                        email,
                        "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
                        equipa if modo == "Attend Open Day + Participate in the Challenge" else "—",
                        datahora
                    )
                    novo_modo = "Open Day + Challenge" if modo == "Attend Open Day + Participate in the Challenge" else "Open Day only"
                    st.success(f"✅ Your registration has been successfully changed to '{novo_modo}' mode!")
                    assunto = "IBM Journey registration updated | 02/12"
                    mensagem = f"""Olá {nome},

Your registration has been updated.

Previous mode: {modo_atual}
New mode: {novo_modo}
Team Name: {equipa if equipa else '—'}

Thank you!
"""
                    enviar_email(email, assunto, mensagem)
            else:
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    nome,
                    apelido,
                    email,
                    "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
                    equipa if modo == "Attend Open Day + Participate in the Challenge" else "—",
                    datahora
                )
                st.success(f"{nome}, your enrollment is confirmed!")
                assunto = "Confirmação de inscrição no IBM Journey | 02/12"
                mensagem = f"""Olá {nome},

Your registration has been confirmed!

Participation: {modo}
Team Name: {equipa if equipa else '—'}

If you wish to cancel or update your registration, use: {st.secrets['APP_URL']}
"""
                enviar_email(email, assunto, mensagem)

# -------------------------------
# 3️⃣ Challenge
# -------------------------------
with st.expander("3️⃣ Challenge", expanded=False):
    st.markdown("""
**The Challenge:** Design an AI agent powered by IBM watsonx Orchestrate.

**What’s Expected?**
- Ideate with watsonx Orchestrate  
- Focus on Real-World Impact  
- Innovate for the Future of Work  
- Reference IBM Technology
""", unsafe_allow_html=True)

# -------------------------------
# 4️⃣ Requirements Checklist
# -------------------------------
with st.expander("4️⃣ Requirements Checklist", expanded=False):
    st.markdown("""
✅ Enroll in "OpenDay Enroll"  
✅ Create your IBM ID: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)
""", unsafe_allow_html=True)

# -------------------------------
# 5️⃣ Judging Criteria
# -------------------------------
with st.expander("5️⃣ Judging Criteria", expanded=False):
    st.markdown("""
**👉 Application of Technology**  
**👉 Presentation**  
**👉 Business Value**  
**👉 Originality**
""", unsafe_allow_html=True)

# -------------------------------
# 6️⃣ Technology
# -------------------------------
with st.expander("6️⃣ Technology", expanded=False):
    st.markdown("""
- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""", unsafe_allow_html=True)

# -------------------------------
# 7️⃣ OpenDay Unenroll / Update Mode
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll / Update Mode", expanded=False):
    email_cancel = st.text_input("📧 Enter your email to cancel or update registration", key="unenroll_email")

    if st.button("Search Registration"):
        if not email_cancel:
            st.warning("The Email field is required.")
        else:
            registos = carregar_registos()
            registro = next((r for r in registos if r["Email"].strip().lower() == email_cancel.strip().lower()), None)

            if registro is None:
                st.info(f"⚠️ No registration found with this email.")
            else:
                modo_atual = "Open Day + Challenge" if registro["Participa Challenge"].strip().lower() == "sim" else "Open Day only"
                st.success(f"✅ Registration found! Current mode: {modo_atual}")

                opcao = st.radio("Choose an action:", ["Cancel registration", "Update mode"], key="unenroll_opcao")

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
                    novo_modo = st.radio("Select new mode:", ["Open Day only", "Open Day + Challenge"], key="unenroll_novo_modo")
                    if st.button("Confirm Mode Update"):
                        if novo_modo == modo_atual:
                            st.info("⚠️ The selected mode is the same as current mode. No changes made.")
                        else:
                            for i, r in enumerate(registos, start=2):
                                if r["Email"].strip().lower() == email_cancel.strip().lower():
                                    if novo_modo == "Open Day only":
                                        sheet.update(f"D{i}", "Não")
                                        sheet.update(f"E{i}", "—")
                                    else:
                                        sheet.update(f"D{i}", "Sim")
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

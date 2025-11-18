import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials

# --- Página ---
st.set_page_config(page_title="IBM Journey - Registo", layout="wide")

# --- CSS personalizado ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    h1, h2, h3 {
        color: #00bfff;
    }
    .stButton>button {
        background-color: #00bfff;
        color: #ffffff;
        font-weight: bold;
    }
    .stDataFrame th {
        background-color: #1f1f1f;
        color: #ffffff;
    }
    .stDataFrame td {
        background-color: #2c2c2c;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Título ---
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p>Aprende a criar agentes com a melhor tecnologia do mercado!</p>", unsafe_allow_html=True)

# -------------------------------------------------------
# 🔗 GOOGLE SHEETS: AUTENTICAÇÃO
# -------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["GOOGLE_SERVICE_ACCOUNT"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1


# --- Funções Google Sheets ---
def carregar_registos():
    data = sheet.get_all_records()
    if len(data) == 0:
        return pd.DataFrame(columns=["Nome", "Apelido", "Email", "Equipa", "DataHora"])
    return pd.DataFrame(data)


def guardar_registo(nome, apelido, email, equipa, datahora):
    sheet.append_row([nome, apelido, email, equipa, datahora])


def apagar_registo(email):
    registos = sheet.get_all_records()

    for i, reg in enumerate(registos, start=2):  # linha 1 = cabeçalho
        if reg["Email"] == email:
            sheet.delete_rows(i)
            return reg
    return None


# -------------------------------------------------------
# EMAIL
# -------------------------------------------------------
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


# -------------------------------------------------------
# ABOUT IBM
# -------------------------------------------------------
with st.expander("💡 About IBM", expanded=False):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades.  
Their contributions span across key fields such as AI, cloud computing, and quantum computing.

• **AI and Machine Learning**  
• **Cloud Solutions**  
• **Quantum Computing**  
• **Research and Development**  
• **Open-Source Leadership**
""")


# -------------------------------------------------------
# ABOUT TIMESTAMP
# -------------------------------------------------------
with st.expander("💡 About Timestamp", expanded=False):
    st.markdown("""
Timestamp provides innovative solutions and services in both national and international markets.  
The Group integrates several Portuguese-owned companies built around excellence and knowledge sharing.

They focus on technological leadership, certified quality, continuous training, and specialized teams.
""")


# -------------------------------------------------------
# TECHNOLOGY
# -------------------------------------------------------
with st.expander("⚙️ Technology", expanded=False):
    st.markdown("""
Explore watsonx Orchestrate and learn how AI agents automate real workflows.

### 📚 Resources
- Product Overview  
- Demo Experience  
- Integrations  
- Resources & Support
""")


# -------------------------------------------------------
# PRIZES
# -------------------------------------------------------
with st.expander("🏆 Prizes", expanded=False):
    st.markdown("### What you can win!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
🥇 **Winning Team Experience**  
A unique professional experience during the **last fortnight of June**.
""")

    with col2:
        st.markdown("""
🎖️ **Participation Rewards**  
Certificate of Participation + exclusive merchandising!
""")


# -------------------------------------------------------
# INSCRIÇÃO
# -------------------------------------------------------
with st.expander("📝 Inscrição no Open Day", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome")
        apelido = st.text_input("👤 Apelido")
    with col2:
        email = st.text_input("📧 Email")
        equipa = st.text_input("👥 Equipa")

    if st.button("✅ Confirmar Inscrição"):
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para registar a inscrição.")
        else:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_registo(nome, apelido, email, equipa, datahora)
            st.success(f"🤖 Confirmamos o registo no Open Day para {nome} {apelido}!")

            assunto = "Confirmação de inscrição no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi confirmado!

Equipa: {equipa}
Data/Hora: {datahora}
"""
            enviar_email(email, assunto, mensagem)


# -------------------------------------------------------
# CANCELAMENTO
# -------------------------------------------------------
with st.expander("❌ Cancelamento de Inscrição"):
    email_cancel = st.text_input("📧 Email para cancelar a inscrição")

    if st.button("Cancelar Presença"):
        if not email_cancel:
            st.warning("O campo Email é obrigatório para cancelar.")
        else:
            registro = apagar_registo(email_cancel)

            if registro is None:
                st.info(f"⚠️ Nenhum registo encontrado para {email_cancel}.")
            else:
                nome_c = registro["Nome"]
                equipa_c = registro["Equipa"]

                st.info(f"🛑 Inscrição cancelada para {email_cancel}")

                assunto = "Cancelamento de inscrição"
                mensagem = f"""Olá {nome_c},

A tua inscrição no Open Day foi cancelada.

Equipa: {equipa_c}
"""
                enviar_email(email_cancel, assunto, mensagem)


# -------------------------------------------------------
# DASHBOARD PROFESSOR
# -------------------------------------------------------
with st.expander("📊 Dashboard do Professor", expanded=True):
    df = carregar_registos()

    if not df.empty:
        st.markdown("### 🤖 Alunos inscritos")
        st.dataframe(df[["Nome", "Apelido", "Equipa", "DataHora"]])

        st.markdown("### 🚀 Número de alunos por equipa")
        count_equipa = df.groupby("Equipa")["Email"].count().reset_index()
        count_equipa.columns = ["Equipa", "Número de alunos"]
        st.bar_chart(count_equipa.set_index("Equipa"))
    else:
        st.info("Ainda não há inscrições.")

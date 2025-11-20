import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials

# --- Página ---
st.set_page_config(page_title="IBM Journey - Registo", layout="wide")

# --- CSS personalizado ---
st.markdown("""
<style>
.stApp { background-color: #0a0a0a; color: #ffffff; font-family: 'Arial', sans-serif; }
h1,h2,h3 { color: #00bfff; }
.stButton>button { background-color: #00bfff; color: #ffffff; font-weight: bold; }
.stDataFrame th { background-color: #1f1f1f; color: #ffffff; }
.stDataFrame td { background-color: #2c2c2c; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p>Aprende a criar agentes com a melhor tecnologia do mercado!</p>", unsafe_allow_html=True)

# -------------------------------------------------------
# GOOGLE SHEETS
# -------------------------------------------------------
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
# REGISTO
# -------------------------------------------------------
with st.expander("📝 Inscrição no Open Day - 2 de dezembro", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome")
        apelido = st.text_input("👤 Apelido")
    with col2:
        email = st.text_input("📧 Email")
        equipa = st.text_input("👥 Nome da Equipa")

    # --- Normalizar o nome da equipa ---
    if equipa:
        equipa = (
            equipa.strip()
                  .lower()
                  .replace("  ", " ")
                  .title()
        )

    if st.button("✅ Confirmar Inscrição"):
        # Validar campos obrigatórios
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios.")
        else:
            df = carregar_registos()
            
            # Limite máximo 2 alunos por equipa
            count_equipa = sum(1 for r in df if r["Equipa"].strip().lower() == equipa.lower())
            if count_equipa >= 2:
                st.error(f"⚠️ A equipa '{equipa}' já atingiu o limite de 2 alunos.")
            elif email in [r["Email"] for r in df]:
                st.warning(f"⚠️ O email {email} já está registado.")
            else:
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(nome, apelido, email, equipa, datahora)
                st.success(f"🤖 Registo confirmado para {nome} {apelido}!")

                # Enviar email de confirmação
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
    email_cancel = st.text_input("📧 Email para cancelar inscrição")

    if st.button("Cancelar Presença"):
        if not email_cancel:
            st.warning("O campo Email é obrigatório.")
        else:
            registro = apagar_registo(email_cancel)
            if registro is None:
                st.info(f"⚠️ Nenhum registo encontrado para {email_cancel}.")
            else:
                st.info(f"🛑 Inscrição cancelada para {email_cancel}")

                # Enviar email de cancelamento
                assunto = "Cancelamento de inscrição"
                mensagem = f"""Olá {registro['Nome']},

A tua inscrição no Open Day da IBM Journey Powered by Timestamp, no dia 2 de dezembro, foi cancelada.

Nome da Equipa: {registro['Equipa']}
"""
                enviar_email(email_cancel, assunto, mensagem)



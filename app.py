import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="IBM Journey - Registo", layout="centered")
st.title("Bem-vindo ao IBM Journey powered by Timestamp - Se queres aprender a fazer agentes de forma rápida e com a melhor tecnologia do mercado, inscreve-te")

# --- Dados temporários em memória ---
if "registos" not in st.session_state:
    st.session_state.registos = pd.DataFrame(columns=["Nome", "Apelido", "Email", "Equipa", "DataHora"])

# --- Função para enviar email ---
def enviar_email(destinatario, assunto, mensagem):
    """
    Esta função envia email. No Streamlit Cloud, os dados de login devem estar como Secrets.
    """
    # Substituir com os teus secrets
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

# --- Inputs do aluno ---
st.subheader("📝 Registo / Cancelamento de presença")
nome = st.text_input("👤 Nome")
apelido = st.text_input("👤 Apelido")
email = st.text_input("📧 Email")
equipa = st.text_input("👥 Equipa")

col1, col2 = st.columns(2)

# Confirmar presença
with col1:
    if st.button("✅ Confirmar Presença"):
        if nome and apelido and email and equipa:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [nome, apelido, email, equipa, datahora]
            st.success(f"Presença registada para {nome} {apelido}!")
            
            # Enviar email de confirmação
            assunto = "Confirmação de registo no IBM Journey"
            mensagem = f"Olá {nome},\n\nO teu registo no IBM Journey foi confirmado com sucesso!\n\nEquipa: {equipa}\nData/Hora: {datahora}"
            enviar_email(email, assunto, mensagem)
        else:
            st.warning("Preenche todos os campos!")

# Cancelar presença
with col2:
    if st.button("❌ Cancelar Presença"):
        mask = ~((st.session_state.registos["Email"] == email))
        st.session_state.registos = st.session_state.registos[mask]
        st.info(f"Registo cancelado para {email}")

        # Enviar email de cancelamento
        assunto = "Cancelamento

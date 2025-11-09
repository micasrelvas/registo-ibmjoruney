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

# --- Confirmar presença ---
with col1:
    if st.button("✅ Confirmar Presença"):
        # Verificar campos obrigatórios
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para registar a presença.")
        else:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [nome, apelido, email, equipa, datahora]
            st.success(f"Presença registada para {nome} {apelido}!")

            # Enviar email de confirmação
            assunto = "Confirmação de registo no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi confirmado com sucesso!

Equipa: {equipa}
Data/Hora: {datahora}
"""
            enviar_email(email, assunto, mensagem)

# --- Cancelar presença ---
with col2:
    if st.button("❌ Cancelar Presença"):
        # Verificar campos obrigatórios
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para cancelar a presença.")
        else:
            mask = ~(st.session_state.registos["Email"] == email)
            st.session_state.registos = st.session_state.registos[mask]
            st.info(f"Registo cancelado para {email}")

            # Enviar email de cancelamento
            assunto = "Cancelamento de registo no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi cancelado.

Equipa: {equipa}
"""
            enviar_email(email, assunto, mensagem)

# --- Mostrar tabela de registos ---
st.subheader("📋 Registos atuais (em memória)")
st.dataframe(st.session_state.registos)

# --- Dashboard do professor ---
st.subheader("📊 Dashboard do Professor")

if not st.session_state.registos.empty:
    st.write("**Alunos inscritos:**")
    # Mostrar tabela completa com Nome, Apelido, Equipa e Data/Hora
    st.dataframe(st.session_state.registos[["Nome", "Apelido", "Equipa", "DataHora"]])

    st.write("**Número de alunos por equipa:**")
    count_equipa = st.session_state.registos.groupby("Equipa")["Email"].count().reset_index()
    count_equipa.columns = ["Equipa", "Número de alunos"]
    st.table(count_equipa)

else:
    st.info("Ainda não há registos para mostrar no dashboard.")

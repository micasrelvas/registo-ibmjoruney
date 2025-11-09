import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# --- Página ---
st.set_page_config(page_title="IBM Journey - Registo", layout="wide")

# --- CSS personalizado ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stDataFrame th {
        background-color: #1f3c52;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Título ---
st.markdown("<h1 style='color:#00ffff;'>🚀 Bem-vindo ao IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#cccccc;'>Aprende a criar agentes com a melhor tecnologia do mercado!</p>", unsafe_allow_html=True)

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

# --- Inputs em expansores ---
with st.expander("📝 Registo de Presença", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome")
        apelido = st.text_input("👤 Apelido")
    with col2:
        email = st.text_input("📧 Email")
        equipa = st.text_input("👥 Equipa")
    
    if st.button("✅ Confirmar Presença"):
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para registar a presença.")
        else:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [nome, apelido, email, equipa, datahora]
            st.success(f"🤖 Presença registada para {nome} {apelido}!")
            
            # Enviar email de confirmação
            assunto = "Confirmação de registo no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi confirmado com sucesso!

Equipa: {equipa}
Data/Hora: {datahora}
"""
            enviar_email(email, assunto, mensagem)

with st.expander("❌ Cancelamento de Presença"):
    if st.button("Cancelar Presença"):
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para cancelar a presença.")
        else:
            mask = ~(st.session_state.registos["Email"] == email)
            st.session_state.registos = st.session_state.registos[mask]
            st.info(f"🛑 Registo cancelado para {email}")
            
            # Enviar email de cancelamento
            assunto = "Cancelamento de registo no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi cancelado.

Equipa: {equipa}
"""
            enviar_email(email, assunto, mensagem)

# --- Dashboard do professor ---
with st.expander("📊 Dashboard do Professor", expanded=True):
    if not st.session_state.registos.empty:
        st.markdown("### 🤖 Alunos inscritos")
        st.dataframe(st.session_state.registos[["Nome", "Apelido", "Equipa", "DataHora"]])

        st.markdown("### 🚀 Número de alunos por equipa")
        count_equipa = st.session_state.registos.groupby("Equipa")["Email"].count().reset_index()
        count_equipa.columns = ["Equipa", "Número de alunos"]
        st.bar_chart(count_equipa.set_index("Equipa"))
    else:
        st.info("Ainda não há registos para mostrar no dashboard.")

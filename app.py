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
    /* Fundo e cores principais */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    /* Cores dos títulos */
    h1, h2, h3 {
        color: #00bfff;
    }
    /* Botões */
    .stButton>button {
        background-color: #00bfff;
        color: #ffffff;
        font-weight: bold;
    }
    /* Tabela */
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

# --- Imagem de topo ---
st.image("https://images.unsplash.com/photo-1581091215365-9f3f07ff14df?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNjA3fDB8MHwxfHNlYXJjaHwxfHx0ZWNobm9sb2d5fGVufDB8fHx8MTY5OTM2MjgwMA&ixlib=rb-4.0.3&q=80&w=1080", use_column_width=True)

# --- Título ---
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p>Aprende a criar agentes com a melhor tecnologia do mercado!</p>", unsafe_allow_html=True)

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

# --- Cancelamento apenas com email ---
with st.expander("❌ Cancelamento de Presença"):
    email_cancel = st.text_input("📧 Email para cancelar registo")

    if st.button("Cancelar Presença"):
        if not email_cancel:
            st.warning("O campo Email é obrigatório para cancelar a presença.")
        else:
            registro = st.session_state.registos[st.session_state.registos["Email"] == email_cancel]
            if registro.empty:
                st.info(f"⚠️ Nenhum registo encontrado para {email_cancel}.")
            else:
                # Pega nome e equipa antes de remover
                nome_c = registro.iloc[0]["Nome"]
                equipa_c = registro.iloc[0]["Equipa"]

                # Remove o registo
                st.session_state.registos = st.session_state.registos[st.session_state.registos["Email"] != email_cancel]
                st.info(f"🛑 Registo cancelado para {email_cancel}")

                # Enviar email de cancelamento
                assunto = "Cancelamento de registo no IBM Journey"
                mensagem = f"""Olá {nome_c},

O teu registo no IBM Journey foi cancelado.

Equipa: {equipa_c}
"""
                enviar_email(email_cancel, assunto, mensagem)

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

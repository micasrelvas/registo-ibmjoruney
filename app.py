import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials
import time

# -------------------------
# Configuração da página
# -------------------------
st.set_page_config(page_title="🚀 IBM Journey powered by Timestamp - Open Day", layout="wide")

# -------------------------
# Inicializar session_state
# -------------------------
for key, val in {
    "update_clicked": False,
    "update_email": "",
    "update_nome": "",
    "update_apelido": "",
    "update_equipe": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------
# CSS / Fonte
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

/* Geral */
.stApp { background-color: #cce6ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; padding-top: 10px; }
h1, h2, h3 { color: #003366; text-align: center; background-color: #cce6ff; padding: 6px 12px; border-radius: 6px; margin: 6px 0; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stButton>button { background-color: #0059b3 !important; color: white !important; font-weight: 600; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame th { background-color: #e6f2ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame td { background-color: #ffffff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
[data-baseweb="expander"] > div > div:first-child { background-color: #00274c !important; color: white !important; font-weight: 600; border-radius: 6px; }
[data-baseweb="expander"][open] > div > div:first-child { background-color: #99ccff !important; color: #003366 !important; font-weight: 600; }
[data-baseweb="expander"] > div > div:first-child:hover { background-color: #3399ff !important; color: black !important; }
div.stTextInput>div>div>input, div.stTextArea>div>div>textarea { background-color: white !important; color: black !important; font-family: 'IBM Plex Sans', Arial, sans-serif; }
div.stTextInput>label, label { color: #003366 !important; font-weight: 600; font-family: 'IBM Plex Sans', Arial, sans-serif; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# ALERTA DE HIBERNAÇÃO
# -------------------------
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="text-align:center; padding:30px;">
        <h2>⚡ A app está a acordar...</h2>
        <p>Pode demorar alguns segundos. Obrigado pela paciência!</p>
    </div>
    """, unsafe_allow_html=True)
time.sleep(1.5)
loading_placeholder.empty()

# -------------------------
# Google Sheets setup
# -------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# -------------------------
# Funções utilitárias
# -------------------------
def carregar_registos():
    data = sheet.get_all_records()
    return data if data else []

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

def apagar_registo(email):
    registros = sheet.get_all_records()
    for i, reg in enumerate(registros, start=2):
        if str(reg.get("Email","")).strip().lower() == str(email).strip().lower():
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

# -------------------------
# Função para verificar se a equipa já tem 2 membros
# -------------------------
def equipe_cheia(nome_equipa, email_atual=None):
    """
    Verifica se a equipa já tem 2 ou mais membros.
    email_atual: opcional, ignora este email na contagem (para updates)
    """
    if not nome_equipa:
        return False

    nome_equipa_norm = nome_equipa.strip().lower()
    registros = carregar_registos()
    
    membros = [
        r for r in registros
        if str(r.get("Participa Challenge","")).strip().lower() == "sim"
           and str(r.get("Nome da Equipa","")).strip().lower() == nome_equipa_norm
           and (email_atual is None or str(r.get("Email","")).strip().lower() != email_atual.lower())
    ]
    
    return len(membros) >= 2

# -------------------------
# Cabeçalho fixo
# -------------------------
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - 2 de dezembro | Edifício Lumnia</p>", unsafe_allow_html=True)
st.markdown("""
**Estás pronto para levar a tua experiência com Inteligência Artificial a outro nível?**

📅 **2 de dezembro | 🕙 10h – 17h30 | 📍 Edifício Lumnia (junto à Gare do Oriente)**
""", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ OpenDay Enroll (com validação de equipa)
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=False):

    email = st.text_input("📧 Introduz o teu Email", key="en_email")

    if st.button("🔍 Verificar email"):
        if not email.strip():
            st.warning("O campo Email é obrigatório.")
            st.stop()
        registros = carregar_registos()
        registro_existente = next(
            (r for r in registros if str(r.get("Email","")).strip().lower() == email.strip().lower()),
            None
        )
        st.session_state.email_verificado = True
        st.session_state.registro_existente = registro_existente

    if st.session_state.get("email_verificado"):
        registro_existente = st.session_state.get("registro_existente")

        # -------------------------------
        # Novo registro
        # -------------------------------
        if registro_existente is None:
            st.success("✔️ Este email não está registado. Continua a inscrição:")

            modo = st.radio(
                "Seleciona o modo de participação:",
                ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
                key="en_modo"
            )

            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("👤 Nome", key="en_nome")
                apelido = st.text_input("👤 Apelido", key="en_apelido")
            with col2:
                equipa = ""
                if modo == "Attend Open Day + Participate in the Challenge":
                    equipa = st.text_input("👥 Nome da Equipa (obrigatório)", key="en_equipa")
                    equipa = equipa.strip().title() if equipa else ""

                    if equipa and equipe_cheia(equipa):
                        st.warning(f"⚠️ A equipa '{equipa}' já está completa (2 membros). Escolhe outro nome de equipa.")
                        st.stop()

            if st.button("✅ Confirmar inscrição"):
                if not nome or not apelido:
                    st.warning("Nome e Apelido são obrigatórios.")
                    st.stop()
                if modo == "Attend Open Day + Participate in the Challenge":
                    if not equipa:
                        st.warning("Nome da Equipa é obrigatório para o Challenge.")
                        st.stop()
                    if equipe_cheia(equipa):
                        st.warning(f"⚠️ A equipa '{equipa}' já está completa (2 membros). Escolhe outro nome de equipa.")
                        st.stop()

                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    nome,
                    apelido,
                    email,
                    "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
                    equipa if modo == "Attend Open Day + Participate in the Challenge" else "—",
                    datahora
                )
                st.success(f"{nome}, a tua inscrição foi confirmada!")
                enviar_email(
                    email,
                    "IBM Journey | Confirmação de inscrição",
                    f"Olá {nome},\n\nA tua inscrição foi confirmada.\nModo: {modo}\nEquipa: {equipa if equipa else '—'}"
                )
                st.session_state.email_verificado = False
                st.stop()

        # -------------------------------
        # Update existente
        # -------------------------------
        else:
            participa = str(registro_existente.get("Participa Challenge","")).strip().lower()
            modo_atual = "Attend Open Day + Participate in the Challenge" if participa == "sim" else "Attend Open Day only"

            st.info(f"Este email já está registado. Modo atual: **{modo_atual}**")

            novo_modo = "Attend Open Day + Participate in the Challenge" if modo_atual == "Attend Open Day only" else "Attend Open Day only"

            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="alt_equipa")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

                if equipa_nova and equipe_cheia(equipa_nova, email_atual=email):
                    st.warning(f"⚠️ A equipa '{equipa_nova}' já está completa (2 membros). Escolhe outro nome de equipa.")
                    st.stop()

            if st.button("🔄 Atualizar inscrição"):
                if novo_modo == "Attend Open Day + Participate in the Challenge":
                    if not equipa_nova:
                        st.warning("Nome da Equipa é obrigatório para o Challenge.")
                        st.stop()
                    if equipe_cheia(equipa_nova, email_atual=email):
                        st.warning(f"⚠️ A equipa '{equipa_nova}' já está completa (2 membros). Escolhe outro nome de equipa.")
                        st.stop()

                apagar_registo(email)
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    registro_existente.get("Nome",""),
                    registro_existente.get("Apelido",""),
                    email,
                    "Sim" if novo_modo == "Attend Open Day + Participate in the Challenge" else "Não",
                    equipa_nova if novo_modo == "Attend Open Day + Participate in the Challenge" else "—",
                    datahora
                )
                st.success(f"✔️ Inscrição atualizada ({novo_modo})")
                enviar_email(
                    email,
                    "IBM Journey | Inscrição atualizada",
                    f"Olá {registro_existente.get('Nome','')},\n\nA tua inscrição foi atualizada.\nNovo modo: {novo_modo}\nEquipa: {equipa_nova if equipa_nova else '—'}"
                )
                st.session_state.email_verificado = False
                st.session_state.registro_existente = None
                st.rerun()



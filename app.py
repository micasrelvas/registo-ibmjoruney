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
# Cabeçalho fixo
# -------------------------
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - 2 de dezembro | Edifício Lumnia</p>", unsafe_allow_html=True)
st.markdown("""
**Estás pronto para levar a tua experiência com Inteligência Artificial a outro nível?**

📅 **2 de dezembro | 🕙 10h – 17h30 | 📍 Edifício Lumnia (junto à Gare do Oriente)**

Junta-te a nós para um dia exclusivo nos escritórios da IBM, onde vais descobrir o futuro do AI e pôr mãos à obra!
""", unsafe_allow_html=True)

# -------------------------------
# 1️⃣ About IBM
# -------------------------------
with st.expander("1️⃣ About IBM", expanded=False):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing.

• **AI and Machine Learning** – Leading the charge in AI development.  
• **Cloud Solutions** – Scalable and flexible cloud services.  
• **Quantum Computing** – Pushing the boundaries of computing.  
• **Research & Open Source** – R&D and collaboration.
""", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ OpenDay Enroll
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=False):

    # 📧 1 — Sempre pedir email primeiro
    email = st.text_input("📧 Introduz o teu Email", key="en_email")

    # 🔍 2 — Verificar email
    if st.button("🔍 Verificar email"):

        if not email.strip():
            st.warning("O campo Email é obrigatório.")
            st.stop()

        registros = carregar_registos()
        registro_existente = next(
            (r for r in registros 
             if str(r.get("Email","")).strip().lower() == email.strip().lower()),
            None
        )

        st.session_state.email_verificado = True
        st.session_state.registro_existente = registro_existente

    # 🧠 3 — Se email foi verificado, começar lógica
    if st.session_state.get("email_verificado"):

        registro_existente = st.session_state.get("registro_existente")

        # -------------------------------------------------------------------
        # 🟦 CASO 1 — Email NÃO está registado → novo registo
        # -------------------------------------------------------------------
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

            if st.button("✅ Confirmar inscrição"):

                if not nome or not apelido:
                    st.warning("Nome e Apelido são obrigatórios.")
                    st.stop()

                if modo == "Attend Open Day + Participate in the Challenge" and not equipa:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
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
                    f"Olá {nome},\n\nA tua inscrição foi confirmada.\nMode: {modo}\nTeam: {equipa if equipa else '—'}\n\nSe quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}"
                )

            st.stop()  # impede que o resto execute
        # -------------------------------------------------------------------
        # 🟥 CASO 2 — Email JÁ EXISTE → mostrar AVISO personalizado
        # -------------------------------------------------------------------
        else:   # <--- ESTA LINHA É A CHAVE! GARANTE QUE O BLOCO FICA DENTRO DO 'if email_verificado'

            participa = str(registro_existente.get("Participa Challenge","")).strip().lower()
            modo_atual = "Attend Open Day + Participate in the Challenge" if participa == "sim" else "Attend Open Day only"

            # Mensagens personalizadas
            if modo_atual == "Attend Open Day + Participate in the Challenge":
                st.warning("⚠️ Este email já está inscrito no Open Day e no Desafio. Queres mudar para participar só no Open Day?")
            else:
                st.warning("⚠️ Este email já está inscrito no Open Day. Queres também participar no Desafio?")

            # Definir novo modo
            novo_modo = (
                "Attend Open Day only"
                if modo_atual == "Attend Open Day + Participate in the Challenge"
                else "Attend Open Day + Participate in the Challenge"
            )

            # Campo equipa se for Challenge
            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="alt_equipa")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

            # Botão atualizar
            if st.button("🔄 Atualizar inscrição"):

                if novo_modo == "Attend Open Day + Participate in the Challenge" and not equipa_nova:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
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

                # Mensagens personalizadas
                if novo_modo == "Attend Open Day + Participate in the Challenge":
                    st.success("✔️ Inscrição atualizada para **Open Day e Desafio**.")
                else:
                    st.success("✔️ Inscrição atualizada **apenas para o Open Day**.")

                enviar_email(
                    email,
                    "IBM Journey | Inscrição atualizada",
                    f"Olá {registro_existente.get('Nome','')},\n\nA tua inscrição foi atualizada.\n"
                    f"Modo anterior: {modo_atual}\nNovo modo: {novo_modo}\nEquipa: {equipa_nova if equipa_nova else '—'}"
                )

                # limpar estado
                st.session_state.email_verificado = False
                st.session_state.registro_existente = None
                st.rerun()


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
""", unsafe_allow_html=True)

# -------------------------------
# 4️⃣ Requirements Checklist
# -------------------------------
with st.expander("4️⃣ Requirements Checklist", expanded=False):
    st.markdown("""
1 — Enroll in the tab "OpenDay Enroll"  
2 — Create your IBM ID: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)  
3 — Request Your Cloud Account following the workshop guide (includes watsonx Orchestrate).
""", unsafe_allow_html=True)

# -------------------------------
# 5️⃣ Judging Criteria
# -------------------------------
with st.expander("5️⃣ Judging Criteria", expanded=False):
    st.markdown("""
**1️⃣ Application of Technology** — How effectively the chosen model(s) are integrated.  
**2️⃣ Presentation** — Clarity and effectiveness of the solution presentation.  
**3️⃣ Business Value** — Practical impact and alignment with business needs.  
**4️⃣ Originality** — Uniqueness and creativity of the solution.
""", unsafe_allow_html=True)

# -------------------------------
# 6️⃣ Technology
# -------------------------------
with st.expander("6️⃣ Technology", expanded=False):
    st.markdown("""
**Explore Before the OpenDay:** Familiarize yourself with watsonx Orchestrate:

- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""", unsafe_allow_html=True)

# -------------------------------
# 7️⃣ OpenDay Unenroll (Cancelamento simples)
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll", expanded=False):

    email_input = st.text_input("📧 Introduz o email para cancelar inscrição", key="unenroll_email_input")

    if st.button("🔍 Verificar inscrição"):

        email_cancel = email_input.strip()

        if not email_cancel:
            st.warning("O campo Email é obrigatório.")
            st.stop()

        registros = carregar_registos()
        registro = next(
            (r for r in registros if str(r.get("Email","")).strip().lower() == email_cancel.lower()),
            None
        )

        if registro is None:
            st.info("⚠️ Não foi encontrada nenhuma inscrição associada a este email.")
            st.stop()

        # Guardar na sessão — AGORA SEM COLISÕES
        st.session_state.unenroll_registro = registro
        st.session_state.unenroll_email_checked = email_cancel

    # Se encontrou registo, pedir confirmação
    if "unenroll_registro" in st.session_state:

        registro = st.session_state.unenroll_registro
        email_cancel = st.session_state.unenroll_email_checked

        modo_atual = (
            "Open Day + Challenge" 
            if str(registro.get("Participa Challenge","")).strip().lower() == "sim" 
            else "Open Day only"
        )

        st.success(f"✅ Inscrição encontrada em modo: **{modo_atual}**")

        st.warning(f"⚠️ Tens a certeza que queres cancelar a inscrição no modo **{modo_atual}**?")

        if st.button("🛑 Confirmar cancelamento definitivo"):

            apagar_registo(email_cancel)

            st.success("🛑 A tua inscrição foi cancelada com sucesso!")

            # Enviar email de cancelamento
            enviar_email(
                email_cancel,
                "IBM Journey | Inscrição cancelada",
                f"Olá {registro.get('Nome','')},\n\n"
                f"A tua inscrição foi cancelada.\n"
                f"Modo anterior: {modo_atual}\n\n"
                f"Se quiseres voltar a inscrever-te, usa o link: {st.secrets['APP_URL']}"
            )

            # limpar
            del st.session_state.unenroll_registro
            del st.session_state.unenroll_email_checked

            st.stop()


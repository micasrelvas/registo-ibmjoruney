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
# Inicializar session_state (evita AttributeError)
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
.stApp {
    background-color: #cce6ff;  /* fundo azul claro */
    color: black;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
    padding-top: 10px;
}

/* Cabeçalho */
h1, h2, h3 {
    color: #003366;
    text-align: center;
    background-color: #cce6ff;
    padding: 6px 12px;
    border-radius: 6px;
    margin: 6px 0;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Botões */
.stButton>button {
    background-color: #0059b3 !important;
    color: white !important;
    font-weight: 600;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Dataframes */
.stDataFrame th { background-color: #e6f2ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }
.stDataFrame td { background-color: #ffffff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; }

/* Expander - cabeçalho fechado */
[data-baseweb="expander"] > div > div:first-child {
    background-color: #00274c !important; /* azul escuro IBM */
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
}

/* Expander - cabeçalho aberto */
[data-baseweb="expander"][open] > div > div:first-child {
    background-color: #99ccff !important; /* azul claro */
    color: #003366 !important;
    font-weight: 600;
}

/* Hover sobre cabeçalho */
[data-baseweb="expander"] > div > div:first-child:hover {
    background-color: #3399ff !important;
    color: black !important;
}

/* Inputs */
div.stTextInput>div>div>input, div.stTextArea>div>div>textarea {
    background-color: white !important;
    color: black !important;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}

/* Labels */
div.stTextInput>label, label {
    color: #003366 !important;
    font-weight: 600;
    font-family: 'IBM Plex Sans', Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# ALERTA DE HIBERNAÇÃO (wake message)
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
    """Retorna lista de dicionários (get_all_records)."""
    data = sheet.get_all_records()
    return data if data else []

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    """Adiciona uma linha ao Google Sheet na ordem esperada:
    Nome | Apelido | Email | Participa Challenge | Nome da Equipa | DataHora
    """
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

def apagar_registo(email):
    """Apaga a primeira ocorrência com o email (case-insensitive). Retorna o registo apagado ou None."""
    registos = sheet.get_all_records()
    for i, reg in enumerate(registos, start=2):  # sheet rows start at 1, header row is 1
        if str(reg.get("Email", "")).strip().lower() == str(email).strip().lower():
            sheet.delete_rows(i)
            return reg
    return None

def enviar_email(destinatario, assunto, mensagem):
    """Envia um e-mail simples por SMTP (GMail)."""
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
# Cabeçalho fixo (nome da app + info do evento)
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

    st.markdown("### Choose your participation mode:")

    modo = st.radio(
        "Select one option:",
        ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
        key="modo_escolhido"
    )

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome", key="en_nome")
        apelido = st.text_input("👤 Apelido", key="en_apelido")
    with col2:
        email = st.text_input("📧 Email", key="en_email")

    equipa = ""
    if modo == "Attend Open Day + Participate in the Challenge":
        equipa = st.text_input("👥 Nome da Equipa (obrigatório para Challenge)", key="en_equipa")
        equipa = equipa.strip().title() if equipa else ""

    # --- Confirm enrollment (single button flow) ---
    if st.button("✅ Confirm enrollment"):

        # validação campos
        if not all([nome, apelido, email]):
            st.warning("Todos os campos exceto Nome da Equipa são obrigatórios.")
            st.stop()

        df = carregar_registos()

        # procura registo pelo email (case-insensitive)
        registro_existente = next(
            (r for r in df if str(r.get("Email","")).strip().lower() == email.strip().lower()),
            None
        )

        # -----------------------
        # CASO 1 — novo registo
        # -----------------------
        if registro_existente is None:

            if modo == "Attend Open Day + Participate in the Challenge" and not equipa:
                st.warning("Nome da Equipa é obrigatório para participar no Challenge.")
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

            st.success(f"{nome}, a tua inscrição foi confirmada! (Mode: {modo})")

            enviar_email(
                email,
                "IBM Journey | Confirmação de inscrição",
                f"Olá {nome},\n\nA tua inscrição foi confirmada.\nMode: {modo}\nTeam: {equipa if equipa else '—'}\n\nSe quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}"
            )
            st.stop()

        # -----------------------
        # CASO 2 — email já existe -> permitir update (um botão)
        # -----------------------
        modo_atual = (
            "Attend Open Day + Participate in the Challenge"
            if str(registro_existente.get("Participa Challenge","")).strip().lower() == "sim"
            else "Attend Open Day only"
        )

        st.warning(f"⚠️ O email já está registado para **{modo_atual}**.")
        # se o modo escolhido for igual ao atual, nada a fazer
        if modo == modo_atual:
            st.info("Não há alterações: selecionaste o mesmo modo que já tinhas.")
            st.stop()

        # Se chegou aqui, o usuário pediu um modo diferente — pedir confirmação e atualizar
        st.info(f"Queres atualizar a inscrição para **{modo}**? (Isto substituirá o registo anterior.)")

        if modo == "Attend Open Day only":
            equipa = "—"
        else:
            # equipa já está capturada do input acima; valida
            if not equipa:
                st.warning("Nome da Equipa é obrigatório para o Challenge.")
                st.stop()

        if st.button("🔄 Confirm update"):

            # apagar registo antigo
            apagado = apagar_registo(email)  # retorna o registo apagado (ou None)

            # gravar novo registo (substitui)
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_registo(
                nome,
                apelido,
                email,
                "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
                equipa,
                datahora
            )

            st.success(f"✅ A tua inscrição foi atualizada para **{modo}**!")

            enviar_email(
                email,
                "IBM Journey | Inscrição atualizada",
                f"Olá {nome},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: {modo}\nTeam: {equipa if equipa else '—'}\n\nObrigado!"
            )
            st.stop()

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
# 7️⃣ OpenDay Unenroll / Update Mode
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll / Update Mode", expanded=False):

    email_cancel = st.text_input("📧 Introduz o email para cancelar/atualizar", key="unenroll_email")

    if st.button("🔍 Search registration"):

        if not email_cancel:
            st.warning("O campo Email é obrigatório.")
            st.stop()

        registos = carregar_registos()
        registro = next(
            (r for r in registos if str(r.get("Email","")).strip().lower() == email_cancel.strip().lower()),
            None
        )

        if registro is None:
            st.info("⚠️ Não foi encontrado nenhum registo com esse email.")
            st.stop()

        modo_atual = (
            "Attend Open Day + Participate in the Challenge"
            if str(registro.get("Participa Challenge","")).strip().lower() == "sim"
            else "Attend Open Day only"
        )

        st.success(f"✅ Registo encontrado! Modo atual: **{modo_atual}**")

        acao = st.radio(
            "Escolhe uma ação:",
            ["Cancelar inscrição", "Atualizar modo"],
            key="acao_unenroll"
        )

        # Cancelar inscrição
        if acao == "Cancelar inscrição":
            if st.button("🛑 Confirmar cancelamento"):
                apagar_registo(email_cancel)
                st.info("🛑 A tua inscrição foi cancelada.")
                enviar_email(
                    email_cancel,
                    "IBM Journey | Inscrição cancelada",
                    f"Olá {registro.get('Nome','')},\n\nA tua inscrição foi cancelada.\nPrevious mode: {modo_atual}\n\nSe quiseres voltar a inscrever-te: {st.secrets['APP_URL']}"
                )
                st.stop()

        # Atualizar modo
        else:
            novo_modo = st.radio(
                "Seleciona o novo modo:",
                ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
                key="novo_modo_unenroll"
            )

            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="unenroll_equipe")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

            if st.button("🔄 Confirmar atualização de modo"):

                if novo_modo == modo_atual:
                    st.info("⚠️ O modo selecionado é igual ao modo atual. Nenhuma alteração foi feita.")
                    st.stop()

                if novo_modo == "Attend Open Day + Participate in the Challenge" and not equipa_nova:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
                    st.stop()

                # apagar e guardar novo
                apagar_registo(email_cancel)
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    registro.get("Nome",""),
                    registro.get("Apelido",""),
                    email_cancel,
                    "Sim" if novo_modo == "Attend Open Day + Participate in the Challenge" else "Não",
                    equipa_nova if novo_modo == "Attend Open Day + Participate in the Challenge" else "—",
                    datahora
                )

                st.success(f"✅ A tua inscrição foi atualizada para **{novo_modo}**")
                enviar_email(
                    email_cancel,
                    "IBM Journey | Inscrição atualizada",
                    f"Olá {registro.get('Nome','')},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: {novo_modo}\nTeam: {equipa_nova if equipa_nova else '—'}"
                )
                st.stop()

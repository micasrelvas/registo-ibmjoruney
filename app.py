import streamlit as st
from datetime import datetime
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
for key, default in {
    "email_checked": False,
    "email": "",
    "existing_user": None,
    "action": "idle",
    "modo_escolhido": "",
    "nome": "",
    "apelido": "",
    "equipa": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------
# CSS / Fonte
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');
.stApp { background-color: #cce6ff; color: black; font-family: 'IBM Plex Sans', Arial, sans-serif; padding-top: 10px; }
h1,h2,h3 { color:#003366; text-align:center; background-color:#cce6ff; padding:6px 12px; border-radius:6px; margin:6px 0; }
.stButton>button { background-color: #0059b3 !important; color:white !important; font-weight:600; }
div.stTextInput>label, label { color:#003366 !important; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# ALERTA DE HIBERNAÇÃO
# -------------------------
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("<div style='text-align:center; padding:30px;'><h2>⚡ A app está a acordar...</h2><p>Pode demorar alguns segundos.</p></div>", unsafe_allow_html=True)
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
    return sheet.get_all_records() or []

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

def apagar_registo(email):
    registros = sheet.get_all_records()
    for i, reg in enumerate(registros, start=2):
        if str(reg.get("Email","")).strip().lower() == email.strip().lower():
            sheet.delete_rows(i)
            return reg
    return None

def enviar_email(destinatario, assunto, mensagem):
    """Email já configurado no Streamlit Secrets, não precisa de inserir aqui credenciais."""
    import smtplib
    from email.mime.text import MIMEText
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
# Cabeçalho
# -------------------------
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - 2 de dezembro | Edifício Lumnia</p>", unsafe_allow_html=True)

# ========================
# BLOCOS DE INSCRIÇÃO
# ========================

st.subheader("📧 Primeiro passo: verifica o teu email")

email_input = st.text_input("Email", value=st.session_state.email, key="input_email")
verifica = st.button("Verificar email")

if verifica:
    email_val = email_input.strip()
    if not email_val:
        st.warning("Por favor insere um email válido.")
    else:
        st.session_state.email = email_val
        registros = carregar_registos()
        existente = next((r for r in registros if str(r.get("Email","")).strip().lower() == email_val.lower()), None)
        st.session_state.existing_user = existente
        st.session_state.email_checked = True
        st.session_state.action = "update" if existente else "new"
        st.experimental_rerun()

# ========================
# Fluxo após verificação do email
# ========================
if st.session_state.email_checked:
    existente = st.session_state.existing_user
    email_val = st.session_state.email

    if st.session_state.action == "new":
        st.success("Email não registado. Preenche os dados para inscrição.")

        modo = st.radio("Seleciona o modo de participação:", ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"], key="modo_escolhido")
        st.session_state.modo_escolhido = modo

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", key="nome")
            apelido = st.text_input("Apelido", key="apelido")
        with col2:
            st.text_input("Email", value=email_val, disabled=True)

        equipa = ""
        if modo == "Attend Open Day + Participate in the Challenge":
            equipa = st.text_input("Nome da Equipa (obrigatório)", key="equipa")
            equipa = equipa.strip().title() if equipa else ""

        if st.button("✅ Confirmar inscrição"):
            if not all([nome, apelido]):
                st.warning("Nome e Apelido são obrigatórios.")
            elif modo == "Attend Open Day + Participate in the Challenge" and not equipa:
                st.warning("Nome da Equipa é obrigatório para o Challenge.")
            else:
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(nome, apelido, email_val, "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não", equipa if equipa else "—", datahora)
                st.success(f"{nome}, a tua inscrição foi confirmada! Mode: {modo}")
                enviar_email(
                    email_val,
                    "IBM Journey | Confirmação de inscrição",
                    f"Olá {nome},\n\nA tua inscrição foi confirmada.\nMode: {modo}\nTeam: {equipa if equipa else '—'}\n\nSe quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}"
                )
                st.stop()

    else:
        # Email já registado -> update
        nome = existente.get("Nome","")
        apelido = existente.get("Apelido","")
        modo_atual = "Attend Open Day + Participate in the Challenge" if str(existente.get("Participa Challenge","")).strip().lower() == "sim" else "Attend Open Day only"
        st.info(f"⚠️ Este email já está registado. Modo atual: {modo_atual}")

        atualizar = st.radio("Queres atualizar a inscrição para o outro modo?", ["Não", "Sim"], key="update_radio")
        if atualizar == "Sim":
            if modo_atual == "Attend Open Day only":
                # Passa para Challenge -> pedir apenas nome da equipa
                equipa = st.text_input("Nome da Equipa (obrigatório)", key="equipa_update")
                equipa = equipa.strip().title() if equipa else ""
                if st.button("🔄 Confirmar atualização"):
                    if not equipa:
                        st.warning("Nome da Equipa é obrigatório para o Challenge.")
                    else:
                        apagar_registo(email_val)
                        datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        guardar_registo(nome, apelido, email_val, "Sim", equipa, datahora)
                        st.success(f"✅ A tua inscrição foi atualizada para **Attend Open Day + Challenge**")
                        enviar_email(
                            email_val,
                            "IBM Journey | Inscrição atualizada",
                            f"Olá {nome},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: Attend Open Day + Challenge\nTeam: {equipa}"
                        )
                        st.stop()
            else:
                # Passa de Challenge -> Open Day only -> não precisa de campos adicionais
                if st.button("🔄 Confirmar atualização"):
                    apagar_registo(email_val)
                    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    guardar_registo(nome, apelido, email_val, "Não", "—", datahora)
                    st.success(f"✅ A tua inscrição foi atualizada para **Attend Open Day only**")
                    enviar_email(
                        email_val,
                        "IBM Journey | Inscrição atualizada",
                        f"Olá {nome},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: Attend Open Day only\nTeam: —"
                    )
                    st.stop()

# ========================
# Outras tabs / expanders
# ========================

with st.expander("1️⃣ About IBM", expanded=False):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing.

• **AI and Machine Learning** – Leading the charge in AI development.  
• **Cloud Solutions** – Scalable and flexible cloud services.  
• **Quantum Computing** – Pushing the boundaries of computing.  
• **Research & Open Source** – R&D and collaboration.
""", unsafe_allow_html=True)

with st.expander("3️⃣ Challenge", expanded=False):
    st.markdown("""
**The Challenge:** Design an AI agent powered by IBM watsonx Orchestrate that helps people and businesses achieve more with less effort.

**What’s Expected?**
- Ideate with watsonx Orchestrate: Design a solution concept with orchestration features, integrations, and digital skills.  
- Focus on Real-World Impact: Address challenges in HR, sales, customer service, finance, or procurement.  
- Innovate for the Future of Work: Enhance human potential and productivity.  
- Reference IBM Technology: Explain how watsonx Orchestrate’s features, skills, integrations, or workflows would be leveraged.
""", unsafe_allow_html=True)

with st.expander("4️⃣ Requirements Checklist", expanded=False):
    st.markdown("""
1 — Enroll in the tab "OpenDay Enroll"  
2 — Create your IBM ID: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)  
3 — Request Your Cloud Account following the workshop guide (includes watsonx Orchestrate).
""", unsafe_allow_html=True)

with st.expander("5️⃣ Judging Criteria", expanded=False):
    st.markdown("""
**1️⃣ Application of Technology** — How effectively the chosen model(s) are integrated.  
**2️⃣ Presentation** — Clarity and effectiveness of the solution presentation.  
**3️⃣ Business Value** — Practical impact and alignment with business needs.  
**4️⃣ Originality** — Uniqueness and creativity of the solution.
""", unsafe_allow_html=True)

with st.expander("6️⃣ Technology", expanded=False):
    st.markdown("""
**Explore Before the OpenDay:** Familiarize yourself with watsonx Orchestrate:

- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""", unsafe_allow_html=True)


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
    "update_equipe": "",
    "email_verificado": False,
    "registro_existente": None,
    "unenroll_registro": None,
    "unenroll_email_checked": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------
# CSS / Fonte
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');
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

/* Cor preta para opções do radio */
[data-baseweb="radio"] span {
    color: black !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# ALERTA DE HIBERNAÇÃO
# -------------------------
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="text-align:center; padding:30px;">
        <h2>⚡ The app is waking up...</h2>
        <p>This may take a few seconds. Thank you for your patience!</p>
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
st.markdown("<p style='text-align:center;'>Open Day - December 2nd | Edifício Lumnia</p>", unsafe_allow_html=True)

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
# 2️⃣ OpenDay Enroll (Atualizado)
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=False):
    email = st.text_input("📧 Introduz o teu Email", key="en_email")
    
    if st.button("🔍 Verificar email"):
        if not email.strip():
            st.warning("O campo Email é obrigatório.")
        else:
            registros = carregar_registos()
            registro_existente = next(
                (r for r in registros if str(r.get("Email","")).strip().lower() == email.strip().lower()),
                None
            )
            st.session_state.email_verificado = True
            st.session_state.registro_existente = registro_existente

    if st.session_state.get("email_verificado"):
        registro_existente = st.session_state.get("registro_existente")

        # ---------- Novo registro ----------
        if registro_existente is None:
            st.success("✔️ Este email não está registado. Continua a inscrição:")

            modo = st.selectbox(
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

            # Botão para confirmar inscrição
            if st.button("✅ Confirmar inscrição"):
                if not nome or not apelido:
                    st.warning("Nome e Apelido são obrigatórios.")
                elif modo == "Attend Open Day + Participate in the Challenge" and not equipa:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
                elif modo == "Attend Open Day + Participate in the Challenge" and equipe_cheia(equipa):
                    st.warning(f"⚠️ A equipa '{equipa}' já está completa (2 membros). Escolhe outro nome de equipa.")
                else:
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
    f"""Olá {nome},

A tua inscrição no Open Day, dia 2 de dezembro, está confirmada.
Inscrição Atual: {modo}
Equipa: {equipa if equipa else '—'}

Se quiseres alterar ou cancelar a inscrição, acede:
https://urldefense.proofpoint.com/v2/url?u=https-3A__registo-2Dibmjoruney-2Debhbpznge9ec9vwgc58jlx.streamlit.app&d=DwIGaQ&c=BSDicqBQBDjDI9RkVyTcHQ&r=YjfJ_kr2WkXR-VrZ0gnxjD2J77rXGfRn9tFVZrDEBkA&m=XeOMlAmpY45XyTBbJFyynVegU2e88NxvRWO0wi3Wq6kpy3n4cGcUXCxXGCNVQgUb&s=JscuoVlLLpHaSfolIh6tAtRiJKinVL4KCA3jhH27sOk&e=

Obrigada,

Mariana Relvas
Brand Storage Sales Specialist
IBM Technology Portugal

Mobile: +351 91 927 93 50
E-mail: mariana.relvas1@ibm.com
"""
)

st.session_state.email_verificado = False
st.session_state.registro_existente = None


        # ---------- Update existente ----------
        else:
            participa = str(registro_existente.get("Participa Challenge","")).strip().lower()
            modo_atual = "Attend Open Day + Participate in the Challenge" if participa == "sim" else "Attend Open Day only"
            st.info(f"Este email já está registado. Modo atual: **{modo_atual}**")

            novo_modo = "Attend Open Day + Participate in the Challenge" if modo_atual == "Attend Open Day only" else "Attend Open Day only"

            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="alt_equipa")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

            # Botão para atualizar inscrição
            if st.button("🔄 Atualizar inscrição"):
                if novo_modo == "Attend Open Day + Participate in the Challenge" and not equipa_nova:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
                elif novo_modo == "Attend Open Day + Participate in the Challenge" and equipe_cheia(equipa_nova, email_atual=email):
                    st.warning(f"⚠️ A equipa '{equipa_nova}' já está completa (2 membros). Escolhe outro nome de equipa.")
                else:
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
                        f"""Olá {registro_existente.get('Nome','')},

A tua inscrição no Open Day, dia 2 de dezembro, foi atualizada.
Inscrição Atual: {novo_modo}
Equipa: {equipa_nova if equipa_nova else '—'}

Se quiseres alterar ou cancelar a inscrição, acede:
https://urldefense.proofpoint.com/v2/url?u=https-3A__registo-2Dibmjoruney-2Debhbpznge9ec9vwgc58jlx.streamlit.app&d=DwIGaQ&c=BSDicqBQBDjDI9RkVyTcHQ&r=YjfJ_kr2WkXR-VrZ0gnxjD2J77rXGfRn9tFVZrDEBkA&m=XeOMlAmpY45XyTBbJFyynVegU2e88NxvRWO0wi3Wq6kpy3n4cGcUXCxXGCNVQgUb&s=JscuoVlLLpHaSfolIh6tAtRiJKinVL4KCA3jhH27sOk&e=

Obrigada,

Mariana Relvas
Brand Storage Sales Specialist
IBM Technology Portugal

Mobile: +351 91 927 93 50
E-mail: mariana.relvas1@ibm.com
"""
                    )

                    st.session_state.email_verificado = False
                    st.session_state.registro_existente = None


# -------------------------------
# 3️⃣ Challenge
# -------------------------------
with st.expander("3️⃣ Challenge", expanded=False):
    st.markdown("""
**The Challenge:** In teams of 2, you'll prepare a few slides to present your use case: identify a current problem, explain how to solve it, and show—through words or a diagram—how watsonx would power your solution.

📍 Presentations will take place on February 3 in front of a diverse jury (ISCTE, IBM, and Timestamp), who will evaluate your work.

...So, no excuses! You have 2 months to create your solution and showcase it in a presentation...

🏆 The best team may even earn a **2-week professional experience** in June/July (availability to be confirmed)!

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
✅ Enroll in the tab "OpenDay Enroll"  
✅ Create your IBM ID using the same email you used to register for the Open Day: [Create your IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)  
  (If you already have an IBMid that uses the same email you used to register for the Open Day, proceed to log in, complete the authentication process)
""", unsafe_allow_html=True)

# -------------------------------
# 5️⃣ Judging Criteria
# -------------------------------
with st.expander("5️⃣ Judging Criteria", expanded=False):
    st.markdown("""
**👉 Application of Technology** — How effectively the chosen model(s) are integrated.  
**👉 Presentation** — Clarity and effectiveness of the solution presentation.  
**👉 Business Value** — Practical impact and alignment with business needs.  
**👉 Originality** — Uniqueness and creativity of the solution.
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
# 7️⃣ OpenDay Unenroll (Cancelamento)
# -------------------------------
with st.expander("7️⃣ OpenDay Unenroll", expanded=False):
    email_input = st.text_input("📧 Enter your email to unenroll", key="unenroll_email_input")

    if st.button("🔍 Check enrollment"):
        email_cancel = email_input.strip()
        if not email_cancel:
            st.warning("Email field is required.")
        else:
            registros = carregar_registos()
            registro = next(
                (r for r in registros if str(r.get("Email","")).strip().lower() == email_cancel.lower()),
                None
            )
            if registro is None:
                st.info("⚠️ No enrollment found for this email.")
            else:
                st.session_state.unenroll_registro = registro
                st.session_state.unenroll_email_checked = email_cancel

    if st.session_state.get("unenroll_registro"):
        registro = st.session_state.unenroll_registro
        email_cancel = st.session_state.unenroll_email_checked
        participa_challenge = str(registro.get("Participa Challenge","")).strip().lower() == "sim"
        modo_atual = "Open Day + Challenge" if participa_challenge else "Open Day only"

        st.success(f"✅ Enrollment found in: **{modo_atual}**")

        # Texto fixo acima do botão de confirmação
        st.markdown("**⚠️ Please confirm your unenrollment below:**")

        # Botão de confirmação (indentado corretamente dentro do expander)
        if st.button("🛑 Confirm Unenrollment"):
            apagar_registo(email_cancel)
            st.success("🛑 Your enrollment has been successfully cancelled! You will receive an email with confirmation!")

            email_text = f"""Olá {registro.get('Nome','')},

A tua inscrição no Open Day, dia 2 de dezembro, foi cancelada.
Participação: {modo_atual} 
Se quiseres voltar a inscrever-te, acede: https://urldefense.proofpoint.com/v2/url?u=https-3A__registo-2Dibmjoruney-2Debhbpznge9ec9vwgc58jlx.streamlit.app&d=DwIGaQ&c=BSDicqBQBDjDI9RkVyTcHQ&r=YjfJ_kr2WkXR-VrZ0gnxjD2J77rXGfRn9tFVZrDEBkA&m=XeOMlAmpY45XyTBbJFyynVegU2e88NxvRWO0wi3Wq6kpy3n4cGcUXCxXGCNVQgUb&s=JscuoVlLLpHaSfolIh6tAtRiJKinVL4KCA3jhH27sOk&e=

Obrigada,

Mariana Relvas
Brand Storage Sales Specialist
IBM Technology Portugal

Mobile: +351 91 927 93 50
E-mail: mariana.relvas1@ibm.com
"""

            enviar_email(
                email_cancel,
                "IBM Journey | Cancelamento da Inscrição",
                email_text
            )

            st.session_state.unenroll_registro = None
            st.session_state.unenroll_email_checked = None



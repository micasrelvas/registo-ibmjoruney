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
initial_keys = {
    "en_nome": "",
    "en_apelido": "",
    "en_email": "",
    "en_equipa": "",
    "modo_escolhido": "Attend Open Day only",
    "pending_enroll": None,          # dict with pending enroll details (used after first click)
    "encontrado": None,              # used by unenroll block
    "email_encontrado": "",
}
for k, v in initial_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
time.sleep(1.2)
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
    """Apaga todas as ocorrências com o email (case-insensitive).
    Usa findall() para obter linhas reais e apaga de trás para a frente.
    Retorna True se apagou >=1 linha, False caso contrário.
    """
    try:
        # localizar todas as células que correspondem ao email (case-insensitive not supported by findall,
        # so verificamos manualmente cada match's cell value)
        matches = sheet.findall(email)
        if not matches:
            # tentativa alternativa: procurar por versões lowercase (procurar emails pode ser exato)
            # vamos também procurar células que, após strip/lower, igualem email
            all_cells = []
            # percorre coluna "Email" para localizar correspondências robustas
            header = sheet.row_values(1)
            if "Email" in header:
                col_idx = header.index("Email") + 1
                col_cells = sheet.col_values(col_idx)
                # col_values inclui header; iterar com index
                rows_to_delete = []
                for r_idx, val in enumerate(col_cells, start=1):
                    if str(val).strip().lower() == str(email).strip().lower():
                        rows_to_delete.append(r_idx)
                if not rows_to_delete:
                    return False
                # delete in reverse order
                for r in sorted(rows_to_delete, reverse=True):
                    sheet.delete_rows(r)
                return True
            return False

        # gather unique row numbers that truly match (case-insensitive)
        header = sheet.row_values(1)
        if "Email" in header:
            col_email_index = header.index("Email") + 1
        else:
            # if header mismatch, fallback to using the cell's column
            col_email_index = None

        rows_to_delete = set()
        for cell in matches:
            # confirm that the matched cell is indeed in the Email column (if possible)
            if col_email_index is None or cell.col == col_email_index:
                # extra check on the cell content
                cell_val = sheet.cell(cell.row, cell.col).value
                if str(cell_val).strip().lower() == str(email).strip().lower():
                    rows_to_delete.add(cell.row)

        if not rows_to_delete:
            return False

        for r in sorted(rows_to_delete, reverse=True):
            sheet.delete_rows(r)

        return True
    except Exception as e:
        st.error(f"Erro ao apagar registo: {e}")
        return False

def contar_por_equipa(equipa_name):
    """Conta quantos registos com Participa Challenge == 'Sim' existem para uma equipa."""
    registos = carregar_registos()
    cnt = sum(
        1 for r in registos
        if str(r.get("Participa Challenge","")).strip().lower() == "sim"
        and str(r.get("Nome da Equipa","")).strip().lower() == str(equipa_name).strip().lower()
    )
    return cnt

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

    # radio with session_state
    modo = st.radio(
        "Select one option:",
        ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
        key="modo_escolhido"
    )

    # inputs bound to session_state keys (prevents losing values on re-renders)
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
        if not all([st.session_state.en_nome, st.session_state.en_apelido, st.session_state.en_email]):
            st.warning("Todos os campos exceto Nome da Equipa são obrigatórios.")
            st.stop()

        # salvar pending_enroll no session_state (para preservar valores entre cliques)
        st.session_state.pending_enroll = {
            "nome": st.session_state.en_nome,
            "apelido": st.session_state.en_apelido,
            "email": st.session_state.en_email.strip().lower(),
            "modo": modo,
            "equipa": equipa.strip() if equipa else ""
        }

        df = carregar_registos()

        # procura registo pelo email (case-insensitive)
        registro_existente = next(
            (r for r in df if str(r.get("Email","")).strip().lower() == st.session_state.pending_enroll["email"]),
            None
        )

        # -----------------------
        # CASO 1 — novo registo
        # -----------------------
        if registro_existente is None:

            # se for challenge, validar equipa e limite
            if st.session_state.pending_enroll["modo"] == "Attend Open Day + Participate in the Challenge":
                if not st.session_state.pending_enroll["equipa"]:
                    st.warning("Nome da Equipa é obrigatório para participar no Challenge.")
                    st.stop()
                # valida limite 2
                if contar_por_equipa(st.session_state.pending_enroll["equipa"]) >= 2:
                    st.error(f"⚠️ A equipa '{st.session_state.pending_enroll['equipa']}' já atingiu o limite de 2 alunos.")
                    st.stop()

            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_registo(
                st.session_state.pending_enroll["nome"],
                st.session_state.pending_enroll["apelido"],
                st.session_state.pending_enroll["email"],
                "Sim" if st.session_state.pending_enroll["modo"] == "Attend Open Day + Participate in the Challenge" else "Não",
                st.session_state.pending_enroll["equipa"] if st.session_state.pending_enroll["modo"] == "Attend Open Day + Participate in the Challenge" else "—",
                datahora
            )

            st.success(f"{st.session_state.pending_enroll['nome']}, a tua inscrição foi confirmada! (Mode: {st.session_state.pending_enroll['modo']})")

            enviar_email(
                st.session_state.pending_enroll["email"],
                "IBM Journey | Confirmação de inscrição",
                f"Olá {st.session_state.pending_enroll['nome']},\n\nA tua inscrição foi confirmada.\nMode: {st.session_state.pending_enroll['modo']}\nTeam: {st.session_state.pending_enroll['equipa'] if st.session_state.pending_enroll['equipa'] else '—'}\n\nSe quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}"
            )

            # limpar pending
            st.session_state.pending_enroll = None
            # limpar inputs
            st.session_state.en_nome = ""
            st.session_state.en_apelido = ""
            st.session_state.en_email = ""
            st.session_state.en_equipa = ""
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
            # limpar pending
            st.session_state.pending_enroll = None
            st.stop()

        # Se chegou aqui, o usuário pediu um modo diferente — pedir confirmação e atualizar
        st.info(f"Queres atualizar a inscrição para **{modo}**? (Isto substituirá o registo anterior.)")

        # Se for para mudar para Challenge, valida equipa e limite antes de permitir update
        if modo == "Attend Open Day + Participate in the Challenge":
            if not st.session_state.pending_enroll["equipa"]:
                st.warning("Nome da Equipa é obrigatório para o Challenge.")
                st.stop()
            if contar_por_equipa(st.session_state.pending_enroll["equipa"]) >= 2:
                st.error(f"⚠️ A equipa '{st.session_state.pending_enroll['equipa']}' já atingiu o limite de 2 alunos.")
                st.stop()

        if st.button("🔄 Confirm update"):
            # apagar registo antigo
            apagado = apagar_registo(st.session_state.pending_enroll["email"])

            # gravar novo registo (substitui)
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_registo(
                st.session_state.pending_enroll["nome"],
                st.session_state.pending_enroll["apelido"],
                st.session_state.pending_enroll["email"],
                "Sim" if st.session_state.pending_enroll["modo"] == "Attend Open Day + Participate in the Challenge" else "Não",
                st.session_state.pending_enroll["equipa"] if st.session_state.pending_enroll["modo"] == "Attend Open Day + Participate in the Challenge" else "—",
                datahora
            )

            st.success(f"✅ A tua inscrição foi atualizada para **{st.session_state.pending_enroll['modo']}**!")

            enviar_email(
                st.session_state.pending_enroll["email"],
                "IBM Journey | Inscrição atualizada",
                f"Olá {st.session_state.pending_enroll['nome']},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: {st.session_state.pending_enroll['modo']}\nTeam: {st.session_state.pending_enroll['equipa'] if st.session_state.pending_enroll['equipa'] else '—'}\n\nObrigado!"
            )

            # limpar pending e inputs
            st.session_state.pending_enroll = None
            st.session_state.en_nome = ""
            st.session_state.en_apelido = ""
            st.session_state.en_email = ""
            st.session_state.en_equipa = ""
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

    # mostrar o email de pesquisa ligado ao session_state (preserva)
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

        # guardar registo na sessão
        st.session_state.encontrado = registro
        st.session_state.email_encontrado = email_cancel.strip().lower()

    # só mostra ações se já foi feita a pesquisa
    if st.session_state.encontrado:

        registro = st.session_state.encontrado
        email_cancel = st.session_state.email_encontrado

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

        # ---- CANCELAR INSCRIÇÃO ----
        if acao == "Cancelar inscrição":

            if st.button("🛑 Confirmar cancelamento"):
                apagado = apagar_registo(email_cancel)
                if apagado:
                    st.info("🛑 A tua inscrição foi cancelada.")
                else:
                    st.warning("Ocorreu um problema ao apagar o registo (não encontrado).")

                enviar_email(
                    email_cancel,
                    "IBM Journey | Inscrição cancelada",
                    f"Olá {registro.get('Nome','')},\n\nA tua inscrição foi cancelada.\nPrevious mode: {modo_atual}\n\nSe quiseres voltar a inscrever-te: {st.secrets['APP_URL']}"
                )

                # limpar estado
                st.session_state.encontrado = None
                st.session_state.email_encontrado = ""
                st.session_state.unenroll_email = ""
                st.stop()

        # ---- ATUALIZAR MODO ----
        if acao == "Atualizar modo":

            novo_modo = st.radio(
                "Seleciona o novo modo:",
                ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
                key="novo_modo_unenroll"
            )

            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="unenroll_team")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

            if st.button("🔄 Confirmar atualização de modo"):

                if novo_modo == modo_atual:
                    st.info("⚠️ O modo selecionado é igual ao modo atual. Nenhuma alteração foi feita.")
                    st.stop()

                # se mudar para challenge, validar equipa e limite
                if novo_modo == "Attend Open Day + Participate in the Challenge":
                    if not equipa_nova:
                        st.warning("Nome da Equipa é obrigatório para o Challenge.")
                        st.stop()
                    if contar_por_equipa(equipa_nova) >= 2:
                        st.error(f"⚠️ A equipa '{equipa_nova}' já atingiu o limite de 2 alunos.")
                        st.stop()

                # apagar e guardar novo
                apagado = apagar_registo(email_cancel)
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

                # limpar estado
                st.session_state.encontrado = None
                st.session_state.email_encontrado = ""
                st.stop()

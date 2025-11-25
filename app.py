import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from email.mime.text import MIMEText
import smtplib
import time

# -------------------------
# Página
# -------------------------
st.set_page_config(page_title="🚀 IBM Journey powered by Timestamp - Open Day", layout="wide")

# Optional: pequena mensagem enquanto acorda (já tinhas isto)
loading = st.empty()
with loading.container():
    st.markdown("""
    <div style="text-align:center; padding:12px;">
        <strong>⚡ A app está a acordar... Pode demorar alguns segundos.</strong>
    </div>
    """, unsafe_allow_html=True)
time.sleep(1.2)
loading.empty()

# -------------------------
# Google Sheets (gspread + service account stored in st.secrets)
# -------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# -------------------------
# Funções utilitárias
# -------------------------
def carregar_registos():
    """Retorna lista de dicts com os registos (get_all_records)."""
    data = sheet.get_all_records()
    return data if data else []

def guardar_registo(nome, apelido, email, participa, equipa, datahora):
    """
    Append a linha com ordem:
    Nome | Apelido | Email | Participa Challenge | Nome da Equipa | DataHora
    """
    sheet.append_row([nome, apelido, email, participa, equipa, datahora])

def apagar_registo(email):
    """
    Apaga a primeira linha que coincida com o email (case-insensitive).
    Retorna o registo apagado (dict) ou None.
    """
    registros = sheet.get_all_records()
    for i, r in enumerate(registros, start=2):  # start=2 => pular header
        if str(r.get("Email","")).strip().lower() == str(email).strip().lower():
            sheet.delete_rows(i)
            return r
    return None

def enviar_email(destinatario, assunto, mensagem):
    """
    Usa as credenciais guardadas em st.secrets (EMAIL_REMETENTE e EMAIL_PASSWORD).
    """
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
# Estado (session_state)
# -------------------------
if "email_checked" not in st.session_state:
    st.session_state.email_checked = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "existing_user" not in st.session_state:
    st.session_state.existing_user = None
if "action" not in st.session_state:  # 'idle', 'new', 'update', 'done'
    st.session_state.action = "idle"

# -------------------------
# Cabeçalho fixo
# -------------------------
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Open Day - 2 de dezembro | Edifício Lumnia</p>", unsafe_allow_html=True)

st.markdown("""
**Estás pronto para levar a tua experiência com Inteligência Artificial a outro nível?**

📅 **2 de dezembro | 🕙 10h – 17h30 | 📍 Edifício Lumnia (junto à Gare do Oriente)**
""", unsafe_allow_html=True)

st.write("---")

# -------------------------
# PASSO A — Pedir apenas Email + botão "Verificar email"
# -------------------------
with st.container():
    st.subheader("Inscrição / Atualização")
    email_input = st.text_input("📧 Introduz o teu email", value=st.session_state.email, key="input_email")
    if st.button("Verificar email"):
        email_val = (email_input or "").strip()
        if not email_val:
            st.warning("Por favor insere um email válido.")
        else:
            st.session_state.email = email_val
            registros = carregar_registos()
            existente = next((r for r in registros if str(r.get("Email","")).strip().lower() == email_val.lower()), None)
            st.session_state.existing_user = existente  # dict ou None
            st.session_state.email_checked = True
            # definir ação inicial conforme existir
            st.session_state.action = "update" if existente else "new"
            st.experimental_rerun()

# If user already clicked verify
if st.session_state.email_checked:

    registros = carregar_registos()     # refresh
    existente = st.session_state.existing_user

    # -----------------------
    # CASO: Email NÃO existe -> novo registo
    # -----------------------
    if existente is None and st.session_state.action == "new":
        st.info(f"O email {st.session_state.email} não está registado. Preenche os dados abaixo para concluir a tua inscrição.")
        modo = st.selectbox("Seleciona o modo de participação", ["Open Day only", "Open Day + Challenge"], key="form_modo")
        # Campos obrigatórios
        nome = st.text_input("👤 Nome", key="form_nome")
        apelido = st.text_input("👤 Apelido", key="form_apelido")
        equipa = ""
        if modo == "Open Day + Challenge":
            equipa = st.text_input("👥 Nome da Equipa (obrigatório para Challenge)", key="form_equipa")
        else:
            equipa = "—"

        if st.button("✅ Confirmar Inscrição"):
            # validações
            if not nome or not apelido or not st.session_state.email:
                st.warning("Preenche Nome, Apelido e verifica o Email.")
            elif modo == "Open Day + Challenge" and (not equipa or equipa.strip() == ""):
                st.warning("Para participar no Challenge, indica o Nome da Equipa.")
            else:
                # validar limite de 2 por equipa (se aplicável)
                if modo == "Open Day + Challenge":
                    count_equipa = sum(1 for r in registros if str(r.get("Nome da Equipa","")).strip().lower() == equipa.strip().lower())
                    if count_equipa >= 2:
                        st.error(f"⚠️ A equipa '{equipa}' já atingiu o limite de 2 alunos.")
                        st.stop()

                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    nome.strip(),
                    apelido.strip(),
                    st.session_state.email.strip(),
                    "Sim" if modo == "Open Day + Challenge" else "Não",
                    equipa.strip() if equipa else "—",
                    datahora
                )

                # email confirmação
                assunto = "Confirmação de inscrição no IBM Journey | 02/12"
                mensagem = f"""Olá {nome},

A tua inscrição foi registada com sucesso!

Modo: {modo}
Nome da Equipa: {equipa if equipa else '—'}
Data/Hora: {datahora}

Se quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}
"""
                enviar_email(st.session_state.email, assunto, mensagem)

                st.success("Inscrição registada com sucesso! Recebeste um email de confirmação.")
                # limpar estado
                st.session_state.email_checked = False
                st.session_state.email = ""
                st.session_state.existing_user = None
                st.session_state.action = "done"
                st.experimental_rerun()

    # -----------------------
    # CASO: Email já existe -> mostrar e oferecer alteração
    # -----------------------
    elif existente is not None and st.session_state.action in ("update", "idle"):
        nome_reg = existente.get("Nome","")
        apelido_reg = existente.get("Apelido","")
        participa_reg = str(existente.get("Participa Challenge","")).strip().lower()
        equipa_reg = existente.get("Nome da Equipa","") or "—"
        modo_atual = "Open Day + Challenge" if participa_reg == "sim" else "Open Day only"

        st.success(f"✅ Registo encontrado para: {nome_reg} {apelido_reg} — Modo atual: **{modo_atual}**")
        st.write("")  # espaçamento

        # Oferecer ações: atualizar (apenas 1 botão) ou cancelar
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("🔄 Alterar inscrição"):
                st.session_state.action = "perform_update"
                st.experimental_rerun()
        with col2:
            if st.button("🗑️ Cancelar inscrição"):
                apagado = apagar_registo(st.session_state.email)
                if apagado:
                    # enviar email de cancelamento (já usavas no unenroll)
                    assunto = "Cancelamento de inscrição no IBM Journey | 02/12"
                    mensagem = f"""Olá {apagado.get('Nome','')},

A tua inscrição foi cancelada.

Nome da Equipa: {apagado.get('Nome da Equipa','—')}

Se quiseres voltar a inscrever-te, acede a: {st.secrets['APP_URL']}
"""
                    enviar_email(st.session_state.email, assunto, mensagem)
                    st.success("🛑 Inscrição cancelada e email enviado.")
                else:
                    st.info("⚠️ Não foi possível apagar o registo (não encontrado).")
                # limpar estado
                st.session_state.email_checked = False
                st.session_state.email = ""
                st.session_state.existing_user = None
                st.session_state.action = "done"
                st.experimental_rerun()

    # -----------------------
    # CASO: utilizador escolheu "Alterar inscrição" -> mostrar form de alteração
    # -----------------------
    elif existente is not None and st.session_state.action == "perform_update":
        # Recarregar registo (garantir fresh)
        registros = carregar_registos()
        existente = next((r for r in registros if str(r.get("Email","")).strip().lower() == st.session_state.email.strip().lower()), None)
        if not existente:
            st.error("Erro: registo já não existe.")
            st.session_state.email_checked = False
            st.experimental_rerun()

        modo_atual = "Open Day + Challenge" if str(existente.get("Participa Challenge","")).strip().lower() == "sim" else "Open Day only"
        st.subheader("Alterar Inscrição")
        st.write(f"Modo atual: **{modo_atual}**")
        novo_modo = st.selectbox("Seleciona o novo modo:", ["Open Day only", "Open Day + Challenge"], index=0 if modo_atual=="Open Day only" else 1)

        # Se está a subir para Challenge, pedir apenas Nome da Equipa (nome/apelido já existem no registo)
        equipa_nova = existente.get("Nome da Equipa","")
        if modo_atual == "Open Day only" and novo_modo == "Open Day + Challenge":
            equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="update_equipa")
        elif modo_atual == "Open Day + Challenge" and novo_modo == "Open Day only":
            st.caption("A mudança para 'Open Day only' não exige Nome da Equipa.")

        if st.button("✅ Confirmar atualização"):
            # validades
            if novo_modo == "Open Day + Challenge" and (not equipa_nova or equipa_nova.strip()==""):
                st.warning("Para participar no Challenge é obrigatório indicar o Nome da Equipa.")
                st.stop()

            # validar limite de 2 por equipa (se aplicável)
            if novo_modo == "Open Day + Challenge":
                registros = carregar_registos()
                count = sum(1 for r in registros if str(r.get("Nome da Equipa","")).strip().lower() == equipa_nova.strip().lower())
                # se já existe o próprio na equipa atual (mesmo email), esse registo vai ser apagado e regravado,
                # então -1 na contagem para permitir a substituição
                if existente.get("Nome da Equipa","").strip().lower() == equipa_nova.strip().lower():
                    pass  # mesma equipa — não bloquear
                elif count >= 2:
                    st.error(f"⚠️ A equipa '{equipa_nova}' já atingiu o limite de 2 alunos.")
                    st.stop()

            # apagar registo antigo e gravar novo
            apagado = apagar_registo(st.session_state.email)  # retorna dict do apagado
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            guardar_registo(
                existente.get("Nome",""),
                existente.get("Apelido",""),
                existente.get("Email",""),
                "Sim" if novo_modo == "Open Day + Challenge" else "Não",
                (equipa_nova.strip() if novo_modo == "Open Day + Challenge" else "—"),
                datahora
            )

            # enviar email de atualização com o modo atual (conforme pediste)
            assunto = "IBM Journey | Inscrição atualizada"
            mensagem = f"""Olá {existente.get('Nome','')},

A tua inscrição foi atualizada.

Novo modo: {novo_modo}
Nome da Equipa: {(equipa_nova if novo_modo == "Open Day + Challenge" else "—")}
Data/Hora: {datahora}

Se quiseres fazer mais alterações, visita: {st.secrets['APP_URL']}
"""
            enviar_email(st.session_state.email, assunto, mensagem)

            st.success(f"✅ A tua inscrição foi atualizada para **{novo_modo}** e o email de confirmação foi enviado.")
            # limpar estado
            st.session_state.email_checked = False
            st.session_state.email = ""
            st.session_state.existing_user = None
            st.session_state.action = "done"
            st.experimental_rerun()

# -------------------------
# Expander: Unenroll / Buscar por email (opcional)
# -------------------------
st.write("---")
with st.expander("❌ Cancelar inscrição / Verificar registo (Pesquisar por email)"):
    procura = st.text_input("📧 Email para procurar", key="unenroll_search")
    if st.button("Pesquisar"):
        if not procura:
            st.warning("Introduz um email para pesquisar.")
        else:
            registros = carregar_registos()
            reg = next((r for r in registros if str(r.get("Email","")).strip().lower() == procura.strip().lower()), None)
            if not reg:
                st.info("⚠️ Nenhum registo encontrado com esse email.")
            else:
                modo_reg = "Open Day + Challenge" if str(reg.get("Participa Challenge","")).strip().lower() == "sim" else "Open Day only"
                st.success(f"Registo encontrado: {reg.get('Nome','')} {reg.get('Apelido','')} — {modo_reg}")
                if st.button("🗑️ Cancelar este registo"):
                    apag = apagar_registo(procura)
                    if apag:
                        st.info("Registo apagado com sucesso.")
                        assunto = "IBM Journey | Inscrição cancelada"
                        mensagem = f"""Olá {apag.get('Nome','')},

A tua inscrição foi cancelada.

Se quiseres voltar a inscrever-te: {st.secrets['APP_URL']}
"""
                        enviar_email(procura, assunto, mensagem)
                    else:
                        st.error("Erro ao apagar o registo.")

# -------------------------
# Rodapé / estado final
# -------------------------
st.write("")

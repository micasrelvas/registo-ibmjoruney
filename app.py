import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

st.set_page_config(page_title="Registo de Presenças - Teste", layout="centered")
st.title("📚 Registo de Presença - Aula (Teste)")

# --- Dados temporários em memória ---
if "registos" not in st.session_state:
    st.session_state.registos = pd.DataFrame(columns=["Aula", "Nome", "Apelido", "Email", "Equipa", "DataHora"])

# --- Inputs do aluno ---
st.subheader("📝 Registo / Cancelamento de presença")
nome = st.text_input("👤 Nome")
apelido = st.text_input("👤 Apelido")
email = st.text_input("📧 Email")
equipa = st.text_input("👥 Equipa")
aula = st.text_input("📘 Nome da Aula")

col1, col2 = st.columns(2)

# Confirmar presença
with col1:
    if st.button("✅ Confirmar Presença"):
        if nome and apelido and email and equipa and aula:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [aula, nome, apelido, email, equipa, datahora]
            st.success(f"Presença registada para {nome} {apelido}!")
            
            # Gerar QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(f"{nome} {apelido} - {aula}")
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            buf = BytesIO()
            img.save(buf)
            st.image(buf)
        else:
            st.warning("Preenche todos os campos!")

# Cancelar presença
with col2:
    if st.button("❌ Cancelar Presença"):
        mask = ~((st.session_state.registos["Email"] == email) & (st.session_state.registos["Aula"] == aula))
        st.session_state.registos = st.session_state.registos[mask]
        st.info(f"Registo cancelado para {email} na aula {aula}")

# --- Mostrar tabela de registos ---
st.subheader("📋 Registos atuais (em memória)")
st.dataframe(st.session_state.registos)

# --- Dashboard do professor ---
st.subheader("📊 Dashboard do Professor")
if not st.session_state.registos.empty:
    st.write("**Número de alunos por aula:**")
    count_aulas = st.session_state.registos.groupby("Aula")["Email"].count().reset_index()
    count_aulas.columns = ["Aula", "Número de alunos"]
    st.table(count_aulas)

    st.write("**Número de alunos por equipa:**")
    count_equipa = st.session_state.registos.groupby("Equipa")["Email"].count().reset_index()
    count_equipa.columns = ["Equipa", "Número de alunos"]
    st.table(count_equipa)
else:
    st.info("Ainda não há registos para mostrar no dashboard.")

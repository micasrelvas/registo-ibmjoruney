import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="IBM Journey - Registo", layout="centered")
st.title("Bem-vindo ao IBM Journey powered by Timestamp - Se queres aprender a fazer agentes de forma rápida e com a melhor tecnologia do mercado, inscreve-te")

# --- Dados temporários em memória ---
if "registos" not in st.session_state:
    st.session_state.registos = pd.DataFrame(columns=["Nome", "Apelido", "Email", "Equipa", "DataHora"])

# --- Inputs do aluno ---
st.subheader("📝 Registo / Cancelamento de presença")
nome = st.text_input("👤 Nome")
apelido = st.text_input("👤 Apelido")
email = st.text_input("📧 Email")
equipa = st.text_input("👥 Equipa")

col1, col2 = st.columns(2)

# Confirmar presença
with col1:
    if st.button("✅ Confirmar Presença"):
        if nome and apelido and email and equipa:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [nome, apelido, email, equipa, datahora]
            st.success(f"Presença registada para {nome} {apelido}!")
        else:
            st.warning("Preenche todos os campos!")

# Cancelar presença
with col2:
    if st.button("❌ Cancelar Presença"):
        mask = ~((st.session_state.registos["Email"] == email))
        st.session_state.registos = st.session_state.registos[mask]
        st.info(f"Registo cancelado para {email}")

# --- Mostrar tabela de registos ---
st.subheader("📋 Registos atuais (em memória)")
st.dataframe(st.session_state.registos)

# --- Dashboard do professor ---
st.subheader("📊 Dashboard do Professor")
if not st.session_state.registos.empty:
    st.write("**Número de alunos por equipa:**")
    count_equipa = st.session_state.registos.groupby("Equipa")["Email"].count().reset_index()
    count_equipa.columns = ["Equipa", "Número de alunos"]
    st.table(count_equipa)
else:
    st.info("Ainda não há registos para mostrar no dashboard.")

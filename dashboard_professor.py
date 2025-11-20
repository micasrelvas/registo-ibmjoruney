import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Configuração da página ---
st.set_page_config(page_title="IBM Journey - Dashboard", layout="wide")
st.markdown("<h1>📊 IBM Journey - Dashboard do Professor</h1>", unsafe_allow_html=True)
st.markdown("<p>Visualiza todas as inscrições e estatísticas das equipas.</p>", unsafe_allow_html=True)

# --- Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["GOOGLE_SERVICE_ACCOUNT"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

def carregar_registos():
    data = sheet.get_all_records()
    if len(data) == 0:
        return pd.DataFrame(columns=["Nome","Apelido","Email","Equipa","DataHora"])
    return pd.DataFrame(data)

# --- Carregar dados ---
df = carregar_registos()

# --- Mostrar dados ---
if df.empty:
    st.info("Ainda não há inscrições para mostrar.")

else:
    st.markdown("### 🤖 Alunos inscritos")
    st.dataframe(df[["Nome", "Apelido", "Email", "Equipa", "DataHora"]])

    st.markdown("### 🚀 Número de alunos por equipa")

    # Mostrar nomes das colunas para debugging
    #st.write("📌 Colunas no DataFrame:", df.columns.tolist())

    # Agrupar e contar
    count_equipa = (
        df.groupby("Equipa")
          .size()
          .reset_index(name="Número de alunos")
    )

    #st.markdown("### 📊 Tabela de equipas e contagem")
    st.dataframe(count_equipa)

    # Validar máximo de 2 alunos por equipa
    over_limit = count_equipa[count_equipa["Número de alunos"] > 2]
    if not over_limit.empty:
        st.error("⚠️ Há equipas com mais de 2 alunos inscritos!")
        st.write(over_limit)

    # Gráfico
    #st.bar_chart(count_equipa.set_index("Equipa"))

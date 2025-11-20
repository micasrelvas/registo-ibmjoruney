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
    st.dataframe(df[["Nome", "Apelido", "Equipa", "DataHora"]])

    st.markdown("### 🚀 Número de alunos por equipa")

    # Debug: see what columns exist
    st.write("Columns in DF:", df.columns.tolist())
    st.write(df.head())

    # Group by Equipa
    count_equipa = df.groupby("Equipa")["Email"].count().reset_index()
    count_equipa.columns = ["Equipa", "Número de alunos"]

    st.bar_chart(count_equipa.set_index("Equipa"))

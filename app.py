import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurações do Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "service_account.json"  # chave do Google API
SHEET_NAME = "Presencas_Aulas"

gc = gspread.service_account(filename=CREDS_FILE)
sheet = gc.open(SHEET_NAME).sheet1

# Streamlit page
st.set_page_config(page_title="Registo de Presenças", page_icon="📚", layout="centered")
st.title("📚 Registo de Presença - Aula")

# --- Inputs ---
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
            sheet.append_row([aula, nome, apelido, email, equipa, datahora])
            st.success(f"Presença registada para {nome} {apelido}!")
        else:
            st.warning("Preenche todos os campos!")

# Cancelar presença
with col2:
    if st.button("❌ Cancelar Presença"):
        all_values = sheet.get_all_values()
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
        mask = (df['Email'] != email) | (df['Aula'] != aula)
        df_new = df[mask]
        # Limpa e reescreve
        sheet.clear()
        sheet.append_row(all_values[0])
        for row in df_new.values.tolist():
            sheet.append_row(row)
        st.info(f"Registo cancelado para {email} na aula {aula}")

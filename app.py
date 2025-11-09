import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# --- Página ---
st.set_page_config(page_title="IBM Journey - Registo", layout="wide")

# --- CSS personalizado ---
st.markdown(
    """
    <style>
    /* Fundo e cores principais */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    /* Cores dos títulos */
    h1, h2, h3 {
        color: #00bfff;
    }
    /* Botões */
    .stButton>button {
        background-color: #00bfff;
        color: #ffffff;
        font-weight: bold;
    }
    /* Tabela */
    .stDataFrame th {
        background-color: #1f1f1f;
        color: #ffffff;
    }
    .stDataFrame td {
        background-color: #2c2c2c;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Título ---
st.markdown("<h1>🚀 IBM Journey powered by Timestamp</h1>", unsafe_allow_html=True)
st.markdown("<p>Aprende a criar agentes com a melhor tecnologia do mercado!</p>", unsafe_allow_html=True)

import streamlit as st

# --- About IBM ---
with st.expander("💡 About IBM", expanded=False):
    st.markdown("""
IBM, a pioneer in the tech industry, has been at the forefront of innovation for decades. Their contributions span across various fields, including AI, cloud computing, and quantum computing. IBM's cutting-edge technology and research continue to drive advancements in multiple sectors:

• **AI and Machine Learning:** Leading the charge in AI development with powerful tools and models.  
• **Cloud Solutions:** Providing scalable and flexible cloud services.  
• **Quantum Computing:** Pushing the boundaries of computing with quantum technology.  
• **Research and Development:** Continuously advancing technology with extensive research and high-quality datasets.  
• **Open-Source Commitment:** Promoting collaboration and innovation through open-source projects.
""")

# --- About Timestamp ---
with st.expander("💡 About Timestamp", expanded=False):
    st.markdown("""
Timestamp, provide innovative solutions and services in both national and international markets. The Timestamp Group integrates several Portuguese-owned companies, built around the principles of **excellence** and **knowledge sharing**.

They focus on **technological leadership**, based on quality, certifications, and continuous training, which is also reflected in the development and delivery of the innovative services we provide globally.

Their operations rely on a **network of competencies** formed by their teams and a set of partnerships with other national and international companies.  
Timestamp goal is to create an extended hub of highly specialized skills, allowing them to respond with quality and rigor to the challenges posed by each project and every organization they collaborate with.
""")

# --- Technology ---
with st.expander("⚙️ Technology", expanded=False):
    st.markdown("""
The IBM Journey leverages cutting-edge technologies such as **watsonx Orchestrate** to develop agentic AI solutions that connect apps, tools, and workflows. Participants will explore automation, digital skills, integrations, and AI orchestration in real-world scenarios.

### 📚 Resources to Explore
In preparation, explore these resources:

- [Product Overview](https://www.ibm.com/products/watsonx-orchestrate)  
- [Demo Experience](https://www.ibm.com/products/watsonx-orchestrate/demos)  
- [Integrations](https://www.ibm.com/products/watsonx-orchestrate/integrations)  
- [Resources & Support](https://www.ibm.com/products/watsonx-orchestrate/resources)
""")


# --- Challenge ---
with st.expander("🚀 Challenge: Build the Next Generation of Agentic AI", expanded=False):
    st.markdown("""
Your challenge is to design and develop an AI agent powered by **IBM watsonx Orchestrate** that helps people and businesses achieve more with less effort. By combining digital skills, integrations, and workflow automation, participants will create agents that can act, decide, and collaborate in real-world scenarios.

### What’s Expected?
• **Harness watsonx Orchestrate:** Use its orchestration features, integrations, and digital skills to build agents that connect across apps, tools, and workflows.  
• **Focus on Real-World Impact:** Create agents that solve common pain points in areas such as HR, sales, customer service, finance, or procurement.  
• **Innovate for the Future of Work:** Demonstrate how agentic AI can augment human potential, reduce friction, and redefine productivity.

### Inspiration & Use Cases
Explore how watsonx Orchestrate is already being applied:  
• **Customer Service:** Deliver faster responses, automate ticket handling, and improve customer experiences.  
• **Finance:** Streamline approvals, reporting, and risk analysis to enhance financial operations.  
• **HR:** Simplify onboarding, manage employee requests, and improve HR efficiency.  
• **Procurement:** Automate supplier management, purchase orders, and procurement cycles.  
• **Sales:** Support sales teams with CRM updates, scheduling, and lead follow-up.
""")

# --- Prizes ---
with st.expander("🏆 Prizes", expanded=False):
    st.markdown("### What you can win!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
🥇 **Winning Team Experience**  
A unique professional experience during the **last fortnight of June**.  
Get hands-on exposure to real-world projects and accelerate your career!
""")

    with col2:
        st.markdown("""
🎖️ **Participation Rewards**  
All participating teams receive a **Certificate of Participation** and **exclusive merchandising**, celebrating your journey and achievements in innovation and AI.
""")



# --- Dados temporários em memória ---
if "registos" not in st.session_state:
    st.session_state.registos = pd.DataFrame(columns=["Nome", "Apelido", "Email", "Equipa", "DataHora"])

# --- Função para enviar email ---
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

# --- Inputs em expansores ---
with st.expander("📝 Registo de Presença", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome")
        apelido = st.text_input("👤 Apelido")
    with col2:
        email = st.text_input("📧 Email")
        equipa = st.text_input("👥 Equipa")
    
    if st.button("✅ Confirmar Presença"):
        if not all([nome, apelido, email, equipa]):
            st.warning("Todos os campos são obrigatórios para registar a presença.")
        else:
            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.registos.loc[len(st.session_state.registos)] = [nome, apelido, email, equipa, datahora]
            st.success(f"🤖 Presença registada para {nome} {apelido}!")
            
            # Enviar email de confirmação
            assunto = "Confirmação de registo no IBM Journey"
            mensagem = f"""Olá {nome},

O teu registo no IBM Journey foi confirmado com sucesso!

Equipa: {equipa}
Data/Hora: {datahora}
"""
            enviar_email(email, assunto, mensagem)

# --- Cancelamento apenas com email ---
with st.expander("❌ Cancelamento de Presença"):
    email_cancel = st.text_input("📧 Email para cancelar registo")

    if st.button("Cancelar Presença"):
        if not email_cancel:
            st.warning("O campo Email é obrigatório para cancelar a presença.")
        else:
            registro = st.session_state.registos[st.session_state.registos["Email"] == email_cancel]
            if registro.empty:
                st.info(f"⚠️ Nenhum registo encontrado para {email_cancel}.")
            else:
                # Pega nome e equipa antes de remover
                nome_c = registro.iloc[0]["Nome"]
                equipa_c = registro.iloc[0]["Equipa"]

                # Remove o registo
                st.session_state.registos = st.session_state.registos[st.session_state.registos["Email"] != email_cancel]
                st.info(f"🛑 Registo cancelado para {email_cancel}")

                # Enviar email de cancelamento
                assunto = "Cancelamento de registo no IBM Journey"
                mensagem = f"""Olá {nome_c},

O teu registo no IBM Journey foi cancelado.

Equipa: {equipa_c}
"""
                enviar_email(email_cancel, assunto, mensagem)

# --- Dashboard do professor ---
with st.expander("📊 Dashboard do Professor", expanded=True):
    if not st.session_state.registos.empty:
        st.markdown("### 🤖 Alunos inscritos")
        st.dataframe(st.session_state.registos[["Nome", "Apelido", "Equipa", "DataHora"]])

        st.markdown("### 🚀 Número de alunos por equipa")
        count_equipa = st.session_state.registos.groupby("Equipa")["Email"].count().reset_index()
        count_equipa.columns = ["Equipa", "Número de alunos"]
        st.bar_chart(count_equipa.set_index("Equipa"))
    else:
        st.info("Ainda não há registos para mostrar no dashboard.")

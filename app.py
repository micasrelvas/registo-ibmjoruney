# -------------------------------
# 2️⃣ OpenDay Enroll
# -------------------------------
with st.expander("2️⃣ OpenDay Enroll", expanded=False):
    # Sempre mostrar o email + botão verificar
    email = st.text_input("📧 Introduz o teu Email", key="en_email")

    if st.button("🔍 Verificar email"):
        if not email.strip():
            st.warning("O campo Email é obrigatório.")
            st.stop()

        registros = carregar_registos()
        registro_existente = next(
            (r for r in registros if str(r.get("Email","")).strip().lower() == email.strip().lower()), None
        )

        st.session_state.email_verificado = True
        st.session_state.registro_existente = registro_existente

    # Se já clicou em "Verificar email", mostrar formulário apropriado
    if st.session_state.get("email_verificado", False):
        registro_existente = st.session_state.get("registro_existente", None)

        if registro_existente is None:
            # Novo registo
            st.info("💡 Email não registado. Preenche os dados para a inscrição.")

            modo = st.radio(
                "Select one option:",
                ["Attend Open Day only", "Attend Open Day + Participate in the Challenge"],
                key="modo_escolhido"
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

            if st.button("✅ Confirm enrollment"):
                if not all([nome, apelido]):
                    st.warning("Todos os campos exceto Nome da Equipa são obrigatórios.")
                    st.stop()
                if modo == "Attend Open Day + Participate in the Challenge" and not equipa:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
                    st.stop()
                datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registo(
                    nome,
                    apelido,
                    email,
                    "Sim" if modo == "Attend Open Day + Participate in the Challenge" else "Não",
                    equipa if modo == "Attend Open Day + Participate in the Challenge" else "—",
                    datahora
                )
                st.success(f"{nome}, a tua inscrição foi confirmada! (Mode: {modo})")
                enviar_email(
                    email,
                    "IBM Journey | Confirmação de inscrição",
                    f"Olá {nome},\n\nA tua inscrição foi confirmada.\nMode: {modo}\nTeam: {equipa if equipa else '—'}\n\nSe quiseres cancelar ou atualizar a inscrição, acede: {st.secrets['APP_URL']}"
                )

        else:
            # Email já existe
            modo_atual = "Attend Open Day + Participate in the Challenge" if str(registro_existente.get("Participa Challenge","")).strip().lower() == "sim" else "Attend Open Day only"
            st.warning(f"⚠️ O email já está registado para **{modo_atual}**.")
            st.info(f"Queres atualizar a inscrição para o outro modo?")

            novo_modo = "Attend Open Day only" if modo_atual == "Attend Open Day + Participate in the Challenge" else "Attend Open Day + Participate in the Challenge"
            equipa_nova = ""
            if novo_modo == "Attend Open Day + Participate in the Challenge":
                equipa_nova = st.text_input("👥 Nome da Equipa (obrigatório)", key="update_team")
                equipa_nova = equipa_nova.strip().title() if equipa_nova else ""

            if st.button("🔄 Confirm update"):
                if novo_modo == "Attend Open Day + Participate in the Challenge" and not equipa_nova:
                    st.warning("Nome da Equipa é obrigatório para o Challenge.")
                    st.stop()
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
                st.success(f"✅ A tua inscrição foi atualizada para **{novo_modo}**")
                enviar_email(
                    email,
                    "IBM Journey | Inscrição atualizada",
                    f"Olá {registro_existente.get('Nome','')},\n\nA tua inscrição foi atualizada.\nPrevious mode: {modo_atual}\nNew mode: {novo_modo}\nTeam: {equipa_nova if equipa_nova else '—'}"
                )

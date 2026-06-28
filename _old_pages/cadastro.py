import streamlit as st
from database import criar_usuario

st.title("🆕 Cadastro")

usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Criar conta"):
    if usuario and senha:

        if criar_usuario(usuario, senha):
            st.success("Conta criada com sucesso!")

            # 👉 leva para login
            st.switch_page("pages/login.py")

        else:
            st.error("Usuário já existe")

    else:
        st.warning("Preencha todos os campos")
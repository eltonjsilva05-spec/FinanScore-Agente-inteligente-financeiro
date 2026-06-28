import streamlit as st

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

from database import (
    listar_receitas_usuario,
    listar_despesas_usuario
)

usuario = st.session_state["usuario"]

st.title("Histórico")

st.subheader("Receitas")
st.table(listar_receitas_usuario(usuario))

st.subheader("Despesas")
st.table(listar_despesas_usuario(usuario))
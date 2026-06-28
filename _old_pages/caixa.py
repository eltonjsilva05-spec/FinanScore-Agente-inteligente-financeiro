import streamlit as st

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

from database import soma_receitas_usuario, soma_despesas_usuario, formatar_brl

usuario = st.session_state["usuario"]

st.title("📊 Caixa")

r = soma_receitas_usuario(usuario)
d = soma_despesas_usuario(usuario)

st.metric("Receitas", formatar_brl(r))
st.metric("Despesas", formatar_brl(d))
st.metric("Saldo", formatar_brl(r - d))
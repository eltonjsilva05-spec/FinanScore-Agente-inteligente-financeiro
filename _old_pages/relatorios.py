import streamlit as st
from database import listar_despesas_usuario

# =========================
# SEGURANÇA
# =========================
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

st.title("📊 Relatórios")

usuario = st.session_state["usuario"]

# =========================
# DADOS
# =========================
dados = listar_despesas_usuario(usuario)

if not dados:
    st.info("Sem dados ainda")
    st.stop()

# =========================
# AGRUPAR POR CATEGORIA
# =========================
resumo = {}

for d in dados:
    categoria = d[1]  # descricao (estrutura atual ainda usa isso)
    valor = d[2]

    resumo[categoria] = resumo.get(categoria, 0) + valor

# =========================
# GRÁFICO
# =========================
st.subheader("📊 Gastos por categoria")

st.bar_chart(resumo)
import streamlit as st
from database import (
    soma_receitas_usuario,
    soma_despesas_usuario,
    listar_despesas_usuario
)
import pandas as pd

# =========================
# SEGURANÇA
# =========================
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

st.title("🏦 Dashboard Financeiro")

usuario = st.session_state["usuario"]

# =========================
# DADOS PRINCIPAIS
# =========================
receitas = soma_receitas_usuario(usuario)
despesas = soma_despesas_usuario(usuario)
saldo = receitas - despesas

# =========================
# KPIs (CARDS)
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Receitas", f"R$ {receitas:.2f}")
col2.metric("💸 Despesas", f"R$ {despesas:.2f}")
col3.metric("📊 Saldo", f"R$ {saldo:.2f}")

st.divider()

# =========================
# ALERTA FINANCEIRO (IA SIMPLES)
# =========================
if saldo < 0:
    st.error("⚠️ Você está no negativo!")
elif saldo < receitas * 0.2:
    st.warning("⚠️ Seu saldo está baixo, atenção aos gastos")
else:
    st.success("✅ Sua saúde financeira está boa")

st.divider()

# =========================
# GASTOS POR CATEGORIA
# =========================
dados = listar_despesas_usuario(usuario)

if dados:
    resumo = {}

    for d in dados:
        categoria = d[1]  # descrição atual usada como categoria base
        valor = d[2]

        resumo[categoria] = resumo.get(categoria, 0) + valor

    st.subheader("📊 Gastos por Categoria")
    st.bar_chart(resumo)
else:
    st.info("Sem despesas cadastradas")

st.divider()

# =========================
# TOP GASTOS
# =========================
if dados:
    st.subheader("🔥 Top gastos recentes")

    df = pd.DataFrame(dados, columns=["ID", "Descrição", "Valor", "Data"])

    df = df.sort_values(by="Valor", ascending=False).head(5)

    st.table(df[["Descrição", "Valor", "Data"]])
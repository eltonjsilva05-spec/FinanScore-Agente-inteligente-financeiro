import streamlit as st
import pandas as pd
from database import conectar

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

st.title("📊 Dashboard Financeiro")

usuario = st.session_state["usuario"]

conn = conectar()
cursor = conn.cursor()

cursor.execute("""
    SELECT categoria, SUM(valor)
    FROM despesas
    WHERE usuario = ?
      AND categoria IS NOT NULL
      AND categoria != ''
    GROUP BY categoria
    ORDER BY SUM(valor) DESC
""", (usuario,))

dados = cursor.fetchall()
conn.close()

if not dados:
    st.info("Cadastre despesas com categoria para visualizar os gráficos.")
    st.stop()

df = pd.DataFrame(dados, columns=["Categoria", "Valor"])

st.subheader("💸 Gastos por Categoria")
st.bar_chart(df.set_index("Categoria"))

st.subheader("📋 Resumo")

for _, linha in df.iterrows():
    valor_formatado = (
        f"R$ {linha['Valor']:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    st.write(f"**{linha['Categoria']}** → {valor_formatado}")
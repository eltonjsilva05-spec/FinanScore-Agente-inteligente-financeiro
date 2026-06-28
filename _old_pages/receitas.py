import streamlit as st
from datetime import datetime
from database import conectar, deletar_receita

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

usuario = st.session_state["usuario"]

st.title("Receitas")

descricao = st.text_input("Descrição")
valor_txt = st.text_input("Valor (ex: 1.000,00)")

def converter(v):
    try:
        return float(v.replace(".", "").replace(",", "."))
    except:
        return 0.0

valor = converter(valor_txt)

if st.button("Salvar"):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO receitas (usuario, descricao, valor, data)
        VALUES (?, ?, ?, ?)
    """, (usuario, descricao, valor, datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()

    st.success("Receita salva!")

st.divider()
st.subheader("Receitas cadastradas")

conn = conectar()
cur = conn.cursor()
cur.execute("SELECT id, descricao, valor FROM receitas WHERE usuario = ?", (usuario,))
dados = cur.fetchall()
conn.close()

for id_, desc, val in dados:
    col1, col2, col3 = st.columns([3,2,1])

    col1.write(desc)
    col2.write(val)

    if col3.button("🗑", key=f"r_{id_}"):
        deletar_receita(id_)
        st.rerun()
import streamlit as st
from datetime import datetime
from database import conectar, deletar_despesa

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

usuario = st.session_state["usuario"]

st.title("💸 Despesas")

categoria = st.selectbox(
    "Categoria",
    [
        "Moradia",
        "Alimentação",
        "Transporte",
        "Lazer",
        "Saúde",
        "Educação",
        "Outros"
    ]
)

descricao = st.text_input("Descrição")

valor_txt = st.text_input("Valor (ex: 1.000,00)")

def converter(v):
    try:
        return float(v.replace(".", "").replace(",", "."))
    except:
        return 0.0

valor = converter(valor_txt)

if st.button("Salvar"):

    if not descricao.strip():
        st.error("Informe uma descrição")
        st.stop()

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO despesas
        (usuario, categoria, descricao, valor, data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario,
        categoria,
        descricao,
        valor,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    st.success("Despesa salva!")
    st.rerun()

# ==========================
# LISTAGEM
# ==========================

st.divider()
st.subheader("Despesas cadastradas")

conn = conectar()
cur = conn.cursor()

cur.execute("""
    SELECT id, categoria, descricao, valor
    FROM despesas
    WHERE usuario = ?
    ORDER BY id DESC
""", (usuario,))

dados = cur.fetchall()

conn.close()

for id_, cat, desc, val in dados:

    col1, col2, col3, col4 = st.columns([2,3,2,1])

    col1.write(cat)
    col2.write(desc)
    col3.write(f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if col4.button("🗑", key=f"d_{id_}"):
        deletar_despesa(id_)
        st.rerun()
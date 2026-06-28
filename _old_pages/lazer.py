import streamlit as st

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

from datetime import datetime
import streamlit as st
from database import conectar

st.title("🎮 Controle de Lazer")

# ================= INPUTS =================
descricao = st.text_input("Descrição do gasto")
valor = st.number_input("Valor", min_value=0.0, format="%.2f")

# ================= BOTÃO =================
if st.button("Salvar Gasto de Lazer"):

    if not descricao.strip():
        st.error("Informe uma descrição.")

    elif valor <= 0:
        st.error("Informe um valor válido.")

    else:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO despesas (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)",
            (
                descricao,
                valor,
                datetime.now().strftime("%Y-%m-%d"),
                "Lazer"
            )
        )

        conn.commit()
        conn.close()

        st.success("Gasto de lazer salvo com sucesso!")
import streamlit as st

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

import streamlit as st

st.title("🎯 Metas Financeiras")

meta = st.number_input("Meta mensal", min_value=0.0, value=2000.0)
atual = st.number_input("Economizado até agora", min_value=0.0, value=0.0)

progresso = (atual / meta) if meta > 0 else 0

st.progress(min(progresso, 1.0))
st.write(f"{progresso*100:.1f}% concluído")
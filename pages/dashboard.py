import streamlit as st
from database import soma_receitas_usuario, obter_total_reserva, formatar_brl

if not st.session_state.get("logado"):
    st.switch_page("app.py")

u = st.session_state.usuario
nome = u["nome"] if isinstance(u, dict) else u

st.title("📊 Painel Financeiro")

# Cálculo da Reserva
receitas = soma_receitas_usuario(u)
reserva_atual = obter_total_reserva(nome)
meta_reserva = receitas * 0.10  # Define a meta como 10% das receitas

st.subheader("🏦 Caixa Reserva")
col1, col2 = st.columns(2)
col1.metric("Total Acumulado", formatar_brl(reserva_atual))
col2.metric("Meta (10% da Receita)", formatar_brl(meta_reserva))

# Barra de progresso visual
progresso = min(reserva_atual / meta_reserva, 1.0) if meta_reserva > 0 else 0
st.progress(progresso, text=f"Progresso da meta de reserva: {progresso*100:.1f}%")

if reserva_atual < meta_reserva:
    st.warning(f"⚠️ Faltam {formatar_brl(meta_reserva - reserva_atual)} para atingir sua meta de reserva.")
else:
    st.success("✅ Meta de reserva alcançada!")
import streamlit as st
from database import (
    soma_receitas_usuario,
    soma_despesas_usuario,
    formatar_brl
)
from utils.openai_service import perguntar_openai
from ai_advisor import gerar_resumo

# ==============================================================================
# CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(page_title="IA Financeira", page_icon="🤖", layout="wide")

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar esta página.")
    st.stop()

# Extração do nome de forma segura
usuario_obj = st.session_state.get("usuario")
nome_usuario = usuario_obj["nome"] if isinstance(usuario_obj, dict) else str(usuario_obj)

# ==============================================================================
# HIGIENIZAÇÃO DE DADOS
# ==============================================================================
receitas = float(soma_receitas_usuario(usuario_obj) or 0.0)
despesas = float(soma_despesas_usuario(usuario_obj) or 0.0)
saldo = receitas - despesas

resumo = gerar_resumo(receitas, despesas)
score = resumo.get('score', 0) if isinstance(resumo, dict) else 0
status = resumo.get('status', 'Sem dados') if isinstance(resumo, dict) else 'Sem dados'

# ==============================================================================
# UI
# ==============================================================================
st.title("🤖 IA Financeira")
st.caption("Seu assistente financeiro integrado ao FinanScore.")

col1, col2, col3 = st.columns(3)
col1.metric("Receitas", formatar_brl(receitas))
col2.metric("Despesas", formatar_brl(despesas))
col3.metric("Seu FinanScore", f"{score} pts")

st.info(f"📊 **Situação Atual:** {status}")

# ==============================================================================
# CHAT
# ==============================================================================
if "chat_ai" not in st.session_state:
    st.session_state.chat_ai = [{
        "role": "assistant",
        "content": f"Olá **{nome_usuario}**! 👋 Posso analisar suas finanças. O que gostaria de saber hoje?"
    }]

for msg in st.session_state.chat_ai:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

pergunta = st.chat_input("Pergunte algo sobre sua vida financeira...")

if pergunta:
    st.session_state.chat_ai.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    contexto = f"""
    DADOS DO USUÁRIO: {nome_usuario}
    Receitas: {formatar_brl(receitas)} | Despesas: {formatar_brl(despesas)}
    Saldo: {formatar_brl(saldo)} | Score: {score} | Risco: {status}
    """

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            resposta_ia = perguntar_openai(pergunta=pergunta, contexto=contexto)
            st.markdown(resposta_ia)

    st.session_state.chat_ai.append({"role": "assistant", "content": resposta_ia})
    st.rerun()
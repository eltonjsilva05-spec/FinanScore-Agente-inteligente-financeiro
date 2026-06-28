import streamlit as st
from datetime import datetime
from database import inserir_transacao, formatar_brl

# ==============================================================================
# SEGURANÇA E VALIDAÇÃO DE SESSÃO
# ==============================================================================
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

# Extração do nome do usuário
usuario_obj = st.session_state.get("usuario")
nome_usuario = usuario_obj["nome"] if isinstance(usuario_obj, dict) else str(usuario_obj)

st.title("💰 Novo Lançamento")
st.caption("Insira receitas ou despesas na sua conta.")
st.divider()

# ==============================================================================
# FORMULÁRIO DE ENTRADA
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f")

with col2:
    categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Salário", "Outros"])
    data = st.date_input("Data", datetime.today())

descricao = st.text_input("Descrição", placeholder="Ex: Mercado, Salário...")

st.divider()

# ==============================================================================
# PROCESSAMENTO E SALVAMENTO
# ==============================================================================
if st.button("💾 Registrar Transação", width='stretch'):
    if not descricao.strip():
        st.warning("⚠️ Insira uma descrição.")
    elif valor <= 0:
        st.warning("⚠️ O valor deve ser maior que zero.")
    else:
        # Chama a função unificada do database.py
        # Parâmetros: (usuario_nome, Data, Descrição, Categoria, Tipo, Valor)
        inserir_transacao(
            nome_usuario, 
            data.strftime("%Y-%m-%d"), 
            descricao.strip(), 
            categoria, 
            tipo, 
            valor
        )
        
        st.toast(f"✅ {tipo} de {formatar_brl(valor)} registrada!")
        st.rerun()
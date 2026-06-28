import streamlit as st
import pandas as pd
import sqlite3
from database import formatar_brl

st.set_page_config(page_title="Extrato - FinanScore", layout="wide")

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.error("🔐 Por favor, faça o login na página inicial (app.py) para acessar esta tela.")
    st.stop()

u = st.session_state.usuario
nome_busca = u["nome"] if isinstance(u, dict) else u

st.title("📄 Extrato Detalhado")
st.write(f"Histórico completo de lançamentos para: **{nome_busca}**")
st.divider()

# Conecta ao banco de dados de forma segura
conn = sqlite3.connect("finanscore.db")

# Consulta corrigida com os nomes exatos das colunas do banco (minúsculas e sem acento)
query = """
    SELECT data, descricao, categoria, tipo, valor 
    FROM transacoes 
    WHERE usuario = ? 
    ORDER BY data DESC
"""

try:
    df = pd.read_sql_query(query, conn, params=(nome_busca,))
finally:
    conn.close()

# Verifica se existem registros
if df.empty:
    st.info("ℹ️ Nenhuma transação encontrada para o seu usuário.")
else:
    # Cria uma cópia para formatação visual amigável
    df_exibicao = df.copy()
    
    # Aplica a formatação de moeda brasileira na coluna de valor
    df_exibicao["valor"] = df_exibicao["valor"].apply(formatar_brl)
    
    # Renomeia as colunas do DataFrame para exibição na tela
    df_exibicao.columns = ["Data", "Descrição", "Categoria", "Tipo", "Valor (R$)"]
    
    # Exibe a tabela formatada no Streamlit
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
import streamlit as st
import pandas as pd
import sqlite3
from database import formatar_brl

st.set_page_config(page_title="Histórico - FinanScore", layout="wide")

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.error("🔐 Por favor, faça o login na página inicial (app.py) para acessar esta tela.")
    st.stop()

u = st.session_state.usuario
nome_busca = u["nome"] if isinstance(u, dict) else u

st.title("🗂️ Histórico Avançado")
st.write(f"Visualização e auditoria de registros para: **{nome_busca}**")
st.divider()

# Conecta ao banco de dados
conn = sqlite3.connect("finanscore.db")

# Consulta 100% corrigida de acordo com os padrões da nova tabela
query_detalhada = """
    SELECT data, descricao, categoria, tipo, valor 
    FROM transacoes 
    WHERE usuario = ? 
    ORDER BY data DESC
"""

try:
    df = pd.read_sql_query(query_detalhada, conn, params=(nome_busca,))
finally:
    conn.close()

if df.empty:
    st.info("ℹ️ Nenhuma transação localizada no histórico deste usuário.")
else:
    df_exibicao = df.copy()
    
    # Formata a moeda para a exibição ficar profissional
    df_exibicao["valor"] = df_exibicao["valor"].apply(formatar_brl)
    
    # Define nomes limpos para o cabeçalho do painel
    df_exibicao.columns = ["Data de Lançamento", "Descrição do Item", "Categoria", "Tipo de Fluxo", "Valor Total"]
    
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
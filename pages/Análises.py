import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Análises Históricas & Banco de Dados")

# 1. Validação de Sessão e Blindagem de Tipo
if "usuario" not in st.session_state:
    st.error("Por favor, acesse a página inicial primeiro.")
    st.stop()

# Captura o usuário e garante que 'u' seja tratado corretamente
u = st.session_state.usuario

# Se 'u' for uma string (nome), transformamos em um dicionário para manter a compatibilidade
if isinstance(u, str):
    u = {"nome": u, "profissao": "N/A", "receitas": 0.0, "despesas": 0.0, "score": 0}

# 2. Conexão com o Banco de Dados
DB_PATH = "finascore.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_perfil (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registro TEXT,
            nome TEXT,
            profissao TEXT,
            receitas REAL,
            despesas REAL,
            score INTEGER
        )
    """)
    
    # Inserção segura
    try:
        data_atual = "2026-06-26"
        cursor.execute("""
            INSERT INTO historico_perfil (data_registro, nome, profissao, receitas, despesas, score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data_atual, 
            u.get("nome", "Usuário"), 
            u.get("profissao", "N/A"), 
            float(u.get("receitas", 0.0)), 
            float(u.get("despesas", 0.0)), 
            int(u.get("score", 0))
        ))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Erro ao salvar no banco: {e}")

    # 3. Leitura dos dados
    st.subheader("📈 Histórico de Sincronizações com o SQLite")
    df_banco = pd.read_sql_query("SELECT * FROM historico_perfil ORDER BY id DESC", conn)

if not df_banco.empty:
    st.dataframe(df_banco, width=None, use_container_width=True, hide_index=True)
    
    st.subheader("Evolução do FinanScore Gravado")
    fig_evolucao = px.line(
        df_banco, 
        x="id", 
        y="score", 
        title="Histórico de Alterações de Pontuação",
        markers=True
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)
else:
    st.info("Nenhum histórico encontrado no banco de dados ainda.")
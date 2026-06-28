import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from database import formatar_brl

st.set_page_config(page_title="Evolução Mensal - FinanScore", layout="wide")

# Garante que o usuário está logado antes de ver a página
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.error("🔐 Por favor, faça o login na página inicial (app.py) para acessar esta tela.")
    st.stop()

u = st.session_state.usuario
nome_busca = u["nome"] if isinstance(u, dict) else u

st.title("📈 Evolução Mensal Dinâmica")
st.write(f"Análise histórica dos fluxos de caixa do usuário: **{nome_busca}**")
st.divider()

# Conecta ao banco de dados para buscar o histórico
conn = sqlite3.connect("finanscore.db")

# Consulta corrigida: usando 'usuario' em vez de 'usuario_nome'
query = """
    SELECT 
        substr(data, 1, 7) as mes, 
        COALESCE(SUM(CASE WHEN tipo = 'Receita' THEN valor END), 0.0) as receitas, 
        COALESCE(SUM(CASE WHEN tipo = 'Despesa' THEN valor END), 0.0) as despesas 
    FROM transacoes 
    WHERE usuario = ? 
    GROUP BY mes 
    ORDER BY mes ASC
"""

try:
    df_evolucao = pd.read_sql_query(query, conn, params=(nome_busca,))
finally:
    conn.close()

# Verifica se existem dados históricos para o usuário
if df_evolucao.empty or (df_evolucao["receitas"].sum() == 0 and df_evolucao["despesas"].sum() == 0):
    st.info("ℹ️ Ainda não há histórico de lançamentos suficientes para gerar o gráfico de evolução mensal.")
else:
    # Calcula o saldo do mês e o acumulado histórico
    df_evolucao["saldo_mes"] = df_evolucao["receitas"] - df_evolucao["despesas"]
    df_evolucao["saldo_acumulado"] = df_evolucao["saldo_mes"].cumsum()

    # --- GRÁFICO DE LINHAS: EVOLUÇÃO ---
    st.subheader("📊 Linha de Tendência Financeira")
    
    # Derrete o DataFrame para o formato longo ideal para o Plotly Express
    df_longo = df_evolucao.melt(
        id_vars=["mes"], 
        value_vars=["receitas", "despesas", "saldo_acumulado"],
        var_name="Indicador", 
        value_name="Valor"
    )
    
    # Mapeamento de nomes amigáveis para a legenda
    nomes_legenda = {
        "receitas": "Receitas (Entradas)",
        "despesas": "Despesas (Saídas)",
        "saldo_acumulado": "Saldo Acumulado"
    }
    df_longo["Indicador"] = df_longo["Indicador"].map(nomes_legenda)

    fig_linha = px.line(
        df_longo, 
        x="mes", 
        y="Valor", 
        color="Indicador",
        markers=True,
        color_discrete_map={
            "Receitas (Entradas)": "#2ecc71",
            "Despesas (Saídas)": "#e74c3c",
            "Saldo Acumulado": "#3498db"
        }
    )
    
    fig_linha.update_layout(
        xaxis_title="Mês de Referência",
        yaxis_title="Valor (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_linha, use_container_width=True)
    
    st.divider()
    
    # --- TABELA DE SUPORTE CONSOLIDADA ---
    st.subheader("📋 Demonstrativo Consolidado por Período")
    
    df_exibicao = df_evolucao.copy()
    # Formata os valores numéricos para o padrão de moeda BRL antes de exibir na tabela
    df_exibicao["receitas"] = df_exibicao["receitas"].apply(formatar_brl)
    df_exibicao["despesas"] = df_exibicao["despesas"].apply(formatar_brl)
    df_exibicao["saldo_mes"] = df_exibicao["saldo_mes"].apply(formatar_brl)
    df_exibicao["saldo_acumulado"] = df_exibicao["saldo_acumulado"].apply(formatar_brl)
    
    df_exibicao.columns = ["Mês", "Total Receitas", "Total Despesas", "Resultado do Mês", "Patrimônio Acumulado"]
    
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
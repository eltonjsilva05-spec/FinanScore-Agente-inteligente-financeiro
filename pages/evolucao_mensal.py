import streamlit as st
import pandas as pd
import plotly.express as px
from database import conectar_bd, formatar_brl

# 1. Verifica se o usuário está logado
if "usuario" not in st.session_state or not st.session_state.get("logado", False):
    st.warning("⚠️ Por favor, faça o login na página inicial para acessar a Evolução Mensal.")
else:
    u = st.session_state["usuario"]
    
    # Tratamento para garantir o texto puro do username
    if isinstance(u, dict):
        nome_limpo = u.get("username", u.get("nome", "admin"))
    else:
        nome_limpo = str(u)

    st.markdown("<h2 style='font-weight: 700;'>📈 Evolução Mensal Financeira</h2>", unsafe_allow_html=True)
    st.write(f"Análise histórica mensal para o usuário: **{nome_limpo}**")
    st.divider()

    # 2. Conecta ao banco de dados para rodar a query do Pandas
    conn = conectar_bd()
    
    # CORREÇÃO DA QUERY: Mudado 'usuario = ?' para 'username = ?'
    query = """
    SELECT 
        substr(data, 1, 7) as mes, 
        COALESCE(SUM(CASE WHEN tipo = 'Receita' THEN valor END), 0.0) as receitas, 
        COALESCE(SUM(CASE WHEN tipo = 'Despesa' THEN valor END), 0.0) as despesas 
    FROM transacoes 
    WHERE username = ? 
    GROUP BY mes 
    ORDER BY mes ASC
    """
    
    try:
        # Executa a query corrigida passando o nome limpo
        df_evolucao = pd.read_sql_query(query, conn, params=(nome_limpo,))
        
        if not df_evolucao.empty and (df_evolucao['receitas'].sum() > 0 or df_evolucao['despesas'].sum() > 0):
            # Calcula o saldo mensal de cada linha do DataFrame
            df_evolucao['saldo'] = df_evolucao['receitas'] - df_evolucao['despesas']
            
            # Monta o gráfico de linhas com a evolução
            st.markdown("##### 📊 Gráfico de Tendência Mensal")
            fig_linha = px.line(
                df_evolucao, 
                x="mes", 
                y=["receitas", "despesas", "saldo"],
                labels={"mes": "Mês", "value": "Valor (R$)", "variable": "Indicador"},
                color_discrete_map={"receitas": "#2ecc71", "despesas": "#e74c3c", "saldo": "#3498db"}
            )
            fig_linha.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_linha, use_container_width=True)
            
            # Tabela de dados explicativa logo abaixo
            st.markdown("##### 📋 Dados Consolidados")
            df_tabela = df_evolucao.copy()
            df_tabela['receitas'] = df_tabela['receitas'].apply(formatar_brl)
            df_tabela['despesas'] = df_tabela['despesas'].apply(formatar_brl)
            df_tabela['saldo'] = df_tabela['saldo'].apply(formatar_brl)
            st.dataframe(df_tabela, use_container_width=True, hide_index=True)
            
        else:
            st.info("Nenhuma movimentação financeira encontrada para gerar o gráfico de evolução.")
            
    except Exception as e:
        st.error(f"Erro ao processar dados de evolução: {e}")
    finally:
        conn.close()
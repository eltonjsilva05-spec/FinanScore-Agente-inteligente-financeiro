import streamlit as st
import pandas as pd
from database import conectar_bd, formatar_brl

# 1. Verifica se o usuário está logado
if "usuario" not in st.session_state or not st.session_state.get("logado", False):
    st.warning("⚠️ Por favor, faça o login na página inicial para acessar o Histórico.")
else:
    u = st.session_state["usuario"]
    
    # Tratamento para garantir o texto puro do username
    if isinstance(u, dict):
        nome_limpo = u.get("username", u.get("nome", "admin"))
    else:
        nome_limpo = str(u)

    st.markdown("<h2 style='font-weight: 700;'>📜 Histórico de Lançamentos</h2>", unsafe_allow_html=True)
    st.write(f"Todos os registros salvos para: **{nome_limpo}**")
    st.divider()

    # 2. Conecta ao banco de dados
    conn = conectar_bd()
    
    # CORREÇÃO DA QUERY: Alterado 'usuario = ?' para 'username = ?'
    query_detalhada = """
    SELECT data, descricao, categoria, tipo, valor 
    FROM transacoes 
    WHERE username = ? 
    ORDER BY data DESC
    """
    
    try:
        # Executa a busca passando o nome tratado
        df = pd.read_sql_query(query_detalhada, conn, params=(nome_limpo,))
        
        if not df.empty:
            # Layout do Histórico em tabela simples e direta
            st.markdown("##### 🗂️ Registro Geral de Movimentações")
            
            df_historico = df.copy()
            df_historico["valor"] = df_historico["valor"].apply(formatar_brl)
            
            # Renomeia colunas para melhor legibilidade
            df_historico.columns = ["Data de Cadastro", "Descrição do Lançamento", "Categoria", "Tipo de Fluxo", "Valor Nominal"]
            
            # Exibe a tabela interativa do Streamlit
            st.dataframe(df_historico, use_container_width=True, hide_index=True)
            
            # Resumo rápido no rodapé do histórico
            total_itens = len(df)
            st.caption(f"Exibindo um total de {total_itens} transações indexadas neste banco de dados.")
            
        else:
            st.info("Nenhum histórico de transações foi encontrado para este perfil.")
            
    except Exception as e:
        st.error(f"Erro ao processar o histórico: {e}")
    finally:
        conn.close()
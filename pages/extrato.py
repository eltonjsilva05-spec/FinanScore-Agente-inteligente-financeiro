import streamlit as st
import pandas as pd
from database import conectar_bd, formatar_brl

# 1. Verifica se o usuário está logado
if "usuario" not in st.session_state or not st.session_state.get("logado", False):
    st.warning("⚠️ Por favor, faça o login na página inicial para acessar o Extrato.")
else:
    u = st.session_state["usuario"]
    
    # Tratamento para garantir o texto puro do username (evita o erro de 'dict')
    if isinstance(u, dict):
        nome_limpo = u.get("username", u.get("nome", "admin"))
    else:
        nome_limpo = str(u)

    st.markdown("<h2 style='font-weight: 700;'>📋 Extrato Detalhado</h2>", unsafe_allow_html=True)
    st.write(f"Histórico completo de lançamentos para: **{nome_limpo}**")
    st.divider()

    # 2. Conecta ao banco de dados
    conn = conectar_bd()
    
    # Query utilizando a coluna correta 'username'
    query = """
    SELECT data, descricao, categoria, tipo, valor 
    FROM transacoes 
    WHERE username = ? 
    ORDER BY data DESC
    """
    
    try:
        # Executa a busca passando o nome tratado
        df = pd.read_sql_query(query, conn, params=(nome_limpo,))
        
        if not df.empty:
            # Filtros interativos na tela do Streammit
            st.markdown("##### 🔍 Filtrar Resultados")
            col1, col2 = st.columns(2)
            
            with col1:
                tipo_filtro = st.selectbox("Tipo de Movimentação", ["Todos", "Receita", "Despesa"])
            with col2:
                # CORREÇÃO AQUI: Nome da variável corrigido para português (com 'i')
                categorias_disponiveis = ["Todas"] + sorted(df["categoria"].unique().tolist())
                cat_filtro = st.selectbox("Categoria", categorias_disponiveis)
                
            # Aplicando os filtros no DataFrame
            df_filtrado = df.copy()
            if tipo_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["tipo"] == tipo_filtro]
            if cat_filtro != "Todas":
                df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_filtro]
                
            # Exibição do Extrato formatado
            if not df_filtrado.empty:
                st.markdown("##### 📝 Lançamentos Encontrados")
                
                # Formata a coluna de valores para exibição bonita em R$
                df_exibicao = df_filtrado.copy()
                df_exibicao["valor"] = df_exibicao["valor"].apply(formatar_brl)
                
                # Renomeia colunas para o usuário ler melhor
                df_exibicao.columns = ["Data", "Descrição", "Categoria", "Tipo", "Valor"]
                
                st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum registro encontrado para os filtros selecionados.")
                
        else:
            st.info("Nenhuma transação encontrada no seu histórico financeiro.")
            
    except Exception as e:
        st.error(f"Erro ao carregar o extrato: {e}")
    finally:
        conn.close()
import streamlit as st
import pandas as pd
import plotly.express as px
from database import (
    soma_receitas_usuario, 
    soma_despesas_usuario, 
    dados_grafico_categorias, 
    obter_total_reserva, 
    formatar_brl
)

# 1. Verifica se o usuário está logado
if "usuario" not in st.session_state or not st.session_state.get("logado", False):
    st.warning("⚠️ Por favor, faça o login na página inicial para acessar o Dashboard.")
else:
    u = st.session_state["usuario"]
    
    # 2. AQUI ESTÁ A CORREÇÃO: Força o Python a pegar apenas o texto do nome
    if isinstance(u, dict):
        nome_limpo = u.get("username", u.get("nome", "admin"))
    else:
        nome_limpo = str(u)

    st.markdown("<h2 style='font-weight: 700;'>📊 Visão Geral do Ecossistema</h2>", unsafe_allow_html=True)
    st.write(f"Análise em tempo real para o usuário: **{nome_limpo}**")
    st.divider()

    # 3. Envia o texto puro ('admin') para as funções do banco de dados
    receitas = soma_receitas_usuario(nome_limpo)
    despesas = soma_despesas_usuario(nome_limpo)
    saldo_operacional = receitas - despesas
    total_reserva = obter_total_reserva(nome_limpo)

    # Grid de Métricas Principais
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Receitas Globais", formatar_brl(receitas))
        c2.metric("Despesas Globais", formatar_brl(despesas), delta=f"-{formatar_brl(despesas)}", delta_color="inverse")
        c3.metric("Saldo Geral", formatar_brl(saldo_operacional))
        c4.metric("Reserva Técnica Guardada", formatar_brl(total_reserva))

    st.write("")

    # Área de Gráficos
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        with st.container(border=True):
            st.markdown("##### 📈 Balanço de Fluxo")
            dados_balanco = pd.DataFrame({"Fluxo": ["Receitas", "Despesas"], "Valor": [receitas, despesas]})
            fig_barra = px.bar(
                dados_balanco, 
                x="Fluxo", 
                y="Valor", 
                color="Fluxo", 
                color_discrete_map={"Receitas": "#2ecc71", "Despesas": "#e74c3c"}, 
                text_auto='.2f'
            )
            fig_barra.update_layout(showlegend=False, height=300, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_barra, use_container_width=True)

    with col_graf2:
        with st.container(border=True):
            st.markdown("##### 🍩 Distribuição por Categorias de Saída")
            dados_bd = dados_grafico_categorias(nome_limpo)
            if dados_bd:
                df_cat = pd.DataFrame(dados_bd, columns=["Categoria", "Total"])
                fig_rosca = px.pie(df_cat, names="Categoria", values="Total", hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
                fig_rosca.update_layout(height=300, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_rosca, use_container_width=True)
            else:
                st.info("Nenhuma despesa registrada para mapeamento de categorias.")
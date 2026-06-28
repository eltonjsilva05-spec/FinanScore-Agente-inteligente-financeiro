import streamlit as st

# ==================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================
st.set_page_config(
    page_title="FinanScore",
    page_icon="💜",
    layout="wide"
)

# ==================================
# CSS
# ==================================
st.markdown("""
<style>

.hero {
    background: linear-gradient(135deg,#7b2cbf,#9d4edd);
    padding: 40px;
    border-radius: 25px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 10px;
}

.hero p {
    font-size: 1.2rem;
    opacity: 0.95;
}

.feature-card {
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #ececec;
    background-color: white;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    height: 100%;
}

.feature-title {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)

# ==================================
# HERO
# ==================================
st.markdown("""
<div class="hero">
    <h1>💜 FinanScore</h1>
    <p>
        Controle suas finanças de forma simples,
        inteligente e profissional.
    </p>
</div>
""", unsafe_allow_html=True)

# ==================================
# APRESENTAÇÃO
# ==================================
st.title("Seu Painel Financeiro Inteligente")

st.caption(
    "Organize receitas, despesas, acompanhe metas e tome decisões melhores."
)

st.write("")

# ==================================
# BOTÕES PRINCIPAIS
# ==================================
col1, col2 = st.columns(2)

with col1:
    st.button(
        "🔐 Login",
        use_container_width=True
    )

with col2:
    st.button(
        "🆕 Cadastro",
        use_container_width=True
    )

st.write("")

# ==================================
# FUNCIONALIDADES
# ==================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💰 Controle Financeiro</div>
        Registre receitas e despesas de forma simples e rápida.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Dashboard Inteligente</div>
        Visualize seus resultados através de gráficos e indicadores.
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 IA Financeira</div>
        Receba recomendações inteligentes para melhorar sua saúde financeira.
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ==================================
# RECURSOS
# ==================================
st.subheader("🚀 Recursos disponíveis")

st.markdown("""
✅ Controle de receitas

✅ Controle de despesas

✅ Histórico financeiro

✅ Extrato completo

✅ Dashboard interativo

✅ Relatórios

✅ Base preparada para Inteligência Artificial
""")

# ==================================
# RODAPÉ
# ==================================
st.markdown("""
<div class="footer">
💜 FinanScore • Projeto Financeiro Profissional
</div>
""", unsafe_allow_html=True)
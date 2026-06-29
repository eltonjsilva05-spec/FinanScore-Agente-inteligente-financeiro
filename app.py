import streamlit as st
import plotly.express as px
import pandas as pd
from database import (
    verificar_login, 
    criar_usuario, 
    inicializar_banco, 
    soma_receitas_usuario, 
    soma_despesas_usuario, 
    obter_total_reserva, 
    inserir_transacao, 
    formatar_brl,
    dados_grafico_categorias,
    listar_transacoes_usuario,
    excluir_transacao,
    atualizar_transacao,
    atualizar_valor_inicial_reserva,
    obter_valor_inicial_reserva,
    inserir_conta_bancaria,
    listar_contas_usuario,
    excluir_conta_bancaria,
    obter_saldo_atual_conta,
    obter_plano_usuario,
    atualizar_plano_usuario,
    listar_todos_usuarios
)

# Inicializa o banco de dados
inicializar_banco()

st.set_page_config(page_title="FinanScore - Gestão Inteligente", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
        html, body, [data-testid="stWidgetLabel"] { font-family: 'Inter', sans-serif !important; }
        .stButton>button[kind="primary"] { background-color: #2ecc71 !important; border: none !important; color: #000000 !important; font-weight: 600 !important; border-radius: 8px !important; transition: all 0.3s ease; }
        .stButton>button[kind="primary"]:hover { background-color: #27ae60 !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(46, 204, 113, 0.2); }
        .banco-card { background: rgba(31, 41, 55, 0.6); backdrop-filter: blur(4px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 16px; border-radius: 12px; border-left: 5px solid #2ecc71; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# 1. INICIALIZAÇÃO DOS ESTADOS GLOBAIS (Executado apenas uma vez no carregamento)
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "id_em_edicao" not in st.session_state:
    st.session_state["id_em_edicao"] = None
if "dados_edicao" not in st.session_state:
    st.session_state["dados_edicao"] = {}

# Estas chaves globais NUNCA serão vinculadas como 'key' de nenhum widget para o Streamlit não as apagar
if "db_meta_global" not in st.session_state:
    st.session_state["db_meta_global"] = 10000.0
if "db_aporte_global" not in st.session_state:
    st.session_state["db_aporte_global"] = 300.0

# Funções de callback para salvar o estado imediatamente ao digitar/clicar nas setas
def atualizar_meta_callback():
    st.session_state["db_meta_global"] = st.session_state["temp_meta"]

def atualizar_aporte_callback():
    st.session_state["db_aporte_global"] = st.session_state["temp_aporte"]


if not st.session_state["logado"]:
    col_centro, _ = st.columns([2, 1])
    with col_centro:
        st.markdown("<h1 style='font-weight: 700; margin-bottom: 0;'>🔐 FinanScore</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: gray; margin-top: 0;'>Sua plataforma inteligente de controle de fluxos e SaaS B2B</p>", unsafe_allow_html=True)
        modo = st.radio("Acesso", ["Acessar Conta", "Criar Nova Conta"], horizontal=True, label_visibility="collapsed")
        
        if modo == "Acessar Conta":
            with st.container(border=True):
                st.markdown("### Entre na sua Conta")
                with st.form("login", border=False):
                    u = st.text_input("Usuário (Username)")
                    p = st.text_input("Senha", type="password")
                    if st.form_submit_button("Entrar no Painel 🚀", use_container_width=True, type="primary"):
                        if verificar_login(u, p):
                            st.session_state.logado = True
                            st.session_state.usuario = {"username": u, "nome": u}
                            st.rerun()
                        else:
                            st.error("Usuário ou senha inválidos.")
        else:
            with st.container(border=True):
                st.markdown("### Abra sua Conta Gratuitamente")
                with st.form("cadastro", border=False):
                    u = st.text_input("Defina seu Usuário (Username)")
                    p = st.text_input("Defina sua Senha", type="password")
                    nome_completo = st.text_input("Nome Completo")
                    email = st.text_input("E-mail para Contato")
                    telefone = st.text_input("Telefone / WhatsApp (com DDD)", value="413384-1560")
                    if st.form_submit_button("Finalizar Cadastro Seguro", type="primary", use_container_width=True):
                        if u.strip() == "" or p.strip() == "" or nome_completo.strip() == "":
                            st.error("Por favor, preencha Usuário, Senha e Nome Completo.")
                        else:
                            if criar_usuario(u, p, nome_completo, email, telefone):
                                st.success("Conta criada! Altere para 'Acessar Conta'.")
                            else:
                                st.error("Este nome de usuário já está sendo utilizado.")
else:
    u = st.session_state.usuario
    nome = u.get("username", u.get("nome", "admin")) if isinstance(u, dict) else str(u)

    # Buscar informações de plano atualizadas direto do Banco de Dados
    plano_atual = obter_plano_usuario(nome)
    eh_admin = (plano_atual == "Admin")
    eh_premium = plano_atual in ["Mensal", "Anual", "Admin"] 

    # --- BARRA LATERAL (SIDEBAR COM REDIRECIONAMENTO KIWIFY) ---
    with st.sidebar:
        st.markdown(f"### 👤 Olá, \n## {nome}")
        
        if eh_admin:
            st.markdown("<div style='background-color: #e74c3c; color: white; padding: 6px 12px; border-radius: 20px; text-align: center; font-weight: bold;'>👑 ADMIN</div>", unsafe_allow_html=True)
        elif eh_premium:
            st.markdown(f"<div style='background-color: #2ecc71; color: black; padding: 6px 12px; border-radius: 20px; text-align: center; font-weight: bold;'>👑 PLANO {plano_atual.upper()}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #374151; color: #9ca3af; padding: 6px 12px; border-radius: 20px; text-align: center; font-weight: bold;'>⚪ GRATUITO</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # Bloqueio comercial com Links Diretos da Kiwify para os 3 Planos reais
        if not eh_premium:
            st.warning("Ganhe acesso às ferramentas de Caixa Reserva e Gestão de Contas Bancárias Corporativas.")
            st.markdown("<p style='font-weight: 600; margin-bottom: 5px; font-size: 14px;'>Escolha o seu plano para liberar:</p>", unsafe_allow_html=True)
            
            # --- PLANO MENSAL ---
            link_mensal = "https://pay.kiwify.com.br/HP7f4nD"
            st.markdown(
                f'<a href="{link_mensal}" target="_blank" style="text-decoration: none;">'
                '<button style="width: 100%; background-color: #374151; color: white; border: 1px solid #4b5563; padding: 8px; font-weight: 500; border-radius: 8px; cursor: pointer; margin-bottom: 8px; text-align: center;">'
                'Plano Mensal - R$ 29,90/mês 💳'
                '</button>'
                '</a>', 
                unsafe_allow_html=True
            )
            
            # --- PLANO SEMESTRAL (6 MESES) ---
            link_semestral = "https://pay.kiwify.com.br/Xx33BV9"
            st.markdown(
                f'<a href="{link_semestral}" target="_blank" style="text-decoration: none;">'
                '<button style="width: 100%; background-color: #3b82f6; color: white; border: none; padding: 8px; font-weight: 500; border-radius: 8px; cursor: pointer; margin-bottom: 8px; text-align: center;">'
                'Plano Semestral - R$ 119,00 🚀'
                '</button>'
                '</a>', 
                unsafe_allow_html=True
            )
            
            # --- PLANO ANUAL ---
            link_anual = "https://pay.kiwify.com.br/EoIhPpa"
            st.markdown(
                f'<a href="{link_anual}" target="_blank" style="text-decoration: none;">'
                '<button style="width: 100%; background-color: #2ecc71; color: black; border: none; padding: 10px; font-weight: 700; border-radius: 8px; cursor: pointer; text-align: center;">'
                'Plano Anual - R$ 197,00 🔥'
                '</button>'
                '</a>', 
                unsafe_allow_html=True
            )
            
        elif eh_premium and not eh_admin:
            st.caption(f"Sua assinatura do plano {plano_atual} está ativa e renovada.")
                
        st.divider()
        if st.button("Sair do Sistema 🚪", use_container_width=True):
            st.session_state.logado = False
            st.rerun()

    st.markdown("<h1 style='font-weight: 800; margin-bottom: 0;'>📊 FinanScore</h1>", unsafe_allow_html=True)
    lista_abas = ["Dashboard", "Novo Lançamento", "🏦 Caixa Reserva", "🏢 Bancos dos Clientes"]
    if eh_admin: lista_abas.append("⚙️ Painel Admin")
    abas = st.tabs(lista_abas)

    # --- ABA 0: DASHBOARD ---
    with abas[0]:
        receitas = float(soma_receitas_usuario(nome) or 0.0)
        despesas = float(soma_despesas_usuario(nome) or 0.0)
        valor_inicial = float(obter_valor_inicial_reserva(nome) or 0.0)
        saldo = receitas - despesas + valor_inicial
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Receitas Globais", formatar_brl(receitas))
            c2.metric("Despesas Globais", formatar_brl(despesas))
            c3.metric("Saldo Geral (+ Reserva)", formatar_brl(saldo))

        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            dados_balanco = pd.DataFrame({"Fluxo": ["Receitas", "Despesas"], "Valor": [receitas, despesas]})
            fig_barra = px.bar(dados_balanco, x="Fluxo", y="Valor", color="Fluxo", color_discrete_map={"Receitas": "#2ecc71", "Despesas": "#e74c3c"})
            st.plotly_chart(fig_barra, use_container_width=True)
        with col_graf2:
            dados_bd = dados_grafico_categorias(nome)
            if dados_bd:
                df_cat = pd.DataFrame(dados_bd, columns=["Categoria", "Total"])
                st.plotly_chart(px.pie(df_cat, names="Categoria", values="Total", hole=0.5), use_container_width=True)
            else:
                st.info("Sem saídas registradas.")

    # --- ABA 1: NOVO LANÇAMENTO ---
    with abas[1]:
        em_edicao = st.session_state["id_em_edicao"] is not None
        contas_disponiveis = listar_contas_usuario(nome) if eh_premium else []
        opcoes_conta = {0: "Dinheiro Vivo / Geral"}
        for c_item in contas_disponiveis:
            opcoes_conta[c_item[0]] = f"{c_item[1]} - Ag: {c_item[2]} C: {c_item[3]}"
        
        with st.form("form_transacao"):
            data = st.date_input("Data")
            valor = st.number_input("Valor", min_value=0.0)
            descricao = st.text_input("Descrição")
            categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Reserva", "Outros"])
            tipo = st.radio("Tipo", ["Receita", "Despesa"])
            conta_id = st.selectbox("Conta", options=list(opcoes_conta.keys()), format_func=lambda x: opcoes_conta[x]) if eh_premium else 0
            if st.form_submit_button("Salvar"):
                if em_edicao:
                    atualizar_transacao(st.session_state["id_em_edicao"], str(data), descricao, categoria, tipo, valor, conta_id)
                    st.session_state["id_em_edicao"] = None
                else:
                    inserir_transacao(nome, str(data), descricao, categoria, tipo, valor, conta_id)
                st.rerun()

        transacoes_puras = listar_transacoes_usuario(nome)
        if transacoes_puras:
            for t in transacoes_puras:
                st.write(f"Data: {t[1]} | {t[2]} | {formatar_brl(t[5])}")
                if st.button("🗑️", key=f"del_{t[0]}"):
                    excluir_transacao(t[0])
                    st.rerun()

    # --- ABA 2: CAIXA RESERVA (RESOLVIDO DEFINITIVAMENTE COM CALLBACKS) ---
    with abas[2]:
        if not eh_premium: 
            st.error("🔒 Funcionalidade exclusiva para parceiros dos Planos Mensal ou Anual.")
        else:
            st.markdown("### 🏦 Caixa Reserva & Simulações Avançadas")
            st.markdown("Gerencie sua reserva técnica, configure metas de patrimônio e calcule a evolução automática de juros.")
            st.markdown("---")

            # Busca o valor atual guardado no banco de dados SQLite
            v_res_banco = float(obter_valor_inicial_reserva(nome) or 0.0)

            st.subheader("⚙️ Configurações da sua Meta")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # O valor atual é salvo diretamente no banco pelo botão, sem segredos
                valor_atual = st.number_input(
                    "Quanto você tem guardado hoje? (R$)", 
                    min_value=0.0, 
                    value=v_res_banco,
                    step=100.0,
                    key="temp_atual"
                )
            with col2:
                # Usamos on_change para interceptar a alteração antes que o Streamlit mude de aba e limpe a memória
                valor_meta = st.number_input(
                    "Qual é a sua meta total? (R$)", 
                    min_value=0.0, 
                    value=float(st.session_state["db_meta_global"]),
                    step=500.0,
                    key="temp_meta",
                    on_change=atualizar_meta_callback
                )
            with col3:
                # Processo idêntico aplicado para manter o aporte mensal fixo
                aporte_mensal = st.number_input(
                    "Aporte Mensal Pretendido (R$)", 
                    min_value=0.0, 
                    value=float(st.session_state["db_aporte_global"]),
                    step=50.0,
                    key="temp_aporte",
                    on_change=atualizar_aporte_callback
                )

            if st.button("Salvar Configurações da Reserva 💾", type="primary", key="btn_salvar_definitivo"):
                # Salva o valor em dinheiro permanentemente no SQLite
                atualizar_valor_inicial_reserva(nome, valor_atual)
                # Garante que os estados globais peguem os últimos dados digitados
                st.session_state["db_meta_global"] = valor_meta
                st.session_state["db_aporte_global"] = aporte_mensal
                st.success("Configurações aplicadas e salvas com absoluto sucesso!")
                st.rerun()

            st.markdown("---")

            # Resgatamos os valores das chaves globais blindadas para as equações matemáticas
            meta_calculo = float(st.session_state["db_meta_global"])
            aporte_calculo = float(st.session_state["db_aporte_global"])

            # 2. Linha de Progresso com Validação contra Divisão por Zero
            if meta_calculo > 0:
                progresso = min(valor_atual / meta_calculo, 1.0)
                porcentagem_atingida = progresso * 100
            else:
                progresso = 1.0 if valor_atual >= 0 else 0.0
                porcentagem_atingida = 100.0 if valor_atual >= 0 else 0.0

            st.markdown("### 📊 Status da Meta Atingida")
            st.progress(progresso)
            
            if meta_calculo == 0:
                st.success(f"🎉 Você não definiu uma meta de longo prazo. Patrimônio atual em caixa: {formatar_brl(valor_atual)}")
            elif porcentagem_atingida >= 100:
                st.success(f"🎉 **Parabéns! Meta 100% Atingida!** Você possui {formatar_brl(valor_atual)} guardados de uma meta de {formatar_brl(meta_calculo)}")
            else:
                st.info(f"🎯 Você atingiu **{porcentagem_atingida:.1f}%** da sua meta corporativa. Faltam **{formatar_brl(max(meta_calculo - valor_atual, 0.0))}**.")

            st.markdown("---")

            # 3. Simulador de Crescimento (Juros Compostos)
            st.subheader("📈 Simulador de Investimento Estratégico")
            col_taxa, col_tempo = st.columns(2)
            
            with col_taxa:
                taxa_anual = st.slider(
                    "Taxa de Juros Anual Média (%)", 
                    min_value=0.0, 
                    max_value=25.0, 
                    value=10.5, 
                    step=0.1,
                    key="slider_taxa"
                )
            with col_tempo:
                meses = st.slider(
                    "Horizonte de Tempo (Meses)", 
                    min_value=1, 
                    max_value=60, 
                    value=12, 
                    step=1,
                    key="slider_meses"
                )

            # Estrutura condicional para taxas nulas
            if taxa_anual > 0:
                taxa_mensal = (1 + (taxa_anual / 100)) ** (1 / 12) - 1
            else:
                taxa_mensal = 0.0

            saldo_total = valor_atual
            total_investido = valor_atual
            
            historico = []
            historico.append({
                "Mês": 0,
                "Total Investido (Sem Juros)": round(total_investido, 2),
                "Evolução com Juros (Patrimônio)": round(saldo_total, 2)
            })
            
            for mes in range(1, meses + 1):
                if taxa_mensal > 0:
                    saldo_total = saldo_total * (1 + taxa_mensal)
                
                saldo_total += aporte_calculo
                total_investido += aporte_calculo
                
                historico.append({
                    "Mês": mes,
                    "Total Investido (Sem Juros)": round(total_investido, 2),
                    "Evolução com Juros (Patrimônio)": round(saldo_total, 2)
                })
                
            df_simulacao = pd.DataFrame(historico)

            df_melted = df_simulacao.melt(
                id_vars=["Mês"], 
                value_vars=["Total Investido (Sem Juros)", "Evolução com Juros (Patrimônio)"],
                var_name="Evolução Financeira", 
                value_name="Valor"
            )
            
            fig = px.line(
                df_melted, 
                x="Mês", 
                y="Valor", 
                color="Evolução Financeira",
                markers=True,
                color_discrete_map={
                    "Total Investido (Sem Juros)": "#9ca3af",
                    "Evolução com Juros (Patrimônio)": "#2ecc71"
                },
                template="plotly_dark"
            )
            fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📋 Resumo das Projeções Obtidas")
            c_res1, c_res2, c_res3 = st.columns(3)
            
            rendimento_juros = max(saldo_total - total_investido, 0.0)
            
            c_res1.metric("Total Aportado (Do Bolso)", formatar_brl(total_investido))
            c_res2.metric("Rendimento em Juros", formatar_brl(rendimento_juros))
            c_res3.metric("Patrimônio Líquido Final", formatar_brl(saldo_total))

    # --- ABA 3: BANCOS DOS CLIENTES ---
    with abas[3]:
        if not eh_premium: 
            st.error("🔒 Funcionalidade exclusiva para parceiros dos Planos Mensal ou Anual.")
        else:
            st.markdown("### 🏢 Vincular Novas Contas Corporativas")
            with st.form("bancos", border=True):
                banco = st.text_input("Instituição Bancária")
                ag = st.text_input("Número da Agência")
                cc = st.text_input("Número da Conta Corrente")
                tipo_c = st.selectbox("Tipo de Conta", ["Conta Corrente", "Poupança"])
                s_ini = st.number_input("Saldo de Abertura Comercial", min_value=0.0)
                if st.form_submit_button("Vincular Nova Conta", type="primary"):
                    if banco and ag and cc:
                        inserir_conta_bancaria(nome, banco, ag, cc, tipo_c, s_ini)
                        st.success("Conta vinculada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha todos os campos para prosseguir.")

    # --- ABA 4: PAINEL ADMINISTRADOR ---
    if eh_admin:
        with abas[4]:
            st.markdown("### 👑 Console de Governança (Admin)")
            for usr in listar_todos_usuarios():
                id_u, username_u, nome_u, email_u, tel_u, plano_u = usr
                desabilitar_seletor = (username_u == nome)
                col_u_dados, col_u_plano = st.columns([3, 1])
                with col_u_dados:
                    st.write(f"👤 **{nome_u}** (`{username_u}`) | Plano Atual: **{plano_u}**")
                with col_u_plano:
                    opcoes_planos = ["Gratuito", "Mensal", "Anual", "Admin"]
                    plano_escolhido = st.selectbox("Nível", options=opcoes_planos, index=opcoes_planos.index(plano_u), key=f"adm_plano_{id_u}", disabled=desabilitar_seletor, label_visibility="collapsed")
                    if plano_escolhido != plano_u:
                        atualizar_plano_usuario(username_u, plano_escolhido)
                        st.rerun()
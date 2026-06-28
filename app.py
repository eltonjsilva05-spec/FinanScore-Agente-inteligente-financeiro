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

# ==========================================
# DESIGN & CUSTOMIZAÇÃO VISUAL (CSS)
# ==========================================
st.markdown("""
    <style>
        /* Importa uma fonte moderna e limpa */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [data-testid="stWidgetLabel"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Customização sutil dos botões primários */
        .stButton>button[kind="primary"] {
            background-color: #2ecc71 !important;
            border: none !important;
            color: #000000 !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #27ae60 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(46, 204, 113, 0.2);
        }
        
        /* Cards customizados com efeito vidro fosco para B2B */
        .banco-card {
            background: rgba(31, 41, 55, 0.6);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 16px; 
            border-radius: 12px; 
            border-left: 5px solid #2ecc71; 
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)


if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "id_em_edicao" not in st.session_state:
    st.session_state["id_em_edicao"] = None
if "dados_edicao" not in st.session_state:
    st.session_state["dados_edicao"] = {}

# ==========================================
# 1. TELA DE ACESSO (CADASTRAR / ENTRAR)
# ==========================================
if not st.session_state["logado"]:
    col_centro, _ = st.columns([2, 1])
    with col_centro:
        st.markdown("<h1 style='font-weight: 700; margin-bottom: 0;'>🔐 FinanScore</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: gray; margin-top: 0;'>Sua plataforma inteligente de controle de fluxos e SaaS B2B</p>", unsafe_allow_html=True)
        
        modo = st.radio("Acesso", ["Acessar Conta", "Criar Nova Conta"], horizontal=True, label_visibility="collapsed")
        st.write("")

        if modo == "Acessar Conta":
            with st.container(border=True):
                st.markdown("### Entre na sua Conta")
                with st.form("login", border=False):
                    u = st.text_input("Usuário (Username)")
                    p = st.text_input("Senha", type="password")
                    if st.form_submit_button("Entrar no Painel 🚀", use_container_width=True, type="primary"):
                        if verificar_login(u, p):
                            st.session_state.logado = True
                            st.session_state.usuario = {"nome": u}
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
                    
                    st.caption("🔒 Seus dados são protegidos por criptografia de ponta SHA-256.")

                    if st.form_submit_button("Finalizar Cadastro Seguro", type="primary", use_container_width=True):
                        if u.strip() == "" or p.strip() == "" or nome_completo.strip() == "":
                            st.error("Por favor, preencha Usuário, Senha e Nome Completo.")
                        else:
                            if criar_usuario(u, p, nome_completo, email, telefone):
                                st.success("Conta criada! Altere para 'Acessar Conta' para fazer o seu login.")
                            else:
                                st.error("Este nome de usuário já está sendo utilizado.")

# ==========================================
# 2. PAINEL DO USUÁRIO (LOGADO)
# ==========================================
else:
    u = st.session_state.usuario
    nome = u["nome"] if isinstance(u, dict) else u

    # Descobre o plano atual
    plano_atual = obter_plano_usuario(nome)
    eh_admin = (plano_atual == "Admin")
    eh_premium = plano_atual in ["Mensal", "Anual"] or eh_admin

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.markdown("<h3 style='margin-bottom:0;'>👤 Olá,</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin-top:0; font-weight:700;'>{nome}</h2>", unsafe_allow_html=True)
        
        # Selo Visual de Plano Elegante
        if eh_admin:
            st.markdown("<div style='background-color: #e74c3c; color: white; padding: 6px 12px; border-radius: 20px; text-align: center; font-size: 13px; font-weight: 600;'>👑 MODO ADMINISTRADOR</div>", unsafe_allow_html=True)
        elif eh_premium:
            st.markdown(f"<div style='background-color: #2ecc71; color: black; padding: 6px 12px; border-radius: 20px; text-align: center; font-size: 13px; font-weight: 600;'>👑 PLANO {plano_atual.upper()} ACESSO TOTAL</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #374151; color: #9ca3af; padding: 6px 12px; border-radius: 20px; text-align: center; font-size: 13px; font-weight: 500;'>⚪ PLANO GRATUITO COM TRAVAS</div>", unsafe_allow_html=True)
        
        st.write("")
        st.divider()
        
        # Simulador de Vendas/Planos (Esconde se for Admin Real)
        if not eh_admin:
            with st.container(border=True):
                st.markdown("🌐 **Simulador SaaS**")
                novo_plano_simulado = st.selectbox("Trocar Plano Atual:", ["Gratuito", "Mensal", "Anual"], index=["Gratuito", "Mensal", "Anual"].index(plano_atual))
                if novo_plano_simulado != plano_atual:
                    atualizar_plano_usuario(nome, novo_plano_simulado)
                    st.toast(f"Plano atualizado!")
                    st.rerun()

        st.write("")
        if st.button("Sair do Sistema 🚪", use_container_width=True, help="Encerrar sessão ativa"):
            st.session_state.logado = False
            st.rerun()

    # --- HEADER DO DASHBOARD ---
    st.markdown("<h1 style='font-weight: 800; letter-spacing: -1px; margin-bottom: 0;'>📊 FinanScore</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; font-size: 15px;'>Seu ecossistema de gestão e inteligência corporativa</p>", unsafe_allow_html=True)

    # Montagem Dinâmica das Abas
    lista_abas = ["Dashboard", "Novo Lançamento", "🏦 Caixa Reserva", "🏢 Bancos dos Clientes"]
    if eh_admin:
        lista_abas.append("⚙️ Painel Admin")
        
    abas = st.tabs(lista_abas)

    # --- ABA 1: DASHBOARD ---
    with abas[0]:
        receitas = soma_receitas_usuario(u)
        despesas = soma_despesas_usuario(u)
        valor_inicial = obter_valor_inicial_reserva(nome)
        saldo = receitas - despesas + valor_inicial

        # Grid de Métricas Modernas com Borda Nativa
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Receitas Globais", formatar_brl(receitas))
            c2.metric("Despesas Globais", formatar_brl(despesas), delta=f"-{formatar_brl(despesas)}", delta_color="inverse")
            c3.metric("Saldo Geral (+ Reserva)", formatar_brl(saldo))
        
        st.write("")
        
        # Diagnóstico de Saúde Financeira Premium
        if receitas > 0:
            comprometimento = (despesas / receitas) * 100
            with st.container(border=True):
                st.markdown("#### 🌡️ Diagnóstico de Saúde Orçamentária")
                st.write(f"Seu índice de comprometimento atual é de **{comprometimento:.1f}%** das entradas.")
                if comprometimento <= 50:
                    st.success("🟢 **Excelente!** Margem saudável para investimentos e expansão operacional.")
                elif comprometimento <= 75:
                    st.warning("🟡 **Atenção:** Custos fixos e variáveis consumindo mais da metade do faturamento.")
                else:
                    st.error("🔴 **Alerta Crítico:** Orçamento severamente comprometido. Risco iminente de déficit de fluxo.")
            
        st.write("")
        
        # Área de Gráficos Lado a Lado
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            with st.container(border=True):
                st.markdown("##### 📈 Balanço Patrimonial")
                dados_balanco = pd.DataFrame({"Fluxo": ["Receitas", "Despesas"], "Valor": [receitas, despesas]})
                fig_barra = px.bar(dados_balanco, x="Fluxo", y="Valor", color="Fluxo", 
                                   color_discrete_map={"Receitas": "#2ecc71", "Despesas": "#e74c3c"}, text_auto='.2f')
                fig_barra.update_layout(showlegend=False, height=320, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_barra, use_container_width=True)

        with col_graf2:
            with st.container(border=True):
                st.markdown("##### 🍩 Distribuição por Categorias")
                dados_bd = dados_grafico_categorias(nome)
                if dados_bd:
                    df_cat = pd.DataFrame(dados_bd, columns=["Categoria", "Total"])
                    fig_rosca = px.pie(df_cat, names="Categoria", values="Total", hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
                    fig_rosca.update_layout(height=320, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_rosca, use_container_width=True)
                else:
                    st.info("Aguardando lançamentos de saídas para estruturar o gráfico.")
                
        st.write("")
        
        # Visão Geral Rápida dos Clientes B2B
        st.markdown("#### 🏛️ Visão Consolidada de Contas")
        if not eh_premium:
            st.warning("🔒 **Recurso Avançado Premium:** Faça upgrade para liberar o espelhamento de contas correntes B2B na sua Home.")
        else:
            contas_dashboard = listar_contas_usuario(nome)
            if not contas_dashboard:
                st.caption("Nenhum banco ou cliente associado no momento.")
            else:
                col_contas = st.columns(min(len(contas_dashboard), 4))
                for idx_c, c_item in enumerate(contas_dashboard):
                    id_c, b_nome, ag, cc, t_cc, s_ini = c_item
                    saldo_dinamico = obter_saldo_atual_conta(id_c, s_ini)
                    with col_contas[idx_c % len(col_contas)]:
                        st.markdown(f"""
                        <div class='banco-card'>
                            <span style='font-weight: 700; font-size: 14px;'>🏦 {b_nome}</span><br>
                            <span style='font-size: 12px; color: #9ca3af;'>{t_cc}</span><br>
                            <span style='font-size: 11px; color: #6b7280;'>Ag: {ag} | C: {cc}</span>
                            <hr style='margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.08);'>
                            <span style='font-weight: 700; font-size: 16px; color: #2ecc71;'>{formatar_brl(saldo_dinamico)}</span>
                        </div>
                        """, unsafe_allow_html=True)

    # --- ABA 2: NOVO LANÇAMENTO ---
    with abas[1]:
        em_edicao = st.session_state["id_em_edicao"] is not None
        contas_disponiveis = listar_contas_usuario(nome) if eh_premium else []
        opcoes_conta = {0: "Dinheiro Vivo / Geral"}
        for c_item in contas_disponiveis:
            id_c, b_nome, ag, cc, _, _ = c_item
            opcoes_conta[id_c] = f"{b_nome} - Ag: {ag} C: {cc}"

        col_manual, col_importacao = st.columns([1.2, 1.0])
        
        with col_manual:
            with st.container(border=True):
                if em_edicao:
                    st.markdown("### ✏️ Ajustar Registro")
                    dados = st.session_state["dados_edicao"]
                    val_data = pd.to_datetime(dados["data"]).date()
                    val_valor = dados["valor"]
                    val_desc = dados["desc"]
                    val_cat = dados["cat"]
                    val_tipo = dados["tipo"]
                    val_conta = dados.get("conta_id", 0)
                else:
                    st.markdown("### 📝 Entrada Manual")
                    val_data = None ; val_valor = 0.0 ; val_desc = "" ; val_cat = "Alimentação" ; val_tipo = "Receita" ; val_conta = 0

                with st.form("form_transacao", border=False, clear_on_submit=not em_edicao):
                    data = st.date_input("Data da Operação", value=val_data)
                    valor = st.number_input("Valor Liquido (R$)", min_value=0.0, format="%.2f", value=val_valor)
                    descricao = st.text_input("Breve Descrição", value=val_desc)
                    
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        categorias = ["Alimentação", "Moradia", "Transporte", "Lazer", "Reserva", "Outros"]
                        idx_cat = categorias.index(val_cat) if val_cat in categorias else 0
                        categoria = st.selectbox("Categoria Mapeada", categorias, index=idx_cat)
                    with col_f2:
                        lista_ids = list(opcoes_conta.keys())
                        idx_conta = lista_ids.index(val_conta) if val_conta in lista_ids else 0
                        if eh_premium:
                            conta_selecionada_id = st.selectbox("Conta Vinculada", options=lista_ids, format_func=lambda x: opcoes_conta[x], index=idx_conta)
                        else:
                            st.selectbox("Conta Vinculada (Bloqueado)", ["Apenas Fluxo Geral no Gratuito"], disabled=True)
                            conta_selecionada_id = 0
                    
                    tipo = st.radio("Natureza do Fluxo", ["Receita", "Despesa"], horizontal=True, index=["Receita", "Despesa"].index(val_tipo))
                    
                    st.write("")
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        submeteu = st.form_submit_button("Atualizar Registro" if em_edicao else "Confirmar Lançamento 💾", type="primary", use_container_width=True)
                    with col_sub2:
                        if em_edicao and st.form_submit_button("Cancelar Ação", use_container_width=True):
                            st.session_state["id_em_edicao"] = None; st.session_state["dados_edicao"] = {}; st.rerun()

                    if submeteu:
                        if valor > 0 and descricao.strip() != "":
                            if em_edicao:
                                atualizar_transacao(st.session_state["id_em_edicao"], str(data), descricao, categoria, tipo, valor, conta_selecionada_id)
                                st.session_state["id_em_edicao"] = None; st.session_state["dados_edicao"] = {}
                            else:
                                inserir_transacao(nome, str(data), descricao, categoria, tipo, valor, conta_selecionada_id)
                            st.rerun()
                        else: 
                            st.error("Erro nos dados de envio.")

        with col_importacao:
            with st.container(border=True):
                st.markdown("### ⚡ Conciliação via Arquivos")
                if not eh_premium:
                    st.error("🔒 **Ferramenta Exclusiva Premium:** O upload inteligente e processamento automático de planilhas CSV requer plano ativo.")
                else:
                    lista_ids_imp = list(opcoes_conta.keys())
                    conta_importar_id = st.selectbox("Direcionar conciliação para:", options=lista_ids_imp, format_func=lambda x: opcoes_conta[x], key="conta_imp")
                    arquivo_extrato = st.file_uploader("Arrastar planilha Extrato (.CSV)", type=["csv"])
                    if arquivo_extrato is not None:
                        try:
                            df_upload = pd.read_csv(arquivo_extrato, sep=";", encoding="utf-8-sig")
                            st.dataframe(df_upload, use_container_width=True, hide_index=True)
                            if st.button("Integrar Lançamentos em Massa 🚀", type="primary", use_container_width=True):
                                for _, row in df_upload.iterrows():
                                    try: inserir_transacao(nome, str(row["Data"]), str(row["Descrição"]), str(row["Categoria"]), str(row["Tipo"]), float(row["Valor"]), conta_importar_id)
                                    except: pass
                                st.toast("Integração concluída!")
                                st.rerun()
                        except Exception as err: st.error(f"Erro de processamento estrutural: {err}")

        st.write("")
        st.markdown("#### 🔍 Histórico Recente e Auditoria")
        transacoes_puras = listar_transacoes_usuario(nome)
        if transacoes_puras:
            df_trans = pd.DataFrame(transacoes_puras, columns=["ID", "Data", "Descrição", "Categoria", "Tipo", "Valor", "Conta_ID"])
            df_trans["Conta_Nome"] = df_trans["Conta_ID"].map(opcoes_conta)
            
            with st.container(border=True):
                for idx, linha in df_trans.iterrows():
                    id_t, dt, desc, cat, tp, val, c_id = int(linha["ID"]), linha["Data"], linha["Descrição"], linha["Categoria"], linha["Tipo"], float(linha["Valor"]), int(linha["Conta_ID"])
                    col_info, col_edit, col_del = st.columns([5, 0.4, 0.4])
                    with col_info: 
                        simbolo = "🟢" if tp=='Receita' else '🔴'
                        st.markdown(f"**{dt}** | {simbolo} *{desc}* (`{cat}`) | **{formatar_brl(val)}** <span style='font-size:11px; color:gray;'>{opcoes_conta.get(c_id, '')}</span>", unsafe_allow_html=True)
                    with col_edit:
                        if st.button("✏️", key=f"edit_{id_t}"):
                            st.session_state["id_em_edicao"] = id_t
                            st.session_state["dados_edicao"] = {"data": dt, "valor": val, "desc": desc, "cat": cat, "tipo": tp, "conta_id": c_id}
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{id_t}"): excluir_transacao(id_t); st.rerun()
                    if idx < len(df_trans) - 1:
                        st.markdown("<hr style='margin: 6px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # --- ABA 3: CAIXA RESERVA ---
    with abas[2]:
        if not eh_premium:
            st.markdown("### 🏦 Planejamento de Reserva Técnica")
            st.error("🔒 **Funcionalidade Exclusiva Premium:** Planejamentos de aportes recorrentes e simuladores de rendimentos compostos estão disponíveis apenas nos planos ativos.")
        else:
            with st.container(border=True):
                st.markdown("### 🏦 Planejamento de Reserva de Caixa")
                valor_inicial_atual = obter_valor_inicial_reserva(nome)
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    novo_val_inicial = st.number_input("Valor Técnico Inicial já Custodiado (R$):", min_value=0.0, value=valor_inicial_atual, format="%.2f")
                with col_c2:
                    st.write("") ; st.write("")
                    if st.button("Gravar Saldo", use_container_width=True, type="primary"): 
                        atualizar_valor_inicial_reserva(nome, novo_val_inicial); st.rerun()

    # --- ABA 4: BANCOS DOS CLIENTES ---
    with abas[3]:
        if not eh_premium:
            st.markdown("### 🏢 Custódia e Contas B2B")
            st.error("🔒 **Funcionalidade Exclusiva Premium:** A centralização bancária e vinculação de carteira de terceiros exige nível Premium.")
        else:
            with st.container(border=True):
                st.markdown("### 🏢 Conectar Nova Conta Cliente / Fornecedor")
                with st.form("form_bancos", border=False):
                    banco_sel = st.selectbox("Instituição Bancária", ["Banco do Brasil", "Itaú", "Bradesco", "Santander", "Nubank", "Caixa Econômica", "Outro"])
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1: agencia_input = st.text_input("Código Agência")
                    with col_b2: conta_input = st.text_input("Número da Conta Corrente")
                    with col_b3: tipo_sel = st.selectbox("Segmento", ["Conta Corrente", "Conta Poupança", "Conta Jurídica (PJ)", "Investimentos"])
                    saldo_ini_input = st.number_input("Aporte / Saldo Inicial (R$)", min_value=0.0, format="%.2f")
                    
                    if st.form_submit_button("Vincular Nova Conta Ativa", type="primary", use_container_width=True):
                        if agencia_input.strip() != "" and conta_input.strip() != "":
                            inserir_conta_bancaria(nome, banco_sel, agencia_input, conta_input, tipo_sel, saldo_ini_input)
                            st.rerun()
            
            st.write("")
            st.markdown("#### Contas Ativas em Monitoramento")
            contas = listar_contas_usuario(nome)
            if contas:
                with st.container(border=True):
                    for idx_cc, c_item in enumerate(contas):
                        id_c, b_nome, ag, cc, t_cc, s_ini = c_item
                        saldo_dinamico = obter_saldo_atual_conta(id_c, s_ini)
                        col_c_info, col_c_del = st.columns([5, 0.4])
                        with col_c_info:
                            st.markdown(f"🏛️ **{b_nome}** <span style='color:gray; font-size:12px;'>{t_cc}</span> | Ag: {ag} | Conta: {cc} | Balance: <b style='color:#2ecc71'>{formatar_brl(saldo_dinamico)}</b>", unsafe_allow_html=True)
                        with col_c_del:
                            if st.button("🗑️", key=f"del_conta_{id_c}"): excluir_conta_bancaria(id_c); st.rerun()
                        if idx_cc < len(contas) - 1:
                            st.markdown("<hr style='margin: 6px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # --- ABA 5: PAINEL ADMIN ---
    if eh_admin:
        with abas[4]:
            with st.container(border=True):
                st.markdown("### 👑 Console de Governança")
                st.write("Controle global de planos e acessos comerciais do ecossistema FinanScore.")
                st.divider()

                usuarios_cadastrados = listar_todos_usuarios()
                if usuarios_cadastrados:
                    for usr in usuarios_cadastrados:
                        id_u, username_u, nome_u, email_u, tel_u, plano_u = usr
                        desabilitar_seletor = (username_u == nome)

                        col_u_dados, col_u_plano = st.columns([3, 1])
                        with col_u_dados:
                            st.markdown(f"👤 **{nome_u}** (`{username_u}`) | {email_u} | {tel_u}")
                        with col_u_plano:
                            opcoes_planos = ["Gratuito", "Mensal", "Anual", "Admin"]
                            plano_escolhido = st.selectbox("Nível", options=opcoes_planos, index=opcoes_planos.index(plano_u), key=f"adm_plano_{id_u}", disabled=desabilitar_seletor, label_visibility="collapsed")
                            if plano_escolhido != plano_u:
                                atualizar_plano_usuario(username_u, plano_escolhido)
                                st.rerun()
                        st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
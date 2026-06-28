import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from database import (
    soma_receitas_usuario,
    soma_despesas_usuario,
    formatar_brl
)

# ==============================================================================
# SEGURANÇA E VALIDAÇÃO DE SESSÃO
# ==============================================================================
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("🔐 Faça login para acessar o sistema")
    st.stop()

st.title("📄 Relatório Mensal em PDF")
st.caption("Exporte o consolidado da sua saúde financeira.")

usuario_obj = st.session_state.get("usuario")

# CORREÇÃO CRÍTICA: Garante o texto puro do username (evita o erro de 'dict')
if isinstance(usuario_obj, dict):
    nome_usuario = usuario_obj.get("username", usuario_obj.get("nome", "admin"))
else:
    nome_usuario = str(usuario_obj)

# ==============================================================================
# LEITURA E HIGIENIZAÇÃO
# ==============================================================================
# CORREÇÃO DE PARÂMETRO: Alterado de 'usuario_obj' para 'nome_usuario' (string pura)
receitas = float(soma_receitas_usuario(nome_usuario) or 0.0)
despesas = float(soma_despesas_usuario(nome_usuario) or 0.0)
saldo = receitas - despesas

col1, col2, col3 = st.columns(3)
col1.metric("Total Receitas", formatar_brl(receitas))
col2.metric("Total Despesas", formatar_brl(despesas))
col3.metric("Saldo Líquido", formatar_brl(saldo))

# ==============================================================================
# MOTOR DE GERAÇÃO DO PDF
# ==============================================================================
def gerar_pdf() -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Nota: Removi acentos do texto para evitar erros de encoding padrão do Reportlab
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Relatorio Financeiro Mensal")
    
    c.setLineWidth(1)
    c.line(50, 785, 545, 785)

    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(50, 765, f"Usuario: {nome_usuario}")
    c.drawString(50, 745, f"Data de Emissao: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, 700, "Balanco Patrimonial:")
    
    c.setFont("Helvetica", 12)
    c.drawString(70, 675, f"Receitas Totais: {formatar_brl(receitas)}")
    c.drawString(70, 655, f"Despesas Totais: {formatar_brl(despesas)}")
    c.drawString(70, 635, f"Saldo Final: {formatar_brl(saldo)}")

    if saldo < 0:
        c.setFillColorRGB(0.8, 0, 0)
        c.drawString(50, 590, "Atencao: Sua conta fechou o ciclo atual com saldo negativo!")
    else:
        c.setFillColorRGB(0, 0.5, 0)
        c.drawString(50, 590, "Parabens: Seus gastos estao dentro da margem.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ==============================================================================
# DOWNLOAD
# ==============================================================================
pdf_buffer = gerar_pdf()

st.download_button(
    label="📥 Baixar Relatório PDF",
    data=pdf_buffer,
    file_name=f"relatorio_{nome_usuario}.pdf",
    mime="application/pdf",
    type="primary" # Botão destacado
)
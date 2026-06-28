def safe_float(valor):
    try:
        return float(valor)
    except:
        return 0.0


def calcular_saldo(receitas, despesas):
    receitas = safe_float(receitas)
    despesas = safe_float(despesas)
    return receitas - despesas


def percentual_gastos(receitas, despesas):
    receitas = safe_float(receitas)
    despesas = safe_float(despesas)

    if receitas <= 0:
        return 0

    return round((despesas / receitas) * 100, 2)


def percentual_saldo(receitas, despesas):
    receitas = safe_float(receitas)
    despesas = safe_float(despesas)

    if receitas <= 0:
        return 0

    return round(((receitas - despesas) / receitas) * 100, 2)


def score_financeiro(receitas, despesas):
    percentual = percentual_saldo(receitas, despesas)

    if percentual >= 60:
        return 950
    elif percentual >= 40:
        return 850
    elif percentual >= 20:
        return 700
    elif percentual >= 0:
        return 550
    return 300


def analisar_financas(receitas, despesas):
    percentual = percentual_saldo(receitas, despesas)

    if receitas <= 0:
        return "🔴 Sem dados suficientes"

    if percentual >= 40:
        return "🟢 Excelente saúde financeira"
    elif percentual >= 20:
        return "🟡 Atenção com gastos"
    else:
        return "🔴 Risco financeiro"


def gerar_dicas(receitas, despesas):
    saldo = calcular_saldo(receitas, despesas)

    if saldo < 0:
        return "Você está gastando mais do que ganha. Reduza despesas imediatamente."

    percentual = percentual_saldo(receitas, despesas)

    if percentual >= 40:
        return "Excelente! Considere investir parte do seu saldo."
    elif percentual >= 20:
        return "Bom controle financeiro, mas ainda pode economizar mais."

    return "Pequenas reduções de gastos podem melhorar muito seu saldo."


def gerar_resumo(receitas, despesas):
    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": calcular_saldo(receitas, despesas),
        "status": analisar_financas(receitas, despesas),
        "percentual_gastos": percentual_gastos(receitas, despesas),
        "score": score_financeiro(receitas, despesas),
        "dica": gerar_dicas(receitas, despesas)
    }


def responder_usuario(pergunta, receitas, despesas):
    pergunta = str(pergunta).lower()
    resumo = gerar_resumo(receitas, despesas)

    if receitas <= 0:
        return "Cadastre receitas para que eu possa te ajudar melhor."

    if "saldo" in pergunta:
        return f"Seu saldo atual é R$ {resumo['saldo']:,.2f}"

    if "receita" in pergunta:
        return f"Suas receitas são R$ {resumo['receitas']:,.2f}"

    if "despesa" in pergunta:
        return f"Suas despesas são R$ {resumo['despesas']:,.2f}"

    if "score" in pergunta:
        return f"Seu FinanScore é {resumo['score']} pontos"

    if "status" in pergunta or "situação" in pergunta:
        return resumo["status"]

    if "econom" in pergunta:
        return resumo["dica"]

    if "gasto" in pergunta:
        return f"Você utilizou {resumo['percentual_gastos']}% da sua renda"

    if "ajuda" in pergunta:
        return "Posso te ajudar com saldo, receitas, despesas, score e análise."

    return "Não entendi sua pergunta."
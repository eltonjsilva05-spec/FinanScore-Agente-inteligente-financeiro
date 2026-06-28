def calcular_score(receitas, despesas):

    if receitas == 0:
        return 0

    taxa = despesas / receitas

    if taxa <= 0.5:
        return 100

    elif taxa <= 0.7:
        return 80

    elif taxa <= 0.9:
        return 60

    return 40
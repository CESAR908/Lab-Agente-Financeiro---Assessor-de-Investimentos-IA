def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def formatar_percentual(valor: float) -> str:
    return f"{valor:.2f}%"

def classificar_risco(score: int) -> str:
    if score < 30:
        return "Muito Baixo"
    elif score < 50:
        return "Baixo"
    elif score < 70:
        return "Moderado"
    elif score < 85:
        return "Alto"
    else:
        return "Muito Alto"

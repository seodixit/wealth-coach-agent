import math


# =============================================================================
# TOOLS DEL AGENTE
# =============================================================================
# Las tools calculan hechos objetivos y devuelven datos estructurados.
# No guardan memoria, no hablan con el usuario y no toman decisiones finales.

HORIZONTE_PLAN_ANOS = 5


def calcular_impacto_financiero(importe_compra: float, ahorro_mensual: float = 2000) -> dict:
    """TOOL: calcula el impacto de una compra puntual sobre el objetivo."""
    return {
        "importe_compra": importe_compra,
        "impacto_patrimonio": -importe_compra,
        "meses_retraso_objetivo": round(importe_compra / ahorro_mensual, 1),
        "ahorro_mensual_equivalente": round(importe_compra / 12, 2),
    }


def calcular_tiempo_objetivo(
    patrimonio: float, ahorro_mensual: float, objetivo: float
) -> dict:
    """TOOL: calcula meses necesarios para llegar al objetivo sin intereses."""
    faltante = objetivo - patrimonio

    if faltante <= 0:
        return {"ok": True, "ya_alcanzado": True, "meses": 0, "faltante": 0.0}

    if ahorro_mensual == 0:
        return {"ok": False, "ya_alcanzado": False, "meses": None, "faltante": faltante}

    meses = math.ceil(faltante / ahorro_mensual)
    return {
        "ok": True,
        "ya_alcanzado": False,
        "meses": meses,
        "anos": meses // 12,
        "meses_restantes": meses % 12,
        "faltante": faltante,
    }


def evaluar_progreso(patrimonio: float, objetivo: float) -> dict:
    """TOOL: mide patrimonio actual, faltante y porcentaje de avance."""
    if objetivo <= 0:
        return {
            "faltante": 0.0,
            "porcentaje_logrado": 100.0,
            "mensaje": "Objetivo no definido o es 0.",
        }

    if patrimonio >= objetivo:
        return {
            "faltante": 0.0,
            "porcentaje_logrado": 100.0,
            "mensaje": "¡Has alcanzado tu objetivo de patrimonio!",
        }

    faltante = objetivo - patrimonio
    pct = min(100.0, (patrimonio / objetivo) * 100)

    return {
        "faltante": faltante,
        "porcentaje_logrado": round(pct, 1),
        "mensaje": (
            f"Llevas el {pct:.1f}% del objetivo. "
            f"Te faltan {faltante:,.0f} € para llegar a {objetivo:,.0f} €."
        ),
    }


def generar_plan_mensual(faltante: float, anos: int = HORIZONTE_PLAN_ANOS) -> dict:
    """TOOL: calcula el ahorro mensual necesario para un horizonte dado."""
    if faltante <= 0:
        return {
            "ahorro_mensual_necesario": 0.0,
            "anos": anos,
            "mensaje": "Ya no necesitas ahorrar más para este objetivo. 🎉",
        }

    meses = anos * 12
    ahorro_mes = math.ceil(faltante / meses)

    return {
        "ahorro_mensual_necesario": ahorro_mes,
        "anos": anos,
        "meses": meses,
        "mensaje": (
            f"Para alcanzar tu objetivo en {anos} años "
            f"deberías ahorrar {ahorro_mes:,.0f} € al mes."
        ),
    }

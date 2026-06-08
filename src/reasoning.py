from tools import (
    HORIZONTE_PLAN_ANOS,
    calcular_tiempo_objetivo,
    evaluar_progreso,
    generar_plan_mensual,
)


# =============================================================================
# RAZONAMIENTO DEL AGENTE
# =============================================================================
# El razonamiento interpreta datos y resultados de tools.
# Aquí viven las reglas, clasificaciones, planes y recomendaciones.

CLAS_EXCELENTE = "Excelente"
CLAS_BUEN_CAMINO = "BuenCamino"
CLAS_NECESITA_MEJORA = "NecesitaMejora"
CLAS_MUY_AMBIOSO = "ObjetivoMuyAmbicioso"

MESES_EXCELENTE = 26
MESES_BUEN_CAMINO = 60
MESES_MUY_AMBIOSO = 120
RATIO_MUY_AMBIOSO = 10
FRACCION_AHORRO_OK = 0.70


def planificar(pregunta: str) -> list[str]:
    """RAZONAMIENTO: decide qué memoria/tools necesita usar el agente."""
    pregunta_normalizada = pregunta.lower()

    if "omega" in pregunta_normalizada:
        return ["leer_perfil", "calcular_impacto_financiero"]

    if "mes" in pregunta_normalizada:
        return ["leer_perfil", "leer_gastos_mes"]

    return ["leer_perfil"]


def razonar(pregunta: str, resultados: dict) -> str:
    """RAZONAMIENTO: convierte resultados de tools en una respuesta útil."""
    if "impacto" in resultados:
        meses = resultados["impacto"]["meses_retraso_objetivo"]
        return f"Comprar el Omega es posible, pero retrasaría tu objetivo unos {meses} meses."

    if "gastos" in resultados:
        desviacion = resultados["gastos"]["desviacion_porcentaje"]
        return f"Este mes tus gastos están un {desviacion}% por encima del presupuesto."

    return "He leído tu perfil financiero. Necesitaría más datos para darte una recomendación completa."


def _ahorro_ideal_mensual(faltante: float, meses: int = MESES_BUEN_CAMINO) -> float:
    """RAZONAMIENTO: ahorro mensual de referencia para llegar en N meses."""
    if faltante <= 0:
        return 0.0
    return faltante / meses


def razonar_suficiencia_ahorro(ahorro_mensual: float, faltante: float) -> dict:
    """RAZONAMIENTO: evalúa si el ahorro actual sostiene el plan."""
    if faltante <= 0:
        return {"es_suficiente": True, "ratio": 1.0, "ahorro_ideal": 0.0}

    ideal = _ahorro_ideal_mensual(faltante)
    if ahorro_mensual == 0:
        return {"es_suficiente": False, "ratio": 0.0, "ahorro_ideal": ideal}

    ratio = ahorro_mensual / ideal
    return {
        "es_suficiente": ratio >= FRACCION_AHORRO_OK,
        "ratio": ratio,
        "ahorro_ideal": ideal,
    }


def razonar_clasificacion(
    progreso: dict,
    tiempo: dict,
    ahorro_info: dict,
    patrimonio: float,
    objetivo: float,
) -> dict:
    """RAZONAMIENTO: clasifica la situación financiera en 4 niveles."""
    meses = tiempo.get("meses")
    ratio_pat = objetivo / patrimonio if patrimonio > 0 else float("inf")
    suficiente = ahorro_info["es_suficiente"]

    if progreso["porcentaje_logrado"] >= 100:
        return {
            "clasificacion": CLAS_EXCELENTE,
            "descripcion": "Has alcanzado tu objetivo de patrimonio.",
        }

    if meses is None or meses > MESES_MUY_AMBIOSO or ratio_pat >= RATIO_MUY_AMBIOSO:
        return {
            "clasificacion": CLAS_MUY_AMBIOSO,
            "descripcion": (
                "El objetivo es muy ambicioso con tu patrimonio y ahorro actuales."
            ),
        }

    if meses <= MESES_EXCELENTE and suficiente:
        return {
            "clasificacion": CLAS_EXCELENTE,
            "descripcion": f"Excelente ritmo: ~{meses} meses al ahorro actual.",
        }

    if meses <= MESES_BUEN_CAMINO and suficiente:
        return {
            "clasificacion": CLAS_BUEN_CAMINO,
            "descripcion": f"Vas por buen camino: ~{meses} meses ({meses // 12} años).",
        }

    if not suficiente or meses > MESES_BUEN_CAMINO:
        return {
            "clasificacion": CLAS_NECESITA_MEJORA,
            "descripcion": (
                "Puedes llegar, pero necesitas mejorar el ahorro mensual o el plazo."
            ),
        }

    return {
        "clasificacion": CLAS_BUEN_CAMINO,
        "descripcion": "Situación estable; mantén la constancia.",
    }


def razonar_recomendaciones(
    clasificacion: str,
    perfil: dict[str, float],
    progreso: dict,
    tiempo: dict,
    ahorro_info: dict,
    plan: dict,
) -> list[str]:
    """RAZONAMIENTO: genera recomendaciones según la clasificación."""
    ahorro = perfil["ahorro_mensual"]
    faltante = progreso["faltante"]
    ideal = ahorro_info["ahorro_ideal"]
    plan_mes = plan["ahorro_mensual_necesario"]

    if clasificacion == CLAS_EXCELENTE:
        return [
            "🌟 Clasificación: Excelente — tu plan es muy sólido.",
            progreso["mensaje"],
            "Automatiza el ahorro el día de cobro y revisa el plan cada 6 meses.",
            "Cuando tengas fondo de emergencia, valora inversiones conservadoras.",
        ]

    if clasificacion == CLAS_BUEN_CAMINO:
        meses = tiempo.get("meses", 0)
        return [
            "✅ Clasificación: Buen camino — vas en la dirección correcta.",
            progreso["mensaje"],
            f"Con {ahorro:,.0f} €/mes llegarías en ~{meses} meses.",
            plan["mensaje"],
            "Mantén el hábito; un pequeño aumento del 5% acortaría el plazo.",
        ]

    if clasificacion == CLAS_NECESITA_MEJORA:
        meses = tiempo.get("meses", "?")
        return [
            "📈 Clasificación: Necesita mejora — el plan es posible pero ajustado.",
            progreso["mensaje"],
            f"Tu ahorro actual: {ahorro:,.0f} €/mes. Referencia ideal: {ideal:,.0f} €/mes.",
            plan["mensaje"],
            f"Al ritmo actual tardarías ~{meses} meses. Prioridad: subir ahorro un 15-20%.",
            "Revisa 3 gastos fijos (suscripciones, seguros) antes de asumir más riesgo.",
        ]

    return [
        "⚠️ Clasificación: Objetivo muy ambicioso para tu situación actual.",
        progreso["mensaje"],
        plan["mensaje"],
        f"Te faltan {faltante:,.0f} €. Valora un hito intermedio (50% del objetivo).",
        f"Para un plan cómodo en 5 años necesitas ~{plan_mes:,.0f} €/mes.",
        "Divide el objetivo en 3 fases y celebra cada una.",
    ]


def analizar_perfil(perfil: dict[str, float]) -> dict:
    """RAZONAMIENTO: orquesta tools de cálculo y reglas de recomendación."""
    patrimonio = perfil["patrimonio"]
    ahorro = perfil["ahorro_mensual"]
    objetivo = perfil["objetivo"]

    progreso = evaluar_progreso(patrimonio, objetivo)
    tiempo = calcular_tiempo_objetivo(patrimonio, ahorro, objetivo)
    plan = generar_plan_mensual(progreso["faltante"], HORIZONTE_PLAN_ANOS)
    ahorro_info = razonar_suficiencia_ahorro(ahorro, progreso["faltante"])
    clasif = razonar_clasificacion(progreso, tiempo, ahorro_info, patrimonio, objetivo)
    recomendaciones = razonar_recomendaciones(
        clasif["clasificacion"],
        perfil,
        progreso,
        tiempo,
        ahorro_info,
        plan,
    )

    return {
        "progreso": progreso,
        "tiempo": tiempo,
        "plan_mensual": plan,
        "ahorro_info": ahorro_info,
        "clasificacion": clasif,
        "recomendaciones": recomendaciones,
    }

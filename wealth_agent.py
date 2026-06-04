#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wealth Coach Agent — versión inteligente (v3)
=============================================

Mapa del código para aprender Agentic AI:
  📁 MEMORIA      → wealth_data.txt + tools que leen/escriben
  🔧 TOOLS       → funciones que calculan y transforman datos
  🧠 RAZONAMIENTO → reglas que evalúan, clasifican y recomiendan
  🖥️  ACCIONES     → menú que conecta al usuario con lo anterior
"""

from __future__ import annotations

import math
from pathlib import Path

# =============================================================================
# 📁 MEMORIA DEL AGENTE
# =============================================================================
# La memoria es información que persiste entre ejecuciones del programa.
# Sin memoria, el agente "olvida" al cerrar la terminal.
#
# En este proyecto la memoria externa es el archivo wealth_data.txt.
# Las tools tool_guardar_datos / tool_leer_datos / tool_cargar_perfil
# son el ÚNICO camino para escribir y leer esa memoria.

WEALTH_DATA_FILE = Path(__file__).with_name("wealth_data.txt")

# Etiquetas de clasificación (salida del razonamiento)
CLAS_EXCELENTE = "Excelente"
CLAS_BUEN_CAMINO = "BuenCamino"
CLAS_NECESITA_MEJORA = "NecesitaMejora"
CLAS_MUY_AMBIOSO = "ObjetivoMuyAmbicioso"

# Criterios del razonamiento (umbrales que el agente usa para decidir)
MESES_EXCELENTE = 24        # ≤ 2 años al ritmo actual
MESES_BUEN_CAMINO = 60      # ≤ 5 años
MESES_MUY_AMBIOSO = 120     # > 10 años → objetivo muy ambicioso
RATIO_MUY_AMBIOSO = 10      # objetivo > 10× patrimonio
FRACCION_AHORRO_OK = 0.70   # 70% del ahorro "ideal" = suficiente
HORIZONTE_PLAN_ANOS = 5     # plan mensual de referencia


# =============================================================================
# 🔧 TOOLS — HERRAMIENTAS DEL AGENTE
# =============================================================================
# Una tool hace UNA tarea concreta. No decide sola: devuelve datos.
# El razonamiento (más abajo) usa esos datos para clasificar y recomendar.
#
# Tools de memoria:  tool_guardar_datos, tool_leer_datos, tool_cargar_perfil
# Tools de cálculo:  tool_calcular_tiempo, tool_evaluar_progreso, tool_generar_plan_mensual
# Tool orquestadora: tool_analizar_perfil (llama a las demás y al razonamiento)


def pedir_numero_positivo(mensaje: str) -> float:
    """Utilidad de entrada: percibe datos del usuario (no es memoria ni razonamiento)."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(texto)
            if valor < 0:
                print("  ⚠️  El valor no puede ser negativo. Inténtalo de nuevo.")
                continue
            return valor
        except ValueError:
            print("  ⚠️  Escribe un número válido (ejemplo: 15000 o 15000.50).")


# --- Tools de MEMORIA ---

def tool_guardar_datos(patrimonio: float, ahorro_mensual: float, objetivo: float) -> None:
    """TOOL (memoria): escribe el perfil en wealth_data.txt."""
    contenido = (
        "💰 Wealth Coach Agent — Datos guardados\n"
        "========================================\n"
        f"Patrimonio actual (€): {patrimonio:,.2f}\n"
        f"Ahorro mensual (€):    {ahorro_mensual:,.2f}\n"
        f"Objetivo patrimonio (€): {objetivo:,.2f}\n"
    )
    WEALTH_DATA_FILE.write_text(contenido, encoding="utf-8")


def tool_leer_datos() -> str | None:
    """TOOL (memoria): lee wealth_data.txt como texto."""
    if not WEALTH_DATA_FILE.exists():
        return None
    return WEALTH_DATA_FILE.read_text(encoding="utf-8")


def _extraer_numero_de_linea(linea: str) -> float:
    valor = linea.split(":", 1)[1].strip().replace("€", "").strip().replace(",", "")
    return float(valor)


def tool_cargar_perfil() -> dict[str, float] | None:
    """TOOL (memoria): convierte el archivo en números para el resto del agente."""
    texto = tool_leer_datos()
    if texto is None:
        return None

    claves = {
        "Patrimonio actual": "patrimonio",
        "Ahorro mensual": "ahorro_mensual",
        "Objetivo patrimonio": "objetivo",
    }
    perfil: dict[str, float] = {}
    for linea in texto.splitlines():
        for frag, nombre in claves.items():
            if frag in linea:
                perfil[nombre] = _extraer_numero_de_linea(linea)
                break

    return perfil if len(perfil) == 3 else None


# --- Tools de CÁLCULO ---

def tool_calcular_tiempo_objetivo(
    patrimonio: float, ahorro_mensual: float, objetivo: float
) -> dict:
    """TOOL: meses necesarios con el ahorro actual (sin intereses)."""
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


def tool_evaluar_progreso(patrimonio: float, objetivo: float) -> dict:
    """
    TOOL: evalúa el patrimonio actual respecto al objetivo.

    Devuelve cuánto falta, qué % del objetivo ya tienes y un mensaje legible.
    """
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


def tool_generar_plan_mensual(faltante: float, anos: int = HORIZONTE_PLAN_ANOS) -> dict:
    """
    TOOL: plan de ahorro mensual sencillo para un horizonte en años.

    Ejemplo de salida: "Para alcanzar tu objetivo en 5 años deberías X €/mes"
    """
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


# =============================================================================
# 🧠 RAZONAMIENTO DEL AGENTE
# =============================================================================
# Aquí el agente "piensa": no guarda en disco ni pide input directamente.
# Lee resultados de las tools y aplica REGLAS (if/elif) para:
#   - clasificar tu situación
#   - elegir recomendaciones distintas
#
# En un agente con LLM, este bloque sería el prompt + decisión del modelo.


def _ahorro_ideal_mensual(faltante: float, meses: int = MESES_BUEN_CAMINO) -> float:
    """Ahorro mensual de referencia para llegar en N meses."""
    if faltante <= 0:
        return 0.0
    return faltante / meses


def razonar_suficiencia_ahorro(ahorro_mensual: float, faltante: float) -> dict:
    """RAZONAMIENTO 1: ¿el ahorro actual es suficiente respecto al plan de 5 años?"""
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
    """
    RAZONAMIENTO 2: clasificación global en 4 niveles.

    Excelente          → ritmo rápido o objetivo cumplido
    BuenCamino         → plan viable en ≤ 5 años con ahorro adecuado
    NecesitaMejora     → se puede llegar, pero hay que subir el ahorro
    ObjetivoMuyAmbicioso → plazo muy largo o salto de patrimonio enorme
    """
    faltante = progreso["faltante"]
    meses = tiempo.get("meses")
    ratio_pat = objetivo / patrimonio if patrimonio > 0 else float("inf")
    suficiente = ahorro_info["es_suficiente"]

    # DECISIÓN: objetivo ya conseguido
    if progreso["porcentaje_logrado"] >= 100:
        return {
            "clasificacion": CLAS_EXCELENTE,
            "descripcion": "Has alcanzado tu objetivo de patrimonio.",
        }

    # DECISIÓN: sin ahorro o plazo > 10 años o objetivo >> patrimonio
    if meses is None or meses > MESES_MUY_AMBIOSO or ratio_pat >= RATIO_MUY_AMBIOSO:
        return {
            "clasificacion": CLAS_MUY_AMBIOSO,
            "descripcion": (
                "El objetivo es muy ambicioso con tu patrimonio y ahorro actuales."
            ),
        }

    # DECISIÓN: llegarías en ≤ 2 años con ahorro suficiente
    if meses <= MESES_EXCELENTE and suficiente:
        return {
            "clasificacion": CLAS_EXCELENTE,
            "descripcion": f"Excelente ritmo: ~{meses} meses al ahorro actual.",
        }

    # DECISIÓN: plan sano (≤ 5 años) y ahorro OK
    if meses <= MESES_BUEN_CAMINO and suficiente:
        return {
            "clasificacion": CLAS_BUEN_CAMINO,
            "descripcion": f"Vas por buen camino: ~{meses} meses ({meses // 12} años).",
        }

    # DECISIÓN: ahorro bajo o plazo entre 5 y 10 años
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
    """
    RAZONAMIENTO 3: recomendaciones personalizadas según la clasificación.

    Cada rama if es una estrategia distinta — polimorfismo de reglas.
    """
    p, a, o = perfil["patrimonio"], perfil["ahorro_mensual"], perfil["objetivo"]
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
            f"Con {a:,.0f} €/mes llegarías en ~{meses} meses.",
            plan["mensaje"],
            "Mantén el hábito; un pequeño aumento del 5% acortaría el plazo.",
        ]

    if clasificacion == CLAS_NECESITA_MEJORA:
        meses = tiempo.get("meses", "?")
        return [
            "📈 Clasificación: Necesita mejora — el plan es posible pero ajustado.",
            progreso["mensaje"],
            f"Tu ahorro actual: {a:,.0f} €/mes. Referencia ideal: {ideal:,.0f} €/mes.",
            plan["mensaje"],
            f"Al ritmo actual tardarías ~{meses} meses. Prioridad: subir ahorro un 15-20%.",
            "Revisa 3 gastos fijos (suscripciones, seguros) antes de asumir más riesgo.",
        ]

    # ObjetivoMuyAmbicioso
    return [
        "⚠️ Clasificación: Objetivo muy ambicioso para tu situación actual.",
        progreso["mensaje"],
        plan["mensaje"],
        f"Te faltan {faltante:,.0f} €. Valora un hito intermedio (50% del objetivo).",
        f"Para un plan cómodo en 5 años necesitas ~{plan_mes:,.0f} €/mes.",
        "Divide el objetivo en 3 fases y celebra cada una.",
    ]


def tool_analizar_perfil(perfil: dict[str, float]) -> dict:
    """
    TOOL orquestadora: une memoria (datos) + cálculos + razonamiento.

    Flujo típico de un agente:
      1) tools calculan hechos
      2) razonamiento interpreta hechos
      3) acción muestra resultado al usuario
    """
    patrimonio = perfil["patrimonio"]
    ahorro = perfil["ahorro_mensual"]
    objetivo = perfil["objetivo"]

    progreso = tool_evaluar_progreso(patrimonio, objetivo)
    tiempo = tool_calcular_tiempo_objetivo(patrimonio, ahorro, objetivo)
    plan = tool_generar_plan_mensual(progreso["faltante"], HORIZONTE_PLAN_ANOS)
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


# =============================================================================
# 🖥️ ACCIONES — interfaz con el usuario (menú)
# =============================================================================
# Las acciones no son memoria ni razonamiento puro: coordinan el flujo.
# Patrón: leer memoria → analizar → mostrar.


def mostrar_analisis_completo(analisis: dict) -> None:
    """Muestra evaluación, clasificación, plan mensual y recomendaciones."""
    prog = analisis["progreso"]
    tiempo = analisis["tiempo"]
    plan = analisis["plan_mensual"]
    clasif = analisis["clasificacion"]

    print("\n" + "=" * 50)
    print("  🧠 Informe Wealth Coach Agent")
    print("=" * 50)

    print("\n  📊 Evaluación patrimonio vs objetivo")
    print(f"     {prog['mensaje']}")

    print(f"\n  🏷️  Clasificación: {clasif['clasificacion']}")
    print(f"     {clasif['descripcion']}")

    if not tiempo.get("ya_alcanzado") and tiempo.get("ok"):
        print(f"\n  ⏱️  Con tu ahorro actual: {tiempo['meses']} meses "
              f"({tiempo['anos']} años y {tiempo['meses_restantes']} meses)")

    print(f"\n  📅 Plan mensual de referencia ({plan['anos']} años)")
    print(f"     {plan['mensaje']}")

    print("\n  💡 Recomendaciones personalizadas:")
    for i, rec in enumerate(analisis["recomendaciones"], start=1):
        print(f"     {i}. {rec}")
    print()


def accion_registrar_perfil() -> None:
    print("\n📋 Registra tu perfil financiero.\n")
    patrimonio = pedir_numero_positivo("  Patrimonio actual (€): ")
    ahorro = pedir_numero_positivo("  Ahorro mensual (€): ")
    objetivo = pedir_numero_positivo("  Objetivo de patrimonio (€): ")

    tool_guardar_datos(patrimonio, ahorro, objetivo)
    print("\n✅ Guardado en memoria (wealth_data.txt)")

    analisis = tool_analizar_perfil(
        {"patrimonio": patrimonio, "ahorro_mensual": ahorro, "objetivo": objetivo}
    )
    print(f"\n  Vista rápida: {analisis['clasificacion']['clasificacion']}")
    print(f"  {analisis['plan_mensual']['mensaje']}")
    print("  Opción 3 → informe completo.")


def accion_ver_datos_guardados() -> None:
    datos = tool_leer_datos()
    if datos is None:
        print("\n📭 Sin datos en memoria. Usa opción 1.")
        return
    print("\n📂 Memoria (wealth_data.txt):")
    print("-" * 40)
    print(datos)


def accion_analizar_plan() -> None:
    perfil = tool_cargar_perfil()
    if perfil is None:
        print("\n📭 No hay perfil en memoria. Usa opción 1.")
        return
    mostrar_analisis_completo(tool_analizar_perfil(perfil))


def mostrar_menu() -> None:
    print("\n" + "=" * 44)
    print("  💰 Wealth Coach Agent v3")
    print("=" * 44)
    print("  1) Registrar / actualizar perfil")
    print("  2) Ver memoria guardada")
    print("  3) Análisis completo (clasificación + plan + consejos)")
    print("  4) Salir")
    print("-" * 44)


def main() -> None:
    print("🤖 Wealth Coach Agent — memoria + tools + razonamiento\n")

    while True:
        mostrar_menu()
        opcion = input("Elige (1-4): ").strip()

        if opcion == "1":
            accion_registrar_perfil()
        elif opcion == "2":
            accion_ver_datos_guardados()
        elif opcion == "3":
            accion_analizar_plan()
        elif opcion == "4":
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción no válida.")


if __name__ == "__main__":
    main()

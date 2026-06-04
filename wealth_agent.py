#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wealth Coach Agent — versión con razonamiento
=============================================

Además de tools y memoria, este agente tiene un "cerebro" basado en REGLAS:
evalúa tu situación y elige recomendaciones distintas según lo que detecte.

En Agentic AI avanzado, un LLM haría estas decisiones en lenguaje natural.
Aquí las simulamos con if/elif claros para que veas DÓNDE decide el agente.
"""

from __future__ import annotations

import math
from pathlib import Path

WEALTH_DATA_FILE = Path(__file__).with_name("wealth_data.txt")

# -----------------------------------------------------------------------------
# UMBRALES DE DECISIÓN (el agente usa estas constantes para "pensar")
# -----------------------------------------------------------------------------
# Cambiar un umbral cambia el comportamiento del agente: son sus "criterios".

MESES_PLAN_RAPIDO = 24       # ≤ 2 años  → plan muy favorable
MESES_PLAN_SANO = 60         # ≤ 5 años  → plan realista
MESES_PLAN_LARGO = 120       # ≤ 10 años → plan exigente
# Más de 120 meses → consideramos el objetivo muy ambicioso con el ahorro actual

RATIO_OBJETIVO_ALTO = 5      # objetivo > 5× patrimonio → salto grande
RATIO_OBJETIVO_MUY_ALTO = 10 # objetivo > 10× patrimonio → muy ambicioso

FRACCION_AHORRO_MINIMA = 0.70  # si ahorras < 70% del "ideal", no es suficiente


# -----------------------------------------------------------------------------
# UTILIDADES
# -----------------------------------------------------------------------------

def pedir_numero_positivo(mensaje: str) -> float:
    """Pide un número válido al usuario (percepción del agente)."""
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


# -----------------------------------------------------------------------------
# TOOLS (memoria y cálculos)
# -----------------------------------------------------------------------------

def tool_guardar_datos(patrimonio: float, ahorro_mensual: float, objetivo: float) -> None:
    """TOOL: persistir perfil en wealth_data.txt (memoria externa)."""
    contenido = (
        "💰 Wealth Coach Agent — Datos guardados\n"
        "========================================\n"
        f"Patrimonio actual (€): {patrimonio:,.2f}\n"
        f"Ahorro mensual (€):    {ahorro_mensual:,.2f}\n"
        f"Objetivo patrimonio (€): {objetivo:,.2f}\n"
    )
    WEALTH_DATA_FILE.write_text(contenido, encoding="utf-8")


def tool_leer_datos() -> str | None:
    """TOOL: leer memoria como texto."""
    if not WEALTH_DATA_FILE.exists():
        return None
    return WEALTH_DATA_FILE.read_text(encoding="utf-8")


def _extraer_numero_de_linea(linea: str) -> float:
    valor = linea.split(":", 1)[1].strip()
    valor = valor.replace("€", "").strip().replace(",", "")
    return float(valor)


def tool_cargar_perfil() -> dict[str, float] | None:
    """TOOL: convertir memoria en números para otras tools y el razonamiento."""
    texto = tool_leer_datos()
    if texto is None:
        return None

    claves_linea = {
        "Patrimonio actual": "patrimonio",
        "Ahorro mensual": "ahorro_mensual",
        "Objetivo patrimonio": "objetivo",
    }
    perfil: dict[str, float] = {}

    for linea in texto.splitlines():
        for fragmento, nombre in claves_linea.items():
            if fragmento in linea:
                perfil[nombre] = _extraer_numero_de_linea(linea)
                break

    if len(perfil) != 3:
        return None
    return perfil


def tool_calcular_tiempo_objetivo(
    patrimonio: float,
    ahorro_mensual: float,
    objetivo: float,
) -> dict:
    """TOOL: meses hasta el objetivo (ahorro lineal, sin intereses)."""
    faltante = objetivo - patrimonio

    if faltante <= 0:
        return {
            "ok": True,
            "ya_alcanzado": True,
            "meses": 0,
            "faltante": 0.0,
        }

    if ahorro_mensual == 0:
        return {
            "ok": False,
            "ya_alcanzado": False,
            "meses": None,
            "faltante": faltante,
        }

    meses = math.ceil(faltante / ahorro_mensual)
    return {
        "ok": True,
        "ya_alcanzado": False,
        "meses": meses,
        "anos": meses // 12,
        "meses_restantes": meses % 12,
        "faltante": faltante,
    }


# -----------------------------------------------------------------------------
# NÚCLEO DE DECISIÓN (aquí el agente "piensa" con reglas)
# -----------------------------------------------------------------------------
# Cada función devuelve etiquetas y datos. Otra función usa eso para recomendar.


def _ahorro_ideal_mensual(faltante: float) -> float:
    """
    Cuánto habría que ahorrar al mes para llegar en MESES_PLAN_SANO (5 años).
    Sirve de referencia para decidir si el ahorro actual es suficiente.
    """
    if faltante <= 0:
        return 0.0
    return faltante / MESES_PLAN_SANO


def decidir_suficiencia_ahorro(ahorro_mensual: float, faltante: float) -> dict:
    """
    DECISIÓN 1: ¿El ahorro mensual es suficiente?

    Compara tu ahorro real con el ahorro "ideal" (llegar en ~5 años).
    """
    if faltante <= 0:
        return {
            "nivel": "no_aplica",
            "etiqueta": "Objetivo ya alcanzado",
            "ahorro_ideal": 0.0,
            "es_suficiente": True,
        }

    if ahorro_mensual == 0:
        return {
            "nivel": "nulo",
            "etiqueta": "Sin ahorro mensual",
            "ahorro_ideal": _ahorro_ideal_mensual(faltante),
            "es_suficiente": False,
        }

    ideal = _ahorro_ideal_mensual(faltante)
    ratio = ahorro_mensual / ideal if ideal > 0 else 1.0

    # DECISIÓN: clasificamos el ahorro según qué fracción del ideal representa.
    if ratio >= 1.0:
        nivel, etiqueta, suficiente = "holgado", "Ahorro suficiente (por encima del ritmo ideal)", True
    elif ratio >= FRACCION_AHORRO_MINIMA:
        nivel, etiqueta, suficiente = "ajustado", "Ahorro justo (llegarás, pero sin mucho margen)", True
    elif ratio >= 0.40:
        nivel, etiqueta, suficiente = "bajo", "Ahorro insuficiente para un plan cómodo", False
    else:
        nivel, etiqueta, suficiente = "muy_bajo", "Ahorro muy por debajo de lo necesario", False

    return {
        "nivel": nivel,
        "etiqueta": etiqueta,
        "ahorro_ideal": ideal,
        "ratio_vs_ideal": ratio,
        "es_suficiente": suficiente,
    }


def decidir_ambicion_objetivo(
    patrimonio: float,
    objetivo: float,
    meses: int | None,
) -> dict:
    """
    DECISIÓN 2: ¿El objetivo es demasiado ambicioso?

    Usa dos señales: cuánto multiplica tu patrimonio actual y cuántos meses tardarías.
    """
    if objetivo <= patrimonio:
        return {
            "nivel": "alcanzado",
            "etiqueta": "Objetivo ya alcanzado",
            "es_ambicioso": False,
            "ratio_objetivo_patrimonio": objetivo / patrimonio if patrimonio > 0 else 1.0,
        }

    ratio = objetivo / patrimonio if patrimonio > 0 else float("inf")

    # DECISIÓN: sin meses calculables (ahorro 0), el objetivo es inviable por ahorro.
    if meses is None:
        return {
            "nivel": "inviable",
            "etiqueta": "Objetivo inalcanzable solo con ahorro actual (ahorro = 0)",
            "es_ambicioso": True,
            "ratio_objetivo_patrimonio": ratio,
        }

    # DECISIÓN: combinamos plazo largo + salto grande de patrimonio.
    if meses > MESES_PLAN_LARGO or ratio >= RATIO_OBJETIVO_MUY_ALTO:
        nivel, etiqueta, ambicioso = (
            "muy_ambicioso",
            "Objetivo muy ambicioso para tu ritmo actual",
            True,
        )
    elif meses > MESES_PLAN_SANO or ratio >= RATIO_OBJETIVO_ALTO:
        nivel, etiqueta, ambicioso = (
            "ambicioso",
            "Objetivo exigente: posible, pero requerirá constancia",
            True,
        )
    elif meses > MESES_PLAN_RAPIDO:
        nivel, etiqueta, ambicioso = "moderado", "Objetivo razonable a medio plazo", False
    else:
        nivel, etiqueta, ambicioso = "alcanzable", "Objetivo alcanzable en poco tiempo", False

    return {
        "nivel": nivel,
        "etiqueta": etiqueta,
        "es_ambicioso": ambicioso,
        "ratio_objetivo_patrimonio": ratio,
        "meses_estimados": meses,
    }


def decidir_situacion_global(
    ya_alcanzado: bool,
    ahorro: dict,
    ambicion: dict,
    meses: int | None,
) -> str:
    """
    DECISIÓN 3: situación global (una etiqueta que resume todo).

    Esta etiqueta elige qué bloque de recomendaciones mostrar después.
    """
    if ya_alcanzado:
        return "objetivo_cumplido"

    if ahorro["nivel"] == "nulo":
        return "sin_ahorro"

    if meses is None:
        return "plan_inviable"

    if ambicion["nivel"] == "muy_ambicioso" and not ahorro["es_suficiente"]:
        return "crisis_plan"  # poco ahorro + objetivo lejano

    if not ahorro["es_suficiente"]:
        return "ahorro_insuficiente"

    if ambicion["nivel"] in ("muy_ambicioso", "ambicioso"):
        return "objetivo_ambicioso"

    if meses <= MESES_PLAN_RAPIDO:
        return "plan_excelente"

    if meses <= MESES_PLAN_SANO:
        return "plan_solido"

    return "plan_largo"


def generar_recomendaciones(
    situacion: str,
    perfil: dict[str, float],
    ahorro: dict,
    ambicion: dict,
    tiempo: dict,
) -> list[str]:
    """
    DECISIÓN 4: recomendaciones distintas según la situación detectada.

    Cada rama del if es un "plan de acción" diferente — como un agente
    que elige distinta estrategia según el contexto.
    """
    p = perfil["patrimonio"]
    a = perfil["ahorro_mensual"]
    o = perfil["objetivo"]
    faltante = tiempo.get("faltante", max(0, o - p))
    ideal = ahorro.get("ahorro_ideal", 0)

    if situacion == "objetivo_cumplido":
        return [
            "🎉 ¡Enhorabuena! Ya has llegado a tu objetivo de patrimonio.",
            "Define un nuevo objetivo (opción 1) o sube el listón poco a poco.",
            "Considera diversificar: fondo de emergencia, inversiones, etc.",
        ]

    if situacion == "sin_ahorro":
        return [
            "⚠️ Sin ahorro mensual no avanzarás hacia el objetivo.",
            f"Para llegar en ~5 años necesitarías ahorrar unos {ideal:,.0f} €/mes.",
            "Empieza pequeño: revisa 3 gastos recurrentes y destina ese importe al ahorro.",
            "Registra de nuevo tu perfil (opción 1) cuando subas el ahorro.",
        ]

    if situacion == "plan_inviable":
        return [
            "🛑 Con los datos actuales el plan no es viable solo ahorrando.",
            f"Te faltan {faltante:,.0f} €. Necesitas ahorro mensual > 0.",
            f"Referencia: ~{ideal:,.0f} €/mes para un horizonte de 5 años.",
        ]

    if situacion == "crisis_plan":
        return [
            "🔴 Situación crítica: objetivo muy lejano y ahorro bajo.",
            f"Sube el ahorro hacia al menos {ideal * FRACCION_AHORRO_MINIMA:,.0f} €/mes (70% del ritmo ideal).",
            "O baja el objetivo a un hito intermedio (ej. la mitad) y celebra cada logro.",
            "Revisa ingresos extra (freelance, venta ocasional) o recorta gastos fijos.",
        ]

    if situacion == "ahorro_insuficiente":
        meses = tiempo["meses"]
        return [
            f"📉 Tu ahorro ({a:,.0f} €/mes) no es suficiente para un plan cómodo.",
            f"Ideal orientativo: {ideal:,.0f} €/mes (llegarías en ~5 años).",
            f"Al ritmo actual tardarías ~{meses} meses ({meses // 12} años).",
            "Prioridad: sube el ahorro un 10-20% antes de buscar inversiones arriesgadas.",
        ]

    if situacion == "objetivo_ambicioso":
        meses = tiempo["meses"]
        return [
            f"🎯 Objetivo exigente: {ambicion['etiqueta']}.",
            f"Tiempo estimado: {meses} meses (~{meses // 12} años) con {a:,.0f} €/mes.",
            "Divide el objetivo en 3 hitos (33%, 66%, 100%) y revisa cada trimestre.",
            "Mantén un fondo de emergencia aparte para no romper el plan.",
        ]

    if situacion == "plan_excelente":
        meses = tiempo["meses"]
        return [
            f"✅ ¡Buen ritmo! Llegarías en ~{meses} meses con tu ahorro actual.",
            "Automatiza la transferencia el día de cobro para no depender de la fuerza de voluntad.",
            "Cuando tengas 3-6 meses de gastos en emergencia, mira productos de bajo riesgo.",
        ]

    if situacion == "plan_solido":
        meses = tiempo["meses"]
        return [
            f"👍 Plan sólido: unos {meses} meses ({meses // 12} años) al ritmo actual.",
            "Tu ahorro mensual es adecuado para el objetivo marcado.",
            "Revisa el progreso cada 6 meses (opción 3) y ajusta si cambia tu sueldo.",
        ]

    # plan_largo
    meses = tiempo["meses"]
    return [
        f"⏳ Plan largo pero posible: ~{meses} meses ({meses // 12} años).",
        "El objetivo no es imposible, pero exige disciplina a largo plazo.",
        "Valora si puedes aumentar ingresos o reducir el objetivo un 15-20% para acortar plazo.",
    ]


def tool_analizar_perfil(perfil: dict[str, float]) -> dict:
    """
    TOOL principal de razonamiento: encadena todas las decisiones.

    Flujo: calcular tiempo → evaluar ahorro → evaluar ambición → situación global → recomendaciones.
    """
    patrimonio = perfil["patrimonio"]
    ahorro_mensual = perfil["ahorro_mensual"]
    objetivo = perfil["objetivo"]

    tiempo = tool_calcular_tiempo_objetivo(patrimonio, ahorro_mensual, objetivo)
    faltante = tiempo.get("faltante", max(0, objetivo - patrimonio))

    eval_ahorro = decidir_suficiencia_ahorro(ahorro_mensual, faltante)
    eval_ambicion = decidir_ambicion_objetivo(
        patrimonio,
        objetivo,
        tiempo.get("meses"),
    )
    situacion = decidir_situacion_global(
        tiempo.get("ya_alcanzado", False),
        eval_ahorro,
        eval_ambicion,
        tiempo.get("meses"),
    )
    recomendaciones = generar_recomendaciones(
        situacion, perfil, eval_ahorro, eval_ambicion, tiempo
    )

    return {
        "tiempo": tiempo,
        "ahorro": eval_ahorro,
        "ambicion": eval_ambicion,
        "situacion": situacion,
        "recomendaciones": recomendaciones,
    }


def mostrar_analisis(analisis: dict) -> None:
    """Presenta al usuario el resultado del razonamiento del agente."""
    tiempo = analisis["tiempo"]
    ahorro = analisis["ahorro"]
    ambicion = analisis["ambicion"]

    print("\n" + "=" * 48)
    print("  🧠 Análisis inteligente de tu plan")
    print("=" * 48)

    if tiempo.get("ya_alcanzado"):
        print("\n  Estado: objetivo ya alcanzado 🎉")
    elif tiempo.get("ok"):
        print(f"\n  Te faltan: {tiempo['faltante']:,.2f} €")
        print(f"  Tiempo estimado: {tiempo['meses']} meses", end="")
        if tiempo.get("anos", 0) > 0:
            print(f" (~{tiempo['anos']} año(s) y {tiempo['meses_restantes']} mes(es))")
        else:
            print()
    else:
        print(f"\n  Te faltan: {tiempo['faltante']:,.2f} €")
        print("  No se puede calcular plazo (ahorro mensual = 0).")

    print(f"\n  💶 Ahorro: {ahorro['etiqueta']}")
    if ahorro.get("ahorro_ideal", 0) > 0:
        print(f"     Referencia ideal (~5 años): {ahorro['ahorro_ideal']:,.0f} €/mes")

    print(f"  🎯 Objetivo: {ambicion['etiqueta']}")
    if ambicion.get("ratio_objetivo_patrimonio"):
        print(f"     Tu objetivo es {ambicion['ratio_objetivo_patrimonio']:.1f}× tu patrimonio actual")

    print(f"\n  📌 Situación detectada: {analisis['situacion'].replace('_', ' ')}")
    print("\n  Recomendaciones personalizadas:")
    for i, rec in enumerate(analisis["recomendaciones"], start=1):
        print(f"    {i}. {rec}")
    print()


# -----------------------------------------------------------------------------
# ACCIONES DEL AGENTE
# -----------------------------------------------------------------------------

def accion_registrar_perfil() -> None:
    print("\n📋 Vamos a registrar tu perfil financiero.")
    print("   (Responde con números en euros)\n")

    patrimonio = pedir_numero_positivo("  Patrimonio actual (€): ")
    ahorro = pedir_numero_positivo("  Ahorro mensual (€): ")
    objetivo = pedir_numero_positivo("  Objetivo de patrimonio (€): ")

    tool_guardar_datos(patrimonio, ahorro, objetivo)

    print("\n✅ Datos guardados en 'wealth_data.txt'")

    # Tras guardar, el agente razona automáticamente sobre el nuevo perfil.
    perfil = {"patrimonio": patrimonio, "ahorro_mensual": ahorro, "objetivo": objetivo}
    analisis = tool_analizar_perfil(perfil)
    print("\n  Vista rápida tras registrar:")
    print(f"  • {analisis['ahorro']['etiqueta']}")
    print(f"  • {analisis['ambicion']['etiqueta']}")
    print("  • Usa la opción 3 para el análisis completo con recomendaciones.")


def accion_ver_datos_guardados() -> None:
    datos = tool_leer_datos()
    if datos is None:
        print("\n📭 Aún no hay datos guardados.")
        print("   Usa la opción 1 del menú para registrar tu perfil.")
        return
    print("\n📂 Datos guardados:")
    print("-" * 40)
    print(datos)


def accion_analizar_plan() -> None:
    """
    Acción inteligente: memoria → tool_analizar_perfil → mostrar decisiones.
    """
    perfil = tool_cargar_perfil()
    if perfil is None:
        print("\n📭 No hay perfil guardado o el archivo está incompleto.")
        print("   Usa la opción 1 para registrar patrimonio, ahorro y objetivo.")
        return

    analisis = tool_analizar_perfil(perfil)
    mostrar_analisis(analisis)


def mostrar_menu() -> None:
    print("\n" + "=" * 44)
    print("  💰 Wealth Coach Agent (con razonamiento)")
    print("=" * 44)
    print("  1) Registrar / actualizar perfil financiero")
    print("  2) Ver datos guardados")
    print("  3) Analizar plan y recibir recomendaciones")
    print("  4) Salir")
    print("-" * 44)


def main() -> None:
    print("🤖 Bienvenido a Wealth Coach Agent")
    print("   Agente con reglas de decisión para aprender Agentic AI.\n")

    while True:
        mostrar_menu()
        opcion = input("Elige una opción (1-4): ").strip()

        if opcion == "1":
            accion_registrar_perfil()
        elif opcion == "2":
            accion_ver_datos_guardados()
        elif opcion == "3":
            accion_analizar_plan()
        elif opcion == "4":
            print("\n👋 ¡Hasta luego! Sigue practicando con agentes.\n")
            break
        else:
            print("\n❌ Opción no válida. Escribe 1, 2, 3 o 4.")


if __name__ == "__main__":
    main()

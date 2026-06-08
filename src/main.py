from __future__ import annotations

import sys

from guardrails import validar_compra_grande, validar_liquidez_minima
from memory import cargar_perfil, guardar_datos, leer_datos, leer_gastos_mes, leer_perfil
from reasoning import analizar_perfil, planificar, razonar
from tools import calcular_impacto_financiero


# =============================================================================
# PUNTO DE ENTRADA DEL AGENTE
# =============================================================================
# main.py coordina el flujo: recibe input, llama a memoria/tools/razonamiento
# y muestra resultados. La lógica de negocio vive en los otros módulos.


def pedir_numero_positivo(mensaje: str) -> float:
    """Entrada de usuario: valida números antes de guardarlos en memoria."""
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


def ejecutar_plan(plan: list[str]) -> dict:
    """Ejecuta el plan llamando a memoria y tools, sin razonar todavía."""
    resultados = {}

    for paso in plan:
        if paso == "leer_perfil":
            resultados["perfil"] = leer_perfil()

        elif paso == "leer_gastos_mes":
            resultados["gastos"] = leer_gastos_mes()

        elif paso == "calcular_impacto_financiero":
            resultados["impacto"] = calcular_impacto_financiero(6000)

    return resultados


def evaluar_guardrails(perfil: dict | None = None, impacto: dict | None = None) -> list[dict]:
    """Valida reglas de seguridad antes de recomendar."""
    alertas = []

    # Guardrail de liquidez: comprueba fondo de emergencia si hay perfil.
    if perfil is not None:
        alertas.append(validar_liquidez_minima(perfil))

    # Guardrail de compra: se ejecuta solo cuando hubo cálculo de impacto.
    if impacto is not None:
        alertas.append(validar_compra_grande(impacto))

    return alertas


def mostrar_alertas_guardrails(alertas: list[dict]) -> None:
    """Muestra alertas antes de la recomendación final."""
    if not alertas:
        return

    print("\n🛡️ Guardrails:")
    for alerta in alertas:
        estado = "OK" if alerta["ok"] else "ALERTA"
        print(f"  {estado}: {alerta['mensaje']}")


def agente(pregunta: str) -> None:
    """Demo agentic: planifica, ejecuta tools y razona una respuesta."""
    print("🧠 Pregunta:", pregunta)

    plan = planificar(pregunta)
    print("📋 Plan:", plan)

    resultados = ejecutar_plan(plan)
    print("🛠️ Resultados tools:", resultados)

    alertas = evaluar_guardrails(
        perfil=resultados.get("perfil"),
        impacto=resultados.get("impacto"),
    )
    mostrar_alertas_guardrails(alertas)

    respuesta = razonar(pregunta, resultados)
    print("✅ Respuesta:", respuesta)


def mostrar_analisis_completo(analisis: dict, alertas: list[dict] | None = None) -> None:
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
        print(
            f"\n  ⏱️  Con tu ahorro actual: {tiempo['meses']} meses "
            f"({tiempo['anos']} años y {tiempo['meses_restantes']} meses)"
        )

    print(f"\n  📅 Plan mensual de referencia ({plan['anos']} años)")
    print(f"     {plan['mensaje']}")

    mostrar_alertas_guardrails(alertas or [])

    print("\n  💡 Recomendaciones personalizadas:")
    for i, rec in enumerate(analisis["recomendaciones"], start=1):
        print(f"     {i}. {rec}")
    print()


def accion_registrar_perfil() -> None:
    """Acción de UI: captura perfil, lo guarda en memoria y muestra resumen."""
    print("\n📋 Registra tu perfil financiero.\n")
    patrimonio = pedir_numero_positivo("  Patrimonio actual (€): ")
    ahorro = pedir_numero_positivo("  Ahorro mensual (€): ")
    objetivo = pedir_numero_positivo("  Objetivo de patrimonio (€): ")

    guardar_datos(patrimonio, ahorro, objetivo)
    print("\n✅ Guardado en memoria (data/wealth_data.txt)")

    perfil = {"patrimonio": patrimonio, "ahorro_mensual": ahorro, "objetivo": objetivo}
    alertas = evaluar_guardrails(perfil=perfil)
    mostrar_alertas_guardrails(alertas)

    analisis = analizar_perfil(perfil)
    print(f"\n  Vista rápida: {analisis['clasificacion']['clasificacion']}")
    print(f"  {analisis['plan_mensual']['mensaje']}")
    print("  Opción 3 → informe completo.")


def accion_ver_datos_guardados() -> None:
    """Acción de UI: muestra la memoria persistente."""
    datos = leer_datos()
    if datos is None:
        print("\n📭 Sin datos en memoria. Usa opción 1.")
        return

    print("\n📂 Memoria (data/wealth_data.txt):")
    print("-" * 40)
    print(datos)


def accion_analizar_plan() -> None:
    """Acción de UI: carga memoria y pide al razonamiento un informe."""
    perfil = cargar_perfil()
    if perfil is None:
        print("\n📭 No hay perfil en memoria. Usa opción 1.")
        return

    alertas = evaluar_guardrails(perfil=perfil)
    mostrar_analisis_completo(analizar_perfil(perfil), alertas)


def mostrar_menu() -> None:
    print("\n" + "=" * 44)
    print("  💰 Wealth Coach Agent v3")
    print("=" * 44)
    print("  1) Registrar / actualizar perfil")
    print("  2) Ver memoria guardada")
    print("  3) Análisis completo (clasificación + plan + consejos)")
    print("  4) Salir")
    print("-" * 44)


def ejecutar_menu() -> None:
    """Modo interactivo del agente."""
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


def main() -> None:
    """Entrada principal: demo por defecto, menú con --menu."""
    if len(sys.argv) > 1 and sys.argv[1] == "--menu":
        ejecutar_menu()
        return

    agente("¿Puedo comprar un Omega Aqua Terra este año?")


if __name__ == "__main__":
    main()

def validar_liquidez_minima(perfil):
    liquidez = perfil.get("liquidez", 0)
    gasto_mensual = perfil.get("gasto_mensual", 0)

    if gasto_mensual == 0:
        return {
            "ok": False,
            "mensaje": "No se puede validar la liquidez porque falta el gasto mensual."
        }

    meses_cubiertos = liquidez / gasto_mensual

    if meses_cubiertos < 6:
        return {
            "ok": False,
            "mensaje": "Fondo de emergencia inferior a 6 meses. Priorizar liquidez antes de asumir más riesgo."
        }

    return {
        "ok": True,
        "mensaje": "Liquidez mínima suficiente."
    }


def validar_compra_grande(impacto):
    meses_retraso = impacto.get("meses_retraso_objetivo", 0)

    if meses_retraso > 3:
        return {
            "ok": False,
            "mensaje": "La compra retrasa demasiado el objetivo patrimonial."
        }

    return {
        "ok": True,
        "mensaje": "La compra no compromete gravemente el objetivo."
    }
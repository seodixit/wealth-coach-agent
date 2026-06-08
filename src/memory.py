from pathlib import Path


# =============================================================================
# MEMORIA DEL AGENTE
# =============================================================================
# La memoria es la parte que lee y escribe datos persistentes.
# El resto del agente no debería tocar directamente el archivo de datos.

WEALTH_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "wealth_data.txt"


def guardar_datos(patrimonio: float, ahorro_mensual: float, objetivo: float) -> None:
    """MEMORIA: guarda el perfil financiero en data/wealth_data.txt."""
    contenido = (
        "💰 Wealth Coach Agent — Datos guardados\n"
        "========================================\n"
        f"Patrimonio actual (€): {patrimonio:,.2f}\n"
        f"Ahorro mensual (€):    {ahorro_mensual:,.2f}\n"
        f"Objetivo patrimonio (€): {objetivo:,.2f}\n"
    )
    WEALTH_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    WEALTH_DATA_FILE.write_text(contenido, encoding="utf-8")


def leer_datos() -> str | None:
    """MEMORIA: lee el archivo de datos como texto."""
    if not WEALTH_DATA_FILE.exists():
        return None
    return WEALTH_DATA_FILE.read_text(encoding="utf-8")


def _extraer_numero_de_linea(linea: str) -> float:
    valor = linea.split(":", 1)[1].strip().replace("€", "").strip().replace(",", "")
    return float(valor)


def cargar_perfil() -> dict[str, float] | None:
    """MEMORIA: transforma los datos guardados en un perfil numérico."""
    texto = leer_datos()
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


def leer_perfil() -> dict:
    """MEMORIA: perfil fijo usado por la demo agentic actual."""
    return {
        "patrimonio_actual": 100000,
        "objetivo_patrimonial": 150000,
        "ahorro_mensual": 2000,
        "moneda": "EUR",
        "fecha_objetivo": "2027-05",
    }


def leer_gastos_mes() -> dict:
    """MEMORIA: gastos mensuales fijos usados por la demo agentic actual."""
    return {
        "mes": "2026-06",
        "gasto_total": 1850,
        "presupuesto": 1500,
        "desviacion": 350,
        "desviacion_porcentaje": 23.3,
    }

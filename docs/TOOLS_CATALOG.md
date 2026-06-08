# Wealth Agent Tools Catalog

## Objetivo

Definir las tools que el futuro Wealth MCP Server expondrá al LLM.

---

## Tool: leer_perfil

### Tipo
Lectura

### Descripción
Obtiene el perfil financiero base del usuario.

### Input
```json
{}

### Output

{
  "patrimonio_actual": 100000,
  "objetivo_patrimonial": 150000,
  "ahorro_mensual": 2000,
  "moneda": "EUR"
}





Tool: leer_gastos_mes
Tipo

Lectura

Descripción

Obtiene los gastos acumulados del mes.

Input
{
  "mes": "2026-06"
}

Output

{
  "gasto_total": 1850,
  "presupuesto": 1500,
  "desviacion_porcentaje": 23.3
}



Tool: calcular_impacto_financiero
Tipo

Cálculo

Descripción

Calcula el impacto de una compra puntual sobre el objetivo patrimonial.

Input
{
  "importe_compra": 6000
}

Output
{
  "meses_retraso_objetivo": 3,
  "ahorro_mensual_equivalente": 500
}

Reglas de diseño
Las tools devuelven JSON.
Las tools no toman decisiones.
El LLM interpreta.
El MCP Server publica y ejecuta las tools.


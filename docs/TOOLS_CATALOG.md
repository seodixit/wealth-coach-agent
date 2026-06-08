# Tools Catalog

## Objetivo

Definir las tools y funciones de memoria que el futuro Wealth MCP Server podría exponer al LLM.

## Memoria

### leer_perfil

Obtiene el perfil financiero base usado por la demo actual.

```json
{
  "patrimonio_actual": 100000,
  "objetivo_patrimonial": 150000,
  "ahorro_mensual": 2000,
  "moneda": "EUR",
  "fecha_objetivo": "2027-05"
}
```

### leer_gastos_mes

Obtiene los gastos acumulados del mes.

```json
{
  "mes": "2026-06",
  "gasto_total": 1850,
  "presupuesto": 1500,
  "desviacion": 350,
  "desviacion_porcentaje": 23.3
}
```

### guardar_datos / leer_datos / cargar_perfil

Gestionan la memoria persistente en `data/wealth_data.txt`.

## Tools de cálculo

### calcular_impacto_financiero

Calcula el impacto de una compra puntual sobre el objetivo patrimonial.

```json
{
  "importe_compra": 6000,
  "impacto_patrimonio": -6000,
  "meses_retraso_objetivo": 3.0,
  "ahorro_mensual_equivalente": 500.0
}
```

### calcular_tiempo_objetivo

Calcula cuántos meses faltan para llegar al objetivo con el ahorro actual.

### evaluar_progreso

Calcula faltante, porcentaje logrado y mensaje de avance.

### generar_plan_mensual

Calcula el ahorro mensual necesario para un horizonte de referencia.

## Reglas de diseño

- Las tools devuelven datos estructurados.
- Las tools no toman decisiones finales.
- La memoria lee/escribe datos persistentes.
- El razonamiento interpreta y recomienda.
- El futuro MCP Server publicará estas capacidades como tools externas.
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





## Tool: leer_gastos_mes


##Tipo

Lectura

##Descripción

Obtiene los gastos acumulados del mes.

##Input
{
  "mes": "2026-06"
}

##Output

{
  "gasto_total": 1850,
  "presupuesto": 1500,
  "desviacion_porcentaje": 23.3
}



##Tool: calcular_impacto_financiero
##Tipo

##Cálculo

##Descripción

##Calcula el impacto de una compra puntual sobre el objetivo patrimonial.

Input
{
  "importe_compra": 6000
}

Output
{
  "meses_retraso_objetivo": 3,
  "ahorro_mensual_equivalente": 500
}


##Reglas de diseño

## Las tools devuelven JSON.
## Las tools no toman decisiones.
## El LLM interpreta.
## El MCP Server publica y ejecuta las tools.




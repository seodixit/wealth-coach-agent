# MCP Design

## Objetivo

Preparar Wealth Coach Agent para que sus capacidades puedan exponerse en el futuro mediante un MCP Server.

## Arquitectura objetivo

```text
Usuario
  ↓
LLM
  ↓
Wealth MCP Server
  ↓
Tools
  ↓
Datos financieros
  ↓
LLM
  ↓
Recomendación
```

## Mapeo actual

- `src/memory.py`: acceso a datos financieros y memoria persistente.
- `src/tools.py`: cálculos objetivos que podrían publicarse como tools MCP.
- `src/reasoning.py`: reglas actuales, sustituibles por razonamiento LLM.
- `src/main.py`: entrada local para probar el flujo antes de MCP.

## Futuras tools MCP

- `leer_perfil`
- `leer_gastos_mes`
- `calcular_impacto_financiero`
- `calcular_tiempo_objetivo`
- `evaluar_progreso`
- `generar_plan_mensual`

## Regla principal

El MCP Server debe ejecutar tools y devolver datos estructurados. La decisión final y la recomendación deben vivir en el LLM o en la capa de razonamiento.

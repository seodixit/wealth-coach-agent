# LLM Tool Calls

## Objetivo

Documentar cómo un LLM decidiría qué tools usar según la pregunta del usuario.

---

## Caso 1: Comprar un Omega

### Pregunta

¿Puedo comprar un Iphpone este año?

### Razonamiento esperado del LLM

Para responder necesito:

- perfil financiero
- impacto de una compra de 6000 €

### Tool calls

```json
[
  {
    "tool": "leer_perfil",
    "input": {}
  },
  {
    "tool": "calcular_impacto_financiero",
    "input": {
      "importe_compra": 6000
    }
  }
]



Respuesta esperada

El LLM debe interpretar los datos y explicar si la compra retrasa o no el objetivo patrimonial.



Caso 2: Revisión mensual
Pregunta

¿Cómo voy este mes?

Razonamiento esperado del LLM

Para responder necesito:

perfil financiero
gastos del mes
inversiones actuales

Tool calls
[
  {
    "tool": "leer_perfil",
    "input": {}
  },
  {
    "tool": "leer_gastos_mes",
    "input": {
      "mes": "2026-06"
    }
  },
  {
    "tool": "leer_inversiones",
    "input": {}
  }
]

Regla de arquitectura

El LLM decide:

qué necesita saber
qué tools usar
con qué parámetros
cómo interpretar la respuesta

Las tools solo ejecutan y devuelven JSON.


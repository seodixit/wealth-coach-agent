# Wealth Agent Loop

## Objetivo

Simular cómo funcionaría un agente financiero antes de introducir un LLM real.

## Flujo

Usuario
↓
Planificación
↓
Ejecución de tools
↓
Observación de resultados
↓
Razonamiento
↓
Respuesta


## Componentes

### 1. main.py

Punto de entrada. Recibe la pregunta, llama a planificación, ejecuta memoria/tools y muestra la respuesta.

### 2. memory.py

Lee y escribe memoria financiera.

Ejemplos:

- `leer_perfil()`
- `leer_gastos_mes()`
- `guardar_datos()`
- `cargar_perfil()`

### 3. tools.py

Ejecuta cálculos objetivos. No recomienda ni toma decisiones.

Ejemplos:

- `calcular_impacto_financiero()`
- `calcular_tiempo_objetivo()`
- `evaluar_progreso()`
- `generar_plan_mensual()`

### 4. reasoning.py

Contiene planificación, reglas y recomendaciones.

Ejemplos:

- `planificar()`
- `razonar()`
- `razonar_clasificacion()`
- `razonar_recomendaciones()`

## Ejemplo de planificación

`planificar()` decide qué memoria/tools necesita usar el agente según la pregunta.

Ejemplo:

Pregunta:
¿Puedo comprar un Omega?

Plan:
- leer_perfil
- calcular_impacto_financiero

---

### 5. ejecutar_plan()

Ejecuta las acciones definidas en el plan.

---

### 6. razonar()

Interpreta los resultados obtenidos y genera una respuesta.

---

## Diferencia con un agente IA real

En esta versión, la planificación y el razonamiento están basados en reglas.

En una versión con LLM:

- el LLM decidiría qué tools usar
- el LLM interpretaría los resultados
- el LLM generaría una respuesta más flexible

## Arquitectura futura

Usuario
↓
LLM
↓
MCP Server
↓
Tools
↓
JSON
↓
LLM
↓
Recomendación
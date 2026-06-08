# Wealth Coach Agent - Architecture

## Objetivo

El objetivo del Wealth Coach Agent es ayudar al usuario a analizar su situación financiera y generar recomendaciones para alcanzar sus objetivos patrimoniales.

---

# Arquitectura actual

## main.py

Punto de entrada del sistema.

Responsabilidades:

* Recibir la pregunta del usuario.
* Coordinar el flujo de ejecución.
* Invocar memoria, tools y razonamiento.
* Mostrar la respuesta final.

---

## memory.py

Gestiona la memoria del agente.

Responsabilidades:

* Leer datos financieros.
* Guardar datos financieros.
* Mantener el estado del usuario.

Ejemplos:

* patrimonio actual
* gastos
* inversiones
* objetivos

---

## tools.py

Contiene herramientas objetivas.

Responsabilidades:

* Realizar cálculos.
* Transformar datos.
* Generar métricas.

Ejemplos:

* calcular_impacto_financiero()
* calcular_ahorro_necesario()
* calcular_progreso_objetivo()

Las tools no toman decisiones.

---

## reasoning.py

Contiene la lógica de análisis.

Responsabilidades:

* Interpretar los datos.
* Detectar riesgos.
* Generar recomendaciones.

Ejemplos:

* clasificar_estado_financiero()
* generar_recomendaciones()

En una versión futura, parte de este módulo será reemplazada o complementada por un LLM.

---

# Flujo actual

Usuario
↓
main.py
↓
memory.py
↓
tools.py
↓
reasoning.py
↓
Respuesta

---

# Evolución futura

## Fase actual

Agente basado en reglas.

Usuario
↓
main.py
↓
memory.py + tools.py
↓
reasoning.py
↓
Respuesta

---

## Fase futura

Agente basado en LLM.

Usuario
↓
LLM
↓
Tools
↓
Datos
↓
LLM
↓
Respuesta

---

# Posibles Tools MCP

* leer_perfil()
* leer_patrimonio()
* leer_gastos_mes()
* leer_inversiones()
* calcular_impacto_financiero()
* generar_snapshot_mensual()

Todas las tools deberán devolver JSON estructurado.

---

# Principio de diseño

Las tools calculan.

La memoria almacena.

El LLM razona.

El MCP conecta.

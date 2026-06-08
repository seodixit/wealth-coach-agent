# Wealth Coach Agent

Proyecto personal para aprender Agentic AI, Python, GitHub, MCP y agentes de IA.

## Objetivo

Construir un asistente financiero capaz de:

- Leer y guardar memoria financiera del usuario.
- Ejecutar tools con cálculos objetivos.
- Razonar con reglas y generar recomendaciones.
- Evolucionar hacia una arquitectura con LLM y MCP.

## Arquitectura actual

```text
src/
  main.py       -> punto de entrada y orquestación
  memory.py     -> lectura/escritura de data/wealth_data.txt
  tools.py      -> cálculos objetivos sin decisiones
  reasoning.py  -> reglas, planificación y recomendaciones

data/
  wealth_data.txt
```

## Cómo ejecutar

Demo agentic actual:

```bash
python src/main.py
```

Modo interactivo:

```bash
python src/main.py --menu
```

## Principio de diseño

- Memoria: persiste y recupera datos.
- Tools: calculan hechos y devuelven JSON/dicts.
- Razonamiento: interpreta resultados y decide recomendaciones.
- Main: conecta las piezas y muestra la respuesta al usuario.

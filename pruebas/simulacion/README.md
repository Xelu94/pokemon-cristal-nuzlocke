# Herramientas de playtest automatizado

Scripts usados para el informe [INFORME-PLAYTEST-v4.3](../../docs/INFORME-PLAYTEST-v4.3.md). Ejecutan la ROM real con PyBoy y leen sus datos; no reimplementan las reglas del juego. **No sustituyen jugar una campaña.**

## Configuración

Las rutas se resuelven en `rutas.py` mediante variables de entorno:

| Variable | Significado | Por defecto |
|---|---|---|
| `CRISTAL_SOURCE` | Árbol de la fuente integrada y **compilada** (`pokecristal.gbc`, `.sym`) | `../source` |
| `CRISTAL_OUT` | Carpeta de informes y capturas | `..` |
| `CRISTAL_V42` | Árbol compilado de la v4.2, solo para `migracion_guardado.py` | `../source-v42` |

Ejecuta los scripts **sin** la opción `-I` de Python (necesitan encontrar `rutas.py` junto a ellos). Dependencias: `pyboy==2.8.1` y `Pillow` (`../requirements.txt`).

## Scripts

| Script | Qué hace |
|---|---|
| `audit_trainers.py`, `audit_evoluciones.py`, `audit_texto.py` | Auditorías estáticas: equipos de entrenadores, evoluciones y legendarios, líneas de diálogo de más de 18 caracteres |
| `simlib.py` | Biblioteca: construye equipos con las rutinas del juego (`TryAddMonToParty`), inicia combates contra cualquier entrenador y los juega con un bot que puntúa movimientos |
| `campaign_sim.py` | Simulación de 63 equipos de jefes/rivales/Ulex/Tito con equipos aleatorios y «fuertes» (`python campaign_sim.py <pruebas> <procesos> <salida.json>`) |
| `early_sim.py` | Primeros líderes con equipos de 2, 3 y 4 Pokémon |
| `analyze_campaign.py` | Resume los resultados en una tabla |
| `smoke_maps.py`, `smoke_run.py`, `smoke_one.py` | Carga los 388 mapas del catálogo del sandbox y camina al azar unos pasos en cada uno |
| `migracion_guardado.py` | Guarda una partida con la ROM v4.2 y la carga con la v4.3 |
| `harness.py` | Montaje común para arrancar la ROM saltando la introducción |

## Limitaciones del bot

Puntúa cada movimiento por potencia × STAB × efectividad × precisión y juega siempre con el Pokémon activo hasta que cae. **No cambia de Pokémon por voluntad propia ni usa objetos.** Los equipos se eligen al azar entre las especies que un jugador tendría a ese nivel (evolucionadas si ya podían evolucionar). Por eso las cifras de victoria son una medida relativa de dureza, no una predicción del éxito de una persona.

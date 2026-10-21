# Pokémon Cristal Nuzlocke — Tito Xeluis

Modificación personal de **Pokémon Cristal** para Game Boy Color con un Nuzlocke integrado en el motor, combate modernizado, aleatorización por niveles y personajes propios. Versión **4.2**.

> *English summary:* a personal ROM hack of Pokémon Crystal (Game Boy Color, SM83 assembly) built on the Spanish source tree of [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal) and the [pret/pokecrystal](https://github.com/pret/pokecrystal) disassembly. It adds built-in Nuzlocke rules, per-move physical/special split, a Fairy type, level caps, a custom NPC (Tito Xeluis), a roaming thief (Ulex), a sandbox build for testing and an offline seed-based randomizer. It is **not** a game written from scratch and **not** an official Pokémon product. Spanish only. Download the single `.gbc` from [Releases](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases/tag/v4.2) and open it in a Game Boy Color emulator.

![Selección de ataques con potencia, tipo, categoría y PP](capturas/combate-panel.png)

## Descarga y cómo jugar

**[⬇ Descargar Pokemon Cristal Nuzlocke.gbc (v4.2)](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases/download/v4.2/Pokemon.Cristal.Nuzlocke.gbc)** — enlace directo al asset de la [Release v4.2](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases/tag/v4.2). GitHub sustituye los espacios del nombre por puntos en la URL; el archivo es el mismo.

| | |
|---|---|
| Archivo | `Pokemon Cristal Nuzlocke.gbc` (2 MiB) |
| Versión | 4.2 |
| SHA-256 | `fc8fd409da5c20f5e7e17f1b0aef34d970f3a61e0fdeb518a41011c966d337f4` |

1. Descarga el único archivo `.gbc` de la Release. No hay ZIP, parches ni instalador: no necesitas una ROM base ni aplicar nada.
2. Ábrelo con un emulador compatible con Game Boy Color (por ejemplo mGBA). El emulador se obtiene por separado y no forma parte de este proyecto.
3. Guarda dentro del juego. Las actualizaciones de esta familia continúan el guardado interno (`.sav`); no uses estados rápidos de otra compilación. Detalles en [compatibilidad de guardados](docs/COMPATIBILIDAD-GUARDADOS.md).

El modo de velocidad ×2 depende de las opciones del emulador de cada jugador; no es una aceleración añadida al motor.

Comprueba la descarga (PowerShell): `Get-FileHash "Pokemon Cristal Nuzlocke.gbc" -Algorithm SHA256`.

## Qué aporta al jugador

- **Nuzlocke dentro del juego.** Muerte permanente (también por veneno fuera de combate), una captura ordinaria por zona con nombre, excepciones para regalos, huevos, iniciales, intercambios y eventos. Sin supervivientes, termina la partida.
- **Combate modernizado.** Categoría física/especial/estado por movimiento, tipo Hada con resistencias actualizadas y 12 movimientos nuevos. Potencia, tipo, categoría y PP aparecen en un subpanel del menú de combate.
- **Límites de nivel progresivos** ligados a los líderes de Johto y Kanto, que también frenan la experiencia, los caramelos raros y la guardería.
- **Aleatorización por restricciones**: iniciales, salvajes, entrenadores, regalos, huevos y eventos, con topes por nivel, línea evolutiva y potencia. Sin legendarios antes del nivel 55.
- **Experiencia repartida**: participantes vivos, mitad para reservas vivas y experiencia por captura.
- **Mochila y objetos**: bolsillos MEDICINA, BAYAS, COMBATE y OTROS; MO como herramientas; objetos equipados útiles; evoluciones por intercambio o amistad sustituidas por nivel o piedra.
- **Tito Xeluis** en 22 Centros Pokémon: intercambios, recordador de movimientos, guía de evoluciones y un jefe extra tras vencer a Rojo.
- **Ulex el Ladrón**: 16 encuentros disfrazados en rutas de Johto y Kanto.
- **Sandbox** (compilación aparte, no se distribuye como descarga): viajes, medallas, equipo y objetos para probar.

![Cuatro orientaciones del sprite de Tito](capturas/tito-direcciones.png)

Reglas completas: [docs/MECANICAS.md](docs/MECANICAS.md).

## Retos de ingeniería

El proyecto evoluciona una base existente de ensamblador SM83 con límites estrictos de memoria e identificadores.

- **Movimientos sin ampliar la tabla.** Los 254 identificadores de movimiento ya estaban usados; nueve movimientos modernos sustituyen a otros en el mismo ID para no romper guardados ([tabla](docs/MOVIMIENTOS-SUSTITUIDOS.md)).
- **Nuevo reparto de experiencia, capturas y topes** integrados en las rutas de combate, caramelos y guardería, con una única rutina de límite (`GetCurrentLevelCap`).
- **Compatibilidad de guardados.** El inventario se amplía de 20 a 50 montones y el PC se reduce de 50 a 20 conservando los 70 espacios combinados, con migración automática de guardados anteriores.
- **Gráficos en VRAM.** El sprite de Tito se define en una cuadrícula nativa de 16×16 y se compila a una hoja de 16×96 en 2bpp con tres colores visibles más transparencia. Ulex necesitó reservar un espacio gráfico para su sprite variable en las tablas de mapas exteriores.
- **Llamadas entre bancos.** Un fallo del sandbox venía de llamar directamente a una rutina de otro banco de ROM ([explicación](docs/ARQUITECTURA.md)).
- **Randomizador sin conexión** en HTML/CSS/JavaScript sin framework: semilla repetible, manifiesto de posiciones mutables y firma de la parte inmutable de la ROM. Genera la ROM en el navegador sin enviar datos a ningún servidor ([documentación](docs/RANDOMIZADOR.md)).
- **Pruebas que ejecutan la ROM** con PyBoy (rutinas reales y recorridos de interfaz con montajes controlados) y Playwright (randomizador en navegador sin solicitudes de red) ([pruebas](docs/COMPILACION-Y-PRUEBAS.md)).

![Randomizador sin conexión](capturas/randomizador.png)

## Tecnología

Ensamblador LR35902/SM83 · RGBDS 1.0.0 (rgbasm, rgblink, rgbfix, rgbgfx) · Make y utilidades C/GCC · Python y Pillow (recursos, manifiestos, hashes) · PyBoy 2.8.1 (pruebas) · HTML, CSS y JavaScript sin framework · Node.js · Playwright · parches BPS y verificación de reconstrucción byte a byte (SHA-256 de las compilaciones; SHA-1 de la ROM de referencia).

No es una aplicación React, Electron, Unity ni Godot, y no usa servidor, base de datos ni cuentas.

## Estado y validación

La versión 4.2 pasó **124 comprobaciones agrupadas** sobre los componentes afectados (servicios y mapas de Tito 48, orientaciones renderizadas 4, rutas de Ulex y Objetos 17, combates de Ulex y menú sandbox 27, cálculos de combate y almacenamiento 11, interfaz real de combate y captura 4, núcleo del randomizador 9, navegador sin conexión 4). Es un recuento de comprobaciones, **no un porcentaje de cobertura**; algunas agrupan muchos casos (Poder Oculto se contrasta con 768 combinaciones de DVs). Las 306 comprobaciones de informes anteriores pertenecen a otra versión.

Límites reales: los montajes omiten la introducción; algunos combates aumentan el daño para recorrer los equipos; en Ruta 17 se desactiva la gravedad solo en la prueba. No se ha completado una campaña entera ni queda demostrado el equilibrio global. El fallo móvil original de Viento Hielo no se reprodujo con el mismo emulador y guardado del usuario. No hay integración continua en este repositorio todavía. Informe: [evidencias/Validacion-v4.2.json](evidencias/Validacion-v4.2.json).

No implementado: habilidades, megaevolución, generaciones tercera/cuarta, recursos de Prism.

## Contenido del repositorio

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs) | Mecánicas, arquitectura, compilación y pruebas, compatibilidad, movimientos, niveles, sandbox, randomizador, recursos |
| [`parches/`](parches) | `Cambios-fuente.patch`: modificaciones del código fuente sobre la base española |
| [`recursos/`](recursos) | Sprites y paleta de Tito Xeluis |
| [`herramientas/`](herramientas) | Randomizador portable y sus fuentes, generador del sprite |
| [`pruebas/`](pruebas) | Scripts de validación portables |
| [`evidencias/`](evidencias) | Informes JSON de las pruebas de 4.2 |
| [`capturas/`](capturas) | Capturas reales |
| [`publicacion/`](publicacion) | Textos de la Release, descripción y resumen para portfolio |

Cambios por versión: [CHANGELOG.md](CHANGELOG.md). Procedencia: [CREDITOS.md](CREDITOS.md). Licencia: [LICENCIA.md](LICENCIA.md).

## Créditos

Basado en la traducción al español de [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal), que a su vez adapta el trabajo inicial de [erosunica](https://github.com/erosunica/), y en el desensamblado de [pret/pokecrystal](https://github.com/pret/pokecrystal). Pokémon y sus personajes pertenecen a sus titulares; este proyecto fan no es oficial ni está afiliado a ellos. Las modificaciones, herramientas y recursos propios (Tito Xeluis, Ulex, reglas, randomizador, pruebas) son de Tito Xeluis; la marca «©2026 Tito Xeluis inc.» identifica el proyecto, no la base. Detalle en [CREDITOS.md](CREDITOS.md).

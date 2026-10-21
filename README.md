# Pokémon Cristal Nuzlocke — Tito Xeluis

Modificación personal de **Pokémon Cristal** para Game Boy Color con un Nuzlocke integrado en el motor, combate modernizado, aleatorización por niveles y personajes propios. Versión **4.3**. Autor: **Tito Xeluis** (apodo de YouTube; [@Xelu94](https://github.com/Xelu94) en GitHub). El NPC Tito Xeluis del juego lleva el nombre del autor.

> *English summary:* a personal ROM hack of Pokémon Crystal (Game Boy Color, SM83 assembly) built on the Spanish source tree of [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal) and the [pret/pokecrystal](https://github.com/pret/pokecrystal) disassembly. It adds built-in Nuzlocke rules, per-move physical/special split, a Fairy type, level caps, a custom NPC (Tito Xeluis), a roaming thief (Ulex), a sandbox build for testing and an offline seed-based randomizer. It is **not** a game written from scratch and **not** an official Pokémon product. Spanish only. Download the single `.gbc` from [Releases](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases) and open it in a Game Boy Color emulator.

![Selección de ataques con potencia, tipo, categoría y PP](capturas/combate-panel.png)

## Descarga y cómo jugar

**ROM normal v4.3:** `Pokemon Cristal Nuzlocke.gbc`. El enlace directo se añade cuando se publica la Release v4.3 (consulta [Releases](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases)).

Versión anterior publicada: [v4.2](https://github.com/Xelu94/pokemon-cristal-nuzlocke/releases/tag/v4.2).

| | |
|---|---|
| Archivo | `Pokemon Cristal Nuzlocke.gbc` (2 MiB) |
| Versión | 4.3 |
| SHA-256 | `a6a232589e9ff8859bc9307c3593707c753dcaf8b6be65a8ba835faafe949b1e` |
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
- **Mochila y objetos**: el tipo de objeto (MEDICINA, BAYAS, COMBATE, OTROS) se lee en el recuadro negro de la bolsa y los bolsillos forman un círculo; 99 caramelos raros infinitos; MO como herramientas (Vuelo también desde el menú del Pokémon); objetos equipados útiles; evoluciones por intercambio o amistad sustituidas por nivel o piedra.
- **Sin curas en las tiendas.** Ninguna tienda vende pociones, revivir ni curas de estado; en la LIGA, el oficial de la CALLE VICTORIA entrega una vez 8 MÁX. POCIÓN, 10 HÍPER POCIÓN y 7 RESTAU. TODO.
- **Tito Xeluis** en 22 Centros Pokémon: intercambios, recordador de movimientos, guía de evoluciones y un jefe extra tras vencer a Rojo.
- **Ulex el Ladrón**: 16 encuentros disfrazados en rutas de Johto y Kanto.
- **Sandbox** (compilación aparte, no se distribuye como descarga): viajes, medallas, equipo y objetos para probar.

![Bolsa con el tipo de objeto en el recuadro negro](capturas/bolsa-medicina.png) ![Menú del Pokémon con VUELO](capturas/menu-vuelo.png)
![Reglas Nuzlocke explicadas por Tito](capturas/tito-reglas.png) ![El anciano entrega el mapa](capturas/anciano-mapa.png)

![Cuatro orientaciones del sprite de Tito](capturas/tito-direcciones.png)

Reglas completas: [docs/MECANICAS.md](docs/MECANICAS.md).

## Retos de ingeniería

El proyecto evoluciona una base existente de ensamblador SM83 con límites estrictos de memoria e identificadores.

- **Movimientos sin ampliar la tabla.** Los 254 identificadores de movimiento ya estaban usados; nueve movimientos modernos sustituyen a otros en el mismo ID para no romper guardados ([tabla](docs/MOVIMIENTOS-SUSTITUIDOS.md)).
- **Nuevo reparto de experiencia, capturas y topes** integrados en las rutas de combate, caramelos y guardería, con una única rutina de límite (`GetCurrentLevelCap`).
- **Compatibilidad de guardados.** El inventario se amplía de 20 a 50 montones y el PC se reduce de 50 a 20 conservando los 70 espacios combinados, con migración automática de guardados anteriores.
- **Límites de memoria.** El banco 4 de la ROM está casi lleno y la WRAM sin hueco: los rótulos de la bolsa viven en una sección propia y el nivel blando del primer Ulex reutiliza un bit existente en vez de reservar una variable ([detalle](docs/ARQUITECTURA.md)).
- **Gráficos en VRAM.** El sprite de Tito se define en una cuadrícula nativa de 16×16 y se compila a una hoja de 16×96 en 2bpp con tres colores visibles más transparencia. Ulex necesitó reservar un espacio gráfico para su sprite variable en las tablas de mapas exteriores.
- **Llamadas entre bancos.** Un fallo del sandbox venía de llamar directamente a una rutina de otro banco de ROM ([explicación](docs/ARQUITECTURA.md)).
- **Randomizador sin conexión** en HTML/CSS/JavaScript sin framework: semilla repetible, manifiesto de posiciones mutables y firma de la parte inmutable de la ROM. Genera la ROM en el navegador sin enviar datos a ningún servidor ([documentación](docs/RANDOMIZADOR.md)).
- **Pruebas que ejecutan la ROM** con PyBoy (rutinas reales y recorridos de interfaz con montajes controlados) y Playwright (randomizador en navegador sin solicitudes de red) ([pruebas](docs/COMPILACION-Y-PRUEBAS.md)).

![Randomizador sin conexión](capturas/randomizador.png)

## Tecnología

Ensamblador LR35902/SM83 · RGBDS 1.0.0 (rgbasm, rgblink, rgbfix, rgbgfx) · Make y utilidades C/GCC · Python y Pillow (recursos, manifiestos, hashes) · PyBoy 2.8.1 (pruebas) · HTML, CSS y JavaScript sin framework · Node.js · Playwright · parche de fuente (git diff) y reconstrucción verificada byte a byte (SHA-256 de las compilaciones; parches BPS solo en versiones anteriores, con SHA-1 de la ROM de referencia).

No es una aplicación React, Electron, Unity ni Godot, y no usa servidor, base de datos ni cuentas.

## Estado y validación

La versión 4.3 pasó **137 comprobaciones agrupadas**: 124 de los componentes ya existentes (servicios y mapas de Tito 48, orientaciones renderizadas 4, rutas de Ulex y Objetos 17, combates de Ulex y menú sandbox 27, cálculos de combate y almacenamiento 11, interfaz real de combate y captura 4, núcleo del randomizador 9, navegador sin conexión 4) y 13 nuevas de esta versión (Vuelo, anciano del mapa, tiendas, suministros de la Liga, caramelos y bolsa). Es un recuento de comprobaciones, **no un porcentaje de cobertura**; algunas agrupan muchos casos (Poder Oculto se contrasta con 768 combinaciones de DVs). Las comprobaciones de informes de versiones anteriores no se suman.

La reconstrucción también está comprobada: aplicar el parche a la base española y compilar con RGBDS 1.0.0 produce exactamente los SHA-256 de la ROM normal y de la compilación sandbox de los informes.

Límites reales: los montajes omiten la introducción; algunos combates aumentan el daño para recorrer los equipos; en Ruta 17 se desactiva la gravedad solo en la prueba. No se ha completado una campaña entera ni queda demostrado el equilibrio global. El fallo móvil original de Viento Hielo no se reprodujo con el mismo emulador y guardado del usuario. No hay integración continua en este repositorio todavía. Informe: [evidencias/Validacion-v4.3.json](evidencias/Validacion-v4.3.json).
No implementado: habilidades, megaevolución, generaciones tercera/cuarta, recursos de Prism.

## Contenido del repositorio

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs) | Mecánicas, arquitectura, compilación y pruebas, compatibilidad, movimientos, niveles, sandbox, randomizador, recursos |
| [`parches/`](parches) | `Cambios-fuente.patch`: modificaciones del código fuente sobre la base española |
| [`recursos/`](recursos) | Sprites y paleta de Tito Xeluis |
| [`herramientas/`](herramientas) | Randomizador portable y sus fuentes, generador del sprite |
| [`pruebas/`](pruebas) | Scripts de validación portables |
| [`evidencias/`](evidencias) | Informes JSON de las pruebas de 4.3 |
| [`capturas/`](capturas) | Capturas reales |
| [`publicacion/`](publicacion) | Textos de la Release, descripción y resumen para portfolio |

Cambios por versión: [CHANGELOG.md](CHANGELOG.md). Procedencia: [CREDITOS.md](CREDITOS.md). Licencias (MIT para el código propio, CC BY-NC 4.0 para documentación y arte de Tito; sin licencia propia para parche y ROM): [LICENCIA.md](LICENCIA.md).

## Créditos

Basado en la traducción al español de [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal), que a su vez adapta el trabajo inicial de [erosunica](https://github.com/erosunica/), y en el desensamblado de [pret/pokecrystal](https://github.com/pret/pokecrystal). Pokémon y sus personajes pertenecen a sus titulares; este proyecto fan no es oficial ni está afiliado a ellos. Las modificaciones, herramientas y recursos propios (Tito Xeluis, Ulex, reglas, randomizador, pruebas) son de Tito Xeluis, apodo del autor; la marca «©2026 Tito Xeluis inc.» identifica el proyecto, no la base. Detalle en [CREDITOS.md](CREDITOS.md).

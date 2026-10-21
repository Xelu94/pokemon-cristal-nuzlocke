# Informe de playtest automatizado de la v4.3

Fecha: 22 de octubre de 2026. ROM probada: la compilación 4.3 con dos correcciones de texto posteriores (ver «Fallos encontrados»).

## Qué se ha hecho y qué no

**No se ha jugado la campaña de principio a fin como lo haría una persona**: no hay forma fiable de recorrer a mano o con un script los miles de mapas, diálogos y decisiones. Lo que sí se ha hecho es automatizar con la ROM real (PyBoy) las partes que se pueden medir:

| Qué | Cómo | Resultado |
|---|---|---|
| Auditoría estática de datos | Equipos de 561 entrenadores y 1346 Pokémon, evoluciones, legendarios, nombres, diálogos | Sin legendarios por debajo del nivel 55 en entrenadores; sin evoluciones por intercambio o amistad restantes; 2 líneas de diálogo desbordadas (corregidas) |
| Combates de jefes | 63 equipos (líderes, Alto Mando, campeón, Azul, Rojo, Tito, 19 equipos de Ulex y 21 combates rivales) × 30 equipos aleatorios y 30 «fuertes» al nivel del tope = **3780 combates reales** | Ninguno colgó ni falló; 3716 terminaron, 64 se cortaron por límite de pasos (la mayoría combates de 40+ turnos) |
| Primeros líderes con equipos pequeños | 6 líderes de Johto × equipos de 2, 3 y 4 Pokémon × 30 + 30 = 1080 combates | Ver «Equilibrio» |
| Carga de mapas | Los 388 mapas del catálogo del sandbox: carga y 24 pasos al azar en cada uno | Todos cargan; 2 mapas no responden si se entra en ellos directamente sin su contexto (ver abajo) |
| Compatibilidad de guardados | Partida guardada con la ROM v4.2 por el menú GUARDAR y cargada con la v4.3 | Mochila, equipo, mapa y posición idénticos |
| Regresión | Las 137 comprobaciones del proyecto sobre la ROM final | 137/137 |
| Interfaz | Mochila fuera y dentro del combate: rótulos y círculo de bolsillos | Correcta |

**No se ha probado**: una campaña humana completa, la captura de salvajes y las reglas de una captura por zona fuera de las pruebas existentes, la experiencia y el tope en partidas largas, las tiendas con su interfaz, las máquinas expendedoras en pantalla, todos los diálogos (solo las líneas nuevas o modificadas se auditaron por anchura), el sonido ni el rendimiento.

Las herramientas y los resultados están en [`pruebas/simulacion/`](../pruebas/simulacion) y [`evidencias/playtest-v4.3/`](../evidencias/playtest-v4.3).

## Fallos encontrados y cómo se resolvieron

### Del juego

1. **Diálogo del juego desbordado por un carácter** (mío, de la 4.3). El texto de la profesora de Ciudad Cerezo decía «para tu #GEAR al» (19 caracteres con «#» expandido a «POKé»; la caja admite 18). Se reescribió como «para tu #GEAR, / al entrar en la / ciudad.».
2. **Diálogo desbordado del santuario del Encinar** (anterior a la 4.3). «comienza a brillar.» ocupa 19 caracteres. Se dividió en dos líneas.
3. El resto de líneas de más de 18 caracteres que detectó la auditoría pertenece al texto original de la base española (Radio Torre Rocket) y no se tocó.

Ambas correcciones están en [`parches/correcciones-v4.3.1.patch`](../parches/correcciones-v4.3.1.patch), que aplica limpiamente sobre la fuente 4.3. Con ellas se recompiló, se regeneró el manifiesto del randomizador y pasan las 137 comprobaciones. **No están publicadas**: cambiarían el hash de la ROM de la Release v4.3.

| Compilación 4.3 con las correcciones (no publicada) | SHA-256 |
|---|---|
| ROM normal | `78b5a6a5e3cff44cc5944f02eb54f1b1bd32316d88f402438c3dbbcf11c890b7` |
| Sandbox | `5f0cb2818219ec98a11e89d44680b37c5cd23a47ea3f28785f8d53730719f82b` |

### Dudas sin resolver

- **POKECENTER_2F y CELADON_DEPT_STORE_ELEVATOR no responden** al aparecer en ellos directamente desde el sandbox. Son mapas que dependen de contexto (enlace y estado del ascensor) y no se alcanzan así en una partida normal; no se ha comprobado si la base original se comporta igual.
- **64 combates de jefes (1,7 %) no terminaron** en el límite de pasos. Los que se inspeccionaron eran combates largos contra rivales con movimientos de recuperación o sin movimientos de daño útiles para el bot, no cuelgues del motor.

### De mis propias herramientas (no del juego)

Durante el trabajo aparecieron tres fallos del simulador, resueltos antes de las cifras finales: restaurar el estado del juego en medio de una interrupción dejaba las interrupciones desactivadas; el bot escribía el cursor de movimientos cuando el juego ya lo había leído (jugaba con un movimiento rezagado); y no reaccionaba a «movimiento desactivado» o «sin PP» y se quedaba repitiéndolo. Las primeras cifras (con el cursor rezagado) eran algo más pesimistas; las de este informe son las corregidas.

## Equilibrio

Qué mide: el equipo del jugador son 6 Pokémon al nivel del tope, elegidos al azar entre las especies que se tendrían a ese nivel («aleatorio») o entre el tercio de mayor suma de estadísticas base («fuerte»). El bot elige el movimiento con más daño esperado y **no cambia de Pokémon ni usa objetos**. Es una medida **relativa** de dureza; una persona con objetos, cambios y experiencia rendirá bastante mejor.

Victorias, equipo fuerte (equipo aleatorio entre paréntesis), con 30 pruebas por celda:

| Tope | Jefe | Victorias | | Tope | Jefe | Victorias |
|---|---|---|---|---|---|---|
| 19 | Pegaso | 100 % (96) | | 65 | Karen | **66 % (36)** |
| 24 | Antón | 100 % (100) | | 65 | Lance | **60 % (43)** |
| 29 | Blanca | 100 % (96) | | 67 | Surge | 70 % (56) |
| 35 | Morti | 96 % (93) | | 70 | Sabrina | 96 % (90) |
| 40 | Aníbal | 100 % (96) | | 73 | Erika | 96 % (66) |
| 44 | Yasmina | 100 % (90) | | 75 | Sachiko | 66 % (50) |
| 48 | Fredo | 100 % (86) | | 77 | Misty | 100 % (90) |
| 53 | Débora | 93 % (86) | | 80 | Brock | 90 % (73) |
| 65 | Mento (Will) | 100 % (86) | | 83 | Blaine | 100 % (86) |
| 65 | Koga | 100 % (83) | | 85 | **Azul** | **40 % (26)** |
| 65 | Bruno | 96 % (73) | | 95 | **Rojo** | **16 % (13)** |
| | | | | 100 | **Tito** | **26 % (0)** |

Resultado global: 87,7 % con equipos fuertes y 72,0 % con equipos aleatorios.

Lecturas:

1. **Johto es fácil para un equipo completo y difícil para uno corto.** Con 6 Pokémon los líderes caen casi siempre, pero con equipos de 3: Pegaso 87 % (70), Blanca 63 % (67), Morti 57 % (40), Aníbal 80 % (53) y Yasmina 67 % (47) con equipo fuerte (aleatorio). Con 2 Pokémon, el mismo tramo va del 27 al 90 % con equipo fuerte (17–47 % con aleatorio). En un Nuzlocke con una captura por zona, es plausible llegar a Morti con 3–4 Pokémon útiles (dato no medido en una partida real), así que la dureza efectiva puede estar en esa franja.
2. **Hay tres puertas claras al final:** Azul, Rojo y Tito. Sin objetos ni cambios son muy duros, y la curva es creciente después de Surge, salvo los líderes de tres Pokémon (Sabrina, Blaine), que son blandos.
3. **Ulex es más duro que el líder del mismo tope**, y se paga con el robo de un Pokémon: Ulex 4 (tope 35) 96 % (66) frente a Morti 96 % (93); Ulex 5, 93 % (56) frente a Aníbal 100 % (96); y los equipos 10 a 12 (topes 67 a 73) están en 60–73 % (26–43) frente a Surge 70 % (56) y Erika 96 % (66). Es coherente con la intención del diseño («shiny al límite») pero es el desvío más claro respecto a los líderes.
4. **El Alto Mando es más blando que el primer tramo de Kanto**, salvo Karen y Lance. Mento, Koga y Bruno caen casi siempre mientras Surge (70 %) y Sachiko (66 %) ya son más difíciles. Es la parte de la curva que cuesta justificar.
5. **Los rivales entre los topes 44 y 53** (nivel máximo 42–50) son más duros que sus líderes: 70–90 % (46–70) con equipos de 6.

Ajustes posibles, solo con datos (a decidir por el autor; no se han aplicado): bajar 1–2 niveles los equipos 4–5 y 10–13 de Ulex o limitarlos a cuatro Pokémon; subir ligeramente al Alto Mando; valorar bajar Rojo (95) o Tito (100) un par de niveles si se quiere que sean ganables sin objetos de combate.

## Propuestas de mejora viables

Basadas en lo que se ha visto del motor: tabla de 13 estructuras de objeto y 16 objetos por mapa, lista de 32 gráficos de sprite, 40 entradas de OAM con 10 por línea, 8 paletas de fondo y 8 de objetos (8 de ellas de PNJ), 105 sprites de mapa de 16×16 en 2bpp y 3 bloques de 128 tiles de VRAM por banco. El banco 4 de la ROM está casi lleno y la WRAM sin hueco.

**Interfaz, bajo coste y seguras**

1. **Mostrar el tope de nivel actual** en la pantalla de estado y en el menú de Tito. Solo requiere texto y una llamada a `GetCurrentLevelCap`.
2. **Iconos físico, especial y estado** en el subpanel de movimientos en lugar de texto. Necesitan dos tiles por icono; conviene antes volcar el uso de VRAM en combate para confirmar que hay hueco.
3. **Extender los rótulos de la bolsa**: la técnica de la 4.3 (rótulos de cinco tiles en una sección propia) permite rotular también MT/MO, Balls y Objetos clave en español sin tocar el arte original. Quedan 5 tiles libres en esa pantalla.
4. **Marcador de tope en la barra de experiencia**, cambiando el tile del extremo cuando el Pokémon ya no gana experiencia (por verificar la distribución de tiles de la barra).

**Gráficos, coste medio**

5. **Animación de reposo de Tito**: la hoja ya tiene tres fotogramas alternos completos, que sirven para un parpadeo o un balanceo sin gastar VRAM.
6. **Más disfraces de Ulex**: el límite son los espacios de gráficos de los mapas exteriores. Las rutas con menos NPC pueden reutilizar espacios, como se hizo con la Ruta 31.
7. **Paletas propias por especie «campeona»** (Tito, Rojo) en el combate, aprovechando las 8 paletas de objeto, para que el equipo final se distinga de un vistazo.

**Fuera de la consola, alto valor**

8. **Randomizador con vista previa** de los iniciales y de los Pokémon de gimnasios (el HTML es local y puede incluir los sprites sin tocar la ROM).
9. **Integración continua** que compile desde el parche y ejecute las 137 comprobaciones, con un `.github/workflows` real; hoy solo hay ejecuciones locales.
10. **Bot con cambios de Pokémon y uso de Full Restore** para que las cifras de equilibrio se parezcan más a una partida real, y un recorrido de «Nuzlocke» con capturas por zona.

Lo que **no** es viable con este motor sin una reescritura grande: sprites de más de 16×16 en el mapa, más de 8 paletas de objeto simultáneas, ampliar la tabla de movimientos más allá de 254 identificadores o añadir habilidades (la estructura de Pokémon no tiene sitio libre garantizado).

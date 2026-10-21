# Sandbox de pruebas y diferencias con la ROM normal

El sandbox es una **compilación separada** (`pokecristal_debug` en el Makefile) para probar mecánicas sin jugar toda la aventura. No se distribuye como descarga del juego: se compila desde la fuente. Tiene su propio nombre y guardado, de modo que no mezcla la partida de la ROM normal.

| | ROM normal | Sandbox |
|---|---|---|
| Archivo de compilación | `pokecristal.gbc` (publicada como `Pokemon Cristal Nuzlocke.gbc`) | `pokecristal_debug.gbc` |
| Descarga pública | Sí (único asset de la Release) | No |
| Menú Start → SANDBOX | No | Sí |
| Guardado | El de la aventura | Distinto, para no mezclarlo |
| SHA-256 de 4.2 | `fc8fd409da5c20f5e7e17f1b0aef34d970f3a61e0fdeb518a41011c966d337f4` | `698d216e4520fcedbba0c367d146057d4c850db2202052f6da99c50acbf799d5` |

El hash del sandbox figura en `evidencias/Validacion-v4.2.json` y corresponde a la compilación probada; no se adjunta ninguna ROM sandbox.

## Menú SANDBOX

Start → SANDBOX abre las herramientas en cualquier mapa donde se pueda usar el menú.

- **VIAJAR**: 41 accesos rápidos (centros, eventos, Rojo y los 16 disfraces de Ulex) y la opción TODOS LOS MAPAS, un catálogo de 388 mapas en 26 grupos con coordenadas transitables verificadas. El recorrido visual completo se muestreó en destinos representativos; no se ha jugado visualmente cada mapa entero.
- **SUBIR MEDALLAS**: selector de 0 a 16 medallas de una vez, con recálculo del límite de nivel.
- **LIGA/ROJO**: con 8 medallas alterna la victoria de Liga; con 16, la de Rojo.
- **EQUIPO DE PRUEBA**: sustituye el equipo sandbox por Bayleef, Houndoom y Togetic shiny al nivel del límite menos uno, con estadísticas y PP correctos, Viento Hielo, Poder Oculto, Fuerza Lunar y Surf, equipados con Banda Focus.
- **REINICIAR RETOS**: limpia capturas de zona, intercambio de Tito, victorias de Tito/Rojo, santuario y Ulex. Hay que salir de la zona y volver para recargar sus actores.
- **OBJETOS**: entrega diez unidades de Repelente, Superrepelente, Máximo Repelente, Banda Focus, Poción y Restaurar Todo, más siete MT aleatorias, si hay capacidad. Se puede repetir. No es un editor arbitrario de objetos.
- **OPCIONES**: ajustes normales del juego.

Los viajes y las medallas son herramientas de prueba: no completan automáticamente las misiones de historia. Los eventos siguen siendo los reales.

## Recetas de prueba

- **Tito**: avanzar a 16 medallas, activar la victoria de Rojo y visitar un centro.
- **Santuario del Encinar**: viajar al santuario, preparar el equipo y usar Master Ball.
- **Ulex**: viajar a su ruta, hablar con él y avanzar una medalla antes del siguiente.
- **Tope de nivel**: el equipo de prueba está un nivel por debajo; un caramelo alcanza el límite y otro comprueba el bloqueo.

## Fallo corregido en 4.2

OBJETOS se bloqueaba al llamar directamente a `ReceiveRandomTM` desde otro banco de ROM. Ver [CHANGELOG](../CHANGELOG.md) y [ARQUITECTURA](ARQUITECTURA.md). Una prueba entra desde el menú real, usa OBJETOS dos veces, comprueba cantidades y MT, y vuelve al mapa.

# Arquitectura y decisiones verificadas

## Motor y estado de la partida

Se modifica el motor de Cristal en ensamblador LR35902/SM83. Las tablas de especies,
movimientos, entrenadores, mapas y eventos alimentan los sistemas de combate y mundo.
Las reglas Nuzlocke, topes y excepciones se integran en las rutas correspondientes;
las comprobaciones ejecutan la ROM, en lugar de reimplementar las reglas en Python.
WRAM y flags existentes guardan el estado; la migración del inventario conserva el
total de espacios combinado entre mochila y PC. No se afirma compatibilidad universal
con cualquier ROM externa o estado de emulador.

## Gráficos y memoria

Tito usa una cuadrícula revisada de 16x16 con tres colores visibles más transparencia.
La hoja 16x96 incluye frente, espalda, izquierda y tres fotogramas alternos completos.
El perfil derecho se refleja. Las pruebas observan OAM y los índices de tiles
dibujados, además de comparar la carga en VRAM con el gráfico compilado.

En exteriores el motor reserva gráficos por grupo de mapas. Ulex carecía de una
entrada para su sprite variable y GetSpriteVTile recurría a los tiles del jugador.
La corrección sustituye un espacio exterior sin uso, de la misma capacidad, por
SPRITE_COPYCAT. Los callbacks eligen el disfraz y el giro carga SPRITE_ROCKET.
Se verificaron el disfraz y la revelación en las 16 rutas con los bytes reales de VRAM.

## Llamadas entre bancos

OBJETOS del sandbox llamaba directamente a ReceiveRandomTM, situada en otro banco.
La dirección se ejecutaba en el banco equivocado. La llamada farcall conserva y
restaura el contexto de banco. La prueba de interfaz entrega objetos dos veces,
comprueba catorce MT en total y regresa al mapa sin bloquearse.

## Randomizador portable

El exportador genera un manifiesto a partir de la fuente y los símbolos compilados.
Solo ciertas referencias de especies, tablas de MT y campos relacionados son
mutables. El HTML integra núcleo y manifiesto, valida tamaño y firma de la parte
inmutable y descarga una nueva ROM sin enviarla a un servidor. Misma semilla y base
compatibles producen los mismos bytes; niveles, MO y código permanecen protegidos.

## Restricciones conservadas

Se reutilizan IDs de movimientos existentes; no se ha ampliado la Pokédex a otras
generaciones. Las habilidades y las megas no están implementadas. Los informes
distinguen pruebas ejecutadas, montajes controlados y límites de la validación.

## Rutinas centrales (fuente integrada)

- `GetCurrentLevelCap` (`engine/pokemon/v2_balance.asm`) devuelve el tope de nivel en B y conserva C, DE y HL. Lo reutilizan la experiencia de combate, los caramelos raros, la guardería y Tito. Lee dos tablas de pares `medalla, tope` (`V3JohtoCaps`, `V3KantoCaps`) y consulta los flags de Hall of Fame y de victoria sobre Rojo.
- `RandomizeFourMoves` genera cuatro movimientos distintos al crear un Pokémon sin tocar la tabla de aprendizaje original, con el primero siempre de daño directo repetible. `ChooseRandomLevelMove` y `ChooseRandomMoveAtDE` eligen movimientos desconocidos al subir de nivel y al retirar de la guardería. Las tablas originales (`EvosAttacks`) se conservan para el recordador de Tito.
- Los movimientos modernos reutilizan IDs de un byte con alias `DEF ... EQU ...` en `constants/move_constants.asm` ([tabla](MOVIMIENTOS-SUSTITUIDOS.md)).

## Compatibilidad de guardados

El inventario ocupa 50 montones y el PC 20 (antes 20 y 50): se conservan los 70 espacios combinados y una rutina migra guardados anteriores, principal y de respaldo. Los recursos de inicio solo se otorgan en partidas nuevas. Detalle en [COMPATIBILIDAD-GUARDADOS.md](COMPATIBILIDAD-GUARDADOS.md).

## Qué distingue base y modificación

La base (motor, mapas, gráficos y textos de Pokémon Cristal en español) procede de MicaelAlighieri/pokecristal y pret/pokecrystal. Las modificaciones están agrupadas en `parches/Cambios-fuente.patch`: 65 archivos de `engine/`, 63 de `maps/`, 57 de `data/`, 16 de `tools/`, 11 de `constants/`, 10 de `gfx/`, 2 de `ram/`, 1 de `home/` y los archivos raíz `.gitattributes` y `main.asm` (227 en total).

## Cambios de la 4.3 con restricciones de memoria

- **Rótulos de la bolsa.** El recuadro negro de la izquierda muestra el bolsillo de objetos con cinco tiles por rótulo (20 tiles, `gfx/pack/pack_categories.png`, generados por `herramientas/fuentes/build_pack_labels.py`). El banco 4 estaba casi lleno y 320 bytes de gráficos lo desbordaban, así que los tiles viven en una sección ROMX propia (`SECTION "Pack category labels"`) y se copian con `FarCopyBytes` a los tiles `$60-$73` de VRAM, libres en esa pantalla. `DrawBagCategoryName` ya no escribe texto en la fila superior: coloca los cinco tiles del rótulo en el recuadro.
- **Círculo de bolsillos.** Al entrar en ITEMS desde BALLS (izquierda) se aterriza en OTROS y desde MT/MO (derecha) en MEDICINA. El cálculo está en `PackSetCategoryOnEntry` (otro banco, vía `farcall`) para ahorrar bytes en el banco 4; antes la categoría se conservaba y desde MT/MO se volvía a entrar en OTROS.
- **Caramelos infinitos.** `RareCandyEffect` termina con `ret` en lugar de `jp UseDisposableItem`: el efecto se aplica y la cantidad no cambia.
- **Nivel blando del primer Ulex.** El área WRAM de `wUlexLocation` y compañía está dimensionada al byte: añadir una variable desplaza la sección alineada siguiente y desborda WRAM0. El nivel 15 se señala con el bit 7 de `wUlexLocation`, que `UlexSelectTeam` activa solo con cero medallas en la Ruta 31 y que `ClampProgressionLevel` consume mientras se lee el equipo; `UlexCommitEncounter` y la rama de combate rechazado lo borran para que ningún combate salvaje posterior se vea afectado.
- **Escena del anciano.** Dos eventos de coordenada en la entrada de Ciudad Cerezo (filas 6 y 7, columna 36), activos solo en la escena inicial, mueven al anciano hasta el jugador; la visita guiada y sus textos se eliminaron.
- **Suministros de la Liga.** Tres flags de evento nuevos (`EVENT_GOT_LEAGUE_*`) en un rango libre de la tabla de eventos permiten reanudar la entrega si la mochila estaba llena.
- **Tiendas.** `data/items/marts.asm` se reescribe sin objetos curativos; los tres casos que quedaban vacíos reciben artículos no curativos. Las máquinas expendedoras (dos mapas) se sustituyen por un texto.

## Cambios de la 4.4

- **Tope de nivel en la pantalla de estado.** `LoadPinkPage` termina imprimiendo «TOPE» en la fila 17 y el nivel con `PrintLevel`. `GetCurrentLevelCap` devuelve el límite en `b`; como `PrintLevel` lee `wTempMonLevel`, se guarda ese byte, se sustituye por el límite y se restaura. No se añade WRAM.
- **Iconos de categoría de ataque.** Tres tiles 2bpp (`gfx/battle/move_categories.png`, generados por `herramientas/fuentes/build_move_icons.py`) en una sección ROMX propia (`SECTION "Move category icons"`), porque el banco del combate (`Battle Core`) está casi lleno. `DrawMoveCategoryIcon` se llama con `farcall` al final del dibujo del recuadro de información del movimiento: lee los dos bits altos del tipo del movimiento (la categoría), copia los tres tiles al identificador de fondo 89 (`MOVE_CATEGORY_ICON_TILE`, libre en la pantalla de combate) con `Get2bpp` y coloca el índice correspondiente en la columna de la categoría.
- **Rótulos nativos de la mochila.** `build_pack_labels.py` redibuja en `gfx/pack/pack_menu.png` los tres rótulos originales (OBJ.CLAVE, MT/MO y BALLS) con la misma tipografía de cinco píxeles que los cuatro propios. Es arte, no código: ocupan los mismos tiles que antes.
- **Animación de reposo.** Nuevo movimiento de sprite `SPRITEMOVEDATA_STANDING_IDLE` (función `MovementFunction_StandingIdle`, acción `OBJECT_ACTION_IDLE`) con la rutina `SetFacingIdle`, que fija el fotograma «paso 0» de la dirección actual y, durante 16 de cada 128 cuadros (según `hVBlankCounter`), el «paso 1». La hoja de Tito (16×96) ya tenía una segunda mitad de fotogramas alternos; `build_tito_sprite.py` la genera ahora como la misma pose con cabeza y tronco un píxel más abajo. Los 22 Tito de los Centros Pokémon usan el nuevo movimiento. Sin VRAM ni WRAM nuevas: los sprites de pie y de paso ya se cargan en dos copias de tiles (`$3c` y `$bc`), por lo que las pruebas aceptan Tito en cualquiera de las dos copias.
- **Vista previa del randomizador.** El exportador añade al manifiesto `speciesNames`, `moveNames`, `leaders` (22 grupos de entrenador, con las claves `.__RZ` de sus ranuras de `parties.asm`) y `starterKeys`; `randomize` devuelve ahora `chosen` con las elecciones por clave. Es solo lectura y no cambia los bytes generados.

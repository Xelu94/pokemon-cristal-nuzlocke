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

La base (motor, mapas, gráficos y textos de Pokémon Cristal en español) procede de MicaelAlighieri/pokecristal y pret/pokecrystal. Las modificaciones están agrupadas en `parches/Cambios-fuente.patch`: 63 archivos de `engine/`, 59 de `maps/`, 56 de `data/`, 14 de `tools/`, 9 de `constants/`, 7 de `gfx/`, 2 de `ram/` y los archivos raíz `.gitattributes` y `main.asm`, más `home/trainers.asm`.

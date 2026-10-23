# Radical Cristal — Tito Xeluis v5.1

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon.

## Descarga

Un único archivo jugable: **`Radical Cristal.gbc`** (ROM normal v5.1).

- SHA-256: `339f38f5d51b9bd1a4adcd28e1767fbbf32ef4e0e343f4965acbdc9cb4fa00e5`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado).
- No necesita partida nueva respecto a la 5.0 ni la 4.4: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

## Novedades de 5.1

1. **Sin Pokémon, el otro protagonista ya no embosca.** Hablar con PLATA junto a la ventana antes del inicial dejaba un combate a medias; el primer encuentro de la ruta se dibujaba como un combate contra ella y el menú daba fallos. Ahora solo hay el empujón de Plata.
2. **GOLD / CRISTAL aparece delante del jugador** (antes salía detrás del cartel de Pueblo Primavera), y **el sprite del jugador ya no se deforma** al volver de un combate.
3. **Imagen trasera de Dark Lugia** nueva, de [SageDeoxys](https://www.deviantart.com/sagedeoxys) (con la marca roja de la barriga quitada).
4. Revisión general: recorridos de historia jugados como chico y como chica, 394 mapas, Pokédex y textos.

Detalle y límites: `CHANGELOG.md`. Las novedades de la 5.0 (Superliga, otro protagonista, duelo de Elm, Dark Lugia, Joy y más) siguen igual.

## Validación

198 comprobaciones agrupadas, no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global; el combate del campeón de la Superliga no se juega entero en las pruebas. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v5.1.json`.

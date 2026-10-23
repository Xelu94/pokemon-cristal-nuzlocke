# Radical Cristal — Tito Xeluis v5.2

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon.

## Descarga

Un único archivo jugable: **`Radical Cristal.gbc`** (ROM normal v5.2).

- SHA-256: `6861c67987485a36df0e3c4a83906bd68f778a7b649466984dffdeb31ffc590b`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado).
- No necesita partida nueva respecto a la 5.1, la 5.0 ni la 4.4: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

## Novedades de 5.2

1. **El mensaje de fin del reto sale entero.** Cuando el reto Nuzlocke ya había terminado y intentabas combatir, el mensaje de «has perdido» aparecía desplazado y cortado sobre el mapa. Ahora se muestra completo sobre una pantalla limpia.
2. **Con el reto terminado, un líder de gimnasio ya no da la medalla** sin combatir.

Detalle y límites: `CHANGELOG.md`. Lo de la 5.1 (emboscada sin Pokémon, sprite del jugador, imagen trasera de Dark Lugia) y de la 5.0 sigue igual.

## Validación

200 comprobaciones agrupadas, no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global; el combate del campeón de la Superliga no se juega entero en las pruebas. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v5.2.json`.

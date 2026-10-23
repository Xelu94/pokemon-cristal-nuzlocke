# Radical Cristal — Tito Xeluis v5.3

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon.

## Descarga

Un único archivo jugable: **`Radical Cristal.gbc`** (ROM normal v5.3).

- SHA-256: `aab4601450c38aa762b643033df21af26dd698cb30d44dce50f92780783e6408`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado).
- No necesita partida nueva respecto a la 5.2, 5.1, 5.0 ni 4.4: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

## Novedades de 5.3

1. **La Superliga ya no reinicia la consola** al ganar o perder contra Ulex o Tito (leían su texto de un banco equivocado).
2. **Elm combate con su propia imagen** (antes la de Oak) y sus tres regalos son **shiny también al ir a la caja**.
3. **Piedras evolutivas en las tiendas** de Ciudad Trigal en adelante (se quita el vendedor del Centro Pokémon).
4. **Caramelos raros por tandas**: selector de cantidad de 1 a 99.
5. Sandbox: «Viajar» a la Liga ya no te deja en la pared y OBJETOS da las siete MO.
6. Además: el guardia de Rojo se aparta tras dejarte pasar, Sudowoodo se ve bien, la imagen trasera de Dark Lugia es más grande y Tito habla en primera persona al abrirse la Superliga.

Detalle y límites: `CHANGELOG.md`.

## Validación

217 comprobaciones agrupadas, no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global; el combate del campeón de la Superliga se prueba perdiendo y con atajos, no ganándolo entero. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v5.3.json`.

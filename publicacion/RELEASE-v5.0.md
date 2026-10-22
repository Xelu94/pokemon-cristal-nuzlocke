# Radical Cristal — Tito Xeluis v5.0

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon. A partir de esta versión se llama **Radical Cristal**.

## Descarga

Un único archivo jugable: **`Radical Cristal.gbc`** (ROM normal v5.0).

- SHA-256: `86052da1d0db6fbdeb0a3a87c784e7c8032395fe54523f6127fc7179736ad089`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado).
- No necesita partida nueva respecto a la 4.4: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

## Novedades de 5.0

1. **Superliga** (se abre al vencer a Tito): cuatro retadores y un campeón al nivel 100, sin muertes, con 99 RESTAU. TODO, y un CHARIZARD shiny con una carta si ganas.
2. **El otro protagonista** (GOLD o CRISTAL): tres emboscadas tras las escenas en que Plata solo habla, combate final en la Meseta Añil con un huevo y una casa en Pueblo Primavera con un canje de ZURULLO.
3. **Duelo con Elm** y tres starters shiny.
4. **Dark Lugia** (Siniestro/Volador) al vencer a Tito por primera vez.
5. Enfermeras Joy en las rutas sin Centro Pokémon cerca, piedras evolutivas en Trigal, bayas doradas en vez de bonguri, Máx. Poción en lugar de Balls y huevos de 10 pasos en un shiny aleatorio.
6. El NPC del tutorial avisa de Ulex; objetos de combate infinitos y de precio 0; arreglos de la animación de andar de los PNJ y de la barra de experiencia.
7. Título «Radical Cristal».

## Validación

173 comprobaciones agrupadas, no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global; el combate del campeón de la Superliga no se juega entero en las pruebas. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v5.0.json`. Detalle de cada novedad: `docs/SUPERLIGA-Y-RIVAL.md` y `CHANGELOG.md`.

## Más información

README, mecánicas, compatibilidad de guardados, tabla de movimientos sustituidos, niveles y evoluciones: ver el repositorio.

# Pokémon Cristal Nuzlocke — Tito Xeluis v4.4

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon.

## Descarga

Un único archivo jugable: **`Pokemon Cristal Nuzlocke.gbc`** (ROM normal v4.4).

- SHA-256: `b4cff3b076988a780d6570653d677b7fecab1cbb4fdfcc6dde8cda5a22c1e3ef`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado).
- No necesita partida nueva respecto a la 4.3: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

## Novedades de 4.4

1. **Tope de nivel visible** en la primera página de estado («TOPE»).
2. **Iconos de categoría** (física, especial, estado) en el subpanel de ataques.
3. **Rótulos en toda la mochila**: MT/MO, BALLS y OBJ.CLAVE con la misma tipografía que el resto.
4. **Tito respira** en los Centros Pokémon.
5. **Randomizador con vista previa** de iniciales, equipos de líderes y MT de la semilla (el `Randomizador.html` de esta versión solo acepta la ROM 4.4).
6. Dos líneas de diálogo desbordadas corregidas (profesora de Ciudad Cerezo y santuario del Encinar).

## Validación

140 comprobaciones agrupadas (137 anteriores más 3 nuevas), no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v4.4.json`.

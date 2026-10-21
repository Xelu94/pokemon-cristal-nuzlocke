# Pokémon Cristal Nuzlocke — Tito Xeluis v4.3

Modificación personal de Pokémon Cristal para Game Boy Color, basada en el código fuente español de MicaelAlighieri/pokecristal y el trabajo de la comunidad pret/pokecrystal. No es un producto oficial de Pokémon.

## Descarga

Un único archivo jugable: **`Pokemon Cristal Nuzlocke.gbc`** (ROM normal v4.3).

- SHA-256: `a6a232589e9ff8859bc9307c3593707c753dcaf8b6be65a8ba835faafe949b1e`
- No necesita ROM base ni aplicar parches. Ábrela con un emulador compatible con Game Boy Color (se obtiene por separado). El modo ×2 depende de las opciones del emulador.
- No necesita partida nueva: guarda dentro del juego y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador requiere partida nueva.

Los archivos «Source code» que GitHub genera automáticamente no son la descarga para jugar.

## Novedades de 4.3

1. **Vuelo desde el menú del Pokémon**, igual que Destello (MO en la mochila + medalla + Pokémon vivo). El mapa del Pokégear sigue funcionando.
2. **El anciano de Ciudad Cerezo te da el mapa solo**, sin hablarle: se acerca, te lo entrega y desaparece.
3. **El primer Ulex (Ruta 31)** saca sus Pokémon al nivel 15; los demás Ulex no cambian.
4. **Sin curas en las tiendas** (ni en las máquinas expendedoras).
5. **Suministros de la Liga:** el oficial de la Calle Victoria entrega una vez 8 Máx. Poción, 10 Híper Poción y 7 Restau. Todo.
6. **Diálogo inicial de Tito reescrito**, con las reglas Nuzlocke explicadas paso a paso.
7. **99 caramelos raros infinitos** en un solo montón (libera espacio de mochila).
8. **Mochila más clara:** el tipo de objeto se ve en el recuadro negro y los bolsillos forman un círculo.

## Validación

137 comprobaciones agrupadas (124 anteriores más 13 nuevas), no un porcentaje de cobertura. No se ha completado una campaña entera ni queda demostrado el equilibrio global. La reconstrucción desde el parche y la base reproduce exactamente los SHA-256 de las ROM. Informe: `evidencias/Validacion-v4.3.json`.

## Más información

README, mecánicas, compatibilidad de guardados, tabla de movimientos sustituidos, niveles y evoluciones: ver el repositorio.
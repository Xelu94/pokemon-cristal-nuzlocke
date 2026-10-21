# Cambios

Formato por versión. Las versiones anteriores a la 4 no están documentadas en este paquete; solo se sabe que la actualización v3→v4 permite continuar el guardado.

## 4.3 — Mejoras de jugabilidad (21 de octubre de 2026)

Ocho cambios pedidos por el autor tras jugar la 4.2. Se validaron con 13 comprobaciones nuevas más las 124 anteriores (137 en total, [evidencias/Validacion-v4.3.json](evidencias/Validacion-v4.3.json)); no equivalen a una campaña completa.

1. **Vuelo desde el menú del Pokémon.** Con la MO Vuelo en la mochila, la medalla de Tormenta y un Pokémon vivo, aparece VUELO en el submenú del Pokémon (igual que Destello). El vuelo desde el mapa exterior del Pokégear se conserva.
2. **El anciano de CIUDAD CEREZO entrega el mapa sin hablarle.** Al entrar en la ciudad le sale una exclamación, se acerca, dice que usó la tarjeta «para limpiarme los mocos» y se la da, y desaparece. Se eliminó la visita guiada. Si el jugador le habla, también se la da.
3. **El primer Ulex (Ruta 31, sin medallas) saca sus Pokémon al nivel 15** en lugar de 19. Solo ese encuentro: los demás Ulex siguen en el límite vigente.
4. **Las tiendas ya no venden objetos curativos.** Se quitaron pociones, revivir, antídotos y demás curas de estado, bebidas curativas y CARAM. FURIA de las 34 tiendas. Tres tiendas que quedaban vacías (Ciudad Orquídea, el primer mostrador de la planta 2 del Gran Almacén de Ciudad Trigal y el herbolario subterráneo) venden ahora Poké Balls, Superrepelentes, repelentes o Cuerdas Huida. Las máquinas expendedoras de Ciudad Trigal y Ciudad Azulona están vacías.
5. **Suministros de la Liga.** El oficial de la Puerta de la CALLE VICTORIA, al comprobar las ocho medallas de Johto, entrega una sola vez 8 MÁX. POCIÓN, 10 HÍPER POCIÓN y 7 RESTAU. TODO.
6. **Diálogo inicial de Tito reescrito.** Sintaxis corregida y reglas Nuzlocke explicadas paso a paso (capturas, excepciones, muerte, fin de la aventura, límite de nivel, intercambios, Ulex).
7. **99 caramelos raros infinitos.** Una partida nueva empieza con un único montón de 99 que no se consume al usarlo (antes 999 finitos en 11 montones). Libera 10 espacios de la mochila. Los guardados existentes conservan sus montones y todos los caramelos pasan a ser infinitos.
8. **Mochila más clara.** El tipo de objeto (MEDICINA, BAYAS, COMBATE, OTROS) se muestra ahora en el recuadro negro de la izquierda, en lugar del rótulo «Objetos» y de la línea superior. La navegación es un círculo: derecha desde OTROS pasa a Balls, Obj.Clave y MT/MO, y vuelve a MEDICINA; izquierda desde MEDICINA llega a MT/MO y, al volver desde Balls, se entra en OTROS.

Notas técnicas: el banco 4 de la ROM está casi lleno, por lo que los gráficos de los rótulos viven en una sección propia y el cálculo del punto de entrada de la mochila está fuera de ese banco. No se añadió WRAM; el nivel blando del primer Ulex usa el bit 7 de `wUlexLocation`. Se añadieron tres flags de evento en el rango antes libre.

### Compatibilidad

No necesita partida nueva. Las curas ya compradas se conservan. Otra semilla del randomizador sigue requiriendo partida nueva, y el randomizador de esta versión solo acepta la ROM 4.3 (cambia la firma de la parte inmutable).
## 4.2 — Sprites y sandbox (20 de octubre de 2026)

Tres correcciones. Las pruebas citadas (124 comprobaciones) se resumieron en evidencias/Validacion-v4.2.json, que se conserva en la etiqueta 4.2 del historial de Git; ninguna equivale a una campaña completa.

### 1. Sprite de Tito: cuadrícula nativa y direcciones

- **Problema.** El sprite de Tito en los centros no tenía la calidad ni la estructura de direcciones que exige el motor: contornos y ojos poco legibles a 16×16 y fotogramas alternos incompletos.
- **Causa.** Según la documentación del generador, reescalar la hoja grande de referencia a 16×16 pierde ojos y contornos, y el motor necesita frente, espalda e izquierda seguidos de fotogramas alternos completos para no leer datos ajenos al gráfico. Esta lectura se basa en la nota del generador y en el registro de cambios 4.2; no se conserva una captura del estado anterior.
- **Solución.** El arte se define ahora en una cuadrícula nativa de 16×16 (contornos, sombreado, ojos separados del bigote, silueta con sombrero y pañuelo). La hoja tiene tres poses (frente, espalda, izquierda) y tres fotogramas alternos completos; la derecha se refleja por hardware. Se compila a 16×96 en 2bpp con `herramientas/fuentes/build_tito_sprite.py`.
- **Validación.** 4 comprobaciones de orientaciones renderizadas (tiles y reflejo reales, no solo la variable de dirección) y 48 de servicios y mapas de Tito.

### 2. Ulex: espacio de gráficos en exteriores

- **Problema.** El sprite variable de Ulex (disfraz y revelación) podía mostrarse con los tiles del jugador.
- **Causa.** Las tablas de gráficos de los mapas exteriores no tenían registro para `SPRITE_COPYCAT`; `GetSpriteVTile` recurría a los tiles del jugador.
- **Solución.** Se reserva un espacio gráfico para el sprite variable reutilizando un espacio exterior sin uso, de la misma capacidad, en lugar de añadir gráficos sin límite (la VRAM es limitada). Los 16 encuentros tienen un disfraz de NPC según la ruta y, tras el giro, cargan siempre el gráfico de recluta Rocket.
- **Validación.** Disfraz y revelación comprobados en las 16 rutas con los bytes reales de VRAM (grupo de 17 comprobaciones junto con Objetos).

### 3. Sandbox: OBJETOS se bloqueaba

- **Problema.** La opción OBJETOS del sandbox colgaba el juego.
- **Causa.** Llamaba directamente a `ReceiveRandomTM`, situada en otro banco de ROM; la dirección se ejecutaba en el banco equivocado.
- **Solución.** Se sustituyó por la llamada que cambia de banco (far call) a `ReceiveRandomTM`, que conserva y restaura el banco. OBJETOS entrega 10 de cada uno de Repelente, Superrepelente, Máximo Repelente, Banda Focus, Poción y Restaurar Todo, y 7 MT aleatorias si hay capacidad; se puede repetir.
- **Validación.** Una prueba entra desde el menú real, usa OBJETOS dos veces, comprueba cantidades y 14 MT en total, y vuelve al mapa.

### Compatibilidad

No necesita partida nueva. Guarda dentro del juego, cierra el emulador y carga el `.sav` con la nueva ROM. No uses estados rápidos de otra compilación. Otra semilla del randomizador sigue requiriendo partida nueva. El retrato de combate de Tito y sus servicios se conservan.

## 4.1 — Interfaz y calidad de vida (19 de octubre de 2026)

1. La potencia, el tipo, la categoría y los PP ocupan un subpanel compacto dentro del marco de combate; los cuatro nombres de ataque conservan todo su ancho.
2. Ulex aparece con el sprite genérico propio de cada ruta antes del giro y revela después su sprite de ladrón.
3. La mochila usa cuatro bolsillos de objetos (MEDICINA, BAYAS, COMBATE, OTROS) navegables con izquierda/derecha junto a MT/MO, Balls y objetos clave. Start deja de alternar filtros y desaparece la vista duplicada TODOS.
4. SUBIR MEDALLAS del sandbox abre un selector de 0 a 16 y recalcula el límite al instante.
5. Una partida nueva recibe 99 Master Balls en un único montón. Los guardados existentes conservan sus cantidades.
6. Todos los intercambios con entrenadores genéricos usan el flujo de Tito: eliges Pokémon, ves la especie exacta y aceptas o cancelas. Solo el primer intercambio completado queda gastado.
7. El sprite de Tito en los centros se sustituye por el nuevo lienzo, con frente, espalda y perfil.

## 4.0 — Sistemas y contenido

1. Tito en los centros: hoja de sprites completa, poses y colores corregidos; los menús muestran su nombre; el retrato de combate se conserva.
2. Recordador: desaparecen los sprites del mapa sobre los menús y se restauran las paletas. Nueva consulta gratuita de evoluciones modificadas.
3. Intercambio: seleccionas, ves la oferta exacta y confirmas. Cancelar no gasta el intercambio de la ciudad.
4. Antes de Oak, Tito explica Nuzlocke, capturas, muertes, límites y Ulex.
5. La madre compra MT aleatorias para su bolsillo. Los revividores encontrados y el regalo de Trigal pasan a MT.
6. Repelentes desde la primera tienda; se renuevan al agotarse con prioridad Máximo, Super, Repelente.
7. Los Pokémon muertos desaparecen al depositarlos en el PC.
8. Mochila de 20 a 50 montones, PC de 50 a 20 (70 combinados), con migración automática comprobada con guardados v3 principal y de respaldo.
9. Ulex el Ladrón: 16 disfraces en Johto y Kanto, giro y revelación, equipo aleatorio shiny al límite de nivel, MT por victoria sin nuevas muertes o robo y ZURULLO (Rattata nivel 5 con Salpicadura) si hay una nueva muerte. Los combates rechazados no consumen el encuentro.
10. El shiny mostrado al encontrarlo se conserva al capturarlo y enviarlo al PC. Eventos salvajes y errantes son shiny garantizado y no consumen la captura ordinaria de la zona.
11. Santuario del Encinar: Misdreavus shiny nivel 25 en la distribución incluida; el randomizador cambia la especie según la semilla.
12. Potencia visible en la selección de combate, estado y detalle de movimientos. Poder Oculto muestra tipo real y potencia calculada con los DVs.
13. Líderes y Alto Mando suben 5 niveles. Rojo tiene seis Pokémon al 95. Límite 95 con 16 medallas y 100 tras Rojo. Salvajes y entrenadores respetan el mínimo del líder anterior menos tres.
14. Los Pokémon intercambiados obedecen hasta el límite vigente incluido.
15. Banda Focus y Cinta-Focus: solo a PS completos, sobreviven con 1 PS ante un golpe directo letal y se consumen; un ataque múltiple puede rematar.
16. Viento Hielo conserva daño y bajada de Velocidad con una animación más simple. Probado con Bayleef en 12 usos completos sin reinicio; el fallo móvil original no se reprodujo.
17. Nueve ataques modernos adicionales con animaciones del motor.
18. Los 254 identificadores estaban ocupados: nueve ataques se sustituyen en su mismo ID ([tabla](docs/MOVIMIENTOS-SUSTITUIDOS.md)).
19. Randomizador portable por semilla, sin instalación ni conexión ([docs](docs/RANDOMIZADOR.md)).
20. Sandbox separado con 41 accesos rápidos y 388 destinos en 26 grupos.

### Validación y límites de 4.0

Se compilaron versiones normal y sandbox con RGBDS 1.0.0 y se ejecutaron rutinas reales en PyBoy, pruebas de interfaz y combate, migración de guardados v3, aleatorización en Node y generación/descarga en navegador. Se mantienen 251 especies. No hay habilidades, megas ni recursos de Prism.

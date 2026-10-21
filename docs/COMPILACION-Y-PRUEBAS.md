# Compilación, herramientas y pruebas

## Qué contiene este repositorio y qué no

Este repositorio **no incluye el árbol completo del código fuente** (miles de archivos de la base española), sino las modificaciones como [`parches/Cambios-fuente.patch`](../parches/Cambios-fuente.patch) (formato `git diff --binary`, acumulado: lleva la base española a la versión 4.3) más los recursos, herramientas y pruebas propios. La fuente integrada se obtiene aplicando el parche sobre la instantánea base española.

- La instantánea base verificada (`base-espanola-verificada.zip`, SHA-256 `99e659b91677e822b2ed31c12e1695ac730b426a7ef79d0bbb4352a07ac0e74b`) se conserva en el material de trabajo local del autor; no se publica aquí.
- El parche vigente tiene SHA-256 `5a0d232457e55de031a75def8b416d5ebdf0c8d794d74570f7e8b8037b3569a7`.
- El identificador de revisión de informes anteriores pertenecía al historial local y **no es un commit descargable** del repositorio upstream.
- La base española procede de [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal). Hasta que se compruebe un commit concreto de ese repositorio con el mismo hash de árbol, la reconstrucción exclusivamente desde GitHub no está garantizada.

Las ROM sin parche no se publican. Los parches BPS históricos (normal y sandbox) de 4.2 y anteriores son material de trabajo local; se aplicaron a la ROM española de referencia con SHA-1 `889a06fc0bb863666865aa69def0adf97945ac2a` y no se adjuntan.

## Herramientas

| Herramienta | Uso |
|---|---|
| RGBDS 1.0.0 | `rgbasm`, `rgblink`, `rgbfix`, `rgbgfx` |
| make y GCC | Construcción y utilidades en C de la fuente |
| Git | Aplicar el parche (`git apply`) |
| Python 3 | Generación de recursos, manifiestos, hashes, pruebas |
| Pillow | Compilar y verificar gráficos |
| PyBoy 2.8.1 | Ejecutar la ROM en pruebas (`pruebas/requirements.txt`) |
| Node.js | Núcleo del randomizador y Playwright |
| Playwright 1.62.1 | Prueba del randomizador en navegador (`pruebas/package.json`) |
| mGBA 0.10.5 | Emulador del portable de desarrollo; no se distribuye |

Las herramientas se resuelven por `PATH` (y `PLAYWRIGHT_CHANNEL`/`NODE_BINARY` si se desea otro navegador o Node); no hay rutas absolutas. En Windows, la reconstrucción se comprobó con RGBDS 1.0.0 (zip oficial de Windows), GCC y make de WinLibs (`mingw32-make`) y las utilidades `sh` de Git for Windows en el `PATH`.

## Reconstruir la fuente y compilar

Desde la raíz del repositorio:

```sh
mkdir pruebas/work/source
# Extrae base-espanola-verificada.zip en pruebas/work/source (instantánea base)
cd pruebas/work/source
git init
git apply --check ../../../parches/Cambios-fuente.patch
git apply ../../../parches/Cambios-fuente.patch
make -j4 cristal cristal_debug      # en Windows con WinLibs: mingw32-make -j4 cristal cristal_debug
```

Salidas: `pokecristal.gbc` (ROM normal) y `pokecristal_debug.gbc` (sandbox), con sus `.sym`.

> **Verificado en la preparación de la v4.3 (21 de octubre de 2026):** el parche aplica sin conflictos (solo un aviso de línea en blanco al final de un archivo) y los 4660 archivos resultantes son idénticos, byte a byte, a la fuente con la que se compiló. Una compilación limpia sobre ese árbol produjo exactamente:
>
> - ROM normal: `a6a232589e9ff8859bc9307c3593707c753dcaf8b6be65a8ba835faafe949b1e`
> - Sandbox: `d6a7449506680bdbb215e3aabeb4f6772585516e55eefe07c396f9543cc401f2`
>
> La compilación de la fuente de la 4.2 sin cambios reprodujo también los hashes publicados de la 4.2.

### Generación del sprite de Tito y de los rótulos de la bolsa

```sh
python herramientas/fuentes/build_tito_sprite.py   # desde la raíz de la fuente integrada
python herramientas/fuentes/build_pack_labels.py   # rótulos MEDICINA/BAYAS/COMBATE/OTROS (40x32)
```

El primero lee `gfx/sprites/tito_xeluis.pixels` y escribe `gfx/sprites/tito_xeluis.png` (16×96). El segundo escribe `gfx/pack/pack_categories.png`, que el Makefile convierte a 2bpp.

### Randomizador

```sh
cd pruebas/work/source
python tools/export_portable_randomizer.py ../v4-randomizer
```

Requiere los símbolos de la ROM recién compilada. **No ejecutes `tools/balanced_randomizer.py`**: pertenece al flujo histórico y restauraría tablas anteriores sobre la fuente vigente.

## Pruebas

Los scripts de [`pruebas/`](../pruebas) conservan la estructura relativa que esperan (`work/…`).

```sh
cd pruebas
python -m pip install -r requirements.txt
npm install
npx playwright install chromium
python work/validate-v43-release.py
```

`validate-v43-release.py` ejecuta los nueve grupos, comprueba el número esperado de comprobaciones de cada uno y genera `work/v43-validation.json`. Las pruebas de PyBoy usan la ROM compilada y sus símbolos; las de navegador usan el randomizador y no envían la ROM a ningún servidor.

### Resultados de 4.3

137 comprobaciones agrupadas, ejecutadas el 21 de octubre de 2026 sobre las ROM de los hashes anteriores (informes en [`evidencias/`](../evidencias)):

| Grupo | Informe | Comprobaciones |
|---|---|---|
| Servicios y mapas de Tito | `v4-tito-tests.json` | 48 |
| Orientaciones renderizadas de Tito | `v42-tito-directions-tests.json` | 4 |
| Rutas de Ulex y Objetos del sandbox | `v42-fixes-tests.json` | 17 |
| Combates de Ulex (incluido el primer Ulex al nivel 15) y menú sandbox | `v41-root-ui-tests.json` | 27 |
| Cálculos de combate y almacenamiento | `v4-battle-tests.json` | 11 |
| Interfaz real de combate y captura | `v41-battle-ui-tests.json` | 4 |
| Núcleo del randomizador | `v4-randomizer-tests.json` | 9 |
| Randomizador en navegador sin conexión | `v4-randomizer-ui-tests.json` | 4 |
| Cambios de la 4.3 (Vuelo, anciano del mapa, tiendas, Liga, caramelos, bolsa) | `v43-changes-tests.json` | 13 |

Las comprobaciones nuevas de la 4.3: la partida nueva empieza con un montón de 99 caramelos y 6 montones en total, usar un caramelo sube el nivel sin gastarlo, el recuadro negro muestra los cuatro rótulos, la navegación derecha e izquierda recorre el círculo de bolsillos, VUELO aparece en el submenú solo con la MO, el anciano entrega el mapa por las dos filas de entrada, ninguna de las 34 tiendas vende curas ni queda vacía, y el oficial entrega 8/10/7 con ocho medallas.

Los informes de 4.2 y anteriores pertenecen a otras compilaciones y no se suman a este recuento.

### Cómo leer los resultados

- No es un porcentaje de cobertura. Un grupo puede contener muchos casos (p. ej. Poder Oculto con 768 combinaciones de DVs).
- Los montajes omiten la introducción; algunos combates de Ulex aumentan el daño para recorrer los equipos; en Ruta 17 se desactiva la gravedad solo en el montaje de prueba.
- No se ha completado una campaña entera ni queda demostrado el equilibrio global.
- Los informes no contienen rutas del equipo: las ROM aparecen por nombre de archivo o ruta relativa.

## Integración continua

No hay integración continua en este repositorio y no se muestra ninguna insignia de estado. Si se añade GitHub Actions, los resultados deben proceder de una ejecución real en este repositorio. Hasta entonces, los resultados anteriores son los de las ejecuciones locales descritas.

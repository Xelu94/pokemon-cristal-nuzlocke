# Compilación, herramientas y pruebas

## Qué contiene este repositorio y qué no

Este repositorio **no incluye el árbol completo del código fuente** (miles de archivos de la base española), sino las modificaciones como [`parches/Cambios-fuente.patch`](../parches/Cambios-fuente.patch) (formato `git diff`, con hunks binarios) más los recursos, herramientas y pruebas propios. La fuente integrada se obtiene aplicando el parche sobre la instantánea base española.

- La instantánea base verificada (`base-espanola-verificada.zip`, SHA-256 `99e659b91677e822b2ed31c12e1695ac730b426a7ef79d0bbb4352a07ac0e74b`) se conserva en el material de trabajo local del autor; no se publica aquí.
- El parche (SHA-256 `3d31cacba5b4141ddbf7475c5de3e8d9064608a05479a95d8b3393a6e0869c77`) se verificó contra esa instantánea al preparar el paquete. El identificador de revisión que aparece en `evidencias/Validacion-v4.2.json` pertenece al historial local y **no debe suponerse un commit descargable** del repositorio upstream.
- La base española procede de [MicaelAlighieri/pokecristal](https://github.com/MicaelAlighieri/pokecristal). Hasta que se compruebe un commit concreto de ese repositorio con el mismo hash de árbol, la reconstrucción exclusivamente desde GitHub no está garantizada.

Las ROM sin parche no se publican. Los parches BPS históricos (normal y sandbox) son material de trabajo local, se aplicaron a la ROM española de referencia con SHA-1 `889a06fc0bb863666865aa69def0adf97945ac2a` y reconstruyen byte a byte las ROM probadas; no se adjuntan.

## Herramientas

| Herramienta | Uso |
|---|---|
| RGBDS 1.0.0 | `rgbasm`, `rgblink`, `rgbfix`, `rgbgfx` |
| make y GCC | Construcción y utilidades en C de la fuente |
| Python 3 | Generación de recursos, manifiestos, hashes, pruebas |
| Pillow | Compilar y verificar gráficos |
| PyBoy 2.8.1 | Ejecutar la ROM en pruebas (`pruebas/requirements.txt`) |
| Node.js | Núcleo del randomizador y Playwright |
| Playwright 1.62.1 | Prueba del randomizador en navegador (`pruebas/package.json`) |
| mGBA 0.10.5 | Emulador del portable de desarrollo; no se distribuye |

Las herramientas se resuelven por `PATH` (y `PLAYWRIGHT_CHANNEL`/`NODE_BINARY` si se desea otro navegador o Node); no hay rutas absolutas.

## Reconstruir la fuente y compilar

Desde la raíz del repositorio (PowerShell, bash adaptado igual con `git`):

```sh
mkdir pruebas/work/source
# Extrae base-espanola-verificada.zip en pruebas/work/source (instantánea base)
cd pruebas/work/source
git init
git apply --check ../../../parches/Cambios-fuente.patch
git apply ../../../parches/Cambios-fuente.patch
make -j2 cristal cristal_debug
```

Salidas: `pokecristal.gbc` (ROM normal) y `pokecristal_debug.gbc` (sandbox), con sus `.sym`. Compara el SHA-256 de `pokecristal.gbc` con el publicado.

> Estado verificado durante la preparación del repositorio (21 de octubre de 2026, Git 2.55): `git apply --check` y `git apply` del parche sobre la instantánea base se completan sin conflictos (solo un aviso de línea en blanco al final de un archivo) y los 4658 archivos resultantes son idénticos, byte a byte, a la fuente integrada del material de trabajo. **No se repitió la compilación** en ese momento porque RGBDS, make y GCC no estaban instalados; que la compilación limpia dé el mismo hash que la ROM publicada procede de `VERIFICACION-TRASLADO.json` del paquete de trabajo (árbol limpio sin `.git`), no de una ejecución nueva.

### Generación del sprite de Tito

```sh
python herramientas/fuentes/build_tito_sprite.py   # desde la raíz de la fuente integrada
```

Lee `gfx/sprites/tito_xeluis.pixels` y escribe `gfx/sprites/tito_xeluis.png` (16×96).

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
python work/validate-v42-release.py
```

`validate-v42-release.py` ejecuta los ocho grupos, comprueba el número esperado de comprobaciones de cada uno y genera `work/v42-validation.json`. Las pruebas de PyBoy usan la ROM compilada y sus símbolos; las de navegador usan el randomizador y no envían la ROM a ningún servidor.

### Resultados de 4.2

124 comprobaciones agrupadas (informes en [`evidencias/`](../evidencias)):

| Grupo | Informe | Comprobaciones |
|---|---|---|
| Servicios y mapas de Tito | `v4-tito-tests.json` | 48 |
| Orientaciones renderizadas de Tito | `v42-tito-directions-tests.json` | 4 |
| Rutas de Ulex y Objetos del sandbox | `v42-fixes-tests.json` | 17 |
| Combates de Ulex y menú sandbox | `v41-root-ui-tests.json` | 27 |
| Cálculos de combate y almacenamiento | `v4-battle-tests.json` | 11 |
| Interfaz real de combate y captura | `v41-battle-ui-tests.json` | 4 |
| Núcleo del randomizador | `v4-randomizer-tests.json` | 9 |
| Randomizador en navegador sin conexión | `v4-randomizer-ui-tests.json` | 4 |

Estos informes se generaron en el equipo original del autor para las compilaciones con los hashes de `Validacion-v4.2.json`. Las 306 comprobaciones históricas de otras versiones no se suman a este recuento.

### Cómo leer los resultados

- No es un porcentaje de cobertura. Un grupo puede contener muchos casos (p. ej. Poder Oculto con 768 combinaciones de DVs).
- Los montajes omiten la introducción; algunos combates de Ulex aumentan el daño para recorrer los equipos; en Ruta 17 se desactiva la gravedad solo en el montaje de prueba.
- No se ha completado una campaña entera ni queda demostrado el equilibrio global.
- Los informes JSON de `test-v4-battle` contienen el nombre de la ROM que se probó; se han revisado para no incluir rutas de equipo.

## Integración continua

No hay integración continua en este repositorio y no se muestra ninguna insignia de estado. Si se añade GitHub Actions, los resultados deben proceder de una ejecución real en este repositorio. Hasta entonces, los resultados anteriores son los de las ejecuciones locales descritas.

"""Rutas de las herramientas de playtest, configurables por entorno.

CRISTAL_SOURCE: arbol de la fuente integrada y compilada (por defecto ../source)
CRISTAL_OUT:    carpeta para informes y capturas (por defecto ..)
CRISTAL_V42:    arbol compilado de la v4.2, solo para la prueba de migracion de guardados
"""
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = Path(os.environ.get('CRISTAL_SOURCE', HERE.parent / 'source')).resolve()
WORK = Path(os.environ.get('CRISTAL_OUT', HERE.parent)).resolve()
V42 = Path(os.environ.get('CRISTAL_V42', HERE.parent / 'source-v42')).resolve()
(WORK / 'caps').mkdir(parents=True, exist_ok=True)

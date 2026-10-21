"""Auditoria estatica de dialogos: lineas de mas de 18 caracteres en los archivos que modifica el parche."""
import re
from pathlib import Path
from rutas import SRC, WORK
PATCH = Path(__file__).resolve().parents[2] / 'parches' / 'Cambios-fuente.patch'
changed = set(re.findall(r'^diff --git a/(\S+)', PATCH.read_text(encoding='utf8', errors='replace'), re.M))
print('archivos modificados por el parche:', len(changed))
EXPAND = {'#': 'POK\u00e9', '<PLAYER>': 'AAAAAAA', '<RIVAL>': 'AAAAAAA', '<TARGET>': 'AAAAAAAAAA', '<USER>': 'AAAAAAAAAA',
          '<PK><MN>': 'PKMN', '<\u2026>': '\u2026', '<\u2026\u2026>': '\u2026\u2026'}
def width(s):
    for k, v in EXPAND.items():
        s = s.replace(k, v)
    s = re.sub(r'<[A-Z_]+>', 'AAAAAA', s)
    s = re.sub(r'\{[^}]*\}', 'AA', s)
    return len(s)
SKIP = ('data/items/descriptions', 'data/moves/descriptions', 'data/pokemon/dex_entries')
problems = []
for f in sorted(changed):
    p = SRC / f
    if p.suffix != '.asm' or not p.exists() or f.startswith(SKIP):
        continue
    for n, line in enumerate(p.read_text(encoding='utf8', errors='replace').splitlines(), 1):
        m = re.match(r'\s*(text|line|cont|para|next)\s+"([^"]*)"', line)
        if m and width(m[2]) > 18:
            problems.append((f, n, width(m[2]), m[2]))
print('lineas de mas de 18 caracteres:', len(problems))
for f, n, w, s in problems:
    print('%s:%d (%d) %s' % (f, n, w, s))
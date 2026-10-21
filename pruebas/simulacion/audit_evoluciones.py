"""Static audit: evolutions, legendary levels, trainer/wild level sanity."""
from rutas import SRC, WORK, V42  # noqa: F401
import re, json
from pathlib import Path
root = SRC
groups = json.load(open(str(WORK / 'parties.json'), encoding='utf8'))
LEGEND = {'ARTICUNO','ZAPDOS','MOLTRES','MEWTWO','MEW','RAIKOU','ENTEI','SUICUNE','LUGIA','HO_OH','CELEBI'}
evos = (root / 'data/pokemon/evos_attacks.asm').read_text(encoding='utf8')
parent = {}
methods = {}
for name, body in re.findall(r'^(\w+)EvosAttacks:\n(.*?)(?=^\w+EvosAttacks:|\Z)', evos, re.M | re.S):
    for line in body.splitlines():
        m = re.match(r'\s*db (EVOLVE_\w+),\s*(.*)', line)
        if m:
            parts = [p.strip() for p in m[2].split(',')]
            methods.setdefault(m[1], []).append((name, parts))
            if m[1] in ('EVOLVE_LEVEL', 'EVOLVE_STAT'):
                lvl = int(parts[0]); tgt = parts[-1]
                parent[tgt] = (name.upper(), lvl)
            elif m[1] == 'EVOLVE_ITEM':
                parent[parts[-1]] = (name.upper(), 20)
print('evolution methods:', {k: len(v) for k, v in methods.items()})
for k in ('EVOLVE_TRADE', 'EVOLVE_HAPPINESS'):
    if k in methods:
        print('REMAINING', k, [(n, p) for n, p in methods[k]])

def minlevel(sp):
    lvl = 1
    seen = set()
    while sp in parent and sp not in seen:
        seen.add(sp)
        sp, l = parent[sp]
        lvl = max(lvl, l)
    return lvl

bad = []
leg = []
for g, trainers in groups.items():
    for t in trainers:
        for lvl, sp, rest in t['mons']:
            if sp in LEGEND and lvl < 55 and g != 'TitoXeluis':
                leg.append((g, t['name'], lvl, sp))
            if lvl < minlevel(sp):
                bad.append((g, t['name'], lvl, sp, minlevel(sp)))
print('trainer mons below their evolution level:', len(bad))
for b in bad[:40]: print('  ', b)
print('legendaries under level 55 in trainer parties:', leg[:20])

# wild tables
issues = []
for f in sorted((root / 'data/wild').glob('*.asm')):
    t = f.read_text(encoding='utf8')
    cur = None
    for line in t.splitlines():
        m = re.match(r'\s*db (\d+), ([A-Z0-9_]+)\s*(;.*)?$', line)
        if m:
            lvl, sp = int(m[1]), m[2]
            if sp in LEGEND and lvl < 55:
                issues.append((f.name, 'legend<55', lvl, sp))
            if sp in parent and lvl < minlevel(sp):
                issues.append((f.name, 'below evo level', lvl, sp, minlevel(sp)))
print('wild issues:', len(issues))
for i in issues[:30]: print('  ', i)

# trainer level histogram vs caps
levels = [l for ts in groups.values() for t in ts for l, _, _ in t['mons']]
print('trainer mon levels: min', min(levels), 'max', max(levels), 'count', len(levels))
import collections
buckets = collections.Counter((l // 10) * 10 for l in levels)
print(sorted(buckets.items()))

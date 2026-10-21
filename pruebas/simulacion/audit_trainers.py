"""Static audit of trainer parties: levels per group against the level caps."""
from rutas import SRC, WORK, V42  # noqa: F401
import re, sys, json
from pathlib import Path
root = SRC
text = (root / 'data/trainers/parties.asm').read_text(encoding='utf8')
groups = {}
cur = None
trainer = None
for line in text.splitlines():
    m = re.match(r'^(\w+)Group:', line)
    if m:
        cur = m[1]; groups[cur] = []; continue
    m = re.match(r'\s*db "([^@]+)@", (TRAINERTYPE_\w+)', line)
    if m:
        trainer = {'name': m[1], 'type': m[2], 'mons': []}; groups[cur].append(trainer); continue
    m = re.match(r'\s*db (\d+), ([A-Z0-9_]+)(.*)', line)
    if m and trainer is not None:
        trainer['mons'].append((int(m[1]), m[2], m[3].strip(', ')))
CAPS = [19, 24, 29, 35, 40, 44, 48, 53, 65, 67, 70, 73, 75, 77, 80, 83, 85, 95, 100]
json.dump(groups, open(str(WORK / 'parties.json'), 'w', encoding='utf8'), ensure_ascii=False)
print('groups', len(groups), 'trainers', sum(len(v) for v in groups.values()), 'mons', sum(len(t['mons']) for v in groups.values() for t in v))
def show(name):
    for t in groups.get(name, []):
        print(f"  {name:12s} {t['name']:10s} {[ (l,s) for l,s,_ in t['mons']]}")
for g in ['Falkner','Bugsy','Whitney','Morty','Chuck','Jasmine','Pryce','Clair','Will','Koga','Bruno','Karen','Lance','LtSurge','Sabrina','Erika','Janine','Misty','Brock','Blaine','Blue','Red']:
    show(g)




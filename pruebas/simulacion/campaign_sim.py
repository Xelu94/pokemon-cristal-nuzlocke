"""Balance simulation: every major trainer fought at its level cap by random
6-Pokemon teams (appropriately evolved), played by a move-scoring bot."""
from rutas import SRC, WORK, V42  # noqa: F401
import sys, re, json, random, time, zlib, multiprocessing as mp
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = SRC

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())

def load_world():
    ids = {}
    for m in re.finditer(r'^\s*const (\w+)\s*; ([0-9a-f]{2})\s*$', (ROOT / 'constants/pokemon_constants.asm').read_text(encoding='utf8'), re.M):
        ids[m[1]] = int(m[2], 16)
    evos = (ROOT / 'data/pokemon/evos_attacks.asm').read_text(encoding='utf8')
    children = {}
    parent = {}
    for name, body in re.findall(r'^(\w+)EvosAttacks:\n(.*?)(?=^\w+EvosAttacks:|\Z)', evos, re.M | re.S):
        n = norm(name)
        for line in body.splitlines():
            m = re.match(r'\s*db (EVOLVE_\w+),\s*(.*)', line)
            if not m: continue
            parts = [p.strip() for p in m[2].split(',')]
            kind = m[1]
            lvl = int(parts[0]) if kind in ('EVOLVE_LEVEL', 'EVOLVE_STAT') else 20
            tgt = norm(parts[-1])
            children.setdefault(n, []).append((tgt, lvl, kind))
            parent[tgt] = (n, lvl)
    return ids, children, parent

def eligible(cap, ids, children, parent):
    legend = {'ARTICUNO','ZAPDOS','MOLTRES','MEWTWO','MEW','RAIKOU','ENTEI','SUICUNE','LUGIA','HOOH','CELEBI','UNOWN','EGG'}
    out = []
    for name, i in ids.items():
        n = norm(name)
        if n in legend or not (1 <= i <= 251):
            continue
        lvl = 1; sp = n
        while sp in parent:
            sp, l = parent[sp]; lvl = max(lvl, l)
        if lvl > cap:
            continue
        kids = [k for k in children.get(n, []) if k[2] in ('EVOLVE_LEVEL', 'EVOLVE_STAT') and k[1] <= cap]
        if kids:
            continue  # a real player would have evolved it already
        out.append(i)
    return out

CAPS = [19, 24, 29, 35, 40, 44, 48, 53, 65, 67, 70, 73, 75, 77, 80, 83, 85, 95, 100]
def stage_for_cap(cap):
    k = CAPS.index(cap)
    if k < 8:   return ((1 << k) - 1, 0), False, False
    if k == 8:  return (255, 0), False, False
    if k == 9:  return (255, 0), True, False
    if k <= 16: return (255, (1 << (k - 9)) - 1), True, False
    if k == 17: return (255, 255), True, False
    return (255, 255), True, True

def base_stat_totals():
    rom = (ROOT / 'pokecristal.gbc').read_bytes()
    sym = {}
    for line in (ROOT / 'pokecristal.sym').read_text().splitlines():
        m = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
        if m: sym[m[3]] = (int(m[1], 16), int(m[2], 16))
    b, p = sym['BaseData']
    base = b * 16384 + p - 16384
    return {i: sum(rom[base + (i - 1) * 32 + 1: base + (i - 1) * 32 + 7]) for i in range(1, 252)}

def build_tasks(trials, modes=('random', 'strong')):
    parties = json.load(open(str(WORK / 'parties.json'), encoding='utf8'))
    order = re.findall(r'dw (\w+)Group', (ROOT / 'data/trainers/party_pointers.asm').read_text(encoding='utf8'))
    cls = {name: i + 1 for i, name in enumerate(order)}
    bosses = []
    def add(label, group, tid, cap, win='Route31SignText'):
        bosses.append(dict(label=label, cls=cls[group], tid=tid, cap=cap, win=win))
    leaders = [('PEGASO', 'Falkner', 19), ('ANTON', 'Bugsy', 24), ('BLANCA', 'Whitney', 29), ('MORTI', 'Morty', 35),
               ('ANIBAL', 'Chuck', 40), ('YASMINA', 'Jasmine', 44), ('FREDO', 'Pryce', 48), ('DEBORA', 'Clair', 53),
               ('MENTO(Will)', 'Will', 65), ('KOGA', 'Koga', 65), ('BRUNO', 'Bruno', 65), ('KAREN', 'Karen', 65),
               ('LANCE(Campeon)', 'Champion', 65), ('SURGE', 'LtSurge', 67), ('SABRINA', 'Sabrina', 70), ('ERIKA', 'Erika', 73),
               ('SACHIKO', 'Janine', 75), ('MISTY', 'Misty', 77), ('BROCK', 'Brock', 80), ('BLAINE', 'Blaine', 83),
               ('AZUL', 'Blue', 85), ('ROJO', 'Red', 95)]
    for label, group, cap in leaders:
        for tid in range(1, len(parties[group]) + 1):
            add(label if len(parties[group]) == 1 else '%s#%d' % (label, tid), group, tid, cap)
    add('TITO XELUIS', 'TitoXeluis', 1, 100, win='TitoXeluisBattleScript.Defeated')
    for k in range(19):
        add('ULEX equipo %02d' % (k + 1), 'Ulex', k + 1, CAPS[k], win='UlexBattleScript.WinText')
    for group in ('Rival1', 'Rival2'):
        for tid, t in enumerate(parties[group], 1):
            mx = max(l for l, _, _ in t['mons'])
            cap = next((c for c in CAPS if c >= mx), 100)
            add('%s#%d (nivel max %d)' % (group, tid, mx), group, tid, cap)
    ids, children, parent = load_world()
    bst = base_stat_totals()
    tasks = []
    for b in bosses:
        pool = eligible(b['cap'], ids, children, parent)
        strong = sorted(pool, key=lambda s: -bst[s])[:max(12, len(pool) // 3)]
        for mode in modes:
            for i in range(trials):
                rng = random.Random(zlib.crc32(('%s|%s|%d' % (b['label'], mode, i)).encode()))
                team = rng.sample(pool if mode == 'random' else strong, 6)
                tasks.append((dict(b, mode=mode), team, i))
    return tasks

def run(task):
    from simlib import arena_fight
    b, team, i = task
    badges, hof, red = stage_for_cap(b['cap'])
    try:
        r = arena_fight(b['cls'], b['tid'], team, b['cap'], badges=badges, hof=hof, red=red, win=b['win'], seed=i, max_iter=9000)
    except Exception as e:
        r = {'error': repr(e)}
    r.update(label=b['label'], cap=b['cap'], team=team, trial=i, mode=b['mode'])
    return r

if __name__ == '__main__':
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    outfile = sys.argv[3] if len(sys.argv) > 3 else str(WORK / 'campaign_results.json')
    tasks = build_tasks(trials)
    print('fights', len(tasks), flush=True)
    t0 = time.time()
    out = []
    with mp.Pool(procs) as pool:
        for n, r in enumerate(pool.imap_unordered(run, tasks, chunksize=2), 1):
            out.append(r)
            if n % 100 == 0:
                print(n, round(time.time() - t0), 's', flush=True)
    json.dump(out, open(outfile, 'w'), indent=1)
    print('done', round(time.time() - t0), 's')


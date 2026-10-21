from rutas import SRC, WORK, V42  # noqa: F401
import json, sys, collections
f = sys.argv[1] if len(sys.argv) > 1 else str(WORK / 'campaign_v1.json')
rs = json.load(open(f))
print('fights', len(rs), 'errors', sum('error' in r for r in rs))
agg = collections.OrderedDict()
for r in sorted(rs, key=lambda r: (r['cap'], r['label'])):
    if 'error' in r: continue
    key = (r['cap'], r['label'])
    a = agg.setdefault(key, {})
    m = a.setdefault(r['mode'], {'n': 0, 'win': 0, 'stall': 0, 'alive': 0, 'turns': 0, 'hp': 0})
    m['n'] += 1
    if not r['finished']:
        m['stall'] += 1
    elif r['won']:
        m['win'] += 1
        m['alive'] += r['alive']; m['hp'] += r['hp_pct']
    m['turns'] += r['turns']
print('cap  boss                      random(win%/alive/hp%)   strong(win%/alive/hp%)  stalls')
for (cap, label), a in agg.items():
    cells = []
    stalls = 0
    for mode in ('random', 'strong'):
        m = a.get(mode)
        if not m: cells.append('-'); continue
        w = m['win']
        cells.append('%3d%% %3.1f %4.0f%%' % (100 * w / m['n'], m['alive'] / w if w else 0, m['hp'] / w if w else 0))
        stalls += m['stall']
    print('%3d  %-24s  %-22s  %-22s  %d' % (cap, label[:24], cells[0], cells[1], stalls))
tot = collections.defaultdict(lambda: [0, 0])
for r in rs:
    if 'error' in r or not r['finished']: continue
    tot[r['mode']][0] += 1; tot[r['mode']][1] += bool(r['won'])
print({k: (v[1], v[0], round(100 * v[1] / v[0], 1)) for k, v in tot.items()})

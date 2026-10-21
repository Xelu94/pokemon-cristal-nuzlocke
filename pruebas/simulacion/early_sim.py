from rutas import SRC, WORK, V42  # noqa: F401
import sys, json, time, multiprocessing as mp
sys.path.insert(0, str(Path(__file__).resolve().parent))
from campaign_sim import *

def run2(task):
    from simlib import arena_fight
    b, team, i, size = task
    badges, hof, red = stage_for_cap(b['cap'])
    try:
        r = arena_fight(b['cls'], b['tid'], team[:size], b['cap'], badges=badges, hof=hof, red=red, win=b['win'], seed=i, max_iter=9000)
    except Exception as e:
        r = {'error': repr(e)}
    r.update(label=b['label'], cap=b['cap'], team=team[:size], trial=i, mode=b['mode'], size=size)
    return r

if __name__ == '__main__':
    labels = {'PEGASO', 'ANTON', 'BLANCA', 'MORTI', 'ANIBAL', 'YASMINA'}
    tasks = []
    for b, team, i in build_tasks(30):
        if b['label'] in labels:
            for size in (2, 3, 4):
                tasks.append((b, team, i, size))
    print('fights', len(tasks), flush=True)
    t0 = time.time()
    out = []
    with mp.Pool(10) as pool:
        for n, r in enumerate(pool.imap_unordered(run2, tasks, chunksize=2), 1):
            out.append(r)
    json.dump(out, open(str(WORK / 'early_results.json'), 'w'))
    import collections
    agg = collections.defaultdict(lambda: [0, 0, 0])
    for r in out:
        if 'error' in r: continue
        k = (r['cap'], r['label'], r['size'], r['mode'])
        agg[k][0] += 1
        agg[k][1] += bool(r.get('won'))
        agg[k][2] += (not r.get('finished')) and not r.get('lost') and not r.get('won')
    print('cap boss size mode win% stalls')
    for k in sorted(agg):
        n, w, st = agg[k]
        print(k[0], k[1], k[2], k[3], '%d%%' % round(100 * w / n), st)
    print('done', round(time.time() - t0), 's')

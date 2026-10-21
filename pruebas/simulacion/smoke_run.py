import sys, re, json, subprocess, time
from rutas import SRC, WORK, V42  # noqa: F401
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke_maps import catalog
PY = sys.executable
def run(e):
    gi, num, x, y, name = e
    try:
        p = subprocess.run([PY, '-I', str(WORK / 'smoke_one.py'), str(gi), str(num), str(x), str(y), name], capture_output=True, text=True, timeout=45)
        for line in p.stdout.splitlines():
            if line.startswith('RESULT'):
                return json.loads(line[6:])
        return {'map': name, 'error': 'no result', 'stderr': p.stderr[-200:]}
    except subprocess.TimeoutExpired:
        return {'map': name, 'group': gi, 'num': num, 'error': 'HANG (45 s timeout)'}
cat = catalog()
t0 = time.time()
with ThreadPoolExecutor(2) as ex:
    out = list(ex.map(run, cat))
json.dump(out, open(str(WORK / 'smoke_maps.json'), 'w'), indent=1)
bad = [r for r in out if 'error' in r or not r.get('loaded') or r.get('pc_bad') or r.get('colors', 9) <= 1]
print('done', len(out), 'problems', len(bad), round(time.time() - t0), 's')
for r in bad[:50]:
    print(r)

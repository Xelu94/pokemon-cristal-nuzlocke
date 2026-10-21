"""Load every map of the sandbox catalog on the normal ROM and exercise it briefly."""
from rutas import SRC, WORK, V42  # noqa: F401
import sys, re, io, json, random, time, multiprocessing as mp
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = SRC

def catalog():
    maps = {}
    group = number = 0
    names = {}
    for line in (ROOT / 'constants/map_constants.asm').read_text(encoding='utf8').splitlines():
        if re.match(r'\s*newgroup ', line): group += 1; number = 0
        m = re.match(r'\s*map_const (\w+)', line)
        if m: number += 1; names[(group, number)] = m[1]
    text = (ROOT / 'engine/debug/sandbox_any_map_data.asm').read_text(encoding='utf8')
    out = []
    for gi, body in re.findall(r'\.Group(\d+)\n(.*?)(?=\n\.Group|\Z)', text, re.S):
        gi = int(gi)
        for m in re.finditer(r'^\s*db (\d+), (\d+), (\d+), PLAYER_\w+\s*; (\w+)', body, re.M):
            out.append((gi, int(m[1]), int(m[2]), int(m[3]), m[4]))
    return out

def one(entry):
    from harness import Game, ROOT as HROOT
    gi, num, x, y, name = entry
    import harness
    harness.maps[name] = [gi, num]
    res = {'map': name, 'group': gi, 'num': num}
    try:
        g = Game(name, x, y)
        g.p.tick(90)
        res['loaded'] = g.mem('wMapGroup', 2) == [gi, num]
        pcs = []
        random.seed(hash(name) & 0xffff)
        start = (g.read('wXCoord'), g.read('wYCoord'))
        moved = False
        for step in range(24):
            g.press(random.choice(['up', 'down', 'left', 'right']), 4, hold=20)
            pcs.append(g.p.register_file.PC)
            if (g.read('wXCoord'), g.read('wYCoord')) != start:
                moved = True
        g.p.tick(30)
        img = g.p.screen.image.convert('L')
        colors = len(set(img.getdata()))
        res.update(moved=moved, still_in_map=g.mem('wMapGroup', 2) == [gi, num], colors=colors,
                   pc_bad=sum(1 for pc in pcs if pc >= 0xC000 and pc < 0xFF00), wram_pc=[hex(p) for p in pcs if 0x8000 <= p < 0xFF80][:3])
        g.close()
    except Exception as e:
        res['error'] = repr(e)
    return res

if __name__ == '__main__':
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cat = catalog()
    print('maps', len(cat), flush=True)
    t0 = time.time()
    out = []
    with mp.Pool(procs) as pool:
        for n, r in enumerate(pool.imap_unordered(one, cat, chunksize=4), 1):
            out.append(r)
            if n % 50 == 0:
                print(n, round(time.time() - t0), 's', flush=True)
    json.dump(out, open(str(WORK / 'smoke_maps.json'), 'w'), indent=1)
    bad = [r for r in out if 'error' in r or not r.get('loaded') or r.get('pc_bad') or r.get('colors', 9) <= 1]
    print('done', len(out), 'problems', len(bad))
    for r in bad[:40]:
        print(r)

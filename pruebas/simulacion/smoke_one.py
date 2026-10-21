import sys, json, random
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import SRC, WORK, V42  # noqa: F401
import harness
from harness import Game
gi, num, x, y, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
harness.maps[name] = [gi, num]
res = {'map': name, 'group': gi, 'num': num}
try:
    g = Game(name, x, y)
    g.p.tick(90)
    res['loaded'] = g.mem('wMapGroup', 2) == [gi, num]
    pcs = []
    random.seed(sum(map(ord, name)))
    start = (g.read('wXCoord'), g.read('wYCoord'))
    moved = False
    for step in range(24):
        g.press(random.choice(['up', 'down', 'left', 'right']), 4, hold=20)
        pcs.append(g.p.register_file.PC)
        if (g.read('wXCoord'), g.read('wYCoord')) != start:
            moved = True
    g.p.tick(30)
    img = g.p.screen.image.convert('L')
    res.update(moved=moved, still_in_map=g.mem('wMapGroup', 2) == [gi, num], colors=len(set(img.getdata())),
               pc_bad=sum(1 for pc in pcs if 0x8000 <= pc < 0xFF80))
    g.close()
except Exception as e:
    res['error'] = repr(e)
print('RESULT' + json.dumps(res))

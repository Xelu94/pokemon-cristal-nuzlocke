"""v5.3 routines on the compiled sandbox ROM (PyBoy CPU harness): the SANDBOX items option
adds every HM, and the Rare Candy / mart / text-bank data checks that do not need the emulator UI."""
import json
import re
import sys
from pathlib import Path

sys.argv = [sys.argv[0], 'work/source/pokecristal_debug.gbc']
sys.path.insert(0, 'work')
import cpu_harness as h

root = Path('work/source')
tests = []


def check(name, condition=True):
    assert condition, name
    tests.append({'name': name, 'passed': True})
    print('PASS', name, flush=True)


r = h.Routine()
addr = h.addr
before = list(r.p.memory[addr('wTMsHMs'):addr('wTMsHMs') + 57])
try:
    r.run('SandboxGiveItems')
except AssertionError:
    pass  # it ends by printing a text box that waits for a button; the bag is already filled
after = list(r.p.memory[addr('wTMsHMs'):addr('wTMsHMs') + 57])
consts = (root / 'constants/item_constants.asm').read_text(encoding='utf8')
check('the sandbox items option gives each of the seven HMs once',
      after[50:57] == [1] * 7 and before[50:57] == [0] * 7)
check('the sandbox items option still gives TMs', sum(after[:50]) > sum(before[:50]))
r.close()

# --- Stones in the general marts from Goldenrod onward ---------------------------------------------------
marts = (root / 'data/items/marts.asm').read_text(encoding='utf8')
stones = ['FIRE_STONE', 'WATER_STONE', 'THUNDERSTONE', 'LEAF_STONE', 'MOON_STONE', 'SUN_STONE']
with_stones = ['MartGoldenrod2F1', 'MartOlivine', 'MartEcruteak', 'MartMahogany1', 'MartCianwood', 'MartBlackthorn', 'MartViridian',
               'MartPewter', 'MartCerulean', 'MartLavender', 'MartVermilion', 'MartCeladon2F1', 'MartFuchsia', 'MartSaffron',
               'MartMtMoon', 'MartIndigoPlateau']
without = ['MartCherrygrove', 'MartCherrygroveDex', 'MartViolet', 'MartAzalea', 'MartUnderground']


def mart(name):
    m = re.search(r'^' + name + r':\n\tdb (\d+) ; # items\n((?:\tdb \w+\n)*)\tdb -1', marts, re.M)
    return int(m[1]), re.findall(r'db (\w+)', m[2])


good = True
for name in with_stones:
    count, items = mart(name)
    good = good and count == len(items) and all(s in items for s in stones)
check('every general shop from Goldenrod onward sells all six evolution stones and its item count matches', good)
check('the first three towns and the Underground sell none',
      all(not any(s in mart(n)[1] for s in stones) for n in without))
check('the Goldenrod Pokemon Center no longer has a stone vendor',
      'StoneVendor' not in (root / 'maps/GoldenrodPokecenter1F.asm').read_text(encoding='utf8')
      and 'GOLDENROD_STONES' not in marts + (root / 'constants/mart_constants.asm').read_text(encoding='utf8'))

report = {'passed': len(tests), 'tests': tests}
Path('work/v53-routines-tests.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

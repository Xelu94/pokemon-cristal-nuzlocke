"""v4.4 interface changes on the real ROM: level cap on the stats page, move category
icons, Tito's idle animation and the redrawn pocket labels."""
import io
import json
import re
from pathlib import Path
from pyboy import PyBoy

base = Path('work/test-v43-changes.py').read_text(encoding='utf8')
exec(base[:base.index('# --- Starting inventory')])   # check(), maps, items and Game

# charmap values used below
T, O, P, E = 0x93, 0x8e, 0x8f, 0x84


def screen_rows(game):
    tilemap = game.mem('wTilemap', 360)
    return [tilemap[i * 20:(i + 1) * 20] for i in range(18)]


# --- Level cap on the stats page ---------------------------------------------
g = Game('ROUTE_31', 21, 14)
g.party([152, 6], level=30)
for n in range(2):   # nicknames: the stats page prints them
    at = g.a('wPartyMonNicknames') + 11 * n
    g.p.memory[at:at + 11] = [0x93, 0x84, 0x92, 0x93, 0x50, 0, 0, 0, 0, 0, 0]
g.write('wJohtoBadges', 1)          # one badge: cap 24
g.press('start', 40)
g.press('a', 40)
g.press('a', 40)
g.press('a', 80)
g.p.tick(120)
g.p.screen.image.save('work/v44-stats-cap.png')
rows = screen_rows(g)
check('the stats page prints TOPE and the level cap (24 with one badge) on its bottom row',
      rows[17][10:14] == [T, O, P, E] and rows[17][16:18] == [0xf6 + 2, 0xf6 + 4])
g.close()

# --- Move category icons ------------------------------------------------------
class Arena(Game):
    def __init__(self):
        rom = root/'pokecristal.gbc'
        self.symbols = {}
        for line in rom.with_suffix('.sym').read_text().splitlines():
            match = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
            if match:
                self.symbols[match[3]] = int(match[1], 16), int(match[2], 16)
        self.rom = bytearray(rom.read_bytes())
        data = bytearray(self.rom)
        for name in ['PlayerProfileSetup', 'OakSpeech', 'ShrinkPlayer', '_InitializeStartDay']:
            data[self.offset(name)] = 0xc9
        data[self.offset('Route31CheckMomCallCallback')] = 0x90
        spawn = self.offset('SpawnPoints')
        data[spawn:spawn+4] = bytes(maps['ROUTE_31'] + [21, 14])
        ptr = self.symbols['Route31SignText'][1]
        script = [0x5e, 1, 1, 0x64, ptr & 0xff, ptr >> 8, ptr & 0xff, ptr >> 8, 0x5f, 0x60, 0x91]  # loadtrainer FALKNER, startbattle
        at = self.offset('Route31Ulex')
        data[at:at + len(script)] = bytes(script)
        self.p = PyBoy(io.BytesIO(data), window='null', sound_emulated=False, log_level='ERROR')
        self.p.set_emulation_speed(0)
        self.counts = {}
        self.p.tick(360)
        self.press('start', 120)
        self.press('start', 120)
        self.p.button_press('a'); self.p.tick(32); self.p.button_release('a'); self.p.tick(300)
        self.write('wOptions', (self.read('wOptions') & 0x38) | 0x41)
        self.p.tick(60)


g = Arena()
g.party([152, 6])
for n in range(2):
    at = g.a('wPartyMonNicknames') + 11 * n
    g.p.memory[at:at + 11] = [0x93, 0x84, 0x92, 0x93, 0x50, 0, 0, 0, 0, 0, 0]
moves = [33, 52, 73, 45]       # Tackle (physical), Ember (special), Leech Seed (status), Growl (status)
base_moves = g.a('wPartyMon1Moves')
g.p.memory[base_moves:base_moves + 4] = moves
g.p.memory[g.a('wPartyMon1PP'):g.a('wPartyMon1PP') + 4] = [35, 25, 10, 40]
hits = {'move': 0, 'menu': 0}
g.p.hook_register(*g.symbols['MoveSelectionScreen'], lambda _: hits.__setitem__('move', hits['move'] + 1), None)
g.p.hook_register(*g.symbols['LoadBattleMenu'], lambda _: hits.__setitem__('menu', hits['menu'] + 1), None)
g.press('up', 20, hold=6)
for _ in range(400):
    if hits['menu']:
        break
    g.press('a', 40, hold=2)
g.press('a', 60, hold=4)              # FIGHT
icons = []
for index in range(3):
    g.p.tick(40)
    icons.append(screen_rows(g)[13][2])
    g.p.screen.image.save('work/v44-move-icon-%d.png' % index)
    g.press('down', 20, hold=6)
b, p_ = g.symbols['MoveCategoryIconsGFX']
rom_icons = bytes(g.rom[b * 16384 + p_ - 16384: b * 16384 + p_ - 16384 + 48])
vram = bytes(g.p.memory[0, 0x9000 + 89 * 16 + i] for i in range(48))
check('the move panel shows a physical, a special and a status icon in its category column',
      icons == [89, 90, 91] and vram == rom_icons)
# The icons borrow the experience bar tiles: once the move is used the bar must be restored.
g.press('a', 60, hold=4)
for _ in range(60):
    g.press('a', 30, hold=4)
    g.p.tick(10)
exp_bank, exp_ptr = g.symbols['ExpBarGFX']
exp_offset = exp_bank * 16384 + exp_ptr - 16384 + 4 * 16
rom_bar = bytes(g.rom[exp_offset:exp_offset + 48])
vram_now = bytes(g.p.memory[0, 0x9000 + 89 * 16 + i] for i in range(48))
check('after a turn the experience bar tiles are restored in VRAM', vram_now == rom_bar and vram_now != rom_icons)
g.close()

# --- Pocket labels (captures)
g = Game('ROUTE_31', 21, 14)
g.press('start', 40)
g.press('a', 60)
for n in range(8):
    g.p.screen.image.save('work/v44-bag-%d-pocket%d-cat%d.png' % (n, g.read('wCurPocket'), g.read('wBagCategory')))
    g.press('right', 20)
g.close()

# --- Tito breathes ---------------------------------------------------------
g = Game('CHERRYGROVE_POKECENTER_1F', 6, 7)
g.p.tick(60)
screens = {}
for _ in range(140):
    g.p.tick(2)
    image = g.p.screen.image.convert('RGB')
    screens.setdefault(image.tobytes(), image)
for n, image in enumerate(screens.values()):
    image.save('work/v44-tito-idle-%d.png' % n)
check('Tito shows two different frames while he stands still', len(screens) == 2)
g.close()

report = {'passed': len(tests), 'tests': tests}
Path('work/v44-changes-tests.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

"""Save made by the published v4.2 ROM, loaded by the v4.3 ROM."""
from rutas import SRC, WORK, V42  # noqa: F401
import sys, io, re, shutil, os
from pathlib import Path
from pyboy import PyBoy

OUT = (WORK / 'caps')
W = (WORK / 'mig'); W.mkdir(exist_ok=True)

def symbols(rom):
    sym = {}
    for line in Path(rom).with_suffix('.sym').read_text().splitlines():
        m = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
        if m: sym[m[3]] = (int(m[1], 16), int(m[2], 16))
    return sym

def patched_copy(rom, name):
    sym = symbols(rom)
    data = bytearray(Path(rom).read_bytes())
    def off(n):
        b, p = sym[n]; return b * 16384 + p - 16384 if b else p
    for n in ['PlayerProfileSetup', 'OakSpeech', 'ShrinkPlayer', '_InitializeStartDay']:
        data[off(n)] = 0xc9
    data[off('Route31CheckMomCallCallback')] = 0x90
    maps = {}; group = number = 0
    for line in (SRC / 'constants/map_constants.asm').read_text(encoding='utf8').splitlines():
        if re.match(r'\s*newgroup ', line): group += 1; number = 0
        m = re.match(r'\s*map_const (\w+)', line)
        if m: number += 1; maps[m[1]] = [group, number]
    sp = off('SpawnPoints'); data[sp:sp + 4] = bytes(maps['ROUTE_31'] + [21, 14])
    path = W / name
    path.write_bytes(bytes(data))
    return path, sym

def boot(path):
    p = PyBoy(str(path), window='null', sound_emulated=False, log_level='ERROR')
    p.set_emulation_speed(0)
    return p

def A(sym, n): return sym[n][1]
def press(p, b, frames=20, hold=8):
    p.button_press(b); p.tick(hold); p.button_release(b); p.tick(frames)

# 1. v4.2: new game, save through the real SAVE menu
for f in W.glob('*'): f.unlink()
path42, sym42 = patched_copy(str(V42 / 'pokecristal.gbc'), 'v42.gbc')
p = boot(path42)
p.tick(360); press(p, 'start', 120); press(p, 'start', 120)
p.button_press('a'); p.tick(32); p.button_release('a'); p.tick(300)
p.memory[A(sym42, 'wOptions')] = (p.memory[A(sym42, 'wOptions')] & 0x38) | 0x41
p.tick(60)
n = p.memory[A(sym42, 'wNumItems')]
items42 = [p.memory[A(sym42, 'wItems') + i] for i in range(n * 2)]
print('v4.2 items', n, items42, flush=True)
stride = A(sym42, 'wPartyMon2') - A(sym42, 'wPartyMon1')
p.memory[A(sym42, 'wPartyCount')] = 1
p.memory[A(sym42, 'wPartySpecies'):A(sym42, 'wPartySpecies') + 2] = [152, 255]
base = A(sym42, 'wPartyMon1')
p.memory[base:base + stride] = [0] * stride
p.memory[base] = 152
p.memory[A(sym42, 'wPartyMon1Level')] = 30
for stat in ['HP', 'MaxHP']:
    p.memory[A(sym42, 'wPartyMon1' + stat):A(sym42, 'wPartyMon1' + stat) + 2] = [0, 90]
press(p, 'start', 40)
for _ in range(3):
    press(p, 'down', 12)
press(p, 'a', 40)
for _ in range(4):
    press(p, 'a', 80)
p.tick(300)
p.screen.image.save(OUT / 'mig_saved42.png')
p.stop(save=True)
ram = W / 'v42.gbc.ram'
print('SRAM file', ram.exists() and ram.stat().st_size, 'non-zero', sum(1 for b in ram.read_bytes() if b) if ram.exists() else 0, flush=True)

# 2. v4.3 ROM loads the same save
sym43 = symbols(str(SRC / 'pokecristal.gbc'))
raw43 = W / 'v43raw.gbc'
shutil.copy(str(SRC / 'pokecristal.gbc'), raw43)
shutil.copy(ram, W / 'v43raw.gbc.ram')
p = boot(raw43)
p.tick(500)
for i in range(70):
    press(p, 'a', 30, hold=4)
    if i == 10:
        p.screen.image.save(OUT / 'mig_loaded43_a.png')
p.tick(200)
n = p.memory[A(sym43, 'wNumItems')]
items43 = [p.memory[A(sym43, 'wItems') + i] for i in range(n * 2)]
print('v4.3 items', n, items43, flush=True)
print('party', p.memory[A(sym43, 'wPartyCount')], p.memory[A(sym43, 'wPartySpecies')], 'level', p.memory[A(sym43, 'wPartyMon1Level')])
print('map', p.memory[A(sym43, 'wMapGroup')], p.memory[A(sym43, 'wMapNumber')], 'xy', p.memory[A(sym43, 'wXCoord')], p.memory[A(sym43, 'wYCoord')])
p.screen.image.save(OUT / 'mig_loaded43.png')
print('identical item list:', items42 == items43)
p.stop(save=False)

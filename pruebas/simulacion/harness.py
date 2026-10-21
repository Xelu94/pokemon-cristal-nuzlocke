"""Small PyBoy harness for v4.3 checks (intro skipped, spawn at any map)."""
from rutas import SRC, WORK, V42  # noqa: F401
import io, re, sys
from pathlib import Path
from pyboy import PyBoy

ROOT = SRC
OUT = (WORK / 'caps')

maps = {}
group = number = 0
for line in (ROOT / 'constants/map_constants.asm').read_text(encoding='utf8').splitlines():
    if re.match(r'\s*newgroup ', line):
        group += 1
        number = 0
    m = re.match(r'\s*map_const (\w+)', line)
    if m:
        number += 1
        maps[m[1]] = [group, number]


class Game:
    def __init__(self, mapname='ROUTE_31', x=21, y=14, debug=False, rom=None, setup=None, patches=None, settle=True):
        rom = Path(rom) if rom else ROOT / ('pokecristal_debug.gbc' if debug else 'pokecristal.gbc')
        self.symbols = {}
        for line in rom.with_suffix('.sym').read_text().splitlines():
            m = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
            if m:
                self.symbols[m[3]] = int(m[1], 16), int(m[2], 16)
        data = bytearray(rom.read_bytes())
        for name in (patches or ['PlayerProfileSetup', 'OakSpeech', 'ShrinkPlayer', '_InitializeStartDay']):
            data[self.offset(name)] = 0xc9
        if 'Route31CheckMomCallCallback' in self.symbols:
            data[self.offset('Route31CheckMomCallCallback')] = 0x90
        spawn = self.offset('SpawnPoints')
        data[spawn:spawn + 4] = bytes(maps[mapname] + [x, y])
        self.p = PyBoy(io.BytesIO(data), window='null', sound_emulated=False, log_level='ERROR')
        self.p.set_emulation_speed(0)
        self.p.tick(360)
        self.press('start', 120)
        self.press('start', 120)
        self.p.button_press('a'); self.p.tick(32); self.p.button_release('a'); self.p.tick(300)
        if not settle:
            return
        self.write('wOptions', (self.read('wOptions') & 0x38) | 0x41)
        if setup:
            setup(self)

    def a(self, name): return self.symbols[name][1]
    def offset(self, name):
        bank, pointer = self.symbols[name]
        return bank * 16384 + pointer - 16384 if bank else pointer
    def read(self, name): return self.p.memory[self.a(name)]
    def write(self, name, value): self.p.memory[self.a(name)] = value
    def mem(self, name, n): return list(self.p.memory[self.a(name):self.a(name) + n])
    def flag(self, n): return bool(self.p.memory[self.a('wEventFlags') + n // 8] & (1 << (n % 8)))
    def press(self, button='a', frames=30, hold=8):
        self.p.button_press(button); self.p.tick(hold)
        self.p.button_release(button); self.p.tick(frames)
    def snap(self, name):
        path = OUT / (name + '.png')
        self.p.screen.image.save(path)
        return str(path)
    def close(self): self.p.stop(save=False)




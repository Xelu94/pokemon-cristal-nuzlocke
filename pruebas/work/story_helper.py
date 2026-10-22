"""Shared helpers for the v4.5 story tests: event flags, bag, party and text-driven advancing."""
import re
from pathlib import Path

root = Path('work/source')


def parse_flags(path):
    flags = {}
    index = 0
    for line in (root / path).read_text(encoding='utf8').splitlines():
        line = line.split(';')[0].strip()
        if not line:
            continue
        m = re.match(r'const_next (\d+)', line)
        if m:
            index = int(m[1])
            continue
        if line.startswith('const_def'):
            index = 0
            continue
        m = re.match(r'const_skip(?: (\d+))?', line)
        if m:
            index += int(m[1] or 1)
            continue
        m = re.match(r'const (\w+)$', line)
        if m:
            flags[m[1]] = index
            index += 1
    return flags


EVENTS = parse_flags('constants/event_flags.asm')


class StoryMixin:
    def event_addr(self, name):
        i = EVENTS[name]
        return self.a('wEventFlags') + i // 8, i % 8

    def set_event(self, name, value=True):
        addr, bit = self.event_addr(name)
        byte = self.p.memory[addr]
        self.p.memory[addr] = (byte | (1 << bit)) if value else (byte & ~(1 << bit) & 0xff)

    def event(self, name):
        addr, bit = self.event_addr(name)
        return bool(self.p.memory[addr] & (1 << bit))

    def party_species(self):
        n = self.read('wPartyCount')
        return self.mem('wPartySpecies', n)

    def mon_dvs(self, i):
        stride = self.a('wPartyMon2') - self.a('wPartyMon1')
        base = self.a('wPartyMon1DVs') + stride * i
        return list(self.p.memory[base:base + 2])

    def is_shiny(self, i):
        atk_def, spd_spc = self.mon_dvs(i)
        return spd_spc == 0xaa and (atk_def >> 4) in (2, 3, 6, 7, 10, 11, 14, 15) and (atk_def & 0xf) == 10

    def pos(self):
        return self.read('wXCoord'), self.read('wYCoord')

    def screen_text(self):
        """Characters of wTilemap decoded with the game charmap (letters and digits only)."""
        raw = self.mem('wTilemap', 360)
        out = []
        for row in range(18):
            line = ''
            for t in raw[row * 20:(row + 1) * 20]:
                line += CHARS.get(t, ' ')
            out.append(line.rstrip())
        return out

    def advance_text(self, n=1, frames=30):
        for _ in range(n):
            self.press('a', frames, hold=4)


CHARS = {}
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    CHARS[0x80 + i] = c
for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
    CHARS[0xa0 + i] = c
for i in range(10):
    CHARS[0xf6 + i] = str(i)
CHARS[0x7f] = ' '

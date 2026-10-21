"""Run the modified LR35902 routines, not a reimplementation of the damage rules.

Usage: python work/test-split.py work/split/pokecristal.gbc
Requires PyBoy 2.8+. Never writes game saves.
"""
import io
import json
import re
import sys
from pathlib import Path

from pyboy import PyBoy

ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'source/pokecristal.gbc'
symbols = {}
for line in ROM.with_suffix('.sym').read_text().splitlines():
    match = re.match(r'([0-9a-fA-F]+):([0-9a-fA-F]+)\s+(\S+)', line)
    if match:
        symbols[match[3]] = (int(match[1], 16), int(match[2], 16))


def addr(name):
    return symbols[name][1]


class Routine:
    def __init__(self):
        self.p = PyBoy(io.BytesIO(ROM.read_bytes()), window='null', sound_emulated=False,
                       log_level='ERROR')
        self.p.set_emulation_speed(0)
        self.result = None
        self.pending = None
        self.p.hook_register(0, 0x100, self.start, None)
        self.p.hook_register(0, 0x102, self.finish, None)
        # Once a routine returns, spin without touching registers or game memory.
        self.p.memory[0, 0x104] = 0x18
        self.p.memory[0, 0x105] = 0xFE

    def write(self, name, value):
        self.p.memory[addr(name)] = value

    def word(self, name, value):
        # Pokemon battle stats and current damage are big endian.
        self.p.memory[addr(name)] = value >> 8
        self.p.memory[addr(name) + 1] = value & 0xFF

    def read_word(self, name):
        return self.p.memory[addr(name)] * 256 + self.p.memory[addr(name) + 1]

    def initialize(self):
        self.p.memory[0xC000:0xE000] = [0] * 0x2000
        self.p.memory[0xFF80:0xFFFF] = [0] * 0x7F
        self.p.memory[0xFF40] = 0  # LCD off; these routines require no renderer.
        self.p.memory[0xFFFF] = 0
        self.p.memory[0xFF0F] = 0
        self.write('hBattleTurn', 0)
        self.write('wBattleMonLevel', 50)
        self.write('wEnemyMonLevel', 50)
        for name, value in [('wBattleMonAttack', 40), ('wBattleMonSpclAtk', 160),
                            ('wEnemyMonAttack', 70), ('wEnemyMonSpclAtk', 180),
                            ('wEnemyMonDefense', 80), ('wEnemyMonSpclDef', 120),
                            ('wBattleMonDefense', 90), ('wBattleMonSpclDef', 130)]:
            self.word(name, value)
        for who in ['Player', 'Enemy']:
            for stat in ['Atk', 'Def', 'SAtk', 'SDef']:
                self.write('w' + who + stat + 'Level', 7)

    def start(self, _):
        routine, setup, registers = self.pending
        self.initialize()
        setup(self)
        self.p.memory[0xFF50] = 1  # Disable the CGB boot ROM before calling cartridge RST vectors.
        bank, pointer = symbols[routine]
        self.p.memory[0x2000] = bank or 1
        self.write('hROMBank', bank or 1)
        reg = self.p.register_file
        reg.SP = 0xDFF0
        self.p.memory[0xDFF0] = 0x02
        self.p.memory[0xDFF1] = 0x01
        reg.A = reg.F = reg.B = reg.C = reg.D = reg.E = 0
        reg.HL = 0
        for name, value in registers.items():
            setattr(reg, name, value)
        reg.PC = pointer

    def finish(self, _):
        r = self.p.register_file
        self.result = {name: getattr(r, name) for name in ['A', 'F', 'B', 'C', 'D', 'E', 'HL', 'SP']}
        r.PC = 0x104

    def run(self, name, setup=lambda r: None, **registers):
        self.result = None
        self.pending = name, setup, registers
        # First call starts at the entry hook after the emulator's boot ROM.
        if self.p.memory[0xFF50]:
            self.p.register_file.PC = 0x100
        for _ in range(160):
            self.p.tick(1, False, False)
            if self.result is not None:
                return self.result
        raise AssertionError('Routine did not return: ' + name)

    def close(self):
        self.p.stop(save=False)


def move_bytes(id):
    bank, pointer = symbols['Moves']
    data = ROM.read_bytes()
    offset = bank * 0x4000 + pointer - 0x4000 + (id - 1) * 7
    return list(data[offset:offset + 7])


def install_move(r, move, enemy=False):
    pointer = addr('wEnemyMoveStruct' if enemy else 'wPlayerMoveStruct')
    r.p.memory[pointer:pointer + 7] = move_bytes(move)

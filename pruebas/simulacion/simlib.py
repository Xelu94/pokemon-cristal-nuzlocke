"""Boss-battle simulator on the real ROM: builds parties with the game's own
routines, starts a trainer battle and plays it with a simple move-scoring bot."""
from rutas import SRC, WORK, V42  # noqa: F401
import io, re, random, json, sys
from pathlib import Path
from pyboy import PyBoy

ROOT = SRC
ROM = ROOT / 'pokecristal.gbc'

class Sim:
    def __init__(self, rom=ROM, state=None, arena=None, win='Route31SignText'):
        self.rom = Path(rom)
        self.data = bytearray(self.rom.read_bytes())
        self.sym = {}
        for line in self.rom.with_suffix('.sym').read_text().splitlines():
            m = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
            if m:
                self.sym[m[3]] = (int(m[1], 16), int(m[2], 16))
        d = bytearray(self.data)
        for name in ['PlayerProfileSetup', 'OakSpeech', 'ShrinkPlayer', '_InitializeStartDay']:
            d[self.off(name)] = 0xc9
        d[self.off('Route31CheckMomCallCallback')] = 0x90
        spawn = self.off('SpawnPoints')
        d[spawn:spawn+4] = bytes([26, 1] + [0, 0])  # placeholder, replaced below
        self.boot_data = d
        if arena:
            cls, tid = arena
            ptr = self.sym[win][1]
            o = self.off('Route31Ulex')
            script = [0x5e, cls, tid, 0x64, ptr & 0xff, ptr >> 8, ptr & 0xff, ptr >> 8, 0x5f, 0x60, 0x91]
            d[o:o + len(script)] = bytes(script)
        self.maps = self._maps()
        # spawn on Route 31 (21,14) like the other tests
        sp = self.off('SpawnPoints')
        self.boot_data[sp:sp+4] = bytes(self.maps['ROUTE_31'] + [21, 14])
        self.p = PyBoy(io.BytesIO(self.boot_data), window='null', sound_emulated=False, log_level='ERROR')
        self.p.set_emulation_speed(0)
        self.p.tick(360)
        self.press('start', 120); self.press('start', 120)
        self.p.button_press('a'); self.p.tick(32); self.p.button_release('a'); self.p.tick(300)
        self.write('wOptions', (self.read('wOptions') & 0x38) | 0x41)
        self.p.tick(60)
        # trap for routine returns
        self.ret_hit = False
        self.pending = None
        self.p.hook_register(0, 0x102, self._ret, None)
        self.p.hook_register(0, self.a('DelayFrame'), self._start, None)
        self.p.memory[0, 0x104] = 0x18; self.p.memory[0, 0x105] = 0xFE
        self.snap_state = io.BytesIO()
        self.p.save_state(self.snap_state)

    def _maps(self):
        maps = {}; group = number = 0
        for line in (ROOT / 'constants/map_constants.asm').read_text(encoding='utf8').splitlines():
            if re.match(r'\s*newgroup ', line): group += 1; number = 0
            m = re.match(r'\s*map_const (\w+)', line)
            if m: number += 1; maps[m[1]] = [group, number]
        return maps

    def off(self, name):
        b, p = self.sym[name]
        return b * 16384 + p - 16384 if b else p
    def a(self, name): return self.sym[name][1]
    def read(self, name, o=0): return self.p.memory[self.a(name) + o]
    def write(self, name, v, o=0): self.p.memory[self.a(name) + o] = v
    def mem(self, name, n): return list(self.p.memory[self.a(name):self.a(name) + n])
    def word(self, name):  # big endian
        return self.read(name) * 256 + self.read(name, 1)
    def press(self, button='a', frames=8, hold=4):
        self.p.button_press(button); self.p.tick(hold)
        self.p.button_release(button); self.p.tick(frames)

    def reload(self):
        self.snap_state.seek(0)
        self.p.load_state(self.snap_state)
        self.p.hook_register(0, 0x102, self._ret, None) if False else None

    # -- calling a game routine from the paused overworld ----------------------
    def _ret(self, _):
        # Restore the interrupted game state right here: the CPU is in normal code, so
        # interrupt-enable state is untouched (restoring at a frame boundary would
        # abandon a pending interrupt handler and leave IME off).
        self.ret_hit = True
        r = self.p.register_file
        self.out = {k: getattr(r, k) for k in ['A', 'F', 'B', 'C', 'D', 'E', 'HL']}
        saved = getattr(self, 'saved', None)
        if saved:
            for k, v in saved.items():
                setattr(r, k, v)
            self.p.memory[0x2000] = self.saved_bank or 1
            self.p.memory[self.a('hROMBank')] = self.saved_bank
            self.saved = None
        else:
            r.PC = 0x104
    def _start(self, _):
        # Runs at DelayFrame: normal code with interrupts enabled, so the called
        # routine (and its own DelayFrame/halt calls) behaves as it does in the game.
        if self.pending is None:
            return
        name, regs = self.pending
        self.pending = None
        r = self.p.register_file
        self.saved = {k: getattr(r, k) for k in ['A', 'F', 'B', 'C', 'D', 'E', 'HL', 'SP', 'PC']}
        self.saved_bank = self.p.memory[self.a('hROMBank')]
        bank = self.sym[name][0]
        sp = r.SP - 2
        self.p.memory[sp] = 0x02; self.p.memory[sp + 1] = 0x01
        r.SP = sp
        self.p.memory[0x2000] = bank or 1
        self.p.memory[self.a('hROMBank')] = bank or 1
        for k, v in regs.items():
            setattr(r, k, v)
        r.PC = self.sym[name][1]
        self.started = True
    def call(self, name, max_frames=40, driver=None, **regs):
        self.ret_hit = False
        self.started = False
        self.pending = (name, regs)
        for _ in range(10):
            self.p.tick(1, False, False)
            if self.started:
                break
        if not self.started:
            raise RuntimeError('could not start routine ' + name)
        frames = 0
        while not self.ret_hit and frames < max_frames:
            if driver:
                driver()
            else:
                self.p.tick(1, False, False)
            frames += 1
        return self.ret_hit, getattr(self, 'out', {})
    def add_mon(self, species, level):
        self.write('wCurPartySpecies', species)
        self.write('wCurPartyLevel', level)
        self.write('wMonType', 0)
        ok, out = self.call('TryAddMonToParty')
        return ok

    def close(self): self.p.stop(save=False)



# ---------------------------------------------------------------------------
class Data:
    """Move/type/species data read from the compiled ROM itself."""
    def __init__(self, sim):
        s = sim
        rom = s.data
        b, p = s.sym['Moves']; self.moves_off = b * 16384 + p - 16384
        b, p = s.sym['TypeMatchups']; o = b * 16384 + p - 16384
        self.chart = {}
        while rom[o] != 0xff:
            if rom[o] != 0xfe:
                self.chart[(rom[o], rom[o + 1])] = rom[o + 2] / 10.0
            o += 3
        effects = re.findall(r'^\s*const (EFFECT_\w+)', (ROOT / 'constants/move_effect_constants.asm').read_text(encoding='utf8'), re.M)
        self.effect = {name: i for i, name in enumerate(effects)}
        self.bad_effects = {self.effect[n] for n in ['EFFECT_SELFDESTRUCT', 'EFFECT_DREAM_EATER', 'EFFECT_SNORE', 'EFFECT_SLEEP_TALK',
                                                     'EFFECT_COUNTER', 'EFFECT_MIRROR_COAT', 'EFFECT_BIDE', 'EFFECT_FUTURE_SIGHT',
                                                     'EFFECT_RAGE', 'EFFECT_ENDURE']}
        self.slow = {self.effect[n] for n in ['EFFECT_RAZOR_WIND', 'EFFECT_SKY_ATTACK', 'EFFECT_HYPER_BEAM', 'EFFECT_SOLARBEAM',
                                              'EFFECT_FLY']}
        self.rom = rom

    def move(self, mid):
        o = self.moves_off + (mid - 1) * 7
        r = self.rom[o:o + 7]
        return {'effect': r[1], 'power': r[2], 'type': r[3] & 0x3f, 'cat': r[3] & 0xc0, 'acc': r[4] / 255.0, 'pp': r[5]}

    def eff(self, mtype, defender_types):
        m = 1.0
        for t in set(defender_types):
            m *= self.chart.get((mtype, t), 1.0)
        return m


class Bot:
    def __init__(self, sim):
        self.s = sim
        self.d = Data(sim)
        self.mode = None
        self.turns = 0
        self.picks = 0
        s = sim
        for label, mode in [('LoadBattleMenu', 'menu'), ('MoveSelectionScreen', 'move'), ('JumpToPartyMenuAndPrintText', 'party')]:
            s.p.hook_register(*s.sym[label], self._hook(mode), None)
        s.p.hook_register(*s.sym['BattleTurn'], self._turn, None)

    def _hook(self, mode):
        def f(_):
            self.mode = mode
        return f

    tracer = None
    last_turn = -1
    last_try = None
    rejected = set()

    def _turn(self, _):
        self.turns += 1
        if self.tracer:
            self.tracer(_)

    def best_move(self):
        s = self.s
        moves = s.mem('wBattleMonMoves', 4)
        pps = s.mem('wBattleMonPP', 4)
        mine = s.mem('wBattleMonType', 2)
        theirs = s.mem('wEnemyMonType', 2)
        best, best_i = -1.0, 0
        disabled = (s.read('wPlayerDisableCount') >> 4) & 0xf   # 1-based index of the Disabled move
        if self.turns != self.last_turn:
            self.last_turn = self.turns; self.rejected = set()
        for i, mid in enumerate(moves):
            if mid == 0 or (pps[i] & 0x3f) == 0 or disabled == i + 1 or i in self.rejected:
                continue
            mv = self.d.move(mid)
            power = mv['power']
            if mv['effect'] == self.d.effect['EFFECT_HIDDEN_POWER']:
                power = 60
            if mv['cat'] == 0xc0 or power <= 1 or mv['effect'] in self.d.bad_effects:
                score = 0.01
            else:
                stab = 1.5 if mv['type'] in mine else 1.0
                score = power * stab * self.d.eff(mv['type'], theirs) * mv['acc']
                if mv['effect'] in self.d.slow:
                    score *= 0.5
            if score > best:
                best, best_i = score, i
        return best_i

    def next_alive(self):
        s = self.s
        n = s.read('wPartyCount')
        stride = s.a('wPartyMon2') - s.a('wPartyMon1')
        cur = s.read('wCurBattleMon')
        order = []
        for i in range(n):
            hp = s.p.memory[s.a('wPartyMon1HP') + stride * i] * 256 + s.p.memory[s.a('wPartyMon1HP') + stride * i + 1]
            dead = s.p.memory[s.a('wPartyMon1CaughtLocation') + stride * i] & 0x80
            if hp > 0 and not dead and i != cur:
                order.append(i)
        return order[0] if order else 0

    def act(self):
        s = self.s
        if self.mode == 'menu':
            s.write('wBattleMenuCursorPosition', 1)
            s.press('a', 2, hold=3)
            self.mode = None
        elif self.mode == 'move':
            # The hook fires at the entry of MoveSelectionScreen: drive the cursor with real
            # presses (writing wCurMoveNum here would arrive after the game already read it).
            idx = self.best_move()
            cur = s.read('wMenuCursorY') - 1
            if cur < idx:
                s.press('down', 3, hold=3)
            elif cur > idx:
                s.press('up', 3, hold=3)
            else:
                if (self.turns, idx) == self.last_try:
                    self.rejected.add(idx)   # the game refused it (disabled, no PP, locked): pick another
                self.last_try = (self.turns, idx)
                s.press('a', 2, hold=3)
                self.mode = None
        elif self.mode == 'party':
            idx = self.next_alive()
            cur = s.read('wMenuCursorY') - 1
            if cur < idx:
                s.press('down', 4, hold=3)
            elif cur > idx:
                s.press('up', 4, hold=3)
            else:
                s.press('a', 2, hold=3)
                self.mode = None
        else:
            s.press('a', 3, hold=2)


def fight(sim, bot, cls, tid, win='Route31SignText', max_iter=12000):
    """Start a trainer battle with the current party and let the bot play it."""
    s = sim
    ptr = s.sym[win][1]
    s.write('wBattleScriptFlags', (1 << 7) | 1)
    s.write('wOtherTrainerClass', cls)
    s.write('wOtherTrainerID', tid)
    for name in ('wWinTextPointer', 'wLossTextPointer'):
        s.write(name, ptr & 0xff); s.write(name, ptr >> 8, 1)
    s.write('wBattleType', 0)
    s.write('wLinkMode', 0)
    bot.turns = 0; bot.mode = None
    s.call('BufferScreen')
    ok, _ = s.call('StartBattle', max_frames=max_iter, driver=bot.act)
    stride = s.a('wPartyMon2') - s.a('wPartyMon1')
    alive = 0
    hp_left = 0
    hp_max = 0
    for i in range(s.read('wPartyCount')):
        hp = s.p.memory[s.a('wPartyMon1HP') + stride * i] * 256 + s.p.memory[s.a('wPartyMon1HP') + stride * i + 1]
        mx = s.p.memory[s.a('wPartyMon1MaxHP') + stride * i] * 256 + s.p.memory[s.a('wPartyMon1MaxHP') + stride * i + 1]
        alive += hp > 0; hp_left += hp; hp_max += mx
    return {'finished': ok, 'result': s.read('wBattleResult') & 0x0f, 'turns': bot.turns, 'alive': alive,
            'hp_pct': round(100 * hp_left / max(1, hp_max), 1), 'enemy_count': s.read('wOTPartyCount')}






def arena_fight(cls, tid, species, level, badges=(0, 0), hof=False, red=False, win='Route31SignText', max_iter=40000, seed=None, debug=False, trace=None):
    """Fresh emulator: build the party with the game's routines, then walk into the
    patched Route 31 script that starts the trainer battle; the bot plays it."""
    s = Sim(arena=(cls, tid), win=win)
    try:
        s.write('wJohtoBadges', badges[0]); s.write('wKantoBadges', badges[1])
        if hof:
            s.write('wStatusFlags', s.read('wStatusFlags') | (1 << 6))
        if red:
            n = 529
            s.p.memory[s.a('wEventFlags') + n // 8] |= 1 << (n % 8)
        for sp in species:
            s.add_mon(sp, level)
        if seed is not None:
            for _ in range(seed % 97):
                s.p.tick(1, False, False)
        bot = Bot(s)
        if trace is not None:
            def tr(_):
                trace.append((bot.turns, s.read('wBattleMonSpecies'), s.word('wBattleMonHP'), s.read('wEnemyMonSpecies'), s.word('wEnemyMonHP'), s.read('wCurPlayerMove'), s.read('wCurEnemyMove'), s.read('wPlayerSubStatus5') if 'wPlayerSubStatus5' in s.sym else 0))
            bot.tracer = tr
        counts = {'win': 0, 'lost': 0, 'reload': 0}
        for label, key in [('WinTrainerBattle', 'win'), ('LostBattle', 'lost'), ('Script_reloadmapafterbattle', 'reload')]:
            def h(_, key=key):
                counts[key] += 1
            s.p.hook_register(*s.sym[label], h, None)
        s.press('up', 20, hold=6)
        started = False
        for i in range(max_iter):
            if counts['reload']:
                break
            bot.act()
        if debug:
            s.p.screen.image.save(str(WORK / 'caps' / 'arena_end.png'))
            print('dbg', counts, 'PC', hex(s.p.register_file.PC), 'curmon', s.read('wCurBattleMon'), 'enemyhp', s.word('wEnemyMonHP'), 'botmode', bot.mode, 'menuY', s.read('wMenuCursorY'), 'partyCur', s.read('wPartyMenuCursor'), 'menuPos', s.read('wMenuCursorPosition') if 'wMenuCursorPosition' in s.sym else '', 'party', s.read('wPartyCount'), flush=True)
        stride = s.a('wPartyMon2') - s.a('wPartyMon1')
        alive = hp_left = hp_max = 0
        for i in range(s.read('wPartyCount')):
            hp = s.p.memory[s.a('wPartyMon1HP') + stride * i] * 256 + s.p.memory[s.a('wPartyMon1HP') + stride * i + 1]
            mx = s.p.memory[s.a('wPartyMon1MaxHP') + stride * i] * 256 + s.p.memory[s.a('wPartyMon1MaxHP') + stride * i + 1]
            alive += hp > 0; hp_left += hp; hp_max += mx
        res = {'won': counts['win'] > 0 and counts['lost'] == 0, 'lost': counts['lost'] > 0, 'finished': bool(counts['reload']),
               'turns': bot.turns, 'alive': alive, 'hp_pct': round(100 * hp_left / max(1, hp_max), 1),
               'enemy_hp': s.word('wEnemyMonHP'), 'enemy_left': None}
        return res
    finally:
        s.close()













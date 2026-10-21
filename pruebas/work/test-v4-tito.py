"""Execute v4 Tito services in the compiled cartridge and real map UI.

Only test setup skips the lengthy existing new-game profile and chooses a
Pokémon Center spawn. Service, tile loading, trade and learning code stay real.
"""
import io
import json
from pathlib import Path

from pyboy import PyBoy
from cpu_harness import ROM, Routine, addr, symbols

results = []


def check(name, value=True):
    assert value, name
    results.append({"name": name, "passed": True})


def offset(name):
    bank, pointer = symbols[name]
    return bank * 0x4000 + pointer - 0x4000 if bank else pointer


r = Routine()
try:
    for species, suffix in [
        (64, "Kadabra"), (67, "Machoke"), (75, "Graveler"), (93, "Haunter"),
        (61, "Poliwhirl"), (79, "Slowpoke"), (95, "Onix"), (117, "Seadra"),
        (123, "Scyther"), (137, "Porygon"), (42, "Golbat"), (113, "Chansey"),
        (172, "Pichu"), (173, "Cleffa"), (174, "Igglybuff"), (175, "Togepi"),
        (133, "Eevee"), (1, "Unchanged"),
    ]:
        answer = r.run("TitoEvolutionText", lambda m: m.write("wCurPartySpecies", species))
        check("Evolution guide for " + suffix,
              answer["HL"] == addr("TitoEvolutionText." + suffix))
finally:
    r.close()


class Center:
    def __init__(self, full_moves=False):
        data = bytearray(ROM.read_bytes())
        for name in ["PlayerProfileSetup", "OakSpeech", "ShrinkPlayer", "_InitializeStartDay"]:
            data[offset(name)] = 0xC9
        start = offset("SpawnPoints")
        data[start:start + 4] = data[start + 4:start + 6] + bytes([6, 5])
        self.p = PyBoy(io.BytesIO(data), window="null", sound_emulated=False, log_level="ERROR")
        self.p.set_emulation_speed(0)
        self.counts = {}
        for name in ["TitoXeluisServices.WaitMainMenu", "SelectTradeOrDayCareMon", "TitoXeluisTrade",
                     "TitoMoveReminder", "ScrollingMenu", "LearnMove", "YesNoBox",
                     "TradeAnimation", "DoPreparedNPCTrade"]:
            def hook(_, name=name):
                self.counts[name] = self.counts.get(name, 0) + 1
            self.p.hook_register(*symbols[name], hook, None)
        self.p.tick(360)
        self.press("start", 120)
        self.press("start", 120)
        self.p.button_press("a")
        self.p.tick(32)
        self.p.button_release("a")
        self.p.tick(300)
        p = self.p
        p.memory[addr("wOptions")] = (p.memory[addr("wOptions")] & 0xF8) | 1
        stride = addr("wPartyMon2") - addr("wPartyMon1")
        p.memory[addr("wPartyCount")] = 2
        p.memory[addr("wPartySpecies"):addr("wPartySpecies") + 3] = [1, 16, 255]
        for index, species, level, moves in [
            (0, 1, 10, [33, 73, 22, 250 if full_moves else 0]),
            (1, 16, 7, [33, 0, 0, 0]),
        ]:
            base = addr("wPartyMon1") + stride * index
            p.memory[base:base + stride] = [0] * stride
            p.memory[base] = species
            p.memory[addr("wPartyMon1Level") + stride * index] = level
            moveaddr = addr("wPartyMon1Moves") + stride * index
            p.memory[moveaddr:moveaddr + 4] = moves
            ppaddr = addr("wPartyMon1PP") + stride * index
            p.memory[ppaddr:ppaddr + 4] = [35, 10, 10, 10 if full_moves else 0]
            for stat in ["HP", "MaxHP", "Attack", "Defense", "Speed", "SpclAtk", "SpclDef"]:
                pointer = addr("wPartyMon1" + stat) + stride * index
                p.memory[pointer:pointer + 2] = [0, 20]
            pointer = addr("wPartyMonNicknames") + 11 * index
            p.memory[pointer:pointer + 11] = [0x93, 0x84, 0x92, 0x93, 0x50, 0, 0, 0, 0, 0, 0]
        self.press("up", 10)

    def press(self, button, frames=100):
        self.p.button_press(button)
        self.p.tick(1 if button == "a" else 8)
        self.p.button_release(button)
        self.p.tick(frames)

    def until(self, name, count, button="a", maximum=30):
        for _ in range(maximum):
            if self.counts.get(name, 0) >= count:
                return
            self.press(button)
        self.snap("failure-" + name.replace(".", "-"))
        raise AssertionError((name, count, self.counts, self.p.register_file.PC))

    def snap(self, name):
        self.p.screen.image.save("work/v4-tito-" + name + ".png")

    def speak(self):
        self.until("TitoXeluisServices.WaitMainMenu", 1)
        self.p.tick(120)

    def used(self):
        flag = 400 + 0x31  # LANDMARK_VIRIDIAN_CITY
        return bool(self.p.memory[addr("wEventFlags") + flag // 8] & (1 << (flag % 8)))

    def close(self):
        self.p.stop(save=False)


c = Center()
try:
    p = c.p
    c.snap("center")
    entries = list(p.memory[addr("wUsedSprites"):addr("wUsedSprites") + 64])
    index = entries[::2].index(0x67)
    tile = entries[index * 2 + 1]
    bank = 0 if tile & 0x80 else 1
    destination = 0x8000 + (tile & 0x7F) * 16
    native = ROM.read_bytes()[offset("TitoXeluisSpriteGFX"):offset("TitoXeluisSpriteGFX") + 192]
    actual = bytes(p.memory[bank, destination + i] for i in range(192))
    check("Complete Tito standing frame data loaded into actual map VRAM", actual == native[:192])
    facings = [native[index:index + 64] for index in range(0, 192, 64)]
    check("Tito has distinct front, back and side artwork", len(set(facings)) == 3)
    actor = next(n for n in range(1, 13) if p.memory[addr(f"wObject{n}Sprite")] == 0x67)
    for direction, pose in [(4, "back"), (8, "left"), (12, "right"), (0, "front")]:
        p.memory[addr(f"wObject{actor}Direction")] = direction
        p.tick(3)
        c.snap("pose-" + pose)
        check("Map sprite renders the complete " + pose + " pose",
              p.memory[addr(f"wObject{actor}Facing")] == direction)
    c.speak()
    c.snap("named-menu")
    title = [0x93, 0x88, 0x93, 0x8E, 0x7F, 0x97, 0x84, 0x8B, 0x94, 0x88, 0x92]
    tilemap = list(p.memory[addr("wTilemap"):addr("wTilemap") + 360])
    check("Service prompt visibly identifies TITO XELUIS",
          any(tilemap[i:i + len(title)] == title for i in range(360 - len(title))))

    party = bytes(p.memory[addr("wPartyCount"):addr("wPartyMon2") + 48])
    c.press("a")
    c.until("SelectTradeOrDayCareMon", 1)
    c.until("YesNoBox", 1)
    proposed = p.memory[addr("wOTTrademonSpecies")]
    check("Trade proposal exists before a Pokémon is removed", p.memory[addr("wPartySpecies")] == 1)
    c.snap("proposal")
    c.press("down", 12)
    c.press("a")
    c.until("TitoXeluisServices.WaitMainMenu", 2)
    check("Declining a proposed exchange preserves the whole party",
          bytes(p.memory[addr("wPartyCount"):addr("wPartyMon2") + 48]) == party)
    check("Declining a proposed exchange preserves the city opportunity", not c.used())
    c.press("a")
    c.until("SelectTradeOrDayCareMon", 2)
    c.until("YesNoBox", 2)
    proposed = p.memory[addr("wOTTrademonSpecies")]
    c.press("a")
    c.until("TitoXeluisServices.WaitMainMenu", 3)
    check("Confirmed trade delivers exactly the species shown in its proposal",
          p.memory[addr("wPartySpecies") + 1] == proposed)
    check("Confirmed trade preserves selected level", p.memory[addr("wPartyMon2Level")] == 10)
    check("Only a completed trade consumes the city's opportunity", c.used())
    check("Tito trade bypasses the exchange animation", c.counts.get("TradeAnimation", 0) == 0)
    c.snap("completed-trade")
finally:
    c.close()

for full in [False, True]:
    c = Center(full_moves=full)
    try:
        p = c.p
        c.speak()
        palbank, paladdr = symbols["wBGPals1"]
        original_pals = bytes(p.memory[palbank, paladdr + i] for i in range(56))
        c.press("down", 8)
        c.press("down", 8)
        c.press("a")
        c.until("SelectTradeOrDayCareMon", 1)
        c.until("ScrollingMenu", 1)
        c.snap("reminder-full-list" if full else "reminder-list")
        rgb = p.screen.image.convert("RGB")
        check("Reminder menu has a clean grayscale background " + str(full),
              all(r == g == b for r, g, b in rgb.getdata()))
        check("Reminder list hides live map sprites " + str(full),
              all(v == 0 for v in p.memory[addr("wShadowOAM"):addr("wShadowOAM") + 160]))
        c.press("a")
        c.until("LearnMove", 1)
        c.until("TitoXeluisServices.WaitMainMenu", 2, maximum=40)
        check("Original move is learned through actual reminder " + str(full),
              45 in p.memory[addr("wPartyMon1Moves"):addr("wPartyMon1Moves") + 4])
        check("Reminder restores map sprite update state " + str(full),
              p.memory[addr("wSpriteUpdatesEnabled")] == 1)
        restored_pals = bytes(p.memory[palbank, paladdr + i] for i in range(56))
        check("Reminder restores original map palette colors " + str(full), restored_pals == original_pals)
        c.snap("reminder-full-restored" if full else "reminder-restored")
    finally:
        c.close()

# Read the real standard exchange prose: sent/received buffers must not be
# swapped, and later fanfare must not make completion depend on scratch buffer 1.
source = ROM.parent
common = (source / "data/text/common_1.asm").read_text(encoding="utf-8")
trade = common.split("Text_NPCTraded::", 1)[1].split("_NPCTradeFanfareText::", 1)[0]
check("NPC exchange narration names the sent Pokémon before the received Pokémon",
      trade.index("wMonOrItemNameBuffer") < trade.index("wStringBuffer2"))
for name in ["_NPCTradeCompleteText1", "_NPCTradeCompleteText2"]:
    text = common.split(name + "::", 1)[1].split("\ndone", 1)[0].split("\n\tdone", 1)[0]
    check(name + " uses the sent Pokémon's durable name buffer", "wMonOrItemNameBuffer" in text)

# Real new-game speech, with only profile/clock input skipped for the test.
intro_data = bytearray(ROM.read_bytes())
for name in ["PlayerProfileSetup", "InitClock"]:
    intro_data[offset(name)] = 0xC9
p = PyBoy(io.BytesIO(intro_data), window="null", sound_emulated=False, log_level="ERROR")
p.set_emulation_speed(0)
portraits = []
rules = []
p.hook_register(*symbols["Intro_PrepTrainerPic"],
                lambda _: portraits.append(p.memory[addr("wTrainerClass")]), None)


def print_hook(_):
    if p.register_file.HL == addr("TitoNuzlockeIntro.Rules"):
        rules.append(True)


p.hook_register(*symbols["PrintText"], print_hook, None)


def intro_press(button="a", frames=120):
    p.button_press(button)
    p.tick(1)
    p.button_release(button)
    p.tick(frames)


try:
    p.tick(360)
    intro_press("start")
    intro_press("start")
    for _ in range(25):
        if rules:
            break
        intro_press()
    check("New game introduces Tito's battle portrait before Professor Oak", portraits == [0x44])
    check("New game reaches the actual Nuzlocke rules text", bool(rules))
    p.tick(120)
    p.screen.image.save("work/v4-tito-introduction.png")
    for _ in range(50):
        if len(portraits) > 1:
            break
        intro_press()
    check("Finishing Tito's rules continues to the original Professor Oak introduction",
          portraits[:2] == [0x44, 0x0A])
finally:
    p.stop(save=False)

report = {"passed": len(results), "tests": results}
Path("work/v4-tito-tests.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))

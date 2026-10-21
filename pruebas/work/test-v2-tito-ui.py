"""Exercise Tito's actual map and UI in PyBoy, with intro-only test shortcuts.

The cartridge bytes are changed only in memory: skip the long profile/Oak
presentation and start at the Viridian center instead of the bedroom. Map,
sprite, service, trade and learning code are the unmodified compiled ROM.
"""
import io
import json
import sys
from pathlib import Path
from pyboy import PyBoy
from cpu_harness import ROM, symbols, addr

data = bytearray(ROM.read_bytes())
def offset(symbol):
    bank, pointer = symbols[symbol]
    return bank*0x4000 + pointer-0x4000 if bank else pointer
for symbol in ['PlayerProfileSetup','OakSpeech','ShrinkPlayer','_InitializeStartDay']:
    data[offset(symbol)] = 0xc9
spawn = offset('SpawnPoints')
data[spawn:spawn+4] = data[spawn+4:spawn+6] + bytes([6,5])
p = PyBoy(io.BytesIO(data),window='null',sound_emulated=False,log_level='ERROR')
p.set_emulation_speed(0)
counts={}
for name in ['TitoMoveReminder','ScrollingMenu','_InitScrollingMenu','_ScrollingMenu','ScrollingMenuJoyAction','ScrollingMenuJoyAction.a_button','LearnMove','TitoXeluisTrade']:
    def hook(_, name=name):
        counts[name]=counts.get(name,0)+1
    p.hook_register(*symbols[name],hook,None)
def press(button, frames=120):
    p.button_press(button)
    p.tick(32 if button=='a' else 8)
    p.button_release(button)
    p.tick(frames)
def snap(name):
    p.screen.image.save('work/v2-tito-'+name+'.png')
try:
    p.tick(360)
    press('start')
    press('start')
    press('a',300)
    p.memory[addr('wOptions')]=(p.memory[addr('wOptions')] & 0xf8) | 1
    stride=addr('wPartyMon2')-addr('wPartyMon1')
    p.memory[addr('wPartyCount')]=2
    p.memory[addr('wPartySpecies'):addr('wPartySpecies')+3]=[1,16,255]
    for index,species,level,moves in [(0,1,10,[33,73,22,0]),(1,16,7,[33,0,0,0])]:
        base=addr('wPartyMon1')+stride*index
        p.memory[base:base+stride]=[0]*stride
        p.memory[base]=species
        p.memory[addr('wPartyMon1Level')+stride*index]=level
        p.memory[addr('wPartyMon1Moves')+stride*index:addr('wPartyMon1Moves')+stride*index+4]=moves
        p.memory[addr('wPartyMon1PP')+stride*index:addr('wPartyMon1PP')+stride*index+4]=[35,10,10,0]
        for stat in ['HP','MaxHP','Attack','Defense','Speed','SpclAtk','SpclDef']:
            p.memory[addr('wPartyMon1'+stat)+stride*index:addr('wPartyMon1'+stat)+stride*index+2]=[0,20]
        p.memory[addr('wPartyMonNicknames')+11*index:addr('wPartyMonNicknames')+11*index+11]=[0x93,0x84,0x92,0x93,0x50,0,0,0,0,0,0]
    snap('center')
    print(json.dumps({'map':[p.memory[addr('wMapGroup')],p.memory[addr('wMapNumber')]],'xy':[p.memory[addr('wXCoord')],p.memory[addr('wYCoord')]],'pc':p.register_file.PC}))
    press('up',10)
    press('a')
    snap('greeting')
    press('down',8)
    press('down',8)
    press('a')
    snap('reminder-party')
    press('a')
    snap('reminder-list')
    press('a',240)
    press('a',240)
    p.tick(600)
    snap('reminder-learned')
    firstmoves=list(p.memory[addr('wPartyMon1Moves'):addr('wPartyMon1Moves')+4])
    print('after reminder',firstmoves)
    assert firstmoves==[33,73,22,45],firstmoves
    assert p.memory[addr('wGameLogicPaused')]==0
    assert p.memory[addr('wInputType')]==0
    # Back in Tito's service menu, choose the repeating trade service.
    press('a')
    press('a')
    snap('trade-party')
    press('down',8)
    press('a',1800)
    snap('trade-animation')
    for _ in range(4):
        press('a')
    snap('trade-completed')
    result=list(p.memory[addr('wPartySpecies'):addr('wPartySpecies')+3])
    level=p.memory[addr('wPartyMon2Level')]
    print('after trade',result,level)
    assert result[0]==16 and result[1]!=1 and result[2]==255,result
    assert level==10,level
    assert counts.get('LearnMove')==1,counts
    assert counts.get('TitoXeluisTrade')==1,counts
    Path('work/v2-tito-ui-tests.json').write_text(json.dumps({'passed':3,'map':[23,9],'reminder_learned':45,'exchange_received_species':result[1],'exchange_preserved_level':level,'counts':counts},indent=2),encoding='utf-8')
    print('3 actual Tito map/UI/learn/trade checks passed')
finally:
    p.stop(save=False)

"""Real v4 battle UI: Icy Wind, actual Hidden Power type, capture-to-PC shiny.
Fixture skips intro and invokes shrine from a center; it gives six living test
mons and makes IcyWind hit for1 so twelve animations can run on one opponent.
The cartridge's animation interpreter, speed drop, capture and storage run.
"""
from pathlib import Path
base=Path('work/test-v2-tito-ui.py').read_text(encoding='utf-8')
exec(base[:base.index('try:')])
for label in ['BattleMenu','BattleCommand_SpeedDown','MoveInfoBox','PokeBallEffect','GiveCaptureExperience','SendMonIntoBox','Start','_Start']:
    def hook(_,label=label):counts[label]=counts.get(label,0)+1
    p.hook_register(*symbols[label],hook,None)
def tiny_hit(_):
    if p.memory[addr('hBattleTurn')]==0:p.memory[addr('wCurDamage'):addr('wCurDamage')+2]=[0,1]
p.hook_register(*symbols['BattleCommand_ApplyDamage'],tiny_hit,None)
bank,pointer=symbols['IlexForestShrineScript'];nb,np=symbols['ViridianPokecenter1FTitoXeluis']
for i,value in enumerate([4,bank,pointer&255,pointer>>8]):p.memory[nb,np+i]=value
def snap(name):p.screen.image.save('work/v4-battle-'+name+'.png')
def memory(name,n=1):return list(p.memory[addr(name):addr(name)+n])
try:
    p.tick(360);press('start');press('start');press('a',300)
    p.memory[addr('wOptions')]=1 # fast text, animations ON
    p.memory[addr('wPartyCount')]=6
    p.memory[addr('wPartySpecies'):addr('wPartySpecies')+7]=[153,19,19,19,19,19,255]
    stride=addr('wPartyMon2')-addr('wPartyMon1')
    for index in range(6):
        offset=stride*index;base=addr('wPartyMon1')+offset
        p.memory[base:base+stride]=[0]*stride
        p.memory[base]=153 if index==0 else 19
        p.memory[addr('wPartyMon1Level')+offset]=30
        p.memory[addr('wPartyMon1Exp')+offset:addr('wPartyMon1Exp')+offset+3]=list((27000).to_bytes(3,'big'))
        p.memory[addr('wPartyMon1Moves')+offset:addr('wPartyMon1Moves')+offset+4]=[196,237,33,45]
        p.memory[addr('wPartyMon1PP')+offset:addr('wPartyMon1PP')+offset+4]=[15,15,35,40]
        p.memory[addr('wPartyMon1DVs')+offset:addr('wPartyMon1DVs')+offset+2]=[255,255]
        p.memory[addr('wPartyMon1ID')+offset:addr('wPartyMon1ID')+offset+2]=memory('wPlayerID',2)
        for stat in ['HP','MaxHP','Attack','Defense','Speed','SpclAtk','SpclDef']:
            p.memory[addr('wPartyMon1'+stat)+offset:addr('wPartyMon1'+stat)+offset+2]=[3,231]
        p.memory[addr('wPartyMonNicknames')+11*index:addr('wPartyMonNicknames')+11*index+11]=[0x93,0x84,0x92,0x93,0x50,0,0,0,0,0,0]
    p.memory[addr('wJohtoBadges')]=255;p.memory[addr('wKantoBadges')]=255
    press('up',10);press('a')
    for _ in range(25):
        if counts.get('BattleMenu',0):break
        press('a',120)
    assert counts.get('BattleMenu',0),counts
    p.memory[addr('wEnemyMonHP'):addr('wEnemyMonHP')+4]=[3,231,3,231]
    p.memory[addr('wEnemyMonMoves'):addr('wEnemyMonMoves')+4]=[150]*4
    p.memory[addr('wEnemyMonPP'):addr('wEnemyMonPP')+4]=[40]*4
    initial_dvs=memory('wEnemyMonDVs',2)
    assert initial_dvs[1]==0xaa and initial_dvs[0]&47==42,initial_dvs
    # First selected move info; second slot is Hidden Power, DARK power70.
    for _ in range(6):
        if counts.get('MoveInfoBox',0):break
        press('a',60)
    snap('icy-power')
    assert list(p.memory[addr('wTilemap')+14*20+1:addr('wTilemap')+14*20+4])==[0x8f,0xfb,0xfb]
    assert p.memory[addr('wTilemap')+13*20+6] != 0x7f
    press('down',8);snap('hidden-power-dark70')
    assert list(p.memory[addr('wTilemap')+14*20+1:addr('wTilemap')+14*20+4])==[0x8f,0xfd,0xf6]
    assert p.memory[addr('wTilemap')+14*20+6] != 0x7f
    press('up',8)
    for _ in range(300):
        if counts.get('BattleCommand_SpeedDown',0)>=12 and p.memory[addr('wBattleMenuCursorPosition')]==1:
            break
        press('a',90)
    assert counts.get('BattleCommand_SpeedDown',0)>=12,counts
    assert counts.get('Start',0)==1 and counts.get('_Start',0)==1,counts
    assert p.memory[addr('hCGB')]==1
    # Complete the turn, return to the action menu and capture into the PC.
    for _ in range(15):press('b',120)
    snap('after-12-icy-winds')
    press('down',8);press('a',120)
    # MEDICINA -> BAYAS -> COMBATE -> OTROS -> BALLS.
    for _ in range(4):press('right',30)
    press('a',240)
    for _ in range(100):
        if counts.get('GiveCaptureExperience',0):break
        press('a',90)
    for _ in range(60):
        if counts.get('SendMonIntoBox',0):break
        press('a',120)
    snap('capture-progress')
    for _ in range(20):press('b',120)
    print('capture counts',counts,'party',memory('wPartyCount'),'enemyDV',memory('wEnemyMonDVs',2),flush=True)
    assert counts.get('PokeBallEffect',0)>0 and counts.get('GiveCaptureExperience',0)==1,counts
    p.memory[0x0000]=10;p.memory[0x4000]=1
    stored=list(p.memory[addr('sBoxMon1DVs'):addr('sBoxMon1DVs')+2])
    assert stored==initial_dvs,(initial_dvs,stored)
    assert p.memory[addr('wPartyCount')]==6
    snap('captured-shiny-to-pc')
    report={'passed':4,'tests':['Actual battle info displays55-power IcyWind',
        'Selected HiddenPower displays its actual Dark type/power70',
        'Bayleef executes at least12 full IcyWind animations/speed drops with no reset and CGB state intact',
        'Actual MasterBall capture with fullparty preserves visible event shiny DVs in PC'],
        'counts':counts,'shiny_dvs':stored,'fixture':'Damage limited to1 only to keep target alive for stress; 6 test mons/intro shortcut'}
    Path('work/v41-battle-ui-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
finally:p.stop(save=False)

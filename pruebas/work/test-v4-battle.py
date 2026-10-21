"""Execute v4 battle/storage code on the LR35902, including previous failures."""
import json
from pathlib import Path
from cpu_harness import Routine, ROM, addr, symbols, move_bytes, install_move

class BattleRoutine(Routine):
    def __init__(self):
        super().__init__()
        self.roll=5
        self.rng_calls=0
        for label in ['Random','BattleRandom']:
            self.p.memory[symbols[label]]=0xc9
            self.p.hook_register(*symbols[label],self.rng,None)
        for label in ['StdBattleTextbox','BattleTextbox','DelayFrame','PlaySFX','WaitSFX','UpdatePlayerHUD','UpdateEnemyHUD']:
            self.p.memory[symbols[label]]=0xc9
    def rng(self,_):
        self.rng_calls+=1
        self.p.register_file.A=self.roll
        self.roll=(self.roll+17)&255
    def start(self,context):
        super().start(context)
        self.p.register_file.SP=0xc0f0
        self.p.memory[0xc0f0:0xc0f2]=[2,1]

r=BattleRoutine();tests=[]
def ok(label):
    tests.append(label);print('PASS',label,flush=True)
def dv(r,name,value):
    r.p.memory[addr(name):addr(name)+2]=value

def expected_hp(b,c):
    top=((b>>7)&1)*8+((b>>3)&1)*4+((c>>7)&1)*2+((c>>3)&1)
    power=(5*top+(c&3))//2+31
    types=[1,2,3,4,5,7,8,9,20,21,22,23,24,25,26,27]
    return types[((b>>4)&3)*4+(b&3)],power
try:
    # Pure menus must agree with actual in-battle Hidden Power on varied DVs.
    for b in range(256):
        for c in [0,0xaa,0xff]:
            expected=expected_hp(b,c)
            def setup(r,b=b,c=c):
                dv(r,'wBattleMonDVs',[b,c]);install_move(r,237)
                r.write('wEnemyMoveStructType',0x5b)
            got=r.run('GetDisplayedMoveData',setup,B=237,D=addr('wBattleMonDVs')>>8,E=addr('wBattleMonDVs')&255)
            assert (got['B'],got['D'])==expected,(b,c,got,expected)
            assert r.p.memory[addr('wPlayerMoveStructType')]==0x80
            assert r.p.memory[addr('wEnemyMoveStructType')]==0x5b
    ok('768 DV cases: Hidden Power menu returns exact type/power without mutating either battler')
    for b,c in [(0,0),(0x2a,0xaa),(255,255),(0xb4,0x9f)]:
        def setup(r):dv(r,'wBattleMonDVs',[b,c]);install_move(r,237)
        got=r.run('HiddenPowerDamage',setup)
        typ,power=expected_hp(b,c)
        assert got['D']==power and r.p.memory[addr('wPlayerMoveStructType')]==(0x80|typ)
    ok('Actual Hidden Power damage command agrees with the pure display calculation')

    # The cap includes equality, with no RNG/disobedience path at legal levels.
    for johto,kanto,league in [(0,0,0),(1,0,0),(0xff,0,0),(0xff,0x2c,64),(0xff,0xff,64)]:
        def capsetup(r):r.write('wJohtoBadges',johto);r.write('wKantoBadges',kanto);r.write('wStatusFlags',league)
        cap=r.run('GetCurrentLevelCap',capsetup)['B']
        for level in [max(1,cap-1),cap]:
            def setup(r):
                capsetup(r);r.write('wBattleMonLevel',level);r.write('wPartyMon1ID',1)
                r.write('wPlayerID',2);r.write('wBattleMonMoves',33);install_move(r,33)
            before=r.rng_calls;r.run('BattleCommand_CheckObedience',setup)
            assert r.rng_calls==before,(johto,kanto,cap,level)
    ok('Traded monsters obey through exact current gym/League cap at all progression stages')

    for turn in [0,1]:
        target='wEnemyMon' if turn==0 else 'wBattleMon'
        party='wOTPartyMon1' if turn==0 else 'wPartyMon1'
        for item in [25,119]:
            for hp,maximum,damage,active in [(100,100,100,True),(100,100,150,True),(99,100,150,False),(1,100,150,False),(100,100,98,False)]:
                def setup(r):
                    r.write('hBattleTurn',turn);r.write('wBattleMode',2);r.write(target+'Item',item);r.write(party+'Item',item)
                    r.word(target+'HP',hp);r.word(target+'MaxHP',maximum);r.word('wCurDamage',damage)
                r.run('BattleCommand_ApplyDamage',setup)
                assert r.read_word(target+'HP')==(1 if active else max(0,hp-damage)),(turn,item,hp,damage,r.read_word(target+'HP'))
                assert r.p.memory[addr(target+'Item')]==(0 if active else item)
                assert r.p.memory[addr(party+'Item')]==(0 if active else item)
    ok('Full damage command: modern and legacy Focus items save only full HP once and consume from both sides')

    for value in [[0x2a,0xaa],[0x73,0x19]]:
        def setup(r):
            r.write('wTempEnemyMonSpecies',153);r.write('wCurPartyLevel',25);r.write('wBattleMode',1)
            r.write('wEnemySubStatus5',8);dv(r,'wEnemyBackupDVs',value)
        # SUBSTATUS_TRANSFORMED is bit3 in Gen2. Capture sets it before reload.
        r.run('LoadEnemyMon',setup)
        assert list(r.p.memory[addr('wEnemyMonDVs'):addr('wEnemyMonDVs')+2])==value,value
    ok('Capture reload preserves original shiny and nonshiny DVs instead of performing a second shiny roll')

    def event_setup(r):
        r.write('wTempEnemyMonSpecies',153);r.write('wCurPartyLevel',25);r.write('wBattleMode',1);r.write('wBattleScriptFlags',128)
    r.run('LoadEnemyMon',event_setup)
    assert list(r.p.memory[addr('wEnemyMonDVs'):addr('wEnemyMonDVs')+2])[1]==0xaa
    ok('Scripted wild event is shiny independently of ordinary 20 percent roll')

    for initialized,value in [(False,[0,0]),(True,[0x3a,0xaa])]:
        r.roll=5 # old20% hook rejects this sample; forcedevent path must pass
        def roam(r):
            r.write('wTempEnemyMonSpecies',153);r.write('wCurPartyLevel',25);r.write('wBattleMode',1)
            r.write('wBattleType',5);r.write('wRoamMon1Species',153)
            r.write('wRoamMon1HP',1 if initialized else 0);dv(r,'wRoamMon1DVs',value)
        r.run('LoadEnemyMon',roam)
        stored=list(r.p.memory[addr('wEnemyMonDVs'):addr('wEnemyMonDVs')+2])
        assert stored[1]==0xaa and stored[0]&47==42,stored
        if initialized:assert stored==value,(stored,value)
    ok('Roaming event initializes shiny once and preserves the stored DVs on later encounters')


    # Deposit, ordinary withdrawal and direct captured-to-box paths retain DVs.
    for value in [[0x2a,0xaa],[0xfa,0xaa],[0x73,0x19]]:
        def init_box(r):
            r.p.memory[0x0000]=10;r.p.memory[0x4000]=1;r.p.memory[0xa000:0xc000]=[0]*8192;r.write('sBoxSpecies',255)
        def deposit(r):
            init_box(r);r.write('wPokemonWithdrawDepositParameter',1);r.write('wPartyCount',2)
            r.write('wPartySpecies',153);r.write('wCurPartySpecies',153);r.write('wPartyMon1Species',153)
            r.write('wPartyMon1Level',30);r.write('wPartyMon1Moves',196);r.write('wPartyMon1PP',15);dv(r,'wPartyMon1DVs',value)
        r.run('SendGetMonIntoFromBox',deposit)
        r.p.memory[0x0000]=10;r.p.memory[0x4000]=1
        assert list(r.p.memory[addr('sBoxMon1DVs'):addr('sBoxMon1DVs')+2])==value
        def withdraw(r):
            init_box(r);r.write('wPokemonWithdrawDepositParameter',0);r.write('wPartyCount',1)
            r.write('sBoxCount',1);r.write('sBoxSpecies',153);r.p.memory[addr('sBoxSpecies')+1]=255
            r.write('sBoxMon1Species',153);r.write('sBoxMon1Level',30);r.write('sBoxMon1Moves',196)
            dv(r,'sBoxMon1DVs',value);r.p.memory[addr('sBoxMon1Exp'):addr('sBoxMon1Exp')+3]=list((27000).to_bytes(3,'big'))
            r.write('wCurPartySpecies',153)
        r.run('SendGetMonIntoFromBox',withdraw)
        assert list(r.p.memory[addr('wPartyMon2DVs'):addr('wPartyMon2DVs')+2])==value
        def direct_box(r):
            init_box(r);r.write('wCurPartySpecies',153);r.write('wCurPartyLevel',25)
            r.write('wEnemyMonSpecies',153);r.write('wEnemyMonMoves',196);r.write('wEnemyMonPP',15);dv(r,'wEnemyMonDVs',value)
        r.run('SendMonIntoBox',direct_box)
        r.p.memory[0x0000]=10;r.p.memory[0x4000]=1
        assert list(r.p.memory[addr('sBoxMon1DVs'):addr('sBoxMon1DVs')+2])==value
    ok('Shiny and ordinary DVs survive party deposit, PC withdrawal and direct full-party capture storage')

    for move,power,typ in [(4,80,7),(132,90,7),(13,80,26),(140,85,26),(117,80,27),(119,70,27),(121,80,9),(159,80,9),(186,40,28)]:
        data=move_bytes(move);assert data[2]==power and data[3]&63==typ
    assert move_bytes(150)[2]==0 # Splash for Zurullo
    for move in [15,19,57,70,148,250,127]:assert move_bytes(move)[0]==move
    ok('Nine modern moves cover Bug/Fairy/Dragon/Dark/Steel; Splash and all7 HM identities remain intact')

    # Render selected Hidden Power and ordinary move info to actual tilemaps.
    for move,power,dvs in [(196,55,[0,0]),(237,70,[255,255]),(63,150,[0,0]),(45,0,[0,0])]:
        def setup(r):
            r.write('wMenuCursorY',1);r.write('wBattleMonMoves',move);r.write('wPartyMon1Moves',move)
            r.write('wBattleMonPP',10);r.write('wPartyMon1PP',10);r.write('wCurSpecies',move)
            dv(r,'wBattleMonDVs',dvs);dv(r,'wPartyMon1DVs',dvs)
            r.p.memory[addr('wTilemap'):addr('wTilemap')+360]=[0x7f]*360
        for label,x,y in [('MoveInfoBox',1,14),('PlaceMoveData',16,12)]:
            r.run(label,setup)
            start=addr('wTilemap')+y*20+x
            if label == 'MoveInfoBox' and 2 <= power < 100:
                expected=[0x8f]+[0xf6+int(c) for c in f'{power:02d}'] # P55
            else:
                expected=([0x7f]*(3-len(str(power)))+[0xf6+int(c) for c in str(power)]) if power else [0xe3]*3
            assert list(r.p.memory[start:start+3])==expected,(label,move,list(r.p.memory[start:start+3]),expected)
    ok('Battle and detailed move screen render true power, including70-power Hidden Power and status dashes')

    def stats_setup(r):
        r.p.memory[addr('wTempMonMoves'):addr('wTempMonMoves')+4]=[196,237,45,4]
        dv(r,'wTempMonDVs',[255,255])
        r.p.memory[addr('wTilemap'):addr('wTilemap')+360]=[0x7f]*360
    r.run('StatsScreen_PlaceMovePowers',stats_setup)
    for y,power in [(11,55),(13,70),(15,0),(17,80)]:
        pointer=addr('wTilemap')+y*20+5
        expected=([0x7f]*(3-len(str(power)))+[0xf6+int(c) for c in str(power)]) if power else [0xe3]*3
        assert list(r.p.memory[pointer:pointer+3])==expected,(y,power,list(r.p.memory[pointer:pointer+3]))
    ok('Actual stats-screen renderer shows each of four move powers alongside its PP line')

finally:r.close()
report={'passed':len(tests),'tests':tests,'rom':str(ROM)}
Path('work/v4-battle-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

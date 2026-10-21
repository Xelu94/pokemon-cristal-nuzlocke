"""Actual Ulex encounter/reward/theft and debug sandbox menu integration."""
import io
import json
import re
from pathlib import Path
from pyboy import PyBoy

root = Path('work/source')
tests = []


def check(name, condition=True):
    assert condition, name
    tests.append({'name': name, 'passed': True})
    print('PASS', name, flush=True)


maps = {}
group = number = 0
for line in (root/'constants/map_constants.asm').read_text().splitlines():
    if re.match(r'\s*newgroup ', line):
        group += 1
        number = 0
    match = re.match(r'\s*map_const (\w+)', line)
    if match:
        number += 1
        maps[match[1]] = [group, number]


class UI:
    def __init__(self, debug=False, steal=False):
        rom = root/('pokecristal_debug.gbc' if debug else 'pokecristal.gbc')
        self.symbols = {}
        for line in rom.with_suffix('.sym').read_text().splitlines():
            match = re.match(r'([\da-fA-F]+):([\da-fA-F]+)\s+(\S+)', line)
            if match:
                self.symbols[match[3]] = int(match[1],16), int(match[2],16)
        data = bytearray(rom.read_bytes())
        for name in ['PlayerProfileSetup','OakSpeech','ShrinkPlayer','_InitializeStartDay']:
            data[self.offset(name)] = 0xc9
        data[self.offset('Route31CheckMomCallCallback')] = 0x90
        spawn = self.offset('SpawnPoints')
        data[spawn:spawn+4] = bytes(maps['VIRIDIAN_POKECENTER_1F'] + [6,5] if debug else maps['ROUTE_31'] + [21,14])
        self.p = PyBoy(io.BytesIO(data),window='null',sound_emulated=False,log_level='ERROR')
        self.p.set_emulation_speed(0)
        self.counts = {}
        self.enemies = {}
        self.revealed = 0
        self.debug = debug
        for label in ['StartBattle','BattleStartMessage','WinTrainerBattle','UlexPrepareBattle',
                      'UlexCheckNewDeaths','UlexStealLivingMon','ReceiveRandomTM','StartMenu',
                      'StartMenu_Option','SandboxMenu','SandboxChooseDestination',
                      'SandboxMenu.loop','SandboxChooseStage','SandboxApplyStage',
                      'SandboxAdvanceStage','SandboxPrepareTeam','ScrollingMenu']:
            if label not in self.symbols:
                continue
            def hook(_, label=label):
                self.counts[label] = self.counts.get(label,0)+1
                if label == 'UlexCheckNewDeaths' and steal:
                    self.write('wUlexPreDeaths', 0)
                    self.word('wPartyMon1HP',0)
                    self.write('wPartyMon1CaughtLocation', self.read('wPartyMon1CaughtLocation')|128)
            self.p.hook_register(*self.symbols[label],hook,None)
        self.p.hook_register(*self.symbols['BattleCommand_ApplyDamage'], self.damage, None)
        self.p.hook_register(*self.symbols['UpdateEnemyHUD'], self.enemy, None)
        self.p.hook_register(*self.symbols['MapTextbox'], self.print_hook, None)
        self.p.tick(360)
        self.press('start',120)
        self.press('start',120)
        self.p.button_press('a');self.p.tick(32);self.p.button_release('a');self.p.tick(300)
        self.write('wOptions',(self.read('wOptions')&0x38)|0x41)
        self.party()

    def a(self, name): return self.symbols[name][1]
    def offset(self,name):
        bank,pointer=self.symbols[name]
        return bank*16384+pointer-16384 if bank else pointer
    def read(self,name):return self.p.memory[self.a(name)]
    def write(self,name,value):self.p.memory[self.a(name)]=value
    def word(self,name,value):self.p.memory[self.a(name):self.a(name)+2]=list(value.to_bytes(2,'big'))
    def mem(self,name,n):return list(self.p.memory[self.a(name):self.a(name)+n])
    def flag(self,n):return bool(self.p.memory[self.a('wEventFlags')+n//8]&(1<<(n%8)))
    def press(self,button='a',frames=100):
        self.p.button_press(button);self.p.tick(1 if button=='a' else 8)
        self.p.button_release(button);self.p.tick(frames)
    def until(self,label,count=1,maximum=60):
        for _ in range(maximum):
            if self.counts.get(label,0)>=count:return
            self.press()
        self.snap('failure-'+label)
        raise AssertionError((label,self.counts,self.p.register_file.PC))
    def snap(self,name):self.p.screen.image.save('work/v4-'+name+'.png')
    def close(self):self.p.stop(save=False)

    def party(self):
        stride=self.a('wPartyMon2')-self.a('wPartyMon1')
        self.write('wPartyCount',2)
        self.p.memory[self.a('wPartySpecies'):self.a('wPartySpecies')+3]=[150,6,255]
        for i,species in enumerate([150,6]):
            base=self.a('wPartyMon1')+stride*i
            self.p.memory[base:base+stride]=[0]*stride
            self.p.memory[base]=species
            self.p.memory[self.a('wPartyMon1Level')+stride*i]=19
            self.p.memory[self.a('wPartyMon1Moves')+stride*i:self.a('wPartyMon1Moves')+stride*i+4]=[33,57,58,53]
            self.p.memory[self.a('wPartyMon1PP')+stride*i:self.a('wPartyMon1PP')+stride*i+4]=[35,35,35,35]
            for stat in ['HP','MaxHP','Attack','Defense','Speed','SpclAtk','SpclDef']:
                pointer=self.a('wPartyMon1'+stat)+stride*i
                self.p.memory[pointer:pointer+2]=[3,231]
            pointer=self.a('wPartyMonNicknames')+11*i
            self.p.memory[pointer:pointer+11]=[0x93,0x84,0x92,0x93,0x50,0,0,0,0,0,0]
    def damage(self,_):
        if self.read('hBattleTurn')==0:self.word('wCurDamage',999)
    def enemy(self,_):
        if self.read('wOtherTrainerClass')!=69:return
        species=self.read('wEnemyMonSpecies')
        if species:self.enemies[species]={'level':self.read('wEnemyMonLevel'),'dvs':self.mem('wEnemyMonDVs',2)}
    def print_hook(self,_):
        if self.p.register_file.HL==self.a('UlexBattleScript.RevealText'):self.revealed+=1


for steal in [False,True]:
    u=UI(steal=steal)
    try:
        prefix='ulex-theft' if steal else 'ulex'
        u.snap(prefix+'-disguise')
        check(prefix+' starts at real Route31 encounter',u.mem('wMapGroup',2)==maps['ROUTE_31'])
        before_tm=sum(u.mem('wTMsHMs',50))
        before_var=u.p.memory[u.a('wVariableSprites')+11]
        u.press('up',10)
        for _ in range(25):
            if u.revealed:break
            u.press()
        u.p.tick(100)
        u.snap(prefix+'-revealed')
        after_var=u.p.memory[u.a('wVariableSprites')+11]
        check(prefix+' disguise spin reveals a different actual overworld sprite',u.revealed==1 and before_var!=after_var)
        u.until('BattleStartMessage')
        u.snap(prefix+'-portrait')
        check(prefix+' loads actual three-mon battle at cap19',u.read('wOTPartyCount')==3)
        for turn in range(250):
            # A result now commits its flags before map reload (including
            # whiteout). Wait for the actual post-battle reward/theft as well.
            completed = (u.counts.get('UlexStealLivingMon',0) if steal else
                         sum(u.mem('wTMsHMs',50)) == before_tm + 1)
            if (u.flag(531) and completed and u.read('wBattleMode')==0
                    and u.read('wMap3ObjectStructID')==255):break
            u.press()
        u.p.tick(120)
        u.snap(prefix+'-result')
        print('ULEX', prefix, u.enemies, u.counts, 'flags', u.flag(531), u.flag(547), flush=True)
        check(prefix+' defeats all three real shiny opponents at cap19',
              len(u.enemies)==3 and all(e['level']==19 and e['dvs'][0]&15==10
              and e['dvs'][0]&0x20 and e['dvs'][1]==0xaa for e in u.enemies.values()))
        check(prefix+' persists defeated location and badge milestone',u.flag(531) and u.flag(547))
        check(prefix+' removes the defeated actor from the map',u.read('wMap3ObjectStructID')==255)
        if steal:
            check('New death triggers real forced theft script instead of TM',u.counts.get('UlexStealLivingMon')==1 and sum(u.mem('wTMsHMs',50))==before_tm)
            check('Theft retains dead mon and gives level5 ZURULLO with only Splash',
                  u.mem('wPartySpecies',3)==[150,19,255] and u.read('wPartyMon2Level')==5
                  and u.mem('wPartyMon2Moves',4)==[150,0,0,0]
                  and u.mem('wPartyMonNicknames',18)[11:18]==[0x99,0x94,0x91,0x94,0x8b,0x8b,0x8e])
        else:
            check('Clean victory awards exactly one real random TM',sum(u.mem('wTMsHMs',50))==before_tm+1)
    finally:u.close()

for refusal in ['empty','dead']:
    u=UI()
    try:
        if refusal=='empty':
            u.write('wPartyCount',0)
            u.write('wPartySpecies',255)
        else:
            stride=u.a('wPartyMon2')-u.a('wPartyMon1')
            for i in range(2):
                pointer=u.a('wPartyMon1HP')+stride*i
                u.p.memory[pointer:pointer+2]=[0,0]
                pointer=u.a('wPartyMon1CaughtLocation')+stride*i
                u.p.memory[pointer]|=128
        u.press('up',10)
        u.until('StartBattle')
        u.p.tick(400)
        u.snap('ulex-refused-'+refusal)
        check('Ulex rejects actual '+refusal+' party without opening combat',
              u.counts.get('BattleStartMessage',0)==0 and u.read('wBattleResult')==2)
        check('Ulex '+refusal+' refusal retains both flags and the encounter actor',
              not u.flag(531) and not u.flag(547) and u.read('wUlexDidBattle')==0
              and u.read('wMap3ObjectStructID')!=255)
    finally:u.close()

u=UI(debug=True)
try:
    u.press('start',100)
    u.snap('sandbox-start-menu')
    items=u.mem('wMenuItemsList',10)
    length=items[0]
    option=items[1:1+length].index(5)+1
    current=u.read('wMenuCursorPosition')
    for _ in range(option-current):u.press('down',12)
    u.press()
    u.until('SandboxMenu')
    u.snap('sandbox-tools')
    check('Debug start menu opens real eight-action SANDBOX menu',u.counts.get('SandboxMenu')==1)
    pixels=list(u.p.screen.image.convert('RGB').getdata())
    check('Sandbox tools are visibly rendered after the menu fade',sum(rgb==(0,0,0) for rgb in pixels)>100)
    u.press('b')
    u.snap('sandbox-return-to-start')
    sandbox_name=[0x92,0x80,0x8d,0x83,0x81,0x8e,0x97]
    tilemap=u.mem('wTilemap',360)
    check('Closing sandbox restores a working start menu without double-pop',
          any(tilemap[i:i+7]==sandbox_name for i in range(354)))
    u.until('SandboxMenu',2)
    # Main sandbox cursor starts on VIAJAR; choose five medals in one operation.
    u.press('down',12);u.press()
    u.until('SandboxChooseStage')
    u.until('ScrollingMenu',1)
    u.p.tick(120)
    for _ in range(5):u.press('down',12)
    u.snap('sandbox-medal-selector-five')
    u.press()
    u.until('SandboxApplyStage')
    check('Sandbox UI selects five badges at once and recalculates the cap',
          u.read('wSandboxStage')==5 and u.read('wJohtoBadges')==47 and u.read('wSandboxCap')==44)
    # Finish stage text, loop to menu, then choose fourth entry for test team.
    u.until('SandboxMenu.loop',3)
    u.p.tick(120)  # loop hook precedes ClearTilemap/WaitBGMap and menu redraw
    for _ in range(3):u.press('down',12)
    u.press()
    u.until('SandboxPrepareTeam')
    u.snap('sandbox-team-created')
    check('Sandbox UI prepares its real three-shiny test team at43',
          u.mem('wPartySpecies',4)==[153,229,176,255] and u.read('wPartyMon1Level')==43)
    # Dismiss result text, select VIAJAR and inspect the genuine scrolling list.
    u.until('SandboxMenu.loop',4)
    u.p.tick(120)
    u.press()
    u.until('SandboxChooseDestination')
    u.until('ScrollingMenu')
    u.p.tick(120)
    u.snap('sandbox-destinations')
    countbank,countaddr=u.symbols['SandboxChooseDestination.List']
    check('Sandbox travel UI presents41 shortcuts plus the complete-map catalog',
          u.p.memory[countbank,countaddr]==42)
    check('Travel menu frame preserves input and game-loop state',
          u.read('wInputType')==0 and u.read('wGameLogicPaused')==0)
    u.p.button_press('a');u.p.tick(32);u.p.button_release('a');u.p.tick(400)
    for _ in range(8):
        if u.mem('wMapGroup',2)==maps['VIOLET_POKECENTER_1F']:break
        u.p.tick(120)
    u.snap('sandbox-warped')
    print('SANDBOX WARP',u.mem('wMapGroup',2),u.read('wSandboxWarpPending'),u.read('wSandboxDestination'),u.counts,hex(u.p.register_file.PC),flush=True)
    check('Sandbox UI executes an actual warp to selected Violet center',u.mem('wMapGroup',2)==maps['VIOLET_POKECENTER_1F'])
finally:u.close()

report={'passed':len(tests),'tests':tests,'fixtures':'Player damage999 only; theft branch adds one death at post-battle check; original battle and event scripts run.'}
Path('work/v41-root-ui-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

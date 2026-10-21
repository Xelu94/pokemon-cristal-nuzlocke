"""Check graphics actually assigned to Ulex and the real sandbox Items action."""
import json
from pathlib import Path
from PIL import Image

base=Path('work/test-v4-root-ui.py').read_text(encoding='utf8')
base=base[:base.index('for steal in [False,True]:')]
base=base.replace('def __init__(self, debug=False, steal=False):','def __init__(self, debug=False, steal=False, route="ROUTE_31", xy=(21,14)):')
base=base.replace("maps['ROUTE_31'] + [21,14]",'maps[route] + list(xy)')
# Freeze the cycling-road gravity only in the fixture; Ulex's script and all
# sprite allocation/loading stay unchanged on this map.
base=base.replace("data[self.offset('Route31CheckMomCallCallback')] = 0x90", "data[self.offset('Route31CheckMomCallCallback')] = 0x90\n        data[self.offset('Route17AlwaysOnBikeCallback')] = 0x90")
exec(base)
reports=[]

def sprite_bytes(u, sprite):
    entries=u.mem('wUsedSprites',64)
    assert sprite in entries[::2], (sprite, entries)
    tile=entries[entries[::2].index(sprite)*2+1]
    bank=0 if tile&128 else 1
    vram=0x8000+(tile&127)*16
    return tile,bytes(u.p.memory[bank,vram+i] for i in range(192))

routes=[]
import re
for path in (root/'maps').glob('Route*.asm'):
    source=path.read_text(encoding='utf8')
    m=re.search(r'object_event\s+(\d+),\s*(\d+), SPRITE_COPYCAT',source)
    if not m:continue
    route='ROUTE_'+path.stem.removeprefix('Route')
    # Stand one tile below the actor so talking targets the correct NPC.
    routes.append((route,(int(m[1]),int(m[2])+1),path.stem))

for route,xy,name in routes:
    u=UI(route=route,xy=xy)
    try:
        tile,loaded=sprite_bytes(u,251)
        actor=next(n for n in range(1,13) if u.read(f'wObject{n}Sprite')==251)
        assert u.read(f'wObject{actor}SpriteTile')&127==tile&127,(name,tile,u.read(f'wObject{actor}SpriteTile'))
        assert tile&127 != u.mem('wUsedSprites',2)[1]&127
        source=(root/'maps'/f'{name}.asm').read_text(encoding='utf8')
        disguise=re.search(r'variablesprite SPRITE_COPYCAT, (\w+)',source)[1]
        sprite_id=u.p.memory[u.a('wVariableSprites')+11]
        constants=(root/'constants/sprite_constants.asm').read_text(encoding='utf8')
        assert sprite_id not in (1,96),sprite_id
        # Compare VRAM to the actual disguise graphics, rather than its variable.
        bank,ptr=u.symbols['OverworldSprites']
        table=bytes(u.p.memory[bank,ptr+i] for i in range(6*103))
        entry=table[(sprite_id-1)*6:sprite_id*6]
        gfx=entry[0]+entry[1]*256;gbank=entry[3]
        expected=bytes(u.p.memory[gbank,gfx+i] for i in range(192))
        assert loaded==expected,(name,disguise,sprite_id)
        u.snap('v42-'+name+'-disguise')
        if name=='Route17':
            u.write('wBikeFlags',0)
        u.press('up',10)
        for _ in range(35):
            if u.revealed:break
            u.press()
        assert u.revealed==1,(name,u.counts)
        tile,revealed=sprite_bytes(u,251)
        rocket_id=0x42 # resolved below from actual variable and graphics table
        rocket_id=u.p.memory[u.a('wVariableSprites')+11]
        entry=table[(rocket_id-1)*6:rocket_id*6]
        gfx=entry[0]+entry[1]*256;gbank=entry[3]
        expected=bytes(u.p.memory[gbank,gfx+i] for i in range(192))
        assert revealed==expected and revealed!=loaded,(name,rocket_id)
        u.snap('v42-'+name+'-revealed')
        reports.append({'map':name,'disguise':disguise,'disguise_id':sprite_id,'reveal_id':rocket_id,'tile':tile,'correct_vram':True})
        print('PASS actual VRAM disguise and Rocket reveal',name,disguise,rocket_id,flush=True)
    finally:u.close()

u=UI(debug=True)
try:
    def grant_hook(_):u.counts['SandboxGiveItems']=u.counts.get('SandboxGiveItems',0)+1
    u.p.hook_register(*u.symbols['SandboxGiveItems'],grant_hook,None)
    u.press('start',100)
    items=u.mem('wMenuItemsList',10)
    option=items[1:1+items[0]].index(5)+1
    for _ in range(option-u.read('wMenuCursorPosition')):u.press('down',12)
    u.press();u.until('SandboxMenu');u.p.tick(120)
    before_tm=sum(u.mem('wTMsHMs',50))
    for _ in range(5):u.press('down',12)
    u.press();u.p.tick(120)
    assert u.counts.get('SandboxGiveItems')==1,u.counts
    u.snap('v42-sandbox-items-granted')
    assert sum(u.mem('wTMsHMs',50))==before_tm+7
    item_ids=[20,9,10,25,18,19] # verify quantities via the ROM's actual list
    bank,ptr=u.symbols['SandboxGiveItems.Items']
    item_ids=list(u.p.memory[bank,ptr:ptr+6])
    bag=u.mem('wItems',u.read('wNumItems')*2)
    quantities={item:sum(bag[i+1] for i in range(0,len(bag),2) if bag[i]==item) for item in item_ids}
    assert all(quantity>=10 for quantity in quantities.values()),quantities
    u.until('SandboxMenu.loop',2);u.p.tick(120)
    # Repeat a grant and return to the world through the actual menu.
    for _ in range(5):u.press('down',12)
    u.press();u.until('SandboxMenu.loop',3);u.p.tick(120)
    assert sum(u.mem('wTMsHMs',50))==before_tm+14
    u.press('b');u.press('b');u.p.tick(120)
    u.snap('v42-sandbox-items-return-world')
    assert u.read('wInputType')==0 and u.read('wGameLogicPaused')==0
    reports.append({'sandbox_items':True,'quantities':quantities,'tms_added_twice':14,'returns_to_world':True})
    print('PASS real sandbox Items twice, quantities, seven TMs each, return to world',flush=True)
finally:u.close()

Path('work/v42-fixes-tests.json').write_text(json.dumps({'passed':len(reports),'tests':reports},ensure_ascii=False,indent=2),encoding='utf8')

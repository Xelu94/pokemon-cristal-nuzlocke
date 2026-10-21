"""Validate rendered OAM tile order, not only the direction variable."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
base=Path('work/test-v4-tito.py').read_text(encoding='utf8')
exec(base[:base.index('c = Center()')])
c=Center()
try:
    p=c.p
    actor=next(n for n in range(1,13) if p.memory[addr(f'wObject{n}Sprite')]==103)
    tile=p.memory[addr(f'wObject{actor}SpriteTile')]&127
    poses=[]
    validated=[]
    for direction,name,frame in [(0,'FRENTE',0),(4,'ESPALDA',4),(8,'IZQUIERDA',8),(12,'DERECHA',8)]:
        p.memory[addr(f'wObject{actor}Direction')]=direction
        p.tick(40)
        c.snap('v42-'+name)
        oam=list(p.memory[0xfe00:0xfea0])
        entries=[oam[i:i+4] for i in range(0,160,4) if tile<=oam[i+2]<tile+12 and oam[i]>0]
        print(name,'tilebase',tile,'OAM',entries,flush=True)
        assert len(entries)==4,(name,entries)
        assert sorted(e[2] for e in entries)==list(range(tile+frame,tile+frame+4)),(name,entries)
        assert all(bool(e[3]&32)==(name=='DERECHA') for e in entries)
        x=min(e[1]-8 for e in entries);y=min(e[0]-16 for e in entries)
        # OAM hardware renders these four tiles as the physical 16x16 NPC.
        crop=p.screen.image.crop((x,y,x+16,y+16)).resize((128,128),Image.Resampling.NEAREST)
        poses.append((name,crop))
        validated.append({'pose':name,'tile_offsets':sorted(e[2]-tile for e in entries),'mirrored':name=='DERECHA','passed':True})
    preview=Image.new('RGB',(512,152),'white');draw=ImageDraw.Draw(preview)
    for i,(name,crop) in enumerate(poses):
        draw.text((i*128+4,4),name,fill='black');preview.paste(crop,(i*128,24))
    preview.save('work/v42-tito-directions.png')
    Path('work/v42-tito-directions-tests.json').write_text(json.dumps({'passed':4,'tests':validated},indent=2),encoding='utf8')
    print('PASS four real rendered facings use correct tile ranges and mirroring',flush=True)
finally:c.close()

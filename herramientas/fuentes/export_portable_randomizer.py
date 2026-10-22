"""Export the compiled address whitelist and an offline single-file HTML tool."""
from pathlib import Path
import collections,hashlib,json,re,sys
from balanced_randomizer import Randomizer,LEGENDS

ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/randomizer'
out.mkdir(parents=True,exist_ok=True)
rom=(ROOT/'pokecristal.gbc').read_bytes();sym={}
for bank,ptr,name in re.findall(r'^([0-9a-f]+):([0-9a-f]+) (\S+)',(ROOT/'pokecristal.sym').read_text(),re.M):
 bank,ptr=int(bank,16),int(ptr,16);sym[name]=bank*16384+ptr-16384 if bank else ptr
site_symbols={name.rsplit('.',1)[-1]:p for name,p in sym.items() if '.__RZ' in name}
def named(suffix):return site_symbols.get(suffix)
rand=Randomizer(20261019)
# Friendship/trade evolutions were changed after the original seed generator.
# Eligibility must follow the CURRENT methods, not the archived cartridge tables.
evos=(ROOT/'data/pokemon/evos_attacks.asm').read_text(encoding='utf8')
normal={re.sub('[^A-Z0-9]','',mon):mon for mon in rand.species}
for name,body in re.findall(r'^(\w+)EvosAttacks:\n(.*?)(?=^\w+EvosAttacks:|\Z)',evos,re.M|re.S):
 parent=normal.get(name.upper())
 if parent is None:continue # Dark Lugia is not part of the randomized species
 for threshold,child in re.findall(r'^\s*db EVOLVE_(?:LEVEL|STAT), (\d+), (?:[^\n,]+, )?([A-Z][A-Z0-9_]+)\s*$',body,re.M):
  if child in rand.ids:rand.parents[child]=(parent,int(threshold))
for mon in rand.species:
 current=mon;minimum=1
 while current in rand.parents:
  current,threshold=rand.parents[current];minimum=max(minimum,threshold)
 rand.minlevel[mon]=minimum
pools={};groups=collections.OrderedDict()
for site in json.loads((ROOT/'data/events/portable_randomizer_sites.json').read_text(encoding='utf8')):
 address=named(site['label'])
 if address is None:continue # unused maps are intentionally absent from the ROM
 address+=site['offset'];original=rand.ids[site['mon']]
 assert rom[address]==original,(site,hex(address),rom[address],original)
 key=site['group'];level=site['level'];kind=site['kind']
 poolkey='starter' if kind=='starter' else f'level{level}'
 if poolkey not in pools:
  if kind=='starter':
   pool=[s for s in rand.species if s not in rand.parents and s not in LEGENDS and 280<=rand.bst[s]<=340 and rand.evolutions[s]]
  else:pool=rand.pool(level)
  pools[poolkey]=[rand.ids[s] for s in pool]
 assert pools[poolkey]
 group=groups.setdefault(key,dict(key=key,pool=poolkey,kind=kind,original=original,sites=[]))
 group['sites'].append(address)
pools['egg']=[rand.ids[s] for s in rand.pool(5)]
trades=[]
for mon in rand.species:
 candidates=[other for other in rand.species if other!=mon and rand.trade_phase[other]==rand.trade_phase[mon] and abs(rand.bst[other]-rand.bst[mon])<=60 and rand.minlevel[other]<=rand.minlevel[mon] and (other in LEGENDS)==(mon in LEGENDS)]
 trades.append([rand.ids[x] for x in candidates] or [rand.ids[mon]])
stats={}
for mon in rand.species:
 stats[rand.ids[mon]]=dict(base=rand.stats[mon],exp5={'GROWTH_MEDIUM_FAST':125,'GROWTH_MEDIUM_SLOW':135,'GROWTH_FAST':100,'GROWTH_SLOW':156}[rand.growth[mon]])
party=sym['wPartyMon1'];stride=sym['wPartyMon2']-party
egg=dict(offset=sym['OddEggs'],stride=stride+11,dv=sym['wPartyMon1DVs']-party,exp=sym['wPartyMon1Exp']-party,stats=sym['wPartyMon1MaxHP']-party)
moveconst=(ROOT/'constants/move_constants.asm').read_text(encoding='utf8')
moveids={s:i for i,s in enumerate(re.findall(r'^\s*const ([A-Z][A-Z0-9_]+)',moveconst,re.M))}
assert moveids['STRUGGLE']==165
manifest=dict(version=4,length=len(rom),groups=list(groups.values()),pools=pools,trades=trades,tradeOffset=sym['BalancedTradePools'],tm=sym['TMHMMoves'],eggs=egg,stats=stats,moves=[i for i in range(1,255) if i!=165],names={v:k for k,v in rand.ids.items()})
mutable=[(a,1) for g in groups.values() for a in g['sites']]+[(manifest['tm'],50),(manifest['tradeOffset'],251*8),(0x14e,2)]
for i in range(20):
 address=egg['offset']+i*egg['stride']
 mutable.extend([(address,1),(address+egg['exp'],3),(address+egg['stats'],12)])
manifest['mutable']=mutable
# Preview data: Spanish names and the trainer slots of the gym leaders, Elite Four, champion, Blue and Red.
species_names=re.findall(r'^\s*(?:db|li|dname) "([^"@]+)@?"',(ROOT/'data/pokemon/names.asm').read_text(encoding='utf8'),re.M)
move_names=re.findall(r'^\s*(?:db|li|dname) "([^"@]+)@?"',(ROOT/'data/moves/names.asm').read_text(encoding='utf8'),re.M)
manifest['speciesNames']=species_names
manifest['moveNames']=move_names
LEADER_GROUPS=['Falkner','Bugsy','Whitney','Morty','Chuck','Jasmine','Pryce','Clair','Will','Koga','Bruno','Karen','Champion','LtSurge','Sabrina','Erika','Janine','Misty','Brock','Blaine','Blue','Red']
leaders=collections.OrderedDict();current=None
for line in (ROOT/'data/trainers/parties.asm').read_text(encoding='utf8').splitlines():
 m=re.match(r'^(\w+)Group:',line)
 if m:
  current=m[1] if m[1] in LEADER_GROUPS else None;continue
 m=re.match(r'\s*db "([^@]+)@", TRAINERTYPE',line)
 if m and current:
  if current not in leaders:leaders[current]={'name':m[1],'keys':[]} # extra parties of the same group (Super League) are not randomized
  continue
 m=re.match(r'^\.(__RZ\d+):',line)
 if m and current:leaders[current]['keys'].append(m[1])
manifest['leaders']=[leaders[g] for g in LEADER_GROUPS if g in leaders]
manifest['starterKeys']=[g['key'] for g in groups.values() if g['kind']=='starter']
masked=bytearray(rom)
for a,n in mutable:masked[a:a+n]=bytes(n)
manifest['immutableSHA256']=hashlib.sha256(masked).hexdigest()
(out/'manifest.json').write_text(json.dumps(manifest,separators=(',',':')),encoding='utf8')
js=(ROOT/'tools/portable_randomizer.js').read_text(encoding='utf8')
template=(ROOT/'tools/portable_randomizer.html').read_text(encoding='utf8')
html=template.replace('/*__CORE__*/',js).replace('/*__MANIFEST__*/',json.dumps(manifest,separators=(',',':')))
(out/'Randomizador.html').write_text(html,encoding='utf8')
print(json.dumps({'groups':len(groups),'sites':sum(len(g['sites']) for g in groups.values()),'sha256':manifest['immutableSHA256'],'html':str(out/'Randomizador.html')}))

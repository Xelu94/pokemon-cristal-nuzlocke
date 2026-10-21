'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const core=require('./source/tools/portable_randomizer.js');
const root=path.join(__dirname,'source'),rom=Uint8Array.from(fs.readFileSync(path.join(root,'pokecristal.gbc')));
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'v4-randomizer/manifest.json'),'utf8'));
const sites=JSON.parse(fs.readFileSync(path.join(root,'data/events/portable_randomizer_sites.json'),'utf8'));
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const checks=[];function ok(label){checks.push(label);console.log('PASS',label);}
const symbols={};for(const line of fs.readFileSync(path.join(root,'pokecristal.sym'),'utf8').split(/\r?\n/)){const m=line.match(/^([0-9a-f]+):([0-9a-f]+) (\S+)/);if(m){const bank=parseInt(m[1],16),ptr=parseInt(m[2],16);symbols[m[3]]=bank?bank*16384+ptr-16384:ptr;}}
const stats={};for(const [id,name] of Object.entries(manifest.names)){const text=fs.readFileSync(path.join(root,'data/pokemon/base_stats/'+name.toLowerCase()+'.asm'),'utf8');const m=text.match(/^\s*db\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/m);stats[+id]=m.slice(1).map(Number);}
const ids=Object.fromEntries(Object.entries(manifest.names).map(([k,v])=>[v,+k]));
const normalized=Object.fromEntries(Object.entries(ids).map(([k,v])=>[k.replace(/[^A-Z0-9]/g,''),v]));
const parents={},children={};
const evotext=fs.readFileSync(path.join(root,'data/pokemon/evos_attacks.asm'),'utf8');
for(const m of evotext.matchAll(/^(\w+)EvosAttacks:\n([\s\S]*?)(?=^\w+EvosAttacks:|$\s*(?![\s\S]))/gm)){
 const parent=normalized[m[1].toUpperCase()];
 for(const evo of m[2].matchAll(/^\s*db (EVOLVE_\w+), ([^\n;]+)/gm)){
  const parts=evo[2].split(',').map(s=>s.trim()),child=ids[parts.at(-1)];
  const bound=['EVOLVE_LEVEL','EVOLVE_STAT'].includes(evo[1])?+parts[0]:0;
  parents[child]={parent,level:bound};(children[parent]??=[]).push(child);
 }
}
function minLevel(id){let n=1,seen=new Set();while(parents[id]){assert(!seen.has(id),'evolution cycle');seen.add(id);n=Math.max(n,parents[id].level);id=parents[id].parent;}return n;}
function stage(id){return !children[id]?.length?2:parents[id]?1:0;}
const legends=new Set(['ARTICUNO','ZAPDOS','MOLTRES','MEWTWO','MEW','RAIKOU','ENTEI','SUICUNE','LUGIA','HO_OH','CELEBI'].map(n=>ids[n]));
const coverage=new Uint8Array(rom.length);for(const [a,n] of manifest.mutable){assert(a>=0&&n>0&&a+n<=rom.length);coverage.fill(1,a,a+n);}
assert.equal(digest(core.masked(rom,manifest)),manifest.immutableSHA256);
ok('Base ROM matches immutable version signature and every mutable range is in bounds');
const seedA='portfolio-test-A',seedB='portfolio-test-B';
const a=core.randomize(rom,manifest,seedA),b=core.randomize(rom,manifest,seedB),again=core.randomize(rom,manifest,seedA);
assert.deepEqual(a.bytes,again.bytes);assert.notDeepEqual(a.bytes,b.bytes);assert.deepEqual(rom,Uint8Array.from(fs.readFileSync(path.join(root,'pokecristal.gbc'))));
ok('Same seed is byte-identical; different seeds differ; source buffer remains unchanged');
assert.deepEqual(core.randomize(b.bytes,manifest,seedA).bytes,a.bytes);
assert.equal(digest(core.masked(b.bytes,manifest)),manifest.immutableSHA256);
ok('Previously generated variants are compatible and reseeding them reproduces canonical output');
let changed=0;for(let i=0;i<rom.length;i++)if(a.bytes[i]!==rom[i]){assert(coverage[i],`immutable byte changed at${i.toString(16)}`);changed++;}
assert(changed>1000);
assert.deepEqual(a.bytes.slice(0x100,0x14e),rom.slice(0x100,0x14e));
assert.deepEqual(a.bytes.slice(manifest.tm+50,manifest.tm+57),rom.slice(manifest.tm+50,manifest.tm+57));
for(const [name,n] of [['GetCurrentLevelCap',90],['BattleCommand_ApplyDamage',100],['RandomizeFourMoves',100],['TitoXeluisGroup',19]]){const at=symbols[name];assert(Number.isInteger(at),name);assert.deepEqual(a.bytes.slice(at,at+n),rom.slice(at,at+n),name);}
const tito=symbols.TitoXeluisGroup;let first=tito;while(rom[first]!==0x50)first++;first+=2;const team=[6,248,149,94,212,150];for(let i=0;i<6;i++){assert.equal(a.bytes[first+i*2],100);assert.equal(a.bytes[first+1+i*2],team[i]);}
ok('Every changed byte is whitelisted; cartridge code, caps, HM table and fixed level100 Tito team remain intact');
for(const group of manifest.groups){const pool=manifest.pools[group.pool];assert(pool.length&&new Set(pool).size===pool.length);for(const id of pool){assert(id>=1&&id<=251);if(group.kind==='starter'){assert(!parents[id]&&children[id]?.length&&!legends.has(id));const bst=stats[id].reduce((a,b)=>a+b,0);assert(bst>=280&&bst<=340);}else{const level=+group.pool.slice(5);assert(minLevel(id)<=level,`${manifest.names[id]} requires${minLevel(id)} atpool${group.pool}`);if(level<55)assert(!legends.has(id),`${manifest.names[id]} legendary below55`);if(level<10)assert(stats[id].reduce((a,b)=>a+b,0)<=360);}}
 for(const output of [a,b]){const chosen=output.bytes[group.sites[0]];assert(pool.includes(chosen));for(const address of group.sites)assert.equal(output.bytes[address],chosen);}
}
assert.equal(a.starters.length,3);assert.equal(new Set(a.starters).size,3);
ok('All species pools obey current evolution thresholds, early strength limits and legendary gating; starters are three distinct unevolved species');
const sitebylabel=Object.fromEntries(sites.map(s=>[s.label,s]));
const symbylabel=Object.fromEntries(Object.entries(symbols).filter(([n])=>n.includes('.__RZ')).map(([n,p])=>[n.split('.').at(-1),p]));
for(const site of sites){const at=symbylabel[site.label];if(at===undefined)continue;const address=at+site.offset;
 const group=manifest.groups.find(g=>g.key===site.group);assert(group?.sites.includes(address));
 // Operands at offsets1 (trainer and wild rows) retain preceding level bytes.
 if(['wild','trainer'].includes(site.kind)&&site.offset===1){assert.equal(a.bytes[address-1],rom[address-1]);assert.equal(b.bytes[address-1],rom[address-1]);}
}
ok('Compiled site whitelist covers the source declarations; every existing wild/trainer level byte is preserved');
for(const output of [a,b]){assert.equal(new Set(output.tms).size,50);for(const move of output.tms)assert(move>=1&&move<=254&&move!==165);for(let i=0;i<251;i++){const source=i+1;for(let j=0;j<8;j++){const target=output.bytes[manifest.tradeOffset+i*8+j];assert(manifest.trades[i].includes(target));assert.equal(stage(source),stage(target));assert.equal(legends.has(source),legends.has(target));assert(Math.abs(stats[source].reduce((a,b)=>a+b,0)-stats[target].reduce((a,b)=>a+b,0))<=60||source===target);}}}
ok('50 unique valid TMs and all251x8 balanced trade mappings preserve stage/strength/legend status');
function big(bytes,a,n){let v=0;for(let i=0;i<n;i++)v=v*256+bytes[a+i];return v;}
const e=manifest.eggs;let shinies=0;
for(let i=0;i<20;i++){const at=e.offset+i*e.stride,id=a.bytes[at],s=manifest.stats[id];assert(manifest.pools.egg.includes(id));assert(!parents[id]&&!legends.has(id));assert.equal(a.bytes[at+31],5);assert.equal(big(a.bytes,at+33,2),0);assert.equal(big(a.bytes,at+e.exp,3),s.exp5);
 const dv0=a.bytes[at+e.dv],dv1=a.bytes[at+e.dv+1],atk=dv0>>4,def=dv0&15,speed=dv1>>4,special=dv1&15,hp=((atk&1)<<3)|((def&1)<<2)|((speed&1)<<1)|(special&1);const dvs=[hp,atk,def,speed,special,special];
 for(let j=0;j<6;j++)assert.equal(big(a.bytes,at+e.stats+2*j,2),Math.floor((stats[id][j]+dvs[j])*5/50)+(j?5:15));
 assert.deepEqual(a.bytes.slice(at+e.dv,at+e.dv+2),rom.slice(at+e.dv,at+e.dv+2));if(dv1===0xaa&&(dv0&0x2f)===0x2a)shinies++;
}
assert.equal(shinies,4);
ok('All20 eggs have valid first-stage species, level5 EXP/stats/currentHP0, preserved DVs and four shiny slots');
for(const output of [a,b]){let sum=0;for(let i=0;i<output.bytes.length;i++)if(i!==0x14e&&i!==0x14f)sum=(sum+output.bytes[i])&65535;assert.equal(big(output.bytes,0x14e,2),sum);}
assert.throws(()=>core.randomize(rom.slice(1),manifest,seedA));assert.throws(()=>core.randomize(rom,manifest,' '));
ok('Global cartridge checksums are correct and invalid size/empty seed are rejected');
const out=path.join(__dirname,'v4-randomizer-seed-a.gbc');fs.writeFileSync(out,a.bytes);fs.copyFileSync(path.join(root,'pokecristal.sym'),out.replace(/\.gbc$/,'.sym'));
const report={passed:checks.length,checks,baseSHA256:digest(rom),generatedSHA256:digest(a.bytes),differentSeedSHA256:digest(b.bytes),changedBytes:changed,starters:a.starters,groups:manifest.groups.length,sites:a.sites,rom:path.basename(out)};fs.writeFileSync(path.join(__dirname,'v4-randomizer-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));

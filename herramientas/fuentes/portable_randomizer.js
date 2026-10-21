/* Pure offline reseeding core. The manifest exposes operands, never executable code. */
(function(root){
 'use strict';
 function rng(seed){
  let x=2166136261;for(const c of String(seed)){x^=c.charCodeAt(0);x=Math.imul(x,16777619)>>>0;}
  if(!x)x=0x9e3779b9;
  return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n;};
 }
 function shuffled(values,roll){
  const a=values.slice();for(let i=a.length-1;i>0;i--){const j=roll(i+1);[a[i],a[j]]=[a[j],a[i]];}return a;
 }
 function masked(bytes,m){
  const b=Uint8Array.from(bytes);for(const [a,n] of m.mutable)b.fill(0,a,a+n);return b;
 }
 function randomize(bytes,m,seed){
  if(bytes.length!==m.length)throw Error('El tamaño no corresponde a esta versión del juego.');
  if(!String(seed).trim())throw Error('Introduce una semilla.');
  const b=Uint8Array.from(bytes),roll=rng(seed),starters=new Set(),chosen={};
  for(const group of m.groups){
   let pool=m.pools[group.pool];
   if(group.kind==='starter')pool=pool.filter(x=>!starters.has(x));
   if(pool.length>1)pool=pool.filter(x=>x!==group.original);
   const mon=pool[roll(pool.length)];chosen[group.key]=mon;
   if(group.kind==='starter')starters.add(mon);
   for(const address of group.sites)b[address]=mon;
  }
  const tms=shuffled(m.moves,roll).slice(0,50);b.set(tms,m.tm);
  for(let i=0;i<m.trades.length;i++){
   const pool=shuffled(m.trades[i],roll);
   for(let j=0;j<8;j++)b[m.tradeOffset+i*8+j]=pool[j%pool.length];
  }
  function big(address,n,length){for(let i=length-1;i>=0;i--){b[address+i]=n&255;n>>>=8;}}
  for(let i=0;i<20;i++){
   const address=m.eggs.offset+i*m.eggs.stride;
   const pool=m.pools.egg,mon=pool[roll(pool.length)],s=m.stats[mon];
   b[address]=mon;
   const dv0=b[address+m.eggs.dv],dv1=b[address+m.eggs.dv+1];
   const atk=dv0>>4,def=dv0&15,speed=dv1>>4,special=dv1&15;
   const hp=((atk&1)<<3)|((def&1)<<2)|((speed&1)<<1)|(special&1);
   const dvs=[hp,atk,def,speed,special,special];
   for(let j=0;j<6;j++)big(address+m.eggs.stats+2*j,Math.floor((s.base[j]+dvs[j])*10/100)+(j===0?15:5),2);
   big(address+m.eggs.exp,s.exp5,3);
  }
  // Cartridge global checksum excludes its own two bytes; no gameplay bytes change.
  let sum=0;for(let i=0;i<b.length;i++)if(i!==0x14e&&i!==0x14f)sum=(sum+b[i])&65535;
  b[0x14e]=sum>>8;b[0x14f]=sum&255;
  return {bytes:b,seed:String(seed),starters:m.groups.filter(g=>g.kind==='starter').map(g=>chosen[g.key]),sites:m.groups.reduce((n,g)=>n+g.sites.length,0),tms};
 }
 const api={randomize,masked,rng};
 if(typeof module!=='undefined')module.exports=api;else root.CristalRandomizer=api;
})(typeof globalThis!=='undefined'?globalThis:this);

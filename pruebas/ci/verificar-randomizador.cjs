'use strict';
// Comprueba que Randomizador.html funciona con la ROM indicada, sin navegador:
// node verificar-randomizador.cjs <Randomizador.html> <ROM.gbc>
// Extrae el núcleo y el manifiesto incrustados en el HTML (lo que usa el usuario) y los ejecuta.
const fs = require('fs'), assert = require('assert/strict'), crypto = require('crypto');

const [htmlPath, romPath] = process.argv.slice(2);
if (!htmlPath || !romPath) { console.error('Uso: node verificar-randomizador.cjs <Randomizador.html> <ROM.gbc>'); process.exit(2); }

const html = fs.readFileSync(htmlPath, 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
assert(scripts.length >= 2, 'el HTML debe incluir el núcleo y el manifiesto');
const module_ = { exports: {} };
new Function('module', 'root', scripts[0])(module_, {});
const core = module_.exports;
assert.equal(typeof core.randomize, 'function');
const manifestText = scripts[1].match(/const manifest=(\{[\s\S]*?\});\s*\n/);
assert(manifestText, 'manifiesto no encontrado');
const manifest = JSON.parse(manifestText[1]);

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const rom = Uint8Array.from(fs.readFileSync(romPath));
const checks = [];
function ok(label) { checks.push(label); console.log('PASS', label); }

assert.equal(rom.length, manifest.length);
assert.equal(sha(core.masked(rom, manifest)), manifest.immutableSHA256);
ok('la ROM coincide con la firma de la parte inmutable del manifiesto');

const a = core.randomize(rom, manifest, 'ci-A'), b = core.randomize(rom, manifest, 'ci-B'), again = core.randomize(rom, manifest, 'ci-A');
assert.deepEqual(a.bytes, again.bytes);
assert.notDeepEqual(a.bytes, b.bytes);
ok('la misma semilla da el mismo resultado y otra semilla da uno distinto');

const mutable = new Uint8Array(rom.length);
for (const [address, length] of manifest.mutable) { assert(address >= 0 && length > 0 && address + length <= rom.length); mutable.fill(1, address, address + length); }
let changed = 0;
for (let i = 0; i < rom.length; i++) if (a.bytes[i] !== rom[i]) { assert(mutable[i], 'byte inmutable modificado en 0x' + i.toString(16)); changed++; }
assert(changed > 1000);
assert.equal(sha(core.masked(a.bytes, manifest)), manifest.immutableSHA256);
ok('solo cambian bytes de los rangos mutables (' + changed + ' bytes)');

assert.deepEqual(core.randomize(b.bytes, manifest, 'ci-A').bytes, a.bytes);
ok('una ROM ya generada se puede volver a aleatorizar con el mismo resultado canónico');

if (manifest.leaders) {
  assert.equal(manifest.leaders.length, 22);
  assert(manifest.leaders.every(group => group.name && group.keys.length > 0));
  assert(a.chosen, 'la vista previa necesita las elecciones');
  ok('el manifiesto trae los 22 grupos de la vista previa y el núcleo devuelve las elecciones');
}

console.log(JSON.stringify({ passed: checks.length, rom: sha(rom) }));

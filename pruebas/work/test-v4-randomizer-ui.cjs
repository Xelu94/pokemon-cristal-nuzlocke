const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
const core=require('./source/tools/portable_randomizer.js');
const manifest=JSON.parse(fs.readFileSync('work/v4-randomizer/manifest.json'));
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHANNEL ? {channel:process.env.PLAYWRIGHT_CHANNEL} : {})});
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1100,height:1000}});
 const page=await context.newPage(),errors=[],requests=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
 try{
  await page.goto(pathToFileURL(path.resolve('work/v4-randomizer/Randomizador.html')).href);
  await page.locator('#rom').setInputFiles('work/source/pokecristal.gbc');
  await page.locator('#seed').fill('aventura-2026');
  const download=page.waitForEvent('download');await page.locator('#generate').click();
  const got=await download;await got.saveAs(path.resolve('work/v4-randomizer-ui-test.gbc'));
  const bytes=fs.readFileSync('work/source/pokecristal.gbc'),actual=fs.readFileSync('work/v4-randomizer-ui-test.gbc');
  if(!actual.equals(Buffer.from(core.randomize(bytes,manifest,'aventura-2026').bytes)))throw Error('Browser and core output differ');
  if(!await page.locator('#status').textContent().then(t=>t.includes('ROM generada')))throw Error('No success status');
  await page.screenshot({path:'work/v4-randomizer-screen.png',fullPage:true});
  const invalid=Buffer.from(bytes);invalid[0x100]^=1;
  await page.locator('#rom').setInputFiles({name:'incorrecta.gbc',mimeType:'application/octet-stream',buffer:invalid});
  await page.locator('#generate').click();await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('no es compatible'));
  await page.locator('#rom').setInputFiles('work/v4-randomizer-ui-test.gbc');await page.locator('#seed').fill('segunda-aventura');
  const second=page.waitForEvent('download');await page.locator('#generate').click();await (await second).saveAs(path.resolve('work/v4-randomizer-ui-test2.gbc'));
  if(fs.readFileSync('work/v4-randomizer-ui-test2.gbc').equals(actual))throw Error('Second seed identical');
  if(errors.length)throw Error(errors.join('\n'));
  if(requests.some(u=>!u.startsWith('file:')&&!u.startsWith('blob:')))throw Error('Unexpected network request');
  const report={passed:4,tests:['Actual offline browser selection/generation/download matches pure core','Incompatible ROM rejected before any mutation','Generated ROM can be reseeded and produces a different adventure','No network requests or browser script errors'],browser:process.env.PLAYWRIGHT_CHANNEL || 'Playwright Chromium headless',sha256:crypto.createHash('sha256').update(bytes).digest('hex')};
  fs.writeFileSync('work/v4-randomizer-ui-tests.json',JSON.stringify(report,null,2));console.log(report);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

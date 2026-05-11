const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ 
    args: ['--no-sandbox','--enable-webgl','--use-gl=swiftshader'] 
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.substring(0,150)));
  
  await page.goto('http://localhost:3000/index.html', { waitUntil: 'domcontentloaded', timeout: 10000 });
  await page.waitForTimeout(3000);
  
  await page.evaluate(() => document.querySelector('#menuScr .mbtn.primary')?.click());
  await page.waitForTimeout(400);
  await page.evaluate(() => document.querySelector('.course-item')?.click());
  await page.waitForTimeout(6000);
  
  await page.screenshot({ path: 'v18b_fly.png' });
  console.log('Flyover taken');
  
  await page.evaluate(() => { if(window.endFly) window.endFly(); });
  await page.waitForTimeout(2500);
  
  await page.screenshot({ path: 'v18b_game.png' });
  console.log('Game taken');
  
  const d = await page.evaluate(() => window._dbg ? window._dbg() : 'none');
  console.log('DBG:', JSON.stringify(d));
  
  if(errors.length) console.log('ERRORS:', errors.join(' | '));
  else console.log('ERRORS: NONE');
  
  await browser.close();
  console.log('DONE');
})();

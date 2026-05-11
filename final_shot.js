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
  
  // Wait longer for flyover to progress to mid-point
  await page.waitForTimeout(8000);
  await page.screenshot({ path: 'v18c_fly_mid.png' });
  console.log('Flyover mid taken');
  
  // Skip flyover
  await page.evaluate(() => { if(window.endFly) window.endFly(); });
  await page.waitForTimeout(2500);
  
  await page.screenshot({ path: 'v18c_game.png' });
  console.log('Game taken');
  
  // Also try a second course (longer course) for variety
  // Simulate swing to see ball flight camera
  await page.evaluate(() => {
    if(window.onSwTap) {
      // Start swing
      window.onSwTap({preventDefault:()=>{}});
    }
  });
  await page.waitForTimeout(500);
  // Set power
  await page.evaluate(() => {
    const G = window.G || null;
    if(G) { G.gaugeVal = 70; }
    if(window.onSwTap) window.onSwTap({preventDefault:()=>{}});
  });
  await page.waitForTimeout(500);
  // Set accuracy
  await page.evaluate(() => {
    const G = window.G || null;
    if(G) { G.accVal = 50; }
    if(window.onSwTap) window.onSwTap({preventDefault:()=>{}});
  });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'v18c_swing.png' });
  console.log('Swing taken');
  
  const d = await page.evaluate(() => window._dbg ? window._dbg() : 'none');
  console.log('DBG:', JSON.stringify(d));
  
  if(errors.length) console.log('ERRORS:', errors.join(' | '));
  else console.log('ERRORS: NONE');
  
  await browser.close();
  console.log('DONE');
})();

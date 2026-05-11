const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ 
    args: ['--use-gl=swiftshader','--no-sandbox'] 
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  
  // Collect console errors
  const errors = [];
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(e.message));
  
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  
  // Screenshot title screen
  await page.screenshot({ path: 'shot_title.png' });
  console.log('Title screen captured');
  
  // Click start button
  const startBtn = await page.$('#startBtn');
  if (startBtn) {
    await startBtn.click();
    console.log('Clicked start');
    await page.waitForTimeout(1500);
  }
  
  // Screenshot after start (might be flyover or game)
  await page.screenshot({ path: 'shot_start.png' });
  
  // Try to skip flyover
  try {
    await page.evaluate(() => { if(window.endFly) window.endFly(); });
    console.log('Called endFly');
    await page.waitForTimeout(1000);
  } catch(e) { console.log('endFly error:', e.message); }
  
  // Screenshot gameplay
  await page.screenshot({ path: 'shot_game.png' });
  
  // Get debug info
  let dbg = null;
  try {
    dbg = await page.evaluate(() => window._dbg ? window._dbg() : null);
  } catch(e) {}
  
  console.log('\n=== VERIFICATION ===');
  console.log('JS Errors:', errors.length === 0 ? 'NONE ✅' : errors.join('; '));
  if (dbg) {
    console.log('State:', dbg.state);
    console.log('Golfer visible:', dbg.golferVis);
    console.log('Golfer pos:', dbg.golferPos);
    console.log('Ball:', JSON.stringify(dbg.ball));
    console.log('Aim:', dbg.aim);
    console.log('AimLine visible:', dbg.aimLineVis);
    console.log('Camera:', JSON.stringify(dbg.cam));
  }
  
  await browser.close();
  console.log('\nDone!');
})();

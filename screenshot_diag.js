const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox','--disable-gpu'] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  
  const errors = [];
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(e.message));
  
  await page.goto('http://localhost:3000/index.html', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  
  // Title screen
  await page.screenshot({ path: 'diag_menu.png' });
  console.log('Menu screenshot taken');
  
  // Start game - click 전국투어
  await page.click('text=전국투어');
  await page.waitForTimeout(500);
  // Select first course
  await page.click('.course-item');
  await page.waitForTimeout(3000);
  
  // Flyover screenshot
  await page.screenshot({ path: 'diag_flyover.png' });
  console.log('Flyover screenshot taken');
  
  // Skip flyover
  await page.click('#flySk');
  await page.waitForTimeout(1500);
  
  // Game view screenshot
  await page.screenshot({ path: 'diag_game.png' });
  console.log('Game screenshot taken');
  
  // Get debug info
  const dbg = await page.evaluate(() => {
    if(window._dbg) return window._dbg();
    return 'no debug';
  });
  console.log('DEBUG:', JSON.stringify(dbg, null, 2));
  
  // Check golfer size on screen
  const golferInfo = await page.evaluate(() => {
    const cam = window.camera || null;
    const g = window.golfer || null;
    if(!cam || !g) return 'no golfer/camera';
    return {
      golferWorldPos: { x: g.position.x, y: g.position.y, z: g.position.z },
      golferScale: { x: g.scale.x, y: g.scale.y, z: g.scale.z },
      golferVisible: g.visible,
      cameraPos: { x: cam.position.x, y: cam.position.y, z: cam.position.z },
      childCount: g.children.length
    };
  });
  console.log('GOLFER:', JSON.stringify(golferInfo, null, 2));
  
  if(errors.length) console.log('ERRORS:', errors.join('\n'));
  else console.log('ERRORS: NONE');
  
  await browser.close();
})();

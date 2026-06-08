const pw = require('playwright');
(async () => {
  const browser = await pw.chromium.launch();
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  
  // Navigate and extract the cached page HTML
  await page.goto('https://3000-i42s5oyu570kv8t20wswg-b237eb32.sandbox.novita.ai', {waitUntil: 'networkidle', timeout: 30000});
  
  const html = await page.content();
  const fs = require('fs');
  fs.writeFileSync('/home/user/webapp/cached_app.html', html);
  console.log('Extracted HTML length:', html.length);
  console.log('Title:', await page.title());
  
  await browser.close();
})();

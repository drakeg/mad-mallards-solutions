import { chromium } from 'playwright-core';
import fs from 'node:fs';

const CHROME = process.env.SCROLLCRAFT_CHROME ||
  (fs.existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : chromium.executablePath());
const root = process.env.MMS_PAGES_TEST_URL || 'http://127.0.0.1:8127/mad-mallards-solutions/';
const browser = await chromium.launch({headless:true,executablePath:CHROME});
let failures = 0;
for (const viewport of [{width:1440,height:900}, {width:390,height:844}]) {
  const page = await browser.newPage({viewport});
  const errors = [];
  page.on('pageerror', error => errors.push('JS error: ' + error.message));
  page.on('response', response => {
    if (response.status() >= 400 && response.url().startsWith(root.split('/mad-mallards-solutions/')[0]))
      errors.push('HTTP ' + response.status() + ' ' + response.url());
  });
  await page.goto(root, {waitUntil:'networkidle'});
  if (!await page.title().then(t => t.includes('Mad Mallards Solutions'))) errors.push('Wrong title');
  if (await page.locator('form').count()) errors.push('Public static preview must not have forms');
  if (!await page.getByText('Contact form coming soon').isVisible()) errors.push('Contact notice missing');
  if (!await page.getByText('Newsletter signup coming soon').isVisible()) errors.push('Subscribe notice missing');
  await page.locator('[data-case="1"]').click();
  if (!await page.locator('#after-title').innerText().then(t => t.includes('A clearer foundation'))) errors.push('Interactive comparison broken');
  const dims = await page.evaluate(() => ({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
  if (dims.scroll > dims.width + 2) errors.push('Horizontal scroll overflow');
  if(viewport.width === 390) {
    await page.locator('.menu-toggle').click();
    if (!await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Journal',exact:true}).isVisible()) errors.push('Mobile navigation hidden');
  }
  await page.goto(root + 'blog/',{waitUntil:'networkidle'});
  if (!await page.getByRole('heading',{name:'Automation without the hype'}).isVisible()) errors.push('Blog links broken');
  await page.locator('a[href*="automation-without-the-hype.html"]').first().click();
  if (!await page.getByRole('heading',{name:'Automation without the hype'}).isVisible()) errors.push('Article broken');
  console.log(JSON.stringify({viewport:viewport.width,results:errors.length ? errors : 'pass'}));
  if (errors.length) failures++;
  await page.close();
}
await browser.close();
if (failures) process.exitCode = 1;

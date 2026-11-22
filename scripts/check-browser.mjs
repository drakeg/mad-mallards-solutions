import { chromium } from 'playwright-core';
import fs from 'node:fs';
const browser = await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-features=PointerLock,MouseCapture']});
let failures=0;
for (const mode of [{name:'desktop',width:1440,height:900},{name:'mobile',width:390,height:844},{name:'reduced',width:390,height:844,reducedMotion:'reduce'}]) {
 const context=await browser.newContext({viewport:{width:mode.width,height:mode.height},reducedMotion:mode.reducedMotion??'no-preference',serviceWorkers:'block'});
 const page=await context.newPage();
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto('http://127.0.0.1:8097/',{waitUntil:'networkidle'});
 await page.screenshot({path:'screenshots/'+mode.name+'-top.png'});
 const sizes=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,scrollHeight:document.documentElement.scrollHeight,heroVisible:document.querySelector('h1').getBoundingClientRect().width>100,actCount:document.querySelectorAll('[data-sc-act]').length}));
 await page.locator('[data-case="2"]').click();
 const outcome=await page.locator('#after-title').innerText();
 if (mode.name==='mobile') {
   await page.locator('.menu-toggle').click();
   if (await page.locator('.topbar nav').evaluate(el=>getComputedStyle(el).display)==='none')errors.push('Mobile menu not visible');
   await page.locator('.menu-toggle').click();
 }
 const step=Math.max(1,Math.floor((sizes.scrollHeight-mode.height)/5));
 for(let i=1;i<=5;i++){
   await page.evaluate(y=>window.scrollTo(0,y),step*i);
   await page.waitForTimeout(300);
   if(i===3)await page.screenshot({path:'screenshots/'+mode.name+'-middle.png'});
 }
 await page.screenshot({path:'screenshots/'+mode.name+'-bottom.png'});
 if(sizes.scrollWidth>sizes.clientWidth+2)errors.push('Horizontal overflow '+sizes.scrollWidth+'/'+sizes.clientWidth);
 if(outcome!=='Fewer blind spots.')errors.push('Comparison interactive control failed');
 if(errors.length)failures++;
 console.log(JSON.stringify({mode:mode.name,sizes,outcome,errors}));
 await context.close();
}
const page=await browser.newPage();
await page.goto('http://127.0.0.1:8097/');
await page.locator('#name').fill('Browser Tester');
await page.locator('#email').fill('browser-test@example.invalid');
await page.locator('#message').fill('A browser test enquiry regarding site consulting services.');
await page.locator('#contact-form button[type="submit"]').click();
await page.waitForFunction(() => document.querySelector('#contact-status').textContent.includes('Message saved'),{timeout:5000});
console.log(JSON.stringify({formStatus:await page.locator('#contact-status').innerText()}));
await browser.close();
if(failures)process.exitCode=1;

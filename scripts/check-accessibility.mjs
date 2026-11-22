import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
const macChrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const executablePath=process.env.SCROLLCRAFT_CHROME || (fs.existsSync(macChrome)?macChrome:chromium.executablePath());
const browser=await chromium.launch({headless:true,executablePath,args:['--disable-features=PointerLock,MouseCapture']});
const axe=fs.readFileSync(path.resolve('node_modules/axe-core/axe.min.js'),'utf8');
let violations=0;
for(const pagePath of ['/','/blog/','/blog/automation-without-the-hype.html','/privacy.html']){
 const context=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
 const page=await context.newPage();
 await page.goto((process.env.MMS_BASE_URL || 'http://127.0.0.1:8099')+pagePath,{waitUntil:'networkidle'});
 await page.evaluate(axe);
 const results=await page.evaluate(()=>window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
 for(const v of results.violations){
   violations++;
   console.log(JSON.stringify({page:pagePath,id:v.id,impact:v.impact,description:v.help,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary?.slice(0,160)})).slice(0,8)}));
 }
 console.log(pagePath,'checked',results.passes.length,'rules passed',results.violations.length,'violations');
 await context.close();
}
await browser.close();
if(violations)process.exitCode=1;

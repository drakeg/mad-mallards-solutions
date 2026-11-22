'use strict';
if (window.ScrollCraft) window.ScrollCraft.mount(document.body);
document.getElementById('year').textContent = new Date().getFullYear();
document.querySelector('.footer-bottom a[href="#content"]').addEventListener('click', e => {e.preventDefault();window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
const toggle = document.querySelector('.menu-toggle'), nav = document.querySelector('.topbar nav');
toggle.addEventListener('click', () => {const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));toggle.textContent=open?'Menu':'Close';nav.classList.toggle('open',!open);});
nav.addEventListener('click', e=>{if(e.target.closest('a')) {nav.classList.remove('open');toggle.setAttribute('aria-expanded','false');toggle.textContent='Menu';}});
const cases=[
 ['Same task. Again.','Manual handoffs, duplicate entry, and important work waiting in someone’s inbox.','A workflow that flows.','Connected steps, useful visibility, and fewer repetitive decisions.'],
 ['Too many moving parts.','Tools accumulate, responsibilities blur, and every change feels harder than it should.','A clearer foundation.','A documented system with ownership, visibility, and room to evolve.'],
 ['The surprise outage.','A critical service stops and the team learns about it from the customer.','Fewer blind spots.','Useful alerts, recovery plans, and risks addressed before they escalate.']
];
document.querySelectorAll('[data-case]').forEach(btn=>btn.addEventListener('click',()=>{const c=cases[Number(btn.dataset.case)];['before-title','before-text','after-title','after-text'].forEach((id,i)=>document.getElementById(id).textContent=c[i]);document.querySelectorAll('[data-case]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));}));
for (const id of ['contact','subscribe']) {const form=document.getElementById(id+'-form');const status=document.getElementById(id+'-status');form.addEventListener('submit',async e=>{e.preventDefault();const submit=form.querySelector('button[type="submit"]');submit.disabled=true;status.textContent='Sending…';try {const response=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});const json=await response.json();if(!response.ok)throw new Error(json.error||'Unable to submit right now.');status.textContent=json.message;form.reset();}catch(err){status.textContent=err.message||'Network error. Please try again.';}finally{submit.disabled=false;}});}

'use strict';
const sample=document.querySelector('#sample');
function update(){
  sample.style.fontWeight=document.querySelector('#weight').value;
  sample.style.fontStyle=document.querySelector('#italic').value;
  const size=document.querySelector('#size').value;
  const tracking=Number(document.querySelector('#tracking').value)/100;
  sample.style.fontSize=size+'px';sample.style.letterSpacing=tracking+'em';
  sample.style.fontVariantNumeric=document.querySelector('#tabular').checked?'tabular-nums':'proportional-nums';
  sample.style.fontFeatureSettings='"ss01" '+(document.querySelector('#alternate').checked?'1':'0');
  document.querySelector('#size-value').textContent=size+'px';
  document.querySelector('#tracking-value').textContent=tracking+'em';
  sample.style.height='auto';sample.style.height=(sample.scrollHeight+4)+'px';
}
for(const control of document.querySelectorAll('.controls input,.controls select'))control.addEventListener('input',update);
sample.addEventListener('input',update);
for(const button of document.querySelectorAll('[data-sample]'))button.addEventListener('click',()=>{sample.value=button.dataset.sample;update();});
document.querySelector('#reverse').addEventListener('click',()=>sample.classList.toggle('reversed'));
document.fonts.ready.then(update);window.addEventListener('resize',update);update();

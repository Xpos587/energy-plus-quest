import '../pass-12/smoke.mjs';
const descriptions={
 before:'Версия 12A: мягко-живописный город; прежняя девушка показана без изменений.',
 after:'Перерисованы не только крыши: здания, деревья, машины и улицы. Не фильтр поверх версии 12.',
};
for(const button of document.querySelectorAll('[data-variant]'))button.addEventListener('click',()=>{
 const key=button.dataset.variant;
 for(const other of document.querySelectorAll('[data-variant]'))other.setAttribute('aria-pressed',String(other===button));
 for(const art of document.querySelectorAll('[data-art]'))art.setAttribute('href',key==='before'?'../pass-12/map-a.jpg':'map.jpg');
 document.querySelector('#description').textContent=descriptions[key];
 document.querySelector('#download').href=`comparison-${key}.jpg`;
 document.querySelector('#crops').href=key==='before'?'../pass-12/crops-a.jpg':'details.jpg';
 document.documentElement.dataset.activeVariant=key;
});
document.querySelector('#zoom').addEventListener('change',event=>{
 document.querySelector('.overview').style.width=`${Number(event.target.value)*100}%`;
});
document.querySelector('#character').addEventListener('change',event=>{
 document.querySelector('.character').style.visibility=event.target.checked?'visible':'hidden';
});

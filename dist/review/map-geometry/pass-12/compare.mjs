import './smoke.mjs';
const descriptions={
 a:'Выборочный живой контур: сильнее силуэты и перекрытия, тише детали.',
 b:'Графичная живопись: объём собирается из крупных световых и теневых плоскостей.',
 c:'Кистевой скетч: заметный мазок, прерывистые края и свободный ритм мазков.',
 control:'Версия 11 до ремонта — контроль рисовки. Геометрические ошибки здесь сохранены для сравнения.',
};
for(const button of document.querySelectorAll('[data-variant]'))button.addEventListener('click',()=>{
 const key=button.dataset.variant;
 for(const other of document.querySelectorAll('[data-variant]'))other.setAttribute('aria-pressed',String(other===button));
 const image=key==='control'?'../pass-11/map.jpg':`map-${key}.jpg`;
 for(const art of document.querySelectorAll('[data-art]'))art.setAttribute('href',image);
 document.querySelector('#description').textContent=descriptions[key];
 document.querySelector('#download').href=key==='control'?'../pass-11/comparison.jpg':`comparison-${key}.jpg`;
 document.querySelector('#crops').href=key==='control'?'../pass-11/map.jpg':`crops-${key}.jpg`;
 document.querySelector('#crew-crop').setAttribute('viewBox',key==='control'?'1145 615 73 77':'1120 422 82 80');
 document.documentElement.dataset.activeVariant=key;
});
document.querySelector('#zoom').addEventListener('change',event=>{
 document.querySelector('.overview').style.width=`${Number(event.target.value)*100}%`;
});
document.querySelector('#character').addEventListener('change',event=>{
 document.querySelector('.character').style.display=event.target.checked?'':'none';
});

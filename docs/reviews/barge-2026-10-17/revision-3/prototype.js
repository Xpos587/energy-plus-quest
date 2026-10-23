const q=new URLSearchParams(location.search),variant=(q.get('v')||'a').toLowerCase(),parcel=q.get('parcel')||'boat';
const ids=['remote','rush','wait','petr'],numbers={remote:1,rush:2,wait:3,petr:4};
const source='../../../../public/scene-art/barge-family-v1/';
const overview=parcel==='boat'?'choice-boat-v1.png':source+'choice-neutral-wide-v7.webp';
document.body.dataset.parcel=parcel;
let active=q.get('active')||'',outcome=ids.includes(q.get('state'))?q.get('state'):'',beat=0;
const gift={boat:'лодку',camera:'фотоаппарат',socks:'вязаные носки'}[parcel];
const scores={remote:[4,4,5],rush:[-4,-3,3],wait:[0,3,-4],petr:[-2,4,-3]};
function art(id){let version={remote:'v4',rush:'v3',wait:parcel==='boat'?'v3':parcel==='socks'?'v2':'v1',petr:'v13'}[id];return source+`${id}-${parcel}-${version}.png`;}
function detail(id,badge=true){return `<div class="detail ${active===id?'active':''}" data-id="${id}" role="img" aria-label="${COPY.labels[id]}">${badge?`<span class="marker">${numbers[id]}</span>`:''}</div>`;}
function map(){return `<div class="overview"><div class="map-frame"><img src="${overview}" alt="Причал, два крана и баржа"><div class="markers"><span class="marker m1 ${active==='remote'?'active':''}">1</span><span class="marker-pair">${['rush','wait'].map(id=>`<span class="marker ${active===id?'active':''}">${numbers[id]}</span>`).join('')}</span><span class="marker m4 ${active==='petr'?'active':''}">4</span></div></div></div>`;}

function resultText(id){return COPY.results[id].map(s=>s.replaceAll('(подарок)',gift).replaceAll('(персонажу)','Майме').replace('Теперь он придет',`Теперь ${parcel==='boat'?'она придет':parcel==='socks'?'они придут':'он придет'}`));}
const main=document.querySelector('main');
function choiceVisual(){
if(variant==='a')return map()+`<div class="detail-strip">${ids.map(id=>detail(id)).join('')}</div>`;
if(variant==='b')return (active?detail(active,false):'')+map();
return map()+`<div class="sequence situation"><div><img class="crop situation-gift" src="${overview}" alt="Подарок на причале"></div><div><img class="crop situation-crane" src="${overview}" alt="Ближний кран"></div><div><img class="crop situation-barge" src="${overview}" alt="Баржа с трубами"></div></div>`;
}
function render(){main.className=`variant-${variant} ${outcome?'result':'choice'}`;main.dataset.variant=variant;main.dataset.state=outcome||'choice';
if(!outcome){
const visual=choiceVisual();
main.innerHTML=`<div class="visual">${visual}</div><section class="rail"><div class="questionbar"><h1>${COPY.question}</h1><button class="about">О задаче</button></div><div class="context"><p>Одно судно уже загружено и готово к отправке, но ближайший кран освободится только через три часа.</p><p class="person-context"><span class="detail context-portrait" data-id="remote" aria-hidden="true"></span>Крановщик Иван ждет ваших распоряжений.</p><p class="person-context"><span class="detail context-portrait" data-id="petr" aria-hidden="true"></span>Пётр — у него вот-вот начнется своя погрузка, поэтому он уже на причале.</p></div><div class="options">${ids.map(id=>`<button class="option ${active===id?'preview':''}" data-option="${id}"><span class="badge">${numbers[id]}</span><span class="thumbnail detail" data-id="${id}" aria-hidden="true"></span><span class="label">${COPY.labels[id]}</span></button>`).join('')}</div></section>`;
main.querySelectorAll('[data-option]').forEach(button=>{button.addEventListener('pointermove',event=>{if(event.pointerType==='mouse'){document.body.dataset.pointerReady='true';preview(button.dataset.option);}});button.addEventListener('focus',()=>preview(button.dataset.option));button.onclick=()=>{outcome=button.dataset.option;beat=0;render();};});main.querySelector('.about').onclick=condition;
}else{
const texts=resultText(outcome),compactRemote=outcome==='remote'&&innerWidth<350&&innerHeight>450,shown=compactRemote?(beat===0?texts.slice(0,2):texts.slice(2)):texts;
const more=compactRemote&&beat===0;
const visual=`<div class="outcome-board ${parcel!=='boat'?'with-gift':''}"><div class="outcome-frame" data-id="${outcome}" role="img" aria-label="Результат погрузки"><img class="outcome-sheet" src="outcomes-${parcel}-v1.png" alt=""></div>${parcel!=='boat'?`<div class="gift-detail" data-parcel="${parcel}" data-location="${outcome==='wait'?'quay':'ship'}" role="img" aria-label="${outcome==='wait'?'Подарок на причале':'Подарок на барже'}"><img src="gift-locations-v1.png" alt=""></div>`:''}</div>`;
main.innerHTML=`<div class="visual">${visual}</div><section class="rail"><h1>Погрузка на баржу</h1><div class="reading">${shown.map(p=>`<p>${p}</p>`).join('')}</div><footer class="nav"><div class="scores">${['Энергия','Эмпатия','Эффективность'].map((name,i)=>`<div><b>${scores[outcome][i]>0?'+':''}${scores[outcome][i]}</b>${name}</div>`).join('')}</div><div class="navbuttons"><button data-revise><span aria-hidden="true">←</span><span>Изменить выбор</span></button><button data-next><span>${more?'Читать дальше':'Продолжить'}</span><span aria-hidden="true">→</span></button></div></footer></section>`;
main.querySelector('[data-revise]').onclick=()=>{outcome='';render();};main.querySelector('[data-next]').onclick=()=>{if(more){beat=1;render();}else{outcome='';render();}};
}window.PROTOTYPE={variant,parcel,active,outcome,beat};}
function preview(id){if(active===id)return;active=id;const visual=main.querySelector('.visual');if(visual)visual.innerHTML=choiceVisual();main.querySelectorAll('[data-option]').forEach(button=>button.classList.toggle('preview',button.dataset.option===id));if(window.PROTOTYPE)window.PROTOTYPE.active=active;}

function condition(){
 const paragraphs=[{boat:'Ваша лодка уже на причале — её вместе с другими грузами привезли со склада на беспилотном тягаче.',camera:'Ваш фотоаппарат уже на причале — его вместе с другими грузами привезли со склада на беспилотном тягаче.',socks:'Ваши вязаные носки уже на причале — их вместе с другими грузами привезли со склада на беспилотном тягаче.'}[parcel],'Теперь подарок нужно погрузить на баржу, которая доставит его по Оби в точку разгрузки — Новый порт. Одно судно уже загружено и готово к отправке, но ближайший кран освободится только через три часа.','Крановщик Иван ждет ваших распоряжений.'];
 const box=document.createElement('section');box.className='condition';let part=0;const paginated=innerHeight<650;const groups=[[paragraphs[0]],[paragraphs[1],paragraphs[2]]];
 const show=()=>{box.innerHTML=`<div><div class="intro-art" ${paginated&&part>0&&innerWidth<700?'hidden':''}><img src="${overview}" alt="Причал, подарок и баржа"></div><div class="intro-copy"><h1>Погрузка на баржу</h1>${(paginated?groups[part]:paragraphs).map(p=>`<p>${p}</p>`).join('')}<div class="condition-actions"><button>${paginated&&part<1?'Далее':'К выбору'}</button></div></div></div>`;box.querySelector('button').onclick=()=>{if(paginated&&part<1){part++;show();}else box.remove();};};show();document.body.append(box);
}
render();
if(!q.has('state'))condition();

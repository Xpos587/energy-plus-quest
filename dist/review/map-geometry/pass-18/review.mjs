const choices = {
  old: { number: 1, title: 'Проверка документов', passport: 'Серо-синяя низкая кабина, светлый старый прицеп. Для №1 используется серый вариант уже существующей сцены №4: тот же тип тягача и тот же сюжет ДПС.' },
  near: { number: 2, title: 'Близко — не значит быстро', passport: 'Синяя современная высокая кабина, светлый прицеп. Тот же перевозчик стоит за водителем, который перекусывает в кафе.' },
  crew: { number: 3, title: 'Два водителя лучше одного', passport: 'Синяя современная кабина, светлый прицеп. Два лица под стеклом на карте; два водителя рядом с той же семьёй тягача в результате.' },
  old4: { number: 4, title: 'Проверка документов', passport: 'Нейтральная серо-синяя низкая кабина и светлый прицеп карты 17 сохранены без изменений. Кабина результата перекрашена под карту; №1 и №4 используют одну нейтральную семью старых тягачей.' },
  express: { title: 'Перевозчик найден автоматически', passport: 'Платформа Express выбирает нового перевозчика после нажатия кнопки. Это отдельный результат на шоссе: синяя кабина, светлый прицеп с надписью Express и два водителя внутри, не №3, не №4 и не пятая машина на исходной карте.' },
};
const $ = (id) => document.getElementById(id);
let selected = 'old';
const mobile = matchMedia('(max-width: 650px)');
function updateDownload() { $('outcome-download').href = `${selected}-${mobile.matches ? 'mobile' : 'desktop'}.png`; }
function select(id) {
  const choice = choices[id];
  if (!choice) return;
  selected = id;
  document.querySelectorAll('[data-choice]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.choice === id)));
  $('route').textContent = `${choice.number ? `№${choice.number}` : 'Автоподбор'} → ${id} → результат`;
  $('title').textContent = choice.title;
  $('passport').textContent = choice.passport;
  $('map-detail').hidden = !choice.number;
  if (choice.number) { $('truck').src = `truck-${choice.number}.png`; $('truck').alt = `Кандидат карты: грузовик №${choice.number}`; }
  $('mobile-source').srcset = `${id}-mobile.png`;
  $('outcome').src = `${id}-desktop.png`;
  $('outcome').alt = `${choice.title}: ${choice.passport}`;
  $('result').dataset.carrier = id;
  $('status').textContent = id === 'express' ? 'Сценарий описывает появление у дверей как реакцию карты, а шоссе — как иллюстрацию результата автоподбора. Результат теперь показывает фуру на шоссе с обоими водителями внутри кабины. Это статичная иллюстрация, не анимация и не проверка скорости.' : 'Кандидат, не игровая интеграция. Форма и цвет семьи машин согласованы; скорость и точная марка не заявляются.';
  updateDownload();
}
$('choices').addEventListener('click', (event) => { const button = event.target.closest('[data-choice]'); if (button) select(button.dataset.choice); });
$('back').addEventListener('click', () => { document.querySelector(`[data-choice="${selected}"]`).focus(); $('choices').scrollIntoView({ block: 'center', behavior: 'auto' }); });
mobile.addEventListener('change', updateDownload);
select('old');

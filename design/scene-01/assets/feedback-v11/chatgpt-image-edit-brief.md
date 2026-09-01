# Scene 01 — brief for ChatGPT Image editing

Этот файл — готовый контекст для ретуши вертикального master-изображения. Его можно целиком переслать в новый чат с ChatGPT Image, а затем добавлять локальные промпты для отдельных машин.

## Техническая история master

Файл `production/carrier-mobile.png` — это не один единственный вызов модели, а финальный результат трёх проходов одной модели:

- **Модель:** `GPT-Image 2 Edit`, вызов через ComfyUI-ноду `GPTImage2Edit_fal` и endpoint `fal-ai/gpt-image-2/edit`.
- **Проход v2:** цельная генерация сцены из layout-guide и референсов — prompt ID `9407b22d-9d2c-4f33-9e64-36fc2ef019ce`.
- **Проход v3:** коррекция масштаба четырёх машин — prompt ID `5525efc8-ae25-46f5-9c19-b4ac210f391e`.
- **Проход v4:** финальная маскированная коррекция OLD, CREW и EXPRESS при сохранённом NEAR — prompt ID `b03bf97a-4a91-4dc8-94f3-3773ba7a3f93`; именно этот output является источником текущего mobile master.

Общие настройки GPT-Image 2 Edit во всех трёх проходах:

```text
image_size: custom
width: 768
height: 1424
quality: high
input_fidelity: high
background: opaque
num_images: 1
output_format: png
sync_mode: false
```

У этой ноды не задавались `seed`, `steps`, `CFG/guidance scale` или `denoise strength`: API GPT-Image 2 Edit их не предоставлял в использованной версии. Повторяемость обеспечивалась исходными изображениями, маской и промптом, но не гарантированным seed. В первом, более раннем V11-прототипе использовался другой вызов — `Flux Pro Kontext Max Multi` (`aspect_ratio: 9:16`, `max_quality: true`, `guidance_scale: 4.5`, `seed: 26083131`); он не является финальным источником текущего `production/carrier-mobile.png`.

## Что загружать

Загружайте изображения в таком порядке и называйте их в сообщении:

1. **Image 1 — master:** `design/scene-01/assets/feedback-v11/production/carrier-mobile.png`
   - PNG, `768 × 1424`.
   - Это рабочий вертикальный master сцены, а не скриншот из браузера.
   - Не используйте вместо него `carrier-mobile-375.png`: это только preview для проверки на телефоне.
2. **Image 2 — OLD reference:** `design/scene-01/assets/feedback-v5/production/outcomes/old-mobile.webp`
   - Использовать только силуэт, возраст машины, детали кузова и зимнюю материальность.
   - Людей, фон и композицию этого кадра не копировать.
3. **Image 3 — NEAR reference:** `design/scene-01/assets/feedback-v5/production/outcomes/near-mobile.webp`
   - Использовать только пропорции компактной развозной машины, кабину, кузов и детали колёс.
   - Фон, вывески, людей и масштаб не копировать.
4. **Image 4 — CREW reference:** `design/scene-01/assets/feedback-v4/production/outcomes/crew-mobile.webp`
   - Главный референс для синего кузова и двух отдельных водителей в одной кабине.
   - Фон и композицию не копировать.
5. **Image 5 — EXPRESS reference:** `design/scene-01/assets/feedback-v4/production/outcomes/express-mobile.webp`
   - Использовать оранжевый современный кузов, кабину, колёса и ощущение движения.
   - Единственный допустимый текст в master — текущее слово `Express` на кузове Image 1; текст и знаки из референса не копировать.

Дополнительный широкий Express-референс, только если не хватает деталей бокового кузова:
`design/scene-01/assets/feedback-v5/production/outcomes/express-desktop.webp`.

Не загружайте в первый чат плоские карточки из `design/scene-01/assets/carriers/` и маленькие диагностические crops из `feedback-v10/comfyui/reference-*.png`: они могут потянуть модель в сторону 2D-схемы или старой композиции.

## Порядок работы

- Работайте с Image 1 как с существующей картиной, а не как с эскизом для новой генерации.
- Сначала сохраните оригинал отдельно. Версии называйте, например, `carrier-mobile-edit-v01`, `v02` и так далее.
- Один запрос — одна локальная правка. Не просите одновременно переделывать все четыре машины и склад.
- Если в интерфейсе доступно выделение или маска, выделяйте машину вместе с её тенью, колеями и небольшим участком дороги; остальную сцену защищайте.
- Не меняйте размер холста, соотношение сторон, камеру, положение склада, железной дороги и перекрёстков.
- Не добавляйте интерфейсные подписи: все подписи и кнопки будут добавлены в DOM игры. В картине разрешено только одно читаемое слово `Express` непосредственно на оранжевом кузове.
- После каждой правки проверяйте изображение в масштабе `375 px` по ширине. Особенно проверяйте двух водителей Crew.

## Готовый контекст для нового чата

Скопируйте следующий блок целиком после загрузки изображений:

```text
Ты работаешь как аккуратный арт-директор и ретушёр для первой сцены образовательного веб-квеста «Энергия+».

Проект: игрок доставляет подарок из Москвы в Лабытнанги. На экране выбора транспорта показан один северный зимний город с центральным логистическим складом, связанными улицами и четырьмя вариантами перевозчика. Карта должна объяснять выбор пространством и действием объектов, а не рекламными надписями.

Image 1 — канонический вертикальный master. Ретушируй именно эту существующую картину. Не создавай новую композицию, не меняй кадр, не обрезай и не растягивай его. Сохраняй все невыделенные пиксели и исходную связь объектов: полный синий склад в центре, три погрузочных ворот, двор, правая калитка/шлагбаум, железная дорога слева, перекрёстки, дома, фонари, снег, бумажно-гуашевую фактуру, мягкий северный свет и тени.

Визуальный язык: человечная сказочная зимняя иллюстрация, выразительные контуры, объёмный приподнятый ракурс 3/4, синие и белые снежные тени, тёплые окна, сигнальный оранжевый и кобальтовый акценты. Не используй плоскую инфографику, строгий aerial-план, глянцевый 3D, low-poly, фотореализм, наклеенные cutout-объекты или коллаж.

В master должны быть ровно четыре и только четыре транспортных средства:
1) OLD — маленький старый, но исправный серо-синий развозной грузовик на дальней верхней левой дороге; он движется безопасно, не сломан и не брошен.
2) NEAR — компактная тёмно-бирюзовая машина непосредственно у правого выезда склада; она связана с воротами, прикреплённым шлагбаумом и снежным ограничением, колёса повернуты на тесный выезд.
3) CREW — синий кузовной грузовик на нижней левой горизонтальной дороге; в кабине видны ровно два разных взрослых водителя, сидящих рядом. Они не должны сливаться в одно лицо, со стойкой кабины или с отражением. Третьего человека быть не должно.
4) EXPRESS — современный сигнально-оранжевый кузовной грузовик на нижней правой свободной дороге; он уже движется, у него самый ясный снежный след и открытая дорога впереди. На кузове ровно одно читаемое слово `Express` и больше никакого текста.

Все машины должны стоять продольно по своим дорогам и иметь естественный контакт с асфальтом и снегом. Ни одна машина не должна пересекать дорогу боком, занимать две полосы, пересекать железную дорогу, висеть в воздухе или выглядеть вставленной поверх фона. Ни одна машина не должна быть шире примерно 18% ширины Image 1; склад заметно шире самой большой машины.

Image 2–5 — только референсы идентичности отдельных машин. Бери из них форму кузова, кабину, колёса, возраст, цвет и читаемость экипажа, но не копируй их фон, людей (кроме двух водителей Crew), знаки, вывески, масштаб, композицию или текст.

Не добавляй парковочные машины, трафик, прицепы, фрагменты кузовов, пятую машину, людей на дорогах, рекламные щиты, номера, стрелки, pin-маркеры, UI, логотипы или подписи. Единственный текст во всей иллюстрации — `Express` на кузове оранжевой машины.

При любой неопределённости сохраняй существующую сцену и делай минимальную локальную правку, а не перерисовывай весь кадр.
```

## Локальные промпты

В каждом запросе повторяйте: «Edit only the selected region; preserve the rest of Image 1 exactly.» Ниже — готовые англоязычные формулировки; их можно вставлять без перевода.

### OLD

```text
Edit only the selected upper-left OLD vehicle and its immediate road contact area. Preserve its current position, heading, depth, and small scale. Make it unmistakably a small older muted blue-grey delivery truck: aged body style, slightly faded paint, modest clean scuffs, older lamps, but fully operational and safe. Keep it moving on the road with a thin exhaust wisp and a short continuous tire trace. Do not show a crash, breakdown, missing parts, abandoned vehicle, trailer, extra vehicle, people, labels, or any new text. Match the existing winter paper-gouache illustration, perspective, light, shadow, and asphalt exactly. Do not alter the warehouse, railway, buildings, roads, or any other carrier.
```

### NEAR

```text
Edit only the selected NEAR vehicle and the immediate area at the right-hand warehouse exit. Keep the complete warehouse, gate, fence post, and attached barrier unchanged. Make the vehicle a clearly recognizable compact dark-teal delivery van, immediately beside the loading exit and physically connected to the gate scene, not floating in an open field. Turn the front wheels into the tight exit, let the snow bank and short wheel traces show that it is constrained and slow. Preserve a natural contact shadow and road continuity. No trailer, duplicate, fifth vehicle, detached barrier, extra person, label, sign, logo, or text. Do not move the warehouse or change the camera.
```

### CREW

```text
Edit only the selected lower-left CREW truck and its immediate road contact area. Keep the truck on the lower-left horizontal road, aligned left-to-right with the lane and completely clear of the railway. Use a distinct medium blue high-box delivery truck with a broad readable windshield. Inside the cab show exactly two separate adult drivers seated side by side: two distinct heads, faces, torsos, and silhouettes, both clearly visible at a 375-pixel-wide mobile preview. No third person and no face-like reflection. Keep the truck smaller than the warehouse, with continuous tire tracks and a safe open route. Match the existing winter paper-gouache style, perspective, shadows, and lighting. Do not alter any other vehicle, road, building, or the warehouse.
```

### EXPRESS

```text
Edit only the selected lower-right EXPRESS truck and its immediate road contact area. Make it a distinct modern signal-orange box truck on the unobstructed lower-right arterial, aligned with the lane and visibly already moving. Keep a contemporary cab, clean wheels, natural contact shadow, subtle wheel-motion cue, small tire spray, and the longest restrained low snow wake trailing behind it. Put exactly one readable word `Express` directly on the side of the cargo body. Remove or avoid every other word, number, logo, sign, advertisement, route arrow, or label. Do not add another vehicle or trailer. Preserve the rest of Image 1 exactly and match its winter paper-gouache camera, light, and texture.
```

### Шлагбаум и склад

Используйте только если связь машины со складом действительно требует исправления:

```text
Edit only the selected warehouse-right-gate detail. Keep the entire warehouse facade, all three loading bays, yard, road network, buildings, railway, and all four vehicles unchanged. Make the barrier a single physical arm attached to the right-side gate/fence post beside the NEAR vehicle. It must cast a natural contact shadow and clearly constrain the vehicle's tight turn. Do not add a floating barrier, extra fence in the road, signs, text, people, or another vehicle. Preserve the existing camera, winter paper-gouache style, lighting, and snow texture.
```

### Локальная чистка без изменения композиции

```text
Perform a minimal local cleanup only in the selected area. Repair broken contours, wheel-to-road contact, snow edges, tire traces, and paper texture while preserving the exact object position, scale, camera, lighting, and all unselected pixels of Image 1. Do not reinterpret the scene. Do not add or remove vehicles, people, buildings, signs, labels, logos, UI, or text. The final image must still contain exactly four vehicles, and the only readable text must be `Express` on the orange vehicle.
```

## Финальный запрос на проверку

Это не просьба «улучшить всё», а контроль перед передачей master:

```text
Inspect Image 1 against the following hard contract and make only the smallest necessary local corrections. Do not redesign or recompose the image.

- exactly four complete vehicles: one OLD, one NEAR, one CREW, one EXPRESS;
- no parked background vehicle, duplicate, trailer, fragment, or fifth vehicle;
- every vehicle follows its own road and has natural contact with the surface;
- the warehouse is complete, central, industrial, and visibly wider than every vehicle;
- NEAR is immediately beside the attached warehouse gate/barrier and visibly constrained;
- CREW shows exactly two separate adult drivers in the cab, readable at 375-pixel mobile width;
- OLD is distant, aged, operational, and not broken;
- EXPRESS is modern orange, on an open road, visibly moving, with exactly one readable `Express` wordmark on its body;
- no UI, labels, pins, route overlays, advertisements, numbers, logos, or readable text other than `Express`;
- preserve the existing vertical canvas, camera, lighting, winter paper-gouache style, warehouse, roads, railway, buildings, and snow.

If a requirement already passes, leave that region untouched.
```

## Что прислать обратно для адаптации

1. Финальный PNG вертикального master в исходном или максимально близком размере (`768 × 1424`), не скриншот из чата и не preview `375 px`.
2. Если ChatGPT Image создал несколько вариантов — один файл с очевидной пометкой `FINAL-MASTER`.
3. Отдельно можно приложить preview шириной `375 px` для проверки мелких деталей.
4. Если использовались маски, полезно прислать и их, но это необязательно.

После этого вертикальный master станет источником истины: desktop сделаем контролируемым боковым outpaint с защищённым центральным содержимым, а tablet/mobile preview и DOM-hotspots пересчитаем отдельно. Мы не будем механически растягивать или заново собирать четыре машины для каждого экрана.

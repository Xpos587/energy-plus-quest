# PPE v10 — локальная правка пяти складских кадров

Дата: 2026-10-01. Метод: встроенный imagegen, шесть отдельных кропов работников, затем Sharp-композит в исходные кадры и lossless WebP. Полные сцены не передавались на генерацию. Код приложения не изменён.

Контракт: [форма](../style-pilot-2026-09-28/uniform-contract.md). Визуально просмотрены исходники, Профессионал, Арсений и официальный лист. Генератору переданы кроп, Профессионал и официальный лист.

## Файлы и границы кропов

Все координаты в пикселях исходного кадра 1672 × 941, формат x/y/width/height.

| Файл в public/scene-art/outcomes | Исходник | Кроп |
|---|---|---|
| inventory-entrance-v10.webp | inventory-entrance-v8.webp | 640/100/360/710 |
| inventory-keeper-v10.webp | inventory-keeper-v8.webp | женщина 455/320/400/450; мужчина 920/105/280/655 |
| inventory-wms-v10.webp | inventory-wms-v8.webp | 575/85/385/795 |
| inventory-alphabet-camera-v10.webp | inventory-alphabet-camera-v8.webp | 605/70/410/871 |
| inventory-alphabet-socks-v10.webp | inventory-alphabet-socks-v9.webp | 550/55/390/835 |

## Сохранение исходника

Генерированные кропы уменьшены обратно до исходного размера. Маски ограничивают замену областью одежды с небольшим запасом по контуру; оригинальные лица, волосы, выбранные контуры рук и предметов наложены сверху. Подарок WMS, сканер, камера с коробкой, коробка носков и документ кладовщика сохранены оригинальными фрагментами. Буквы на стойках находятся вне кропов.

Проверка декодированных RGB-пикселей: вне указанных кропов изменено **0 пикселей во всех пяти файлах**. Это проверка изображения, не расчёт метаданных или хеша. Внутри кропов пиксельная идентичность всего фона не заявляется: узкий запас масок может содержать часть сгенерированного окружения.

## Визуальная проверка

Просмотрены все шесть крупных генерированных кропов и все пять финальных кадров. Видимые капюшоны, короткие серебристые вставки на обоих плечах, два передних уровня с синей центральной планкой, рукавные полосы без красной окантовки, оранжевые бёдра и серебристые голенные кольца с тонкими красными краями присутствуют. Скрытые объектами/телом детали не считаются отдельно проверенными. У присевшей работницы отдельной итерацией удалены две полосы, ошибочно продолжавшиеся на видимую спину; оставлен оранжевый верх и синий низ.

Ограничения: мелкие буквы эмблем в конечном игровом масштабе не являются доказанно точной типографической копией референса. Положение и общий рисунок знаков проверены визуально; полная схема спины с короткой верхней полосой и знаком в этих ракурсах не видна. Это исправленные варианты для просмотра, а не свидетельство согласования заказчиком.

## Основной промпт

Use case: identity-preserve. Edit ONLY WORK CLOTHING in image 1, a tightly cropped existing illustration. Images 2 and 3 are exact clothing references, not people to copy. Keep original image 1 composition, pose, face, hair, hands, objects, background and crop framing unchanged. Do not zoom or reframe. Match the illustration linework. Replace the uniform with reference Arctic uniform: orange lined hood folded BEHIND neck, orange shoulder yoke and front panels, navy sleeves and broad navy chest pocket flaps and centre placket. EXACTLY ONE SHORT SILVER RECTANGULAR TAB ON EACH SHOULDER, two total, no long vertical straps. Two horizontal silver levels across front only: waist orange/navy junction and near jacket hem, BOTH interrupted by solid navy central placket. Two silver bands on EACH sleeve at elbow and above wrist, no red sleeve edges. Orange UPPER THIGHS including cargo pockets, navy knees and lower legs. ONE silver band around EACH calf WITH very thin red edge above AND below. Small white Gazprom Neft badge on wearer's LEFT chest pocket flap; white industry chevron on LEFT upper sleeve; Russian tricolour on RIGHT upper sleeve. Respect occlusions and anatomy, do not draw details over hands/objects or through body. Ensure hood and both shoulder tabs are clearly visible wherever not genuinely occluded. Preserve original face identity exactly and all background geometry. Output ONLY edited crop image 1 with same aspect ratio.

К каждому запросу добавлено Target crop: entrance / keeper-woman / keeper-man / wms / alphabet-camera / alphabet-socks.

## Дополнительная итерация keeper-woman

Precise clothing correction to cropped illustration image 1. Keep EVERYTHING else unchanged, identical pose face hands shoes background framing and jacket front and sleeves. ONLY on the visible BACK of the crouching woman's jacket (the wedge to image-right behind her left elbow): remove BOTH silver bands currently wrapping around her back. Her back must have orange upper panel and plain navy lower panel, no horizontal reflective bands at waist or hem wrapping onto the back. Do not remove either band from sleeves or visible front. Keep existing hood, shoulder tabs, badges, orange thighs and calf red-edged silver bands. Output same exact crop aspect ratio, no reframe.

## Сохранённые результаты генератора

- entrance: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-891376fc-30a4-459f-9391-adae49ad785b.png
- keeper-woman: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-973bbf31-7567-4850-8d81-6e6a03235dc2.png
- keeper-man: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-00edb368-f6cb-4b24-a76f-3970573be45b.png
- wms: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-5fa5c620-d316-4428-9b6f-997421c0b542.png
- alphabet-camera: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-64215124-6d76-453e-8fbb-3d1cde6f47d4.png
- alphabet-socks: /home/michael/.config/codex/generated_images/01a0f8d6-8645-7210-ad9c-30c70431453c/exec-0290dbb0-32c6-4630-83f8-6b195169331b.png


## v11 — читаемость правых плечевых вставок

После независимого просмотра выпущены inventory-entrance-v11.webp и inventory-keeper-v11.webp. На увеличенных исходных кропах серебристые вставки были видны, но узки и сливались с капюшоном. Встроенным imagegen отредактированы только маленькие кропы плеч; обратно вставлены лишь два многоугольника.

- entrance: изменённый участок целиком внутри x=748, y=227, width=30, height=30; 601 изменённый RGB-пиксель; за этим прямоугольником 0 отличий от v10.
- keeper: изменённый участок целиком внутри x=986, y=234, width=21, height=24; 350 изменённых RGB-пикселей; за этим прямоугольником 0 отличий от v10.

Обе вставки просмотрены в пятикратном увеличении. Остальные три кадра остаются v10. Промпт двух запросов:

Precise tiny clothing edit. Image 1 is a tightly cropped worker RIGHT shoulder (viewer LEFT) from an illustration. Keep exact crop framing, background, hood, collar, face fragment, chest pocket, orange fabric shape and all lines unchanged. ONLY improve the SMALL SILVER REFLECTIVE SHOULDER TAB: make it a clearly visible short broad silver rectangle/trapezoid resting on the exposed orange shoulder directly below/left of the hood edge. It must be a SHORT shoulder tab like an epaulette, not a long vertical strap and not a collar trim. Existing tiny pale sliver near the hood should become this single clear silver tab, no duplicate. Follow shoulder perspective, subtly outlined and fabric shaded, distinctly silver against orange. Change nothing else. Output exact same crop composition and aspect ratio.

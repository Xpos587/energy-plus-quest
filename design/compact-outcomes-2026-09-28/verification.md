# Проверка результатов погрузки

14 минимальных иллюстраций покрывают 15 веток сцены Compact (носки / фотоаппарат / лодка × четыре места и автоматика). Сценарные подписи и весь исходный рассказ сохранены. Подробная первая серия отклонена и вынесена из public.

Карточка: отдельная страница иллюстрации без пустого абзаца, без нижней линии, общий размер текста 18px/16px. Прежняя область измерения текста сохранена независимо от высоты иллюстрации, чтобы пагинация не зацикливалась.

Проверки: 34 unit-теста; 9 браузерных тестов на ширинах 320, 390 и 1440 (все 15 веток на каждом размере). Проверены загрузка изображений, подписи, границы figure, отмена/подтверждение и автоматика. Ручной просмотр через CUA: desktop и фактический viewport 320×567, фотоаппарат auto; изображение загружено, подпись16px, border-bottom0px, карточка помещается. Две иллюстрации затем уточнены визуально: фотоаппарат на ящике и перегруз оси без ошибочной загрузки на крышу.

## Уточняющие промпты ImageGen

### camera-dishes

Keep this minimal neutral grey-blue pictogram style, plain background and no text. Correct object placement ONLY: the small camera must REST ON TOP of the closed dishes carton, on a tiny flat pad. Its entire body is ABOVE the box top, not hanging on front face. A simple blue horizontal cargo belt holds camera in place. Remove triangular hanging neck strap. Keep plate symbol on box and dashed empty-space rectangle ABOVE camera. No extra detail, no scenery.

### boat-axle

Keep the same very minimal flat grey-blue instructional style on plain pale background. Replace this incorrect roof-loaded trailer drawing with a SIMPLE EXPLANATORY STACK: inflatable boat WITHOUT MOTOR sits on one heavy rectangular crate marked small kettlebell, crate on a flat axle beam with TWO wheels. There is NO trailer box/body/roof, just boat -> heavy crate -> wheels directly underneath to convey excess rear axle load. Small amber warning triangle beside wheel. Axle unbroken, wheels intact. No perspective interior, no realism, no lettering, no scenery. Sparse neutral pictogram.


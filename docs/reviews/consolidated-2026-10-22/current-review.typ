#set page(paper: "a4", flipped: true, margin: 12mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 11pt)
#set par(leading: 0.6em)
= Energy+ Quest — текущий обзор
Обновлено 23 октября 2026 · проверенная локальная версия: http://127.0.0.1:4344/

*Применено:* компактная общая панель выбора грузовика на десктопе; радиальная светлая подложка вступления; обработанное изображение получателя Альвы F0001; результат зелёной фуры F0075 на mobile/tablet; удаление синей обводки осмотра фуры; навигация и блок баллов вступления; финал с popup «Поделиться» и официальным MAX.

В этом PDF — только последний законченный набор, по совпадающим размерам экрана «до / после». Мобильные пары также показаны: сохранение мобильной компоновки не означает её редизайн.

*Качество медиа:* в runtime подтверждены 23 обработанных исходника: 19 выборочных Flowers и 4 обычных увеличения. Последняя общая проверка: 120 уникальных runtime-состояний, HTTP и JS ошибок нет. Это не означает готовность всей графики. По решению Михаила от 22 октября обязательный Flowers для всех 113 отменён: для общей массы — обычное увеличение с проверкой видимой пользы, для проблемных крупных иллюстраций — выборочная AI-реконструкция. Обычное увеличение не восстанавливает реальные детали.

*Не готово:* новый склад и вертолёт по референсу; оставшиеся проверки графики. Они перечислены в конце и не выдаются за применённые.

Внешний сайт energy-plus-quest.hypcat.net этим отчётом не проверен и не обновлён. Старые отчёты и эксперименты удалены. Склад на рабочем сайте остаётся отклонённым; новый вариант не принят.

#pagebreak()
= Грузовики · 1440x900
Вопрос, варианты и навигация собраны в единую панель. Lucide Truck в четырёх цветах, без видимых подписей цветов. Это экран выбора, не проверка удаления обводки при осмотре фуры.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../general-ux-2026-10-21/before/carrier-1440x900.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../general-ux-2026-10-21/after/carrier-1440x900.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Грузовики · 390x844
Вопрос, варианты и навигация собраны в единую панель. Lucide Truck в четырёх цветах, без видимых подписей цветов. Это экран выбора, не проверка удаления обводки при осмотре фуры.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../general-ux-2026-10-21/before/carrier-390x844.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../general-ux-2026-10-21/after/carrier-390x844.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · 1440x900
Радиальная светлая подложка вместо заметного прямоугольного поля. Текст сохранён. Это стартовый экран, не исправление навигации следующего вводного экрана.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../general-ux-2026-10-21/before/intro-1440x900.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../general-ux-2026-10-21/after/intro-1440x900.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · 390x844
Радиальная светлая подложка вместо заметного прямоугольного поля. Текст сохранён. Это стартовый экран, не исправление навигации следующего вводного экрана.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../general-ux-2026-10-21/before/intro-390x844.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../general-ux-2026-10-21/after/intro-390x844.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Альва · F0001 · desktop, DPR 2
Два прохода, мастер 8192×4096; в игре декодирован ресурс 1600×800. Это реконструированная детализация, не единая native-генерация 8K. Изменён только media URL; новый popup финала в эту публикацию не входит.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0001/before/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0001/after/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Альва · F0001 · mobile, DPR 2
Два прохода, мастер 8192×4096; в игре декодирован ресурс 1600×800. Это реконструированная детализация, не единая native-генерация 8K. Изменён только media URL; новый popup финала в эту публикацию не входит.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0001/before/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0001/after/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Зелёная фура · F0075 · mobile, DPR 2
Применён выборочный двухпроходный мастер. Силуэт правого водителя и прилегающая область сохранены из исходника, чтобы исключить двойной контур. Проверены 8 случаев: 390/800/844/1440 × DPR 1/2; новый F0075 виден в шести. На 1440 остаётся прежний crew-wide-v6 — этот wide источник данным обновлением не улучшен. Видимый F0075: HTTP 200, JS ошибок нет; в ранней публикации был посторонний prefetch /assets/assets/... 404; в последней общей проверке 120 состояний HTTP ошибок нет.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0075/before/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0075/after/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Зелёная фура · F0075 · tablet, DPR 2
Применён выборочный двухпроходный мастер. Силуэт правого водителя и прилегающая область сохранены из исходника, чтобы исключить двойной контур. Проверены 8 случаев: 390/800/844/1440 × DPR 1/2; новый F0075 виден в шести. На 1440 остаётся прежний crew-wide-v6 — этот wide источник данным обновлением не улучшен. Видимый F0075: HTTP 200, JS ошибок нет; в ранней публикации был посторонний prefetch /assets/assets/... 404; в последней общей проверке 120 состояний HTTP ошибок нет.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0075/before/800-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0075/after/800-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Осмотр фуры · без синей обводки · 1440px
Синяя обводка и заливка удалены. Проверены все четыре фуры: мышь, touch, клавиатура; 5 размеров экрана, 15 after-снимков. Оранжевый контур 2px сохранён только при клавиатурном фокусе для доступности — это не выделение выбранной машины.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../feedback-2026-10-22/carrier/before/1440-inspection.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../feedback-2026-10-22/carrier/after/1440-inspection.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Осмотр фуры · без синей обводки · 390px
Синяя обводка и заливка удалены. Проверены все четыре фуры: мышь, touch, клавиатура; 5 размеров экрана, 15 after-снимков. Оранжевый контур 2px сохранён только при клавиатурном фокусе для доступности — это не выделение выбранной машины.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../feedback-2026-10-22/carrier/before/390-inspection.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../feedback-2026-10-22/carrier/after/390-inspection.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0144 · desktop 1440, DPR 2
Обработан wide-источник, runtime 5120×2560. На mobile этот wide слой скрыт (rect 0×0); F0144 сам по себе не улучшает портретную версию.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0144/before/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0144/after/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Последняя миля · F0095 · 1440px, DPR 2
Выборочная обработка качества результата наземной доставки. Она не закрывает отдельную задачу перерисовать вертолёт по референсу ОС.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0095/before/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0095/after/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Последняя миля · F0095 · 390px, DPR 2
Выборочная обработка качества результата наземной доставки. Она не закрывает отдельную задачу перерисовать вертолёт по референсу ОС.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/F0095/before/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/F0095/after/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Обычное увеличение · F0082 · результат старой фуры · 1440px
Интерполяция с сохранением исходника. Не Flowers и не AI-реконструкция: новые достоверные детали не восстановлены. Сравнивается отображение в игре, а не только экспортированный размер.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../conventional-media-2026-10-22/carrier-old-wide-v8-v1/before/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../conventional-media-2026-10-22/carrier-old-wide-v8-v1/after/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Обычное увеличение · F0082 · результат старой фуры · 390px
Интерполяция с сохранением исходника. Не Flowers и не AI-реконструкция: новые достоверные детали не восстановлены. Сравнивается отображение в игре, а не только экспортированный размер.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../conventional-media-2026-10-22/carrier-old-wide-v8-v1/before/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../conventional-media-2026-10-22/carrier-old-wide-v8-v1/after/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Обычное увеличение · F0107 · снегоболотоход · 1440px
Интерполяция с сохранением исходника. Не Flowers и не AI-реконструкция: новые достоверные детали не восстановлены. Сравнивается отображение в игре, а не только экспортированный размер.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../conventional-media-2026-10-22/rover-boat-khor-v1/before/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../conventional-media-2026-10-22/rover-boat-khor-v1/after/1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Обычное увеличение · F0107 · снегоболотоход · 390px
Интерполяция с сохранением исходника. Не Flowers и не AI-реконструкция: новые достоверные детали не восстановлены. Сравнивается отображение в игре, а не только экспортированный размер.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../conventional-media-2026-10-22/rover-boat-khor-v1/before/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../conventional-media-2026-10-22/rover-boat-khor-v1/after/390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0025 · 390px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0025-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0025-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0026 · 1440px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0026-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0026-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0027 · 1440px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0027-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0027-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0028 · 1440px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0028-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0028-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0145 · 1440px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0145-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0145-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0145 · 390px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0145-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0145-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0146 · 1440px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0146-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0146-1440-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Compact · F0146 · 390px, DPR 2
Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../flowers-all-2026-10-20/integrations/compact-six/before/F0146-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../flowers-all-2026-10-20/integrations/compact-six/after/F0146-390-dpr2.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · Навигация · 1440px
Применено на4344: «Назад» и «Далее» по противоположным краям; порядок чтения блока баллов по исходному сценарию и ОС. Проверены15экранов на320/390/844/1440/1920: действия видимы и не меньше44px, границы навигации совпадают, overflow нет, HTTP ошибок нет. Исправлены абсолютные URL фонов. Текст не переизобретён — применён исходный комментарий.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../intro-2026-10-22-feedback/before/1440-story.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../intro-2026-10-22-feedback/after/1440-story.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · Навигация · 390px
Применено на4344: «Назад» и «Далее» по противоположным краям; порядок чтения блока баллов по исходному сценарию и ОС. Проверены15экранов на320/390/844/1440/1920: действия видимы и не меньше44px, границы навигации совпадают, overflow нет, HTTP ошибок нет. Исправлены абсолютные URL фонов. Текст не переизобретён — применён исходный комментарий.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../intro-2026-10-22-feedback/before/390-story.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../intro-2026-10-22-feedback/after/390-story.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · Баллы по исходной ОС · 1440px
Применено на4344: «Назад» и «Далее» по противоположным краям; порядок чтения блока баллов по исходному сценарию и ОС. Проверены15экранов на320/390/844/1440/1920: действия видимы и не меньше44px, границы навигации совпадают, overflow нет, HTTP ошибок нет. Исправлены абсолютные URL фонов. Текст не переизобретён — применён исходный комментарий.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../intro-2026-10-22-feedback/before/1440-scores.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../intro-2026-10-22-feedback/after/1440-scores.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Вступление · Баллы по исходной ОС · 390px
Применено на4344: «Назад» и «Далее» по противоположным краям; порядок чтения блока баллов по исходному сценарию и ОС. Проверены15экранов на320/390/844/1440/1920: действия видимы и не меньше44px, границы навигации совпадают, overflow нет, HTTP ошибок нет. Исправлены абсолютные URL фонов. Текст не переизобретён — применён исходный комментарий.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../intro-2026-10-22-feedback/before/390-scores.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../intro-2026-10-22-feedback/after/390-scores.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Финал · 1440x900
Применено на обычном4344: понятная кнопка «Поделиться», соцсети и скачивание перенесены в popup, официальный знак MAX. Четыре viewport проверены; два runtime-теста поведения пройдены. Сценарные абзацы и CTA сохранены. Запись на практику остаётся заглушкой.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../ending-2026-10-21-share-feedback/before-1440x900-result.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../ending-2026-10-21-share-feedback/runtime-1440x900-result.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Финал · 390x844
Применено на обычном4344: понятная кнопка «Поделиться», соцсети и скачивание перенесены в popup, официальный знак MAX. Четыре viewport проверены; два runtime-теста поведения пройдены. Сценарные абзацы и CTA сохранены. Запись на практику остаётся заглушкой.

#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*

#image("../ending-2026-10-21-share-feedback/before-390x844-result.png", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*

#image("../ending-2026-10-21-share-feedback/runtime-390x844-result.png", width: 100%, height: 145mm, fit: "contain")])

#pagebreak()
= Финал · новое окно «Поделиться»
Применено на4344. Соцсети и явно подписанное скачивание сертификата внутри popup. Проверены открытие, скачивание PNG, удержание фокуса, Escape, закрытие и возврат фокуса. Native share файла зависит от браузера; ссылки соцсетей передают текст и URL.

#grid(columns: (1fr, 1fr), gutter: 6mm,
[*Desktop 1440×900* #image("../ending-2026-10-21-share-feedback/runtime-1440x900-popup.png", width: 100%, height: 135mm, fit: "contain")],
[*Mobile 390×844* #image("../ending-2026-10-21-share-feedback/runtime-390x844-popup.png", width: 100%, height: 135mm, fit: "contain")])

#pagebreak()
= Баржа · варианты A/B/C — только для обсуждения
Не внедрено в игру. Слева текущий runtime, далее три предложения мобильного экрана выбора. Проверены 120 состояний без overflow и 6 клавиатурных случаев; это техническая проверка, не приёмка Федей и не тест с игроками.

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 3mm,
[*Текущая игра* #image("../barge-2026-10-22/frames/mobile-runtime-boat-choice.png", height: 125mm)],
[*Вариант A* #image("../barge-2026-10-22/frames/mobile-a-boat-choice.png", height: 125mm)],
[*Вариант B* #image("../barge-2026-10-22/frames/mobile-b-boat-choice.png", height: 125mm)],
[*Вариант C* #image("../barge-2026-10-22/frames/mobile-c-boat-choice.png", height: 125mm)])

#link("http://127.0.0.1:4344/review/barge-2026-10-22/index.html")[Открыть интерактивное сравнение mobile/desktop и результатов]. Прототип «Продолжить» возвращает к сравнению; исходный crop 768×512 не является финальной графикой desktop DPR 2. Вопросы офис/ПРУ и обоснования крана для маленьких подарков остаются открыты.

#pagebreak()
= Compact · последние три применённых исходника
Выборочные Flowers, actual4344. Ниже компактные пары desktop1440 DPR2; в receipts F0136/137 также проверен mobile390. Сохранённые исходные области раскрыты владельцами. Слева до, справа после.

*F0136*
#grid(columns: (1fr, 1fr), gutter: 5mm, image("../flowers-all-2026-10-20/integrations/F0136/before/F0136-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"), image("../flowers-all-2026-10-20/integrations/F0136/after/F0136-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"))

*F0137*
#grid(columns: (1fr, 1fr), gutter: 5mm, image("../flowers-all-2026-10-20/integrations/F0137/before/F0137-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"), image("../flowers-all-2026-10-20/integrations/F0137/after/F0137-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"))

*F0029*
#grid(columns: (1fr, 1fr), gutter: 5mm, image("../flowers-all-2026-10-20/integrations/F0029/before/F0029-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"), image("../flowers-all-2026-10-20/integrations/F0029/after/F0029-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"))

#pagebreak()
= Баржа · два обычных увеличения — применено
F0061 экран выбора и F0063 результат «Пётр», mobile390 DPR2. Это интерполяция, не Flowers и не восстановление новых деталей. Не внедрение предложений A/B/C.

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 3mm,
[*F0061 до* #image("../conventional-media-2026-10-22/barge-choice-tall-v1/before/390-dpr2.png", height: 137mm)],
[*F0061 после* #image("../conventional-media-2026-10-22/barge-choice-tall-v1/after/390-dpr2.png", height: 137mm)],
[*F0063 до* #image("../conventional-media-2026-10-22/barge-petr-boat-v1/before/390-dpr2.png", height: 137mm)],
[*F0063 после* #image("../conventional-media-2026-10-22/barge-petr-boat-v1/after/390-dpr2.png", height: 137mm)])

#pagebreak()
= Что осталось

- *Вертолёт:* содержание и окраска по референсу ОС, в том числе во вступлении. Повышение резкости старого вертолёта эту задачу не закрывает.
- *Склад:* проверить художественную доработку геометрически согласованного каркаса. Предыдущая портретная версия отклонена; новый 3D preview не опубликован как готовая игровая иллюстрация.
- *Медиа:* применить принятые результаты без ожидания полного набора; проверить обычное увеличение там, где оно помогает. Незавершённые проходы и отклонённые фрагменты не считать готовыми.

*Границы проверки:* использованы сохранённые снимки и runtime receipts владельца интеграции, без повторного прохождения всей игры. Этот PDF визуально проверен после сборки; он не заменяет художественную приёмку Михаилом.

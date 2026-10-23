from pathlib import Path
import subprocess
import shutil
D=Path(__file__).resolve().parent
R=D.parents[2]
s='''#set page(paper: "a4", flipped: true, margin: 12mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 11pt)
#set par(leading: 0.6em)
= Energy+ Quest — текущий обзор
Обновлено 23 октября 2026 · проверенная локальная версия: http://127.0.0.1:4344/

*Применено:* компактная общая панель выбора грузовика на десктопе; радиальная светлая подложка вступления; обработанное изображение получателя Альвы F0001; результат зелёной фуры F0075 на mobile/tablet; удаление синей обводки осмотра фуры; навигация и блок баллов вступления; финал с popup «Поделиться» и официальным MAX.

В этом PDF — только последний законченный набор, по совпадающим размерам экрана «до / после». Мобильные пары также показаны: сохранение мобильной компоновки не означает её редизайн.

*Качество медиа:* в runtime подтверждены 23 обработанных исходника: 19 выборочных Flowers и 4 обычных увеличения. Последняя общая проверка: 120 уникальных runtime-состояний, HTTP и JS ошибок нет. Это не означает готовность всей графики. По решению Михаила от 22 октября обязательный Flowers для всех 113 отменён: для общей массы — обычное увеличение с проверкой видимой пользы, для проблемных крупных иллюстраций — выборочная AI-реконструкция. Обычное увеличение не восстанавливает реальные детали.

*Не готово:* новый склад и вертолёт по референсу; оставшиеся проверки графики. Они перечислены в конце и не выдаются за применённые.

Внешний сайт energy-plus-quest.hypcat.net этим отчётом не проверен и не обновлён. Старые отчёты и эксперименты удалены. Склад на рабочем сайте остаётся отклонённым; новый вариант не принят.
'''
def pair(title,root,before,after,note):
 global s
 s+='\n#pagebreak()\n= '+title+'\n'+note+'\n\n'
 s+=f'#grid(columns: (1fr, 1fr), gutter: 6mm, [*До*\n\n#image("{root}/{before}", width: 100%, height: 145mm, fit: "contain")], [*После — применено на 4344*\n\n#image("{root}/{after}", width: 100%, height: 145mm, fit: "contain")])\n'
for scene,label,note in [('carrier','Грузовики','Вопрос, варианты и навигация собраны в единую панель. Lucide Truck в четырёх цветах, без видимых подписей цветов. Это экран выбора, не проверка удаления обводки при осмотре фуры.'),('intro','Вступление','Радиальная светлая подложка вместо заметного прямоугольного поля. Текст сохранён. Это стартовый экран, не исправление навигации следующего вводного экрана.')]:
 for viewport in ['1440x900','390x844']:
  pair(f'{label} · {viewport}','../general-ux-2026-10-21',f'before/{scene}-{viewport}.png',f'after/{scene}-{viewport}.png',note)
for width,label in [('1440','desktop'),('390','mobile')]:
 pair(f'Альва · F0001 · {label}, DPR 2','../flowers-all-2026-10-20/integrations/F0001',f'before/{width}-dpr2.png',f'after/{width}-dpr2.png','Два прохода, мастер 8192×4096; в игре декодирован ресурс 1600×800. Это реконструированная детализация, не единая native-генерация 8K. Изменён только media URL; новый popup финала в эту публикацию не входит.')
for width,label in [('390','mobile'),('800','tablet')]:
 pair(f'Зелёная фура · F0075 · {label}, DPR 2','../flowers-all-2026-10-20/integrations/F0075',f'before/{width}-dpr2.png',f'after/{width}-dpr2.png','Применён выборочный двухпроходный мастер. Силуэт правого водителя и прилегающая область сохранены из исходника, чтобы исключить двойной контур. Проверены 8 случаев: 390/800/844/1440 × DPR 1/2; новый F0075 виден в шести. На 1440 остаётся прежний crew-wide-v6 — этот wide источник данным обновлением не улучшен. Видимый F0075: HTTP 200, JS ошибок нет; в ранней публикации был посторонний prefetch /assets/assets/... 404; в последней общей проверке 120 состояний HTTP ошибок нет.')
for width in ['1440','390']:
 pair(f'Осмотр фуры · без синей обводки · {width}px','../feedback-2026-10-22/carrier',f'before/{width}-inspection.png',f'after/{width}-inspection.png','Синяя обводка и заливка удалены. Проверены все четыре фуры: мышь, touch, клавиатура; 5 размеров экрана, 15 after-снимков. Оранжевый контур 2px сохранён только при клавиатурном фокусе для доступности — это не выделение выбранной машины.')
pair('Compact · F0144 · desktop 1440, DPR 2','../flowers-all-2026-10-20/integrations/F0144','before/1440-dpr2.png','after/1440-dpr2.png','Обработан wide-источник, runtime 5120×2560. На mobile этот wide слой скрыт (rect 0×0); F0144 сам по себе не улучшает портретную версию.')
for width in ['1440','390']:
 pair(f'Последняя миля · F0095 · {width}px, DPR 2','../flowers-all-2026-10-20/integrations/F0095',f'before/{width}-dpr2.png',f'after/{width}-dpr2.png','Выборочная обработка качества результата наземной доставки. Она не закрывает отдельную задачу перерисовать вертолёт по референсу ОС.')
for folder,title in [('carrier-old-wide-v8-v1','F0082 · результат старой фуры'),('rover-boat-khor-v1','F0107 · снегоболотоход')]:
 for width in ['1440','390']:
  pair(f'Обычное увеличение · {title} · {width}px','../conventional-media-2026-10-22/'+folder,f'before/{width}-dpr2.png',f'after/{width}-dpr2.png','Интерполяция с сохранением исходника. Не Flowers и не AI-реконструкция: новые достоверные детали не восстановлены. Сравнивается отображение в игре, а не только экспортированный размер.')
for asset,widths in [('F0025',['390']),('F0026',['1440']),('F0027',['1440']),('F0028',['1440']),('F0145',['1440','390']),('F0146',['1440','390'])]:
 for width in widths:
  pair(f'Compact · {asset} · {width}px, DPR 2','../flowers-all-2026-10-20/integrations/compact-six',f'before/{asset}-{width}-dpr2.png',f'after/{asset}-{width}-dpr2.png','Пакет шести выборочно обработанных исходников применён на4344; 16 runtime-состояний проверены с DPR 1/2. Сохранённые из исходника области не считаются восстановленной детализацией. Это проверка качества медиа, не новое утверждение о выполнении всех требований сцены.')
for screen,label in [('story','Навигация'),('scores','Баллы по исходной ОС')]:
 for width in ['1440','390']:
  pair(f'Вступление · {label} · {width}px','../intro-2026-10-22-feedback',f'before/{width}-{screen}.png',f'after/{width}-{screen}.png','Применено на4344: «Назад» и «Далее» по противоположным краям; порядок чтения блока баллов по исходному сценарию и ОС. Проверены15экранов на320/390/844/1440/1920: действия видимы и не меньше44px, границы навигации совпадают, overflow нет, HTTP ошибок нет. Исправлены абсолютные URL фонов. Текст не переизобретён — применён исходный комментарий.')
for viewport in ['1440x900','390x844']:
 pair(f'Финал · {viewport}','../ending-2026-10-21-share-feedback',f'before-{viewport}-result.png',f'runtime-{viewport}-result.png','Применено на обычном4344: понятная кнопка «Поделиться», соцсети и скачивание перенесены в popup, официальный знак MAX. Четыре viewport проверены; два runtime-теста поведения пройдены. Сценарные абзацы и CTA сохранены. Запись на практику остаётся заглушкой.')
s+='''
#pagebreak()
= Финал · новое окно «Поделиться»
Применено на4344. Соцсети и явно подписанное скачивание сертификата внутри popup. Проверены открытие, скачивание PNG, удержание фокуса, Escape, закрытие и возврат фокуса. Native share файла зависит от браузера; ссылки соцсетей передают текст и URL.

#grid(columns: (1fr, 1fr), gutter: 6mm,
[*Desktop 1440×900* #image("../ending-2026-10-21-share-feedback/runtime-1440x900-popup.png", width: 100%, height: 135mm, fit: "contain")],
[*Mobile 390×844* #image("../ending-2026-10-21-share-feedback/runtime-390x844-popup.png", width: 100%, height: 135mm, fit: "contain")])
'''
s+='''
#pagebreak()
= Баржа · варианты A/B/C — только для обсуждения
Не внедрено в игру. Слева текущий runtime, далее три предложения мобильного экрана выбора. Проверены 120 состояний без overflow и 6 клавиатурных случаев; это техническая проверка, не приёмка Федей и не тест с игроками.

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 3mm,
[*Текущая игра* #image("../barge-2026-10-22/frames/mobile-runtime-boat-choice.png", height: 125mm)],
[*Вариант A* #image("../barge-2026-10-22/frames/mobile-a-boat-choice.png", height: 125mm)],
[*Вариант B* #image("../barge-2026-10-22/frames/mobile-b-boat-choice.png", height: 125mm)],
[*Вариант C* #image("../barge-2026-10-22/frames/mobile-c-boat-choice.png", height: 125mm)])

#link("http://127.0.0.1:4344/review/barge-2026-10-22/index.html")[Открыть интерактивное сравнение mobile/desktop и результатов]. Прототип «Продолжить» возвращает к сравнению; исходный crop 768×512 не является финальной графикой desktop DPR 2. Вопросы офис/ПРУ и обоснования крана для маленьких подарков остаются открыты.
'''
s+='''
#pagebreak()
= Compact · последние три применённых исходника
Выборочные Flowers, actual4344. Ниже компактные пары desktop1440 DPR2; в receipts F0136/137 также проверен mobile390. Сохранённые исходные области раскрыты владельцами. Слева до, справа после.
'''
for asset in ['F0136','F0137','F0029']:
 s+=f'\n*{asset}*\n#grid(columns: (1fr, 1fr), gutter: 5mm, image("../flowers-all-2026-10-20/integrations/{asset}/before/{asset}-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"), image("../flowers-all-2026-10-20/integrations/{asset}/after/{asset}-1440-dpr2.png", width: 100%, height: 40mm, fit: "contain"))\n'
s+='''
#pagebreak()
= Баржа · два обычных увеличения — применено
F0061 экран выбора и F0063 результат «Пётр», mobile390 DPR2. Это интерполяция, не Flowers и не восстановление новых деталей. Не внедрение предложений A/B/C.

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 3mm,
[*F0061 до* #image("../conventional-media-2026-10-22/barge-choice-tall-v1/before/390-dpr2.png", height: 137mm)],
[*F0061 после* #image("../conventional-media-2026-10-22/barge-choice-tall-v1/after/390-dpr2.png", height: 137mm)],
[*F0063 до* #image("../conventional-media-2026-10-22/barge-petr-boat-v1/before/390-dpr2.png", height: 137mm)],
[*F0063 после* #image("../conventional-media-2026-10-22/barge-petr-boat-v1/after/390-dpr2.png", height: 137mm)])
'''
s+='''
#pagebreak()
= Что осталось

- *Вертолёт:* содержание и окраска по референсу ОС, в том числе во вступлении. Повышение резкости старого вертолёта эту задачу не закрывает.
- *Склад:* проверить художественную доработку геометрически согласованного каркаса. Предыдущая портретная версия отклонена; новый 3D preview не опубликован как готовая игровая иллюстрация.
- *Медиа:* применить принятые результаты без ожидания полного набора; проверить обычное увеличение там, где оно помогает. Незавершённые проходы и отклонённые фрагменты не считать готовыми.

*Границы проверки:* использованы сохранённые снимки и runtime receipts владельца интеграции, без повторного прохождения всей игры. Этот PDF визуально проверен после сборки; он не заменяет художественную приёмку Михаилом.
'''
(D/'current-review.typ').write_text(s)
subprocess.run(['typst','compile','--root',str(R),str(D/'current-review.typ'),str(D/'current-review.pdf')],check=True)
# Screen captures contain far more pixels than a landscape A4 page displays.
# Keep the source screenshots separately and make the distributable report small.
if shutil.which('gs'):
 compact=D/'current-review.compact.pdf'
 subprocess.run(['gs','-q','-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite',
  '-dCompatibilityLevel=1.6','-dPDFSETTINGS=/ebook',
  '-dPassThroughJPEGImages=false','-dPassThroughJPXImages=false',
  '-dDownsampleColorImages=true','-dColorImageResolution=120',
  '-dColorImageDownsampleThreshold=1.0','-dAutoFilterColorImages=false',
  '-dColorImageFilter=/DCTEncode','-dDownsampleGrayImages=true',
  '-dGrayImageResolution=120','-dGrayImageDownsampleThreshold=1.0',
  '-dAutoFilterGrayImages=false','-dGrayImageFilter=/DCTEncode','-dJPEGQ=80',
  f'-sOutputFile={compact}',str(D/'current-review.pdf')],check=True)
 compact.replace(D/'current-review.pdf')

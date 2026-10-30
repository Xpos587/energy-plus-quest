# Передача игры на площадку Energy Plus

Каноническая инструкция для принимающей стороны —
[README-DEPLOY.txt](../public/README-DEPLOY.txt). Она входит в архив вместе
с [фрагментом Nginx](../deploy/nginx-joydelivery.conf). Здесь описаны основания
формата передачи и границы проверки; серверные шаги следует брать из README.

## Текущий пакет

`sh scripts/package-static.sh` собирает текущую рабочую директорию и создаёт
`release/energy-plus-quest-static.zip`. Это статическая игра с подготовкой
отправления и всеми пятью этапами, а не preview первой сцены. Пакет включает
используемые иллюстрации, шрифты и видео; материалы ревью и страницы референсов
не предназначены для публикации и не входят в runtime-пакет.

Целевой адрес: `https://e-plus.media/specprojects/joydelivery/`.
Содержимое архива должно начинаться с `index.html`, без дополнительного `dist/`.
Сборка использует относительную базу `./`, отдельный минифицированный JavaScript
и CSS (`BUILD_MINIFY=true`, `BUILD_SINGLEFILE=false`). Минификация не является
обфускацией. Прогресс хранится локально в браузере; серверная база данных
и интеграция с WordPress не требуются.

## Что взято из рабочего примера

Предоставленный `RS.zip` служит примером статического спецпроекта Readymag,
который площадка умеет размещать. Формат передачи нашей игры следует той же
модели: самостоятельный HTML и внешние ресурсы с сохранением структуры
каталогов. Исходники Readymag и его собственные скрипты в игру не переносятся.

Сам факт работоспособности примера не устанавливает причину прежнего сбоя
на площадке. В частности, из него не следует, что виновата минификация
или что весь JavaScript обязательно нужно встроить в HTML. Причину можно
подтвердить только ответами сервера и ошибками браузера проблемной публикации.

Для этой игры приложен собственный Nginx-фрагмент: область действия ограничена
`/specprojects/joydelivery/`, адрес без завершающего слеша перенаправляется,
MIME-типы заданы явно, отсутствующие ресурсы возвращают 404. HTML и необязательный
скрипт кеширования требуют перевалидации; immutable применяется только к
ресурсам с хешем в имени. Фрагмент необходимо адаптировать к фактическому
webroot и существующему server-блоку, как описано в README.

## Что подтверждают проверки

Упаковщик проверяет распакованный архив через временный Nginx в Podman.
`scripts/verify-static-runtime.mjs` проверяет транспорт: HTTP-ответы,
перенаправление, MIME-типы, ресурсы и отсутствие подмены отсутствующего файла
HTML-страницей. Это не браузерный тест игрового процесса.

Отдельная проверка в браузере должна подтвердить запуск и прохождение игры
на сборке, отдаваемой по целевому подпути. Проверка площадки после публикации
остаётся необходимой: её конфигурация, CDN, CSP и CMS могут отличаться
от локального окружения. В этом документе не утверждается, что конкретная
сборка уже прошла проверки или опубликована у заказчика; результаты фиксируются
в отчёте соответствующей передачи.

## Подтверждённая проблема действующей публикации

28 сентября 2026 года проверен публичный адрес
`https://e-plus.media/specprojects/joydelivery/`. Он вернул HTTP 200 с
`Content-Type: text/html` и ссылками старой сборки от 17 августа на
`./assets/index-Bzu12aGt.js` и `./assets/index-D_EN9uWn.css`. CSS возвращался
с HTTP 200 и `Content-Type: text/css`. Запрос JavaScript вместо файла получил
HTTP 301 с перенаправлением на
`https://e-plus.media/specprojects/joydelivery/assets/index-bzu12agtjs/`,
заголовками `x-redirect-by: WordPress` и `x-powered-by: PHP`.
Переход по этому перенаправлению завершался HTTP 404 с `Content-Type: text/html`.

Таким образом, запрос JavaScript попадает в CMS, а браузер не получает
ожидаемый JS-файл. Минификация не объясняет этот подтверждённый сбой доставки:
до выполнения JavaScript дело не доходит. По внешним ответам нельзя определить,
отсутствует ли файл на диске или запрос перехватывается правилами маршрутизации.
На площадке необходимо проверить обе причины. Изоляция каталога игры через
`^~` в приложенном Nginx-фрагменте защищает его от внешних regex-location,
но не заменяет размещение самих файлов по правильному пути.

Эта диагностика выполнена без публикации новой версии на сервере заказчика.

## Final invitation links

The last screen has one target path: the words «Узнайте больше о компании» in the certificate text open https://supply.gazprom-neft.ru/ in a new tab. The home icon links to https://e-plus.media/.

Share links (Telegram, VK, MAX, phone share sheet) point to a public result page `r/<profile>-<type>/` (7 pages, no player data). The build (`scripts/share-pages.ts`) writes each page with Open Graph tags and a 1200×630 `card.jpg`; chats show the card as the link preview, and the page button leads into the game. `og:url`/`og:image` must be absolute: the build uses `PUBLIC_URL` (default `https://e-plus.media/specprojects/joydelivery/`; the Dokploy image sets `https://energy-plus-quest.hypcat.net/`). Building on another address requires `PUBLIC_URL=<address ending in />`. Messengers cache previews: after a change, refresh Telegram via @WebpageBot and VK via the `pages.clearCache` API method.

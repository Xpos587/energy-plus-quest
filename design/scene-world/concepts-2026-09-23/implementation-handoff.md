# Передача в реализацию

Стиль и источники: [DESIGN.md](DESIGN.md), [контракт](design-contract.md).

- Общая оболочка: `src/scenes/WorldArt.tsx`, новый prop `illustration?: (format: "desktop" | "mobile") => ReactNode`; при его наличии SVG заменяет прежнюю картинку. Размеры и маркеры задаёт `worldManifest.json`.
- Склад: `inventory/InventoryConcept.tsx` + `InventoryArt.tsx`. Результаты entrance/alphabet/keeper/wms. Кладовщик и WMS оба размещают рядом с отгрузкой: различается сохранение адреса, а не правильность места.
- Баржа: `crane/CraneConcept.tsx` + `CraneArt.tsx`. Два крана, один Иван, Пётр у дальнего. wait оставляет подарок на причале, остальные грузят; rush утомляет Ивана, petr задерживает собственную работу Петра, remote показывает пульт в офисе.
- Последние препятствия: `lastmile/LastmileConcept.tsx` + `LastmileArt.tsx`. helicopter — для Алвы/Хора ещё ≥10 км на снегоболотоходе; rover плывёт через реку; robot застревает в грунте; гусеничный pipe-carrier останавливается у воды, подарок переправляет дрон либо снегоболотоход для лодки, трубы возвращаются.
- Не менять index.ts, сценарную прозу, баллы и progress reducer. Не использовать сторонние изображения как игровые ассеты.
- Проверка: TypeScript, unit tests сцен, browser journey и фактический осмотр SVG в обоих форматах.

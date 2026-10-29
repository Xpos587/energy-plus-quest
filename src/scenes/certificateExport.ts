import type { logistProfileCopy } from "./endingCopy";

export type LogistCopy = ReturnType<typeof logistProfileCopy>;
/* The player shares the certificate as their own, so it speaks as «я».
   «Мне удалось …» avoids guessing the player's gender in past-tense verbs. */
const firstPerson: [RegExp, string][] = [
  [/^Вы — /u, "Я — "],
  [/^Вы только начинаете/u, "Я только начинаю"],
  [
    /^Вы не только сделали сюрприз (.+?)\. Вы также успешно позаботились/u,
    "Мне удалось не только сделать сюрприз $1, но и успешно позаботиться",
  ],
  [/^Вы не только (доставили|сделали)/u, "Мне удалось не только $1"],
  [/доставили/gu, "доставить"],
  [/сэкономили/gu, "сэкономить"],
  [/но и позаботились/gu, "но и позаботиться"],
  [/вы находили/gu, "мне удавалось находить"],
  [/вы выбирали/gu, "мне удавалось выбирать"],
  [/которая вам помогала/gu, "которая мне помогала"],
  /* «мы» is the company; from the player it would claim a job there. */
  [/мы тоже знаем/gu, "тоже знают"],
  [/ваших/giu, "моих"],
];
export function certificateCopy(copy: LogistCopy) {
  return [copy.title, ...copy.paragraphs].map((text) =>
    firstPerson.reduce((t, [from, to]) => t.replace(from, to), text),
  );
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () =>
      reject(new Error("Не удалось загрузить иллюстрацию сертификата."));
    image.src = src;
  });
}

/** Render the share artifact independently of responsive screen layout. */
export async function exportCertificate(copy: LogistCopy, artwork: string) {
  await document.fonts.ready;
  const [image, brand] = await Promise.all([
    loadImage(artwork),
    loadImage(`${import.meta.env.BASE_URL}brand/quest-brand-lockup.svg`),
  ]);
  /* Story format (R15): Telegram, VK and MAX stories take a 9:16 picture. */
  const W = 1080;
  const H = 1920;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Не удалось подготовить картинку.");
  ctx.fillStyle = "#fffdf7";
  ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = "#07629c";
  ctx.lineWidth = 4;
  ctx.strokeRect(28, 28, W - 56, H - 56);
  ctx.lineWidth = 1;
  ctx.strokeRect(40, 40, W - 80, H - 80);
  ctx.fillStyle = "#ff6500";
  for (const [x, y] of [
    [28, 28],
    [W - 28, 28],
    [28, H - 28],
    [W - 28, H - 28],
  ]) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(Math.PI / 4);
    ctx.fillRect(-12, -12, 24, 24);
    ctx.restore();
  }
  const brandWidth = 700;
  const brandHeight = brandWidth * (brand.naturalHeight / brand.naturalWidth);
  ctx.drawImage(brand, (W - brandWidth) / 2, 100, brandWidth, brandHeight);
  const artSize = 640;
  const artTop = 100 + brandHeight + 60;
  ctx.drawImage(image, (W - artSize) / 2, artTop, artSize, artSize);
  const family = getComputedStyle(document.body).fontFamily;
  let y = artTop + artSize + 70;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillStyle = "#123750";
  const wrap = (text: string, size: number, weight: number) => {
    ctx.font = `${weight} ${size}px ${family}`;
    const lines: string[] = [];
    let line = "";
    for (const word of text.split(/\s+/u)) {
      const candidate = line ? `${line} ${word}` : word;
      if (line && ctx.measureText(candidate).width > 900) {
        lines.push(line);
        line = word;
      } else line = candidate;
    }
    if (line) lines.push(line);
    for (const row of lines) {
      ctx.fillText(row, W / 2, y);
      y += size * 1.32;
    }
    y += 28;
  };
  const [title, ...paragraphs] = certificateCopy(copy);
  ctx.fillStyle = "#07629c";
  wrap(title, 64, 700);
  ctx.fillStyle = "#123750";
  for (const paragraph of paragraphs) wrap(paragraph, 38, 400);
  ctx.font = `400 30px ${family}`;
  ctx.fillStyle = "#44667d";
  const footer = location.host + location.pathname.replace(/\/$/u, "");
  ctx.fillText(footer, W / 2, H - 120);
  if (y > H - 150)
    throw new Error("Текст не помещается в картинку.");
  const jpeg = await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (value) =>
        value
          ? resolve(value)
          : reject(new Error("Не удалось сохранить изображение.")),
      "image/jpeg",
      0.92,
    ),
  );
  return new File([jpeg], `dostavlyaem-radost-${copy.type}.jpg`, {
    type: "image/jpeg",
  });
}

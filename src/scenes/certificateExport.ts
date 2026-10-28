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

/** One-page PDF around a JPEG; a page of `width`×`height` points. */
export function jpegPdf(
  jpeg: Uint8Array,
  pixels: [number, number],
  width: number,
  height: number,
) {
  const encoder = new TextEncoder();
  const parts: Uint8Array[] = [];
  let size = 0;
  const push = (part: string | Uint8Array) => {
    const bytes = typeof part === "string" ? encoder.encode(part) : part;
    parts.push(bytes);
    size += bytes.length;
  };
  const content = `q ${width} 0 0 ${height} 0 0 cm /Im0 Do Q`;
  const objects: (string | Uint8Array)[][] = [
    ["<< /Type /Catalog /Pages 2 0 R >>"],
    ["<< /Type /Pages /Kids [3 0 R] /Count 1 >>"],
    [
      `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${width} ${height}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>`,
    ],
    [
      `<< /Type /XObject /Subtype /Image /Width ${pixels[0]} /Height ${pixels[1]} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>\nstream\n`,
      jpeg,
      "\nendstream",
    ],
    [`<< /Length ${content.length} >>\nstream\n${content}\nendstream`],
  ];
  const offsets: number[] = [];
  push("%PDF-1.4\n");
  objects.forEach((object, index) => {
    offsets.push(size);
    push(`${index + 1} 0 obj\n`);
    for (const part of object) push(part);
    push("\nendobj\n");
  });
  const xref = size;
  push(
    `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n${offsets
      .map((offset) => `${String(offset).padStart(10, "0")} 00000 n \n`)
      .join("")}trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`,
  );
  return new Blob(parts as BlobPart[], { type: "application/pdf" });
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
  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 1400;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Не удалось подготовить сертификат.");
  ctx.fillStyle = "#fffdf7";
  ctx.fillRect(0, 0, 1200, 1400);
  ctx.strokeStyle = "#07629c";
  ctx.lineWidth = 4;
  ctx.strokeRect(28, 28, 1144, 1344);
  ctx.lineWidth = 1;
  ctx.strokeRect(40, 40, 1120, 1320);
  ctx.fillStyle = "#ff6500";
  for (const [x, y] of [
    [28, 28],
    [1172, 28],
    [28, 1372],
    [1172, 1372],
  ]) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(Math.PI / 4);
    ctx.fillRect(-12, -12, 24, 24);
    ctx.restore();
  }
  const brandWidth = 740;
  const brandHeight = brandWidth * (brand.naturalHeight / brand.naturalWidth);
  ctx.drawImage(brand, (1200 - brandWidth) / 2, 60, brandWidth, brandHeight);
  ctx.drawImage(image, 350, 190, 500, 500);
  const family = getComputedStyle(document.body).fontFamily;
  let y = 775;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillStyle = "#123750";
  const wrap = (text: string, size: number, weight: number) => {
    ctx.font = `${weight} ${size}px ${family}`;
    const lines: string[] = [];
    let line = "";
    for (const word of text.split(/\s+/u)) {
      const candidate = line ? `${line} ${word}` : word;
      if (line && ctx.measureText(candidate).width > 980) {
        lines.push(line);
        line = word;
      } else line = candidate;
    }
    if (line) lines.push(line);
    for (const row of lines) {
      ctx.fillText(row, 600, y);
      y += size * 1.32;
    }
    y += 24;
  };
  const [title, ...paragraphs] = certificateCopy(copy);
  wrap(title, 54, 700);
  for (const paragraph of paragraphs) wrap(paragraph, 32, 400);
  if (y > 1340)
    throw new Error("Текст сертификата не помещается в изображение.");
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
  /* 1200×1400 px on a 600×700 pt page: about 144 dpi, sharp in print. */
  const pdf = jpegPdf(
    new Uint8Array(await jpeg.arrayBuffer()),
    [1200, 1400],
    600,
    700,
  );
  return new File([pdf], `dostavlyaem-radost-${copy.type}.pdf`, {
    type: "application/pdf",
  });
}

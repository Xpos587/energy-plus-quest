import type { logistProfileCopy } from "./endingCopy";

export type LogistCopy = ReturnType<typeof logistProfileCopy>;
export function certificateCopy(copy: LogistCopy) {
  return [copy.title, ...copy.paragraphs].map((text) =>
    text.replace(/ваших/giu, "моих"),
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
  const blob = await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (value) =>
        value
          ? resolve(value)
          : reject(new Error("Не удалось сохранить изображение.")),
      "image/png",
    ),
  );
  return new File([blob], `dostavlyaem-radost-${copy.type}.png`, {
    type: "image/png",
  });
}

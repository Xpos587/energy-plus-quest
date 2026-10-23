import path from "node:path";

const root = path.resolve(import.meta.dir, "..");
const server = Bun.serve({
  hostname: "127.0.0.1",
  port: Number(process.env.QUEST_PREVIEW_PORT ?? 4344),
  async fetch(request) {
    const pathname = decodeURIComponent(new URL(request.url).pathname);
    const [directory, relative] = pathname.startsWith("/review/")
      ? [path.join(root, "docs/reviews"), pathname.slice(8)]
      : pathname.startsWith("/public/")
        ? [path.join(root, "public"), pathname.slice(8)]
        : [path.join(root, "dist"), pathname.slice(1)];
    const filename = path.resolve(directory, relative || "index.html");
    if (!filename.startsWith(directory + path.sep)) return new Response("Invalid path", { status: 400 });
    const file = Bun.file(filename);
    if (!await file.exists()) return new Response("Missing", { status: 404 });
    return new Response(file, { headers: { "Content-Type": file.type, "Cache-Control": "no-cache" } });
  },
});
console.log(`Current game: ${server.url}`);

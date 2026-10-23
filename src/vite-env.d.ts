/// <reference types="vite/client" />

declare module "virtual:thumbnail-images" {
  const images: Record<string, string>;
  export default images;
}

declare module "virtual:optimized-images" {
  const images: Record<string, string>;
  export default images;
}
declare module "virtual:responsive-images" {
  const images: Record<string, { avif: string; desktopAvif?: string; desktopWebp?: string; avifSrcSet: string; webpSrcSet: string; width: number; height: number }>;
  export default images;
}

// GitHub Pages serves main:/, while Astro writes docs/. Sync only Music Mirror.
import { readFile, writeFile, cp, rm, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
const support = await readFile('docs/music-mirror/support.html/index.html');
await rm('docs/music-mirror/support.html', { recursive: true });
await writeFile('docs/music-mirror/support.html', support);
await mkdir('music-mirror', { recursive: true });
await cp('docs/music-mirror', 'music-mirror', { recursive: true });
const pages = ['index.html', 'get-started/index.html', 'faq/index.html', 'support.html'];
const assets = new Set();
for (const page of pages) {
  const html = await readFile(join('docs/music-mirror', page), 'utf8');
  for (const match of html.matchAll(/(?:href|src)="(\/_astro\/[^"?#]+)"/g)) assets.add(match[1]);
}
await mkdir('_astro', { recursive: true });
for (const asset of assets) await cp('docs' + asset, '.' + asset);
// These exact files belong to the superseded, unpublished October 17 draft.
for (const base of ['public', 'docs', '.']) {
  for (const name of ['music-mirror-upcoming-preview.mp4', 'preview-poster.jpg', 'preview.vtt']) {
    await rm(join(base, 'music-mirror/assets', name), { force: true });
  }
}
await rm('_astro/index.f5GFQ90o.css', { force: true });
console.log('Synced Music Mirror pages and their CSS to the GitHub Pages root.');

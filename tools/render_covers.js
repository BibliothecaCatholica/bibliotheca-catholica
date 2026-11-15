// Render edition covers (tools/covers.py --build): each assets/covers/<edition>.svg is drawn in Chromium with the
// site's own self-hosted fonts (inlined, so nothing is fetched) and saved as <edition>.png (600x900, converted to WebP
// by covers.py) and <edition>-og.jpg (1200x630 social image: the cover centred on the site's paper colour).
// Usage: node tools/render_covers.js assets/covers <edition> [<edition> ...]
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const face = (family, weight, file) => `@font-face{font-family:'${family}';font-weight:${weight};font-style:normal;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(ROOT, 'fonts', file)).toString('base64')}) format('woff2')}`;
const FONTS = [
  face('Cormorant Garamond', 500, 'cormorantgaramond-normal-latin.woff2'),
  face('EB Garamond', 400, 'ebgaramond-normal-latin.woff2'),
].join('') + [
  // latin-ext second, so accented capitals (Thérèse, Ávila) come from the same families
  `@font-face{font-family:'Cormorant Garamond';font-weight:500;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(ROOT, 'fonts/cormorantgaramond-normal-latin-ext.woff2')).toString('base64')}) format('woff2');unicode-range:U+0100-024F,U+1E00-1EFF}`,
  `@font-face{font-family:'EB Garamond';font-weight:400;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(ROOT, 'fonts/ebgaramond-normal-latin-ext.woff2')).toString('base64')}) format('woff2');unicode-range:U+0100-024F,U+1E00-1EFF}`,
].join('');

(async () => {
  const [out, ...ids] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
  for (const id of ids) {
    const svg = fs.readFileSync(path.join(out, id + '.svg'), 'utf8');
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>${FONTS}html,body{margin:0;background:#f6f0e2}
      #c{width:600px;height:900px}#c svg{display:block;width:600px;height:900px}
      #og{width:1200px;height:630px;display:flex;align-items:center;justify-content:center;background:#f6f0e2}
      #og svg{display:block;width:380px;height:570px;box-shadow:0 2px 6px rgba(42,33,24,.25),0 14px 34px rgba(42,33,24,.18)}</style>
      <div id="c">${svg}</div><div id="og">${svg}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.locator('#c').screenshot({ path: path.join(out, id + '.png') });
    await page.locator('#og').screenshot({ path: path.join(out, id + '-og.jpg'), type: 'jpeg', quality: 86 });
  }
  await browser.close();
})();

#!/usr/bin/env node
/* Browser check for the Advent reading plan (docs/ADVENT-LAUNCH.md, Implementation/QA).
 * Not part of CI or `npm run validate`; it needs Playwright with Chromium installed.
 *
 *   python3 tools/serve.py &                      # local copy at http://127.0.0.1:4173
 *   node tools/check_plan_ui.js                   # or pass a base URL, e.g. https://bibliothecacatholica.com
 *   node tools/check_plan_ui.js <base> <shotDir>  # also writes phone screenshots in both themes
 *
 * Checks, on an emulated iPhone 13: /reading/advent-2026/ in light and dark (26 days, no horizontal scroll, no page
 * errors); keyboard (every Tab stop on the page shows a focus style and ends up on screen); the app view with the clock
 * set to December 8, 2026 (that day highlighted with aria-current="date"; Space marks it read, the mark survives a
 * reload, and Clear marks removes it); and every day's "Read day N" link (the reader opens at reading-p-<anchor>, the
 * excerpt's first words are in the passage, and the anchor settles under the header). Prints one line per check and
 * exits 1 on any failure. Reads data/advent-2026.json and data/reading-plans.json from this checkout.
 */
const { chromium, devices } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const BASE = (process.argv[2] || 'http://127.0.0.1:4173').replace(/\/$/, '');
const SHOTS = process.argv[3] || '';
const TEXT = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/advent-2026.json'), 'utf8'));
const PLAN = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/reading-plans.json'), 'utf8')).plans.find(p => p.id === 'advent-2026');
const PHONE = devices['iPhone 13'];
const norm = s => s.replace(/_/g, '').replace(/\[\d+\]|\(\d+\)/g, '').replace(/\s+/g, ' ').trim();
let failed = 0;
const report = (ok, name, detail) => { if (!ok) failed++; console.log((ok ? 'ok   ' : 'FAIL ') + name + (detail ? '  ' + detail : '')); };

(async () => {
  const browser = await chromium.launch();

  for (const theme of ['light', 'dark']) {
    const ctx = await browser.newContext({ ...PHONE, colorScheme: theme });
    await ctx.addInitScript(t => { try { localStorage.setItem('hub-theme', t); } catch (e) {} }, theme);
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(BASE + '/reading/advent-2026/', { waitUntil: 'networkidle' });
    const r = await page.evaluate(() => ({ theme: document.documentElement.dataset.theme, days: document.querySelectorAll('.plan-day').length,
      overflow: document.documentElement.scrollWidth - window.innerWidth }));
    report(r.theme === theme && r.days === 26 && r.overflow <= 0 && !errors.length, 'phone ' + theme, JSON.stringify(r) + (errors.length ? ' ' + errors[0] : ''));
    if (SHOTS) {
      fs.mkdirSync(SHOTS, { recursive: true });
      await page.screenshot({ path: path.join(SHOTS, 'advent-phone-' + theme + '.png') });
    }
    await ctx.close();
  }

  {
    const ctx = await browser.newContext({ ...PHONE, isMobile: false, hasTouch: false });
    const page = await ctx.newPage();
    await page.goto(BASE + '/reading/advent-2026/', { waitUntil: 'networkidle' });
    let stops = 0; const bad = []; let first = null;
    for (let i = 0; i < 400; i++) { // one full pass: stop when focus wraps back to the first stop
      await page.keyboard.press('Tab');
      await page.waitForTimeout(350); // the page scrolls smoothly to the focused element
      const f = await page.evaluate(() => {
        const e = document.activeElement; if (!e || e === document.body || e.tagName === 'IFRAME') return null; // the Substack embed draws its own focus
        const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
        return { name: e.tagName + ' ' + (e.getAttribute('aria-label') || e.textContent || '').trim().slice(0, 30),
          styled: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none', onScreen: r.bottom > 0 && r.top < innerHeight };
      });
      if (!f) continue;
      if (first === null) first = f.name; else if (f.name === first) break;
      stops++;
      if (!f.styled || !f.onScreen) bad.push(f);
    }
    report(stops > 100 && !bad.length, 'keyboard', stops + ' stops' + (bad.length ? '; ' + JSON.stringify(bad.slice(0, 3)) : ''));
    await ctx.close();
  }

  {
    const ctx = await browser.newContext(PHONE);
    const page = await ctx.newPage();
    await page.clock.setFixedTime(new Date('2026-12-08T10:00:00-06:00'));
    await page.goto(BASE + '/#/reading/advent-2026', { waitUntil: 'networkidle' });
    await page.waitForSelector('.plan-day input[data-day]');
    const today = await page.evaluate(() => { const x = document.querySelector('.plan-day.is-today'); return x && [x.id, x.getAttribute('aria-current')]; });
    report(JSON.stringify(today) === '["day-10","date"]', 'today highlight on Dec 8', JSON.stringify(today));
    await page.locator('#day-10 input[data-day]').focus(); await page.keyboard.press('Space');
    const marked = await page.evaluate(() => document.querySelector('#day-10 input[data-day]').checked);
    await page.reload({ waitUntil: 'networkidle' }); await page.waitForSelector('.plan-day input[data-day]');
    const kept = await page.evaluate(() => document.querySelector('#day-10 input[data-day]').checked);
    await page.locator('#plan-reset').focus(); await page.keyboard.press('Enter');
    const cleared = await page.evaluate(() => !document.querySelector('#day-10 input[data-day]').checked && localStorage.getItem('bc-plan:advent-2026') === null);
    report(marked && kept && cleared, 'mark as read by keyboard', JSON.stringify({ marked, kept, cleared }));
    await ctx.close();
  }

  const ctx = await browser.newContext(PHONE);
  for (const t of TEXT.days) {
    const d = PLAN.days[t.day - 1];
    const page = await ctx.newPage();
    try {
      await page.goto(BASE + '/#' + t.links.reader.split('#')[1], { waitUntil: 'networkidle' });
      await page.waitForSelector('#reading-p-' + d.anchor, { timeout: 15000 });
      await page.waitForTimeout(2500); // long chapters take a moment to scroll smoothly
      const r = await page.evaluate(([a, s, e]) => {
        const top = Math.round(document.getElementById('reading-p-' + a).getBoundingClientRect().top);
        const text = []; for (let i = s; i <= e; i++) { const x = document.getElementById('reading-p-' + i); text.push(x ? x.textContent : '\u0000'); }
        return { top, passage: text.join(' ') };
      }, [d.anchor, d.start, d.end]);
      const first = norm(t.excerpt.split('…')[0]).slice(0, 50);
      const ok = norm(r.passage).includes(first) && !r.passage.includes('\u0000') && r.top >= 0 && r.top < 300;
      report(ok, 'day ' + t.day + ' reader', '#reading-p-' + d.anchor + ' top=' + r.top);
    } catch (e) { report(false, 'day ' + t.day + ' reader', String(e).slice(0, 120)); }
    await page.close();
  }
  await browser.close();
  console.log(failed ? failed + ' failed' : 'all passed');
  process.exit(failed ? 1 : 0);
})();

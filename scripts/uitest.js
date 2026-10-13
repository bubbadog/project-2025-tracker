// Browser test of the site. Usage: python3 -m http.server 8765 --directory site & node scripts/uitest.js
// Opens every record, checks every link is https and opens in a new tab, checks contrast and phone layout.
// Env: UITEST_BASE (default http://127.0.0.1:8765/index.html), UITEST_SNAPSHOT (default site/snapshot.json),
// UITEST_CHROME (optional path to a Chromium binary when Playwright's own download is not available).
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = process.env.UITEST_BASE || 'http://127.0.0.1:8765/index.html';
const path = require('path');
const snap = JSON.parse(fs.readFileSync(process.env.UITEST_SNAPSHOT || path.join(__dirname, '..', 'site', 'snapshot.json'), 'utf8'));
const fails = [], notes = [];
const ok = (c, m) => { if (!c) fails.push(m); };

(async () => {
  const browser = await chromium.launch(process.env.UITEST_CHROME ? { executablePath: process.env.UITEST_CHROME } : {});
  async function open(opts, route) {
    const ctx = await browser.newContext(opts);
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push('CONSOLE ' + m.text()); });
    await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
    if (route) await route(page);
    await page.goto(BASE, { waitUntil: 'load' });
    await page.waitForTimeout(700);
    return { ctx, page, errs };
  }

  // ---- 1. every objective opens, every link is a real, safe, new-tab link
  {
    const { ctx, page, errs } = await open({ viewport: { width: 1280, height: 900 } });
    await page.click('button[data-view="list"]');
    await page.waitForTimeout(300);
    const n = await page.locator('.row').count();
    const shown = i => i.tracked !== false && ((snap.meta && snap.meta.show_layer3) || !(i.headline === false || (+i.layer || 1) >= 3));
    const tracked = snap.items.filter(shown).length;
    ok(n === tracked, `list shows ${n} rows, expected ${tracked}`);
    let links = 0, badLinks = 0, emptyText = 0, noPageLink = 0, plainSources = 0;
    for (let i = 0; i < n; i++) {
      await page.locator('.row').nth(i).click();
      await page.waitForSelector('#sheet[open]', { timeout: 3000 }).catch(() => fails.push('sheet did not open for row ' + i));
      const info = await page.evaluate(() => {
        const b = document.getElementById('sh-body');
        const as = [...b.querySelectorAll('a')];
        return {
          title: (document.getElementById('sh-title') || {}).textContent || '',
          id: (document.querySelector('#sh-k .mono') || {}).textContent || '',
          links: as.map(a => ({ h: a.getAttribute('href'), t: a.getAttribute('target'), r: a.getAttribute('rel'), x: a.textContent.trim() })),
          archive: as.filter(a => /archive\.org\/details/.test(a.href)).length,
          plain: [...b.querySelectorAll('.srcs li, .events .s')].filter(li => !li.querySelector('a') && !li.querySelector('.chk')).length,
          overflow: b.scrollWidth > b.clientWidth + 1,
          sections: [...b.querySelectorAll('h3')].map(h => h.textContent),
        };
      });
      ok(info.title.length > 5, `empty title at row ${i}`);
      ok(!info.overflow, `sheet overflows sideways for ${info.id}`);
      ok(info.sections.includes('What the document recommends') && info.sections.includes('Where it stands'), `missing core sections for ${info.id}`);
      for (const l of info.links) {
        links++;
        if (!/^https?:\/\/[^\s]+$/.test(l.h || '') || l.t !== '_blank' || !/noopener/.test(l.r || '')) { badLinks++; notes.push(`bad link in ${info.id}: ${l.h}`); }
        if (!l.x) { emptyText++; notes.push(`link with no text in ${info.id}: ${l.h}`); }
      }
      if (!info.archive) { noPageLink++; notes.push(`no document page link in ${info.id}`); }
      plainSources += info.plain;
      if (info.plain) notes.push(`${info.plain} source line(s) without a link in ${info.id}`);
      await page.click('#sh-close');
      await page.waitForTimeout(15);
    }
    console.log(`objectives opened: ${n}; links checked: ${links}; bad: ${badLinks}; empty text: ${emptyText}; no page link: ${noPageLink}; unlinked source lines: ${plainSources}`);
    ok(badLinks === 0, `${badLinks} malformed or unsafe links`);
    ok(emptyText === 0, `${emptyText} links with no visible text`);
    ok(noPageLink === 0, `${noPageLink} objectives without a document page link`);

    // ---- 2. filters, search, tabs, keyboard, deep link
    for (const stage of ['completed', 'implemented', 'in_progress', 'proposed', 'blocked', 'diverged', 'not_started', 'pending']) {
      const want = snap.items.filter(i => shown(i) && i.stage === stage).length;
      if (!want) continue;
      const chip = page.locator('.legend .chip').filter({ has: page.locator('.gl-' + stage) });
      await chip.click(); await page.waitForTimeout(120);
      const got = await page.locator('.row').count();
      ok(got === want, `stage filter ${stage}: ${got} rows, expected ${want}`);
      await chip.click(); await page.waitForTimeout(60);
    }
    await page.fill('#q', 'Schedule F'); await page.waitForTimeout(200);
    ok(await page.locator('.row').count() >= 1, 'search "Schedule F" found nothing');
    await page.fill('#q', 'zzzz-no-such-thing'); await page.waitForTimeout(200);
    ok(await page.locator('.empty').count() === 1, 'no empty state for a search with no results');
    await page.click('#clear'); await page.waitForTimeout(150);
    ok(await page.locator('.row').count() === tracked, 'clear filters did not restore all rows');
    for (const v of ['timeline', 'changes', 'method', 'list']) { await page.click(`button[data-view="${v}"]`); await page.waitForTimeout(150); ok((await page.locator('#main').innerText()).length > 40, `view ${v} rendered empty`); }
    ok(await page.locator('#tab-manage').isHidden(), 'Requirements tab is visible to a public viewer');
    await page.click('button[data-view="timeline"]'); await page.waitForTimeout(150);
    await page.locator('.tl-ch').first().focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(150);
    ok(await page.locator('.tl-item').count() > 0, 'keyboard Enter did not expand a chapter');
    await page.locator('.tl-item').first().focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(250);
    ok(await page.locator('#sheet[open]').count() === 1, 'keyboard Enter did not open an objective');
    await page.keyboard.press('Escape'); await page.waitForTimeout(200);
    ok(await page.locator('#sheet[open]').count() === 0, 'Escape did not close the sheet');
    const methodLinks = await (async () => { await page.click('button[data-view="method"]'); await page.waitForTimeout(150); return page.$$eval('#main a', as => as.map(a => a.href)); })();
    ok(methodLinks.length >= 3 && methodLinks.every(h => /^https?:/.test(h)), 'method view links missing or malformed');
    ok(errs.length === 0, 'script errors: ' + errs.join(' | '));
    await ctx.close();
    const dl = await open({ viewport: { width: 1280, height: 900 } });
    await dl.page.goto(BASE + '#c03-01'); await dl.page.reload(); await dl.page.waitForTimeout(900);
    ok(await dl.page.locator('#sheet[open]').count() === 1, 'deep link #c03-01 did not open the objective');
    await dl.ctx.close();
  }

  // ---- 3. phone: no sideways scroll anywhere, sheet fits
  {
    const { ctx, page, errs } = await open({ viewport: { width: 380, height: 780 }, deviceScaleFactor: 2 });
    for (const v of ['timeline', 'list', 'changes', 'method']) {
      await page.click(`button[data-view="${v}"]`); await page.waitForTimeout(200);
      const o = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      ok(o <= 1, `phone: page scrolls sideways in ${v} view by ${o}px`);
    }
    await page.click('button[data-view="list"]'); await page.waitForTimeout(200);
    for (const i of [0, 40, 100, 150]) {
      await page.locator('.row').nth(i).click(); await page.waitForTimeout(250);
      const o = await page.evaluate(() => { const d = document.getElementById('sheet'); return d.scrollWidth - d.clientWidth; });
      ok(o <= 1, `phone: sheet scrolls sideways at row ${i} by ${o}px`);
      await page.click('#sh-close'); await page.waitForTimeout(80);
    }
    ok(errs.length === 0, 'phone script errors: ' + errs.join(' | '));
    await ctx.close();
  }

  // ---- 4. hostile data cannot run script or create unsafe links
  {
    const evil = JSON.parse(JSON.stringify(snap));
    const it = evil.items[0];
    it.title = '<img src=x onerror="window.__xss=1"><script>window.__xss=2</script>';
    it.status_summary = '"><svg onload=window.__xss=3>';
    it.timeline = [{ date: '2025-02-01', event: '<b onmouseover=window.__xss=4>x</b>', url: 'javascript:window.__xss=5', source: 'evil', kind: 'primary' }];
    it.sources = [{ title: 'bad', url: 'data:text/html,<script>window.__xss=6</script>', publisher: 'x', date: '2025-01-01', kind: 'news' }];
    const { ctx, page, errs } = await open({ viewport: { width: 1280, height: 900 } }, async p => p.route('**/snapshot.json', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify(evil) })));
    await page.click('button[data-view="list"]'); await page.waitForTimeout(250);
    await page.locator('.row').first().click(); await page.waitForTimeout(300);
    const r = await page.evaluate(() => ({ xss: window.__xss, bad: [...document.querySelectorAll('a')].filter(a => /^(javascript|data):/i.test(a.getAttribute('href') || '')).length, imgs: document.querySelectorAll('#sh-body img, #sh-body script, #sh-body svg').length }));
    ok(r.xss === undefined, 'injected script ran: ' + r.xss);
    ok(r.bad === 0, 'javascript: or data: link rendered');
    ok(r.imgs === 0, 'injected markup rendered as elements');
    ok(errs.length === 0, 'hostile-data script errors: ' + errs.join(' | '));
    await ctx.close();
  }

  // ---- 5. data file missing: page still stands
  {
    const { ctx, page, errs } = await open({ viewport: { width: 1280, height: 900 } }, async p => p.route('**/snapshot.json', r => r.fulfill({ status: 404, body: 'nope' })));
    const t = await page.locator('#main').innerText();
    ok(/empty|appear|could not be loaded/i.test(t), 'no empty state when the data file is missing: ' + t.slice(0, 80));
    ok(errs.length === 0, 'missing-data script errors: ' + errs.join(' | '));
    await ctx.close();
  }

  // ---- 6. dark theme legibility of key tokens (contrast ratio of text on its background)
  {
    const { ctx, page } = await open({ viewport: { width: 1280, height: 900 }, colorScheme: 'dark' });
    const res = await page.evaluate(() => {
      function lum(c) { const m = c.match(/[\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]); }
      function bg(el) { while (el) { const c = getComputedStyle(el).backgroundColor; if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c; el = el.parentElement; } return 'rgb(255,255,255)'; }
      const out = [];
      for (const sel of ['.head h1', '.head p', '.hero-n', '.hero-t span', '.stat span', '.chip', '.tabs button', '.tl-ch .nm', '.count', '.betanote', '.tl-key']) {
        const el = document.querySelector(sel); if (!el) continue;
        const a = lum(getComputedStyle(el).color), b = lum(bg(el)); const r = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
        out.push([sel, Math.round(r * 10) / 10]);
      }
      return out;
    });
    for (const [sel, r] of res) ok(r >= 4.5, `dark theme contrast ${r}:1 for ${sel}`);
    console.log('dark contrast', JSON.stringify(res));
    await ctx.close();
  }
  {
    const { ctx, page } = await open({ viewport: { width: 1280, height: 900 }, colorScheme: 'light' });
    const res = await page.evaluate(() => {
      function lum(c) { const m = c.match(/[\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]); }
      function bg(el) { while (el) { const c = getComputedStyle(el).backgroundColor; if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c; el = el.parentElement; } return 'rgb(255,255,255)'; }
      const out = [];
      for (const sel of ['.head p', '.hero-t span', '.stat span', '.count', '.betanote', '.tl-key', '.eyebrow', '.tl-axis .yr']) {
        const el = document.querySelector(sel); if (!el) continue;
        const a = lum(getComputedStyle(el).color), b = lum(bg(el)); out.push([sel, Math.round(((Math.max(a, b) + .05) / (Math.min(a, b) + .05)) * 10) / 10]);
      }
      return out;
    });
    for (const [sel, r] of res) ok(r >= 4.5, `light theme contrast ${r}:1 for ${sel}`);
    console.log('light contrast', JSON.stringify(res));
    await ctx.close();
  }

  await browser.close();
  console.log('\nNOTES (' + notes.length + '):'); notes.slice(0, 40).forEach(x => console.log('  ' + x));
  console.log('\nFAILURES (' + fails.length + '):'); fails.forEach(x => console.log('  ' + x));
})().catch(e => { console.error('TEST CRASHED', e.message); process.exit(1); });

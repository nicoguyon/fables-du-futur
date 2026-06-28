// Génère les visuels réseaux sociaux en capturant scripts/social_cards.html avec Chromium.
// Usage: NODE_PATH=$(npm root -g) node scripts/gen_social.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const SRC = 'file://' + path.join(ROOT, 'scripts', 'social_cards.html');
const OUT = path.join(ROOT, 'social');

const CARDS = ['vertical', 'carousel-1', 'carousel-2', 'carousel-3', 'carousel-4', 'wide'];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--no-sandbox', '--force-color-profile=srgb'],
  });
  const page = await browser.newPage({ viewport: { width: 2000, height: 2000 }, deviceScaleFactor: 1 });
  await page.goto(SRC, { waitUntil: 'load' });
  // attendre les polices Google (avec garde-fou si offline)
  try { await page.waitForFunction(() => document.fonts.ready.then(() => true), null, { timeout: 8000 }); } catch (e) { console.log('fonts: fallback serif'); }
  await page.waitForTimeout(600);

  for (const id of CARDS) {
    const el = await page.$('#' + id);
    if (!el) { console.log('❌ introuvable: ' + id); continue; }
    const file = path.join(OUT, `all-in-278-${id}.png`);
    await el.screenshot({ path: file });
    const kb = Math.round(fs.statSync(file).size / 1024);
    console.log(`✅ ${path.basename(file)} (${kb} Ko)`);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });

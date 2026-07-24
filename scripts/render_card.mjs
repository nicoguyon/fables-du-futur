// Rend la carte de situation (social/card-template.html + data/capferret-live.json)
// en PNG 1200x675. Usage : node scripts/render_card.mjs [sortie.png]
// Dépend de playwright-core (npm i --no-save playwright-core) et du Chromium
// préinstallé (/opt/pw-browsers/chromium).
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import path from 'path';
import http from 'http';
import fs from 'fs';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = process.argv[2] || '/tmp/capferret-card.png';

// playwright-core : cherché près du repo, sinon dans NODE_PATH
let chromium;
for (const base of [repoRoot, process.cwd(), process.env.PW_MODULES || '']) {
  try {
    const require = createRequire(path.join(base || '.', 'x.js'));
    ({ chromium } = require('playwright-core'));
    break;
  } catch { /* essai suivant */ }
}
if (!chromium) {
  console.error('playwright-core introuvable — lancer : npm i --no-save playwright-core');
  process.exit(1);
}

// petit serveur statique pour que le fetch() du template fonctionne
const server = http.createServer((req, res) => {
  const p = path.join(repoRoot, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200); res.end(data);
  });
});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1200, height: 675 }, deviceScaleFactor: 2 });
await page.goto(`http://127.0.0.1:${port}/social/card-template.html`);
await page.waitForFunction(() => document.title === 'ready', { timeout: 15000 });
await page.waitForTimeout(400);
await page.screenshot({ path: out });
await browser.close();
server.close();
console.log('carte générée :', out);

// make-frontend-gif.mjs
// Capture the Solar Flow hero page (solar-flow-elementor.html) in a headless
// Edge/Chrome and save one PNG per animation timestamp.
//
// Determinism: after load, every frame pauses ALL CSS animations (Web
// Animations API, includes ::before/::after) and scrubs them to an exact
// currentTime before screenshotting - so frames are reproducible.
//
// Env overrides: GIF_FPS (default 20), CAPTURE_S (default 6.2 s:
// ~2.2 s entrance + ambient), VIEW_W (default 1280), BROWSER_EXE.
// No npm dependencies: uses Node's built-in fetch + WebSocket (CDP).
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const HTML = path.join(ROOT, 'solar-flow-elementor.html');
const OUT = path.join(ROOT, 'frontend-frames');
const FPS = Number(process.env.GIF_FPS || 20);
const T_TOTAL = Number(process.env.CAPTURE_S || 6.2);
const VIEW_W = Number(process.env.VIEW_W || 1280);

const EXE = [
  process.env.BROWSER_EXE,
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
].filter(Boolean).find(p => fs.existsSync(p));
if (!EXE) { console.error('No Edge/Chrome found; set BROWSER_EXE.'); process.exit(1); }
console.log('browser:', EXE);

const PORT = 9223;
const PROFILE = path.join(ROOT, '.cdp-profile');
fs.rmSync(PROFILE, { recursive: true, force: true });

const proc = spawn(EXE, [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PROFILE}`,
  '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--hide-scrollbars', '--disable-background-networking',
  'about:blank',
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function findPage() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await r.json();
      const page = list.find(t => t.type === 'page');
      if (page) return page;
    } catch { /* browser not up yet */ }
    await sleep(250);
  }
  throw new Error('CDP endpoint never came up');
}

const page = await findPage();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws error')); });

let nextId = 1;
const pending = new Map();
const eventWaiters = [];
ws.onmessage = ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); return; }
  if (msg.method) {
    const idx = eventWaiters.findIndex(w => w.method === msg.method);
    if (idx >= 0) eventWaiters.splice(idx, 1)[0].res(msg);
  }
};
const send = (method, params = {}) => new Promise(res => {
  const id = nextId++;
  pending.set(id, res);
  ws.send(JSON.stringify({ id, method, params }));
});
const waitEvent = (method, timeout = 15000) => new Promise((res, rej) => {
  eventWaiters.push({ method, res });
  setTimeout(() => rej(new Error('timeout waiting ' + method)), timeout);
});

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride',
  { width: VIEW_W, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: pathToFileURL(HTML).href });
await waitEvent('Page.loadEventFired');
await sleep(300); // let first paint / fonts settle

await send('Runtime.evaluate', { expression: "document.body.style.margin='0'" });
const dims = await send('Runtime.evaluate', {
  expression: "JSON.stringify((r => ({x: r.x, y: r.y, w: r.width, h: r.height}))(document.querySelector('.solar-hero').getBoundingClientRect()))",
  returnByValue: true,
});
const { x, y, w, h } = JSON.parse(dims.result.result.value);
console.log('hero rect:', x, y, w, 'x', h);

const nAnim = await send('Runtime.evaluate',
  { expression: 'document.getAnimations().length', returnByValue: true });
console.log('animations found:', nAnim.result.result.value);
if (!nAnim.result.result.value) throw new Error('no animations found');

fs.mkdirSync(OUT, { recursive: true });
const nFrames = Math.round(T_TOTAL * FPS);
for (let k = 0; k < nFrames; k++) {
  const t = k / FPS;
  await send('Runtime.evaluate', {
    expression: `document.getAnimations().forEach(a => { a.pause(); a.currentTime = ${Math.round(t * 1000)}; });`,
  });
  const shot = await send('Page.captureScreenshot', {
    format: 'png',
    clip: { x, y, width: w, height: h, scale: 1 },
    captureBeyondViewport: true,
  });
  fs.writeFileSync(path.join(OUT, `f${String(k).padStart(4, '0')}.png`),
    Buffer.from(shot.result.data, 'base64'));
  if (k % 20 === 0) console.log(`captured ${k + 1}/${nFrames} (t=${t.toFixed(2)}s)`);
}

try { ws.close(); } catch { /* ignore */ }
try { execSync(`taskkill /PID ${proc.pid} /T /F`, { stdio: 'ignore' }); } catch { /* ignore */ }
await sleep(500);
try { fs.rmSync(PROFILE, { recursive: true, force: true, maxRetries: 3, retryDelay: 500 }); }
catch (e) { console.warn('profile cleanup skipped:', e.code); }
console.log('done:', OUT, '-', nFrames, 'frames');

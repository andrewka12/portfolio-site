// Behavioural check of the portfolio-site price calculator.
// Extracts the inline <script> from index.html, runs it against a minimal DOM stub,
// then simulates checkbox changes and asserts the rendered total / term / summary.

const fs = require('fs');
const path = require('path');

const SITE = String.raw`C:\Users\zyabk\Documents\deepseek-harness\default-workspace\freelance\projects\portfolio-site\index.html`;
const html = fs.readFileSync(SITE, 'utf8');

// ---- pull the option metadata straight out of the markup -------------------
const optRe = /<input type="checkbox"([^>]*?data-price="(\d+)"[^>]*?)>/g;
const opts = [];
let m;
while ((m = optRe.exec(html)) !== null) {
  const attrs = m[1];
  const price = Number(m[2]);
  const days = Number((attrs.match(/data-days="(\d+)"/) || [])[1] || 0);
  const label = (attrs.match(/data-label="([^"]*)"/) || [])[1] || '';
  const checked = /\bchecked\b/.test(attrs);
  opts.push({ price, days, label, checked });
}
if (opts.length === 0) { console.error('FAIL: no calculator options found in HTML'); process.exit(1); }

// ---- minimal DOM stub ------------------------------------------------------
function makeEl(id) {
  return {
    id, textContent: '', _classes: new Set(), dataset: {},
    classList: {
      add(c) { this._p._classes.add(c); },
      remove(c) { this._p._classes.delete(c); },
      contains(c) { return this._p._classes.has(c); },
    },
    _listeners: {},
    addEventListener(ev, fn) { (this._listeners[ev] = this._listeners[ev] || []).push(fn); },
    fire(ev) { (this._listeners[ev] || []).forEach((f) => f()); },
  };
}

const boxes = opts.map((o, i) => {
  const wrap = makeEl('wrap' + i);
  const box = makeEl('box' + i);
  wrap._classes = new Set();
  wrap.classList._p = wrap;
  box.classList._p = box;
  box.dataset = { price: String(o.price), days: String(o.days), label: o.label };
  box.checked = o.checked;
  box.closest = (sel) => (sel === '.opt' ? wrap : null);
  box._wrap = wrap;
  return box;
});

const byId = {};
['total', 'term', 'summary', 'year'].forEach((id) => { byId[id] = makeEl(id); byId[id].classList._p = byId[id]; });

const document = {
  querySelectorAll: (sel) => (/checkbox/.test(sel) ? boxes : []),
  getElementById: (id) => byId[id] || null,
};

// ---- run the site's own script --------------------------------------------
const scriptBody = (html.match(/<script>([\s\S]*?)<\/script>/) || [])[1];
if (!scriptBody) { console.error('FAIL: no inline script found'); process.exit(1); }

new Function('document', 'Date', scriptBody)(document, Date);

// ---- assertions ------------------------------------------------------------
let failures = 0;
function check(name, actual, expected) {
  const ok = actual === expected;
  if (!ok) failures++;
  console.log(`  [${ok ? 'OK  ' : 'FAIL'}] ${name}`);
  console.log(`         получилось: ${JSON.stringify(actual)}`);
  if (!ok) console.log(`         ожидалось:  ${JSON.stringify(expected)}`);
}

function setAll(value) {
  boxes.forEach((b) => { b.checked = value; b.fire('change'); });
}

console.log(`вариантов в калькуляторе: ${opts.length}\n`);

console.log('Сценарий 1: состояние по умолчанию (отмечен только первый пункт)');
check('итог', byId.total.textContent, '6 000 ₽');
check('срок', byId.term.textContent, 'Срок: 2 рабочих дня');

console.log('\nСценарий 2: снять всё');
setAll(false);
check('итог', byId.total.textContent, '0 ₽');
check('срок', byId.term.textContent, 'Выберите хотя бы одну задачу');

console.log('\nСценарий 3: отметить все пункты');
setAll(true);
const sum = opts.reduce((a, o) => a + o.price, 0);
const maxDays = Math.max(...opts.map((o) => o.days));
check('итог', byId.total.textContent, String(sum).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽');
check('срок', byId.term.textContent, `Срок: ${maxDays} рабочих дней`);

console.log('\nСценарий 4: только AI-бот (40 000 ₽, 7 дней)');
setAll(false);
const ai = boxes[2];
ai.checked = true; ai.fire('change');
check('итог', byId.total.textContent, '40 000 ₽');
check('срок', byId.term.textContent, 'Срок: 7 рабочих дней');
check('подсветка выбранного', ai._wrap.classList.contains('on'), true);

console.log('\nСценарий 5: форматирование разрядов');
setAll(false);
boxes[0].checked = true; boxes[3].checked = true; boxes[1].checked = true; boxes[4].checked = true;
boxes[0].fire('change');
const expected5 = opts[0].price + opts[3].price + opts[1].price + opts[4].price;
check('итог', byId.total.textContent, String(expected5).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽');

console.log(`\nгод в подвале: ${byId.year.textContent}`);

console.log('');
if (failures) { console.log(`ПРОВАЛ: ${failures} проверок не прошло`); process.exit(1); }
console.log('ВСЕ ПРОВЕРКИ КАЛЬКУЛЯТОРА ПРОШЛИ');

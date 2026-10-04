// Проверка витрины перед публикацией.
//
// Запуск:  node tools/prepublish-check.js
//
// Проверяет, что ты не выложил сайт с заглушками, что все картинки кейсов на месте
// и что обязательные блоки страницы никуда не делись.

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const INDEX = path.join(ROOT, 'index.html');
const html = fs.readFileSync(INDEX, 'utf8');

let failures = 0;
let warnings = 0;

function ok(msg) { console.log(`  [OK]    ${msg}`); }
function fail(msg) { failures++; console.log(`  [ОШИБКА] ${msg}`); }
function warn(msg) { warnings++; console.log(`  [ВНИМАНИЕ] ${msg}`); }

function lineOf(needle) {
  const idx = html.indexOf(needle);
  return idx === -1 ? '?' : html.slice(0, idx).split('\n').length;
}

console.log('\n1. Заглушки, которые нужно заменить своими данными');
const placeholders = ['ВАШ_НИК', 'ВАШ_ЛОГИН', 'Ваше Имя'];
let leftover = 0;
for (const p of placeholders) {
  const count = html.split(p).length - 1;
  if (count === 0) {
    ok(`«${p}» — заменено`);
  } else {
    leftover += count;
    fail(`«${p}» встречается ${count} раз (первое вхождение — строка ${lineOf(p)})`);
  }
}

console.log('\n2. Контактные ссылки');
const tg = [...html.matchAll(/href="(https:\/\/t\.me\/[^"]*)"/g)].map((m) => m[1]);
if (tg.length === 0) {
  fail('не найдено ни одной ссылки на Telegram');
} else {
  const unique = [...new Set(tg)];
  ok(`ссылок на Telegram: ${tg.length}, уникальных: ${unique.length}`);
  for (const u of unique) {
    if (/ВАШ_НИК/.test(u)) fail(`ссылка ведёт на заглушку: ${u}`);
    else ok(`контакт: ${u}`);
  }
}

console.log('\n3. Картинки кейсов');
const imgs = [...html.matchAll(/<img[^>]+src="([^"]+)"/g)].map((m) => m[1]);
if (imgs.length === 0) {
  warn('на странице нет ни одной картинки');
}
for (const src of imgs) {
  if (/^https?:/.test(src)) { ok(`внешняя картинка: ${src}`); continue; }
  const p = path.join(ROOT, src);
  if (fs.existsSync(p)) {
    const kb = Math.round(fs.statSync(p).size / 1024);
    ok(`${src} — на месте (${kb} КБ)`);
  } else {
    fail(`${src} — файл не найден, на сайте будет пустое место`);
  }
}

console.log('\n4. Обязательные блоки страницы');
const required = ['services', 'cases', 'calc', 'process', 'faq', 'contact'];
for (const id of required) {
  if (html.includes(`id="${id}"`)) ok(`блок #${id}`);
  else fail(`пропал блок #${id} — на него ведёт меню в шапке`);
}

console.log('\n5. Технические требования');
if (html.includes('@media')) ok('есть адаптив под телефон (@media)');
else fail('нет ни одного @media — на телефоне будет неудобно');

if (/cdn\.|unpkg\.com|jsdelivr|googleapis/.test(html)) {
  warn('подключены внешние ресурсы — страница перестанет работать без интернета');
} else {
  ok('нет внешних зависимостей, работает без интернета');
}

if (html.includes('<meta name="viewport"')) ok('есть meta viewport');
else fail('нет meta viewport — на телефоне сайт откроется в desktop-масштабе');

const hasTitle = /<title>([^<]*)<\/title>/.exec(html);
if (hasTitle && hasTitle[1].trim().length > 10) ok(`title: «${hasTitle[1].trim().slice(0, 60)}»`);
else fail('нет осмысленного тега <title> — плохо для поиска');

const desc = /<meta name="description" content="([^"]*)"/.exec(html);
if (desc && desc[1].trim().length > 40) ok('есть meta description');
else warn('нет meta description — снижает привлекательность ссылки в поиске');

console.log('');
if (leftover > 0) {
  console.log(`ИТОГ: осталось заглушек — ${leftover}. Найди их по слову ЗАМЕНИТЕ и замени.`);
}
console.log(`Проверок не пройдено: ${failures}, предупреждений: ${warnings}`);
if (failures > 0) {
  console.log('ПУБЛИКОВАТЬ РАНО.\n');
  process.exit(1);
}
console.log('ВСЁ ГОТОВО К ПУБЛИКАЦИИ.\n');

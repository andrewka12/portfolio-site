"""Generate placeholder case previews for the portfolio landing page."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\zyabk\Documents\deepseek-harness\default-workspace\freelance\projects\portfolio-site\assets"
W, H = 1200, 750

REG = r"C:\Windows\Fonts\segoeui.ttf"
BOLD = r"C:\Windows\Fonts\segoeuib.ttf"


def font(size, bold=False):
    path = BOLD if bold else REG
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def vgrad(top, bottom, size):
    img = Image.new("RGB", (1, size[1]))
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        d.point((0, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize(size)


def window_chrome(d, w, h, title):
    d.rounded_rectangle([40, 40, w - 40, h - 40], radius=18, fill=(20, 27, 36), outline=(38, 50, 66), width=2)
    d.rounded_rectangle([40, 40, w - 40, 92], radius=18, fill=(26, 34, 45))
    d.rectangle([40, 74, w - 40, 92], fill=(26, 34, 45))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([66 + i * 26, 57, 82 + i * 26, 73], fill=c)
    d.text((w / 2, 66), title, font=font(20, True), fill=(150, 165, 185), anchor="mm")


def card(d, box, label, value, color):
    d.rounded_rectangle(box, radius=12, fill=(24, 32, 43), outline=(38, 50, 66), width=1)
    x0, y0, x1, y1 = box
    d.text((x0 + 18, y0 + 14), label, font=font(17), fill=(140, 156, 176))
    d.text((x0 + 18, y0 + 42), value, font=font(32, True), fill=color)


def line_chart(d, box, series, colors):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=12, fill=(24, 32, 43), outline=(38, 50, 66), width=1)
    d.text((x0 + 18, y0 + 14), "Динамика цен за 30 дней", font=font(19, True), fill=(214, 224, 236))
    gx0, gy0, gx1, gy1 = x0 + 26, y0 + 58, x1 - 26, y1 - 30
    for i in range(5):
        y = gy0 + (gy1 - gy0) * i / 4
        d.line([gx0, y, gx1, y], fill=(38, 50, 66), width=1)
    allv = [v for s in series for v in s]
    lo, hi = min(allv), max(allv)
    span = max(1, hi - lo)

    def pt(i, v, n):
        x = gx0 + (gx1 - gx0) * i / max(1, n - 1)
        y = gy1 - (gy1 - gy0) * (v - lo) / span
        return x, y

    for idx, s in enumerate(series):
        pts = [pt(i, v, len(s)) for i, v in enumerate(s)]
        d.line(pts, fill=colors[idx], width=3, joint="curve")
        d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5], fill=colors[idx])
    lx = gx0
    for idx, name in enumerate(["Ваш товар", "Конкурент А", "Конкурент Б"]):
        d.line([lx, y1 - 14, lx + 22, y1 - 14], fill=colors[idx], width=4)
        d.text((lx + 30, y1 - 22), name, font=font(15), fill=(150, 165, 185))
        lx += 175


def table_rows(d, box, rows):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=12, fill=(24, 32, 43), outline=(38, 50, 66), width=1)
    d.text((x0 + 18, y0 + 14), "Товары и тревоги", font=font(19, True), fill=(214, 224, 236))
    y = y0 + 56
    for name, price, delta, flag, col in rows:
        badge_w = 104
        bx0 = x1 - 18 - badge_w
        d.text((x0 + 18, y), name, font=font(17, True), fill=(214, 224, 236))
        d.rounded_rectangle([bx0, y - 2, x1 - 18, y + 24], radius=13,
                            fill=(col[0] // 5, col[1] // 5, col[2] // 5))
        d.text(((bx0 + x1 - 18) / 2, y + 11), flag, font=font(14, True), fill=col, anchor="mm")
        d.text((x0 + 18, y + 30), price, font=font(16), fill=(150, 165, 185))
        d.text((x0 + 150, y + 30), delta, font=font(16, True), fill=col)
        y += 56
        d.line([x0 + 18, y - 12, x1 - 18, y - 12], fill=(32, 42, 56), width=1)


def make_mp_monitor():
    img = vgrad((14, 19, 26), (10, 14, 19), (W, H))
    d = ImageDraw.Draw(img)
    window_chrome(d, W, H, "MP Monitor — дашборд селлера Wildberries")
    card(d, (70, 116, 320, 210), "Средняя цена", "1 842 ₽", (232, 237, 244))
    card(d, (340, 116, 590, 210), "Позиция", "#7", (79, 140, 255))
    card(d, (610, 116, 860, 210), "Рейтинг", "4.3", (255, 176, 32))
    card(d, (880, 116, 1130, 210), "Тревоги", "3", (255, 99, 99))

    import math
    s1 = [1900 - i * 9 + int(40 * math.sin(i / 3.1)) for i in range(30)]
    s2 = [1810 - i * 5 + int(30 * math.sin(i / 2.4 + 1)) for i in range(30)]
    s3 = [1980 - i * 12 + int(25 * math.sin(i / 3.7 + 2)) for i in range(30)]
    line_chart(d, (70, 230, 700, 500), [s1, s2, s3], [(79, 140, 255), (38, 208, 160), (255, 176, 32)])
    table_rows(d, (720, 230, 1130, 500), [
        ("Кроссовки Urban", "2 190 ₽", "+4.1%", "норма", (38, 208, 160)),
        ("Худи Oversize", "1 640 ₽", "-7.3%", "демпинг", (255, 99, 99)),
        ("Рюкзак City", "3 050 ₽", "-1.2%", "остаток", (255, 176, 32)),
    ])
    d.rounded_rectangle([70, 520, 1130, 690], radius=12, fill=(24, 32, 43), outline=(38, 50, 66), width=1)
    d.text((94, 540), "Отчёт в Telegram · 09:00", font=font(19, True), fill=(214, 224, 236))
    lines = [
        "Худи Oversize — конкурент снизил цену на 7.3%, вы на 2 месте из 6",
        "Кроссовки Urban — 4 новых отзыва, средняя оценка выросла до 4.8",
        "Рюкзак City — остаток 6 шт, при текущем темпе хватит на 3 дня",
    ]
    for i, t in enumerate(lines):
        d.text((94, 578 + i * 34), "•  " + t, font=font(17), fill=(150, 165, 185))
    img.save(os.path.join(OUT, "mp-monitor.png"), "PNG")


def bubble(d, box, text, mine, fnt):
    x0, y0, x1, y1 = box
    fill = (35, 78, 140) if mine else (32, 42, 56)
    d.rounded_rectangle(box, radius=14, fill=fill)
    d.text((x0 + 18, y0 + 14), text, font=fnt, fill=(232, 237, 244))


def make_ai_bot():
    img = vgrad((14, 19, 26), (10, 14, 19), (W, H))
    d = ImageDraw.Draw(img)
    window_chrome(d, W, H, "AI Support Bot — автосервис «Гараж 24»")
    f = font(18)
    fb = font(18, True)
    bubble(d, (80, 120, 620, 200), "Здравствуйте! Сколько стоит замена масла\nна Toyota Camry и сколько это займёт?", False, f)
    bubble(d, (300, 215, 1120, 340),
           "Замена масла и масляного фильтра на Toyota Camry — 2 400 ₽\nвместе с работой. Занимает около 40 минут.\n\nМожно приехать сегодня: есть свободное время в 15:30 и 17:00.", True, f)
    bubble(d, (80, 355, 700, 435), "А если масло своё? И есть ли гарантия?", False, f)
    bubble(d, (300, 450, 1120, 545),
           "Со своим маслом работа — 1 200 ₽. Гарантия на работу 6 месяцев,\nна ваши запчасти гарантия не распространяется.", True, f)
    bubble(d, (80, 552, 700, 624), "Хочу пожаловаться на качество прошлого ремонта", False, f)
    d.rounded_rectangle([300, 640, 1120, 698], radius=14, fill=(60, 46, 20), outline=(255, 176, 32), width=1)
    d.text((322, 655), "Передаю оператору — он ответит в течение 10 минут. Тикет #142 создан.",
           font=fb, fill=(255, 200, 90))
    img.save(os.path.join(OUT, "ai-support-bot.png"), "PNG")


def make_landing():
    img = vgrad((13, 17, 23), (10, 14, 19), (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=(16, 21, 28))
    d.line([0, 64, W, 64], fill=(36, 48, 64), width=2)
    d.text((60, 32), "автоматизация.WB", font=font(21, True), fill=(232, 237, 244), anchor="lm")
    d.rounded_rectangle([880, 16, 1140, 50], radius=10, fill=(79, 140, 255))
    d.text((1010, 33), "Написать в Telegram", font=font(17, True), fill=(255, 255, 255), anchor="mm")

    d.text((60, 110), "Telegram-боты и автоматизация", font=font(40, True), fill=(232, 237, 244))
    d.text((60, 162), "для селлеров Wildberries и Ozon", font=font(40, True), fill=(79, 140, 255))
    d.text((60, 226), "Убираю ручную рутину. Отчёт, который вы собираете три часа,", font=font(19), fill=(147, 161, 181))
    d.text((60, 254), "формируется за 20 секунд и приходит в Telegram.", font=font(19), fill=(147, 161, 181))

    d.rounded_rectangle([60, 310, 340, 362], radius=11, fill=(79, 140, 255))
    d.text((200, 336), "Обсудить задачу", font=font(19, True), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle([356, 310, 600, 362], radius=11, outline=(36, 48, 64), width=2)
    d.text((478, 336), "Посмотреть кейсы", font=font(19, True), fill=(232, 237, 244), anchor="mm")

    labels = [("3", "рабочих инструмента"), ("20 сек", "вместо 3 часов"), ("2–5 дней", "до результата")]
    for i, (v, l) in enumerate(labels):
        x = 60 + i * 370
        d.text((x, 480), v, font=font(34, True), fill=(38, 208, 160))
        d.text((x, 522), l, font=font(17), fill=(147, 161, 181))
    d.line([60, 440, 1140, 440], fill=(36, 48, 64), width=2)

    for i in range(3):
        x = 60 + i * 370
        d.rounded_rectangle([x, 580, x + 340, 720], radius=12, fill=(22, 29, 40), outline=(36, 48, 64), width=1)
        d.text((x + 20, 604), ["MP Monitor", "AI Support Bot", "Страница услуги"][i], font=font(20, True), fill=(232, 237, 244))
        d.text((x + 20, 642), ["Мониторинг WB, отчёты,", "Ответы по базе знаний", "Чистые HTML, CSS, JS"][i], font=font(16), fill=(147, 161, 181))
        d.text((x + 20, 668), ["тревоги в Telegram", "и передача оператору", "без сборки и зависимостей"][i], font=font(16), fill=(147, 161, 181))
    img.save(os.path.join(OUT, "landing.png"), "PNG")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    make_mp_monitor()
    make_ai_bot()
    make_landing()
    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        print(f"{f}: {os.path.getsize(p)} bytes")

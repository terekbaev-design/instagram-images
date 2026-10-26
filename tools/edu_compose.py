#!/usr/bin/env python3
"""Carrousel éducatif STEPDREAM — design « actu Dubaï » (validé le 26/10/2026).

Photo de Dubaï sombre (coucher de soleil / nuit), titres condensés jaune et blanc,
gros numéros dorés « 01 », compteur « 01 / 08 », flèches jaunes, texte posé en code.
Slide 1 : rond avec la photo de Беслан + nom. Dernière slide : abonnement (texte fixe).

Usage : python3 edu_compose.py spec.json fonts_dir photos_dir out_dir beslan-circle.jpg
  fonts_dir : 'Oswald[wght].ttf' et 'Roboto[wdth,wght].ttf' (google/fonts)
  photos_dir : p1.png, p2.png, … (numéro = champ "photo" de chaque slide)
Types de slide : cover, point, checklist, subscribe (voir tools/spec-edu-exemple.json).
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
YEL = (245, 196, 0)
GOLD_TOP, GOLD_BOT = (250, 214, 90), (176, 128, 20)
WHITE = (255, 255, 255)

spec_p, fdir, pdir, odir, circle_p = sys.argv[1:6]
spec = json.load(open(spec_p, encoding="utf-8"))
slides = spec["slides"]

# Contrôles bloquants (règles de l'utilisateur du 07/10/2026)
if not os.path.isfile(circle_p):
    sys.exit("ERREUR : photo du rond (beslan-circle.jpg) introuvable")
if slides[0]["kind"] != "cover":
    sys.exit("ERREUR : la slide 1 doit être 'cover' (avec le rond photo)")
if slides[-1]["kind"] != "subscribe":
    sys.exit("ERREUR : la dernière slide doit être 'subscribe'")

os.makedirs(odir, exist_ok=True)
OSW = os.path.join(fdir, "Oswald[wght].ttf")
ROB = os.path.join(fdir, "Roboto[wdth,wght].ttf")


def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght] if "Oswald" in path else [100, wght])
    except Exception:
        pass
    return f


def cover_photo(p):
    im = Image.open(p).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r + .5), int(im.height * r + .5)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def shade(im, top=0.3, bottom=0.97, start=0.3):
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        if t < start:
            a = top * (1 - t / start) * 0.8
        else:
            a = top * 0.2 + (bottom - top * 0.2) * ((t - start) / (1 - start)) ** 0.7
        ov.putpixel((0, y), int(255 * min(a, 1)))
    ov = ov.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, ov)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    # typographie russe : pas de tiret en début de ligne
    for i in range(1, len(lines)):
        if lines[i].startswith("—"):
            lines[i - 1] += " —"; lines[i] = lines[i][1:].strip()
    # ni de petit mot seul en fin de ligne
    for i in range(len(lines) - 1):
        last = lines[i].split()[-1]
        if len(last) <= 2 and last != "—" and len(lines[i].split()) > 1:
            lines[i] = " ".join(lines[i].split()[:-1]); lines[i + 1] = last + " " + lines[i + 1]
    return lines


def center(d, y, text, f, fill, maxw=940, lh=1.12):
    for ln in wrap(d, text, f, maxw):
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def overlay_box(im, box, radius, alpha, outline=None):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(box, radius=radius, fill=(0, 0, 0, alpha), outline=outline, width=3)
    im.alpha_composite(lay)


def counter(im, n, total):
    d = ImageDraw.Draw(im)
    f = font(ROB, 30, 600)
    s1, s2 = f"{n:02d}", f" / {total:02d}"
    w = d.textlength(s1 + s2, font=f)
    x0, y0 = W - 70 - w - 36, 52
    overlay_box(im, (x0, y0, x0 + w + 36, y0 + 56), 28, 150, outline=(110, 110, 110, 255))
    d = ImageDraw.Draw(im)
    d.text((x0 + 18, y0 + 10), s1, font=f, fill=YEL)
    d.text((x0 + 18 + d.textlength(s1, font=f), y0 + 10), s2, font=f, fill=WHITE)


def chevrons(im, x=880, y=170):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(3):
        ox = x + k * 30
        pts = [(ox, y), (ox + 36, y + 40), (ox, y + 80), (ox + 16, y + 80), (ox + 52, y + 40), (ox + 16, y)]
        d.polygon(pts, fill=YEL + (90 + k * 80,))
    im.alpha_composite(lay)


def gold_number(im, text, x, y, size):
    f = font(OSW, size, 700)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).text((x, y), text, font=f, fill=255)
    grad = Image.new("RGBA", im.size)
    gd = ImageDraw.Draw(grad)
    bb = mask.getbbox() or (0, y, W, y + size)
    for yy in range(bb[1], bb[3] + 1):
        t = (yy - bb[1]) / max(1, bb[3] - bb[1])
        c = tuple(int(GOLD_TOP[i] + (GOLD_BOT[i] - GOLD_TOP[i]) * t) for i in range(3))
        gd.line([(0, yy), (W, yy)], fill=c + (255,))
    im.paste(grad, (0, 0), mask)


def footer(d, text):
    f = font(ROB, 24, 400)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, H - 70), text, font=f, fill=(160, 160, 160))


def circle(im, x, y, size, name):
    c = Image.open(circle_p).convert("RGB")
    s = min(c.size)
    c = c.crop(((c.width - s) // 2, (c.height - s) // 2, (c.width + s) // 2, (c.height + s) // 2)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255)
    d = ImageDraw.Draw(im)
    d.ellipse((x - 10, y - 10, x + size + 10, y + size + 10), fill=YEL)
    d.ellipse((x - 4, y - 4, x + size + 4, y + size + 4), fill=(10, 10, 10))
    im.paste(c, (x, y), m)
    f = font(OSW, 34, 500)
    w = d.textlength(name, font=f)
    d.text((x + size / 2 - w / 2, y + size + 22), name, font=f, fill=WHITE)


TOTAL = len(slides)
for s in slides:
    n = s["n"]
    im = shade(cover_photo(os.path.join(pdir, f"p{s['photo']}.png")), **s.get("shade", {})).convert("RGBA")
    if s["kind"] in ("point", "checklist"):
        chevrons(im)
    counter(im, n, TOTAL)
    d = ImageDraw.Draw(im)

    if s["kind"] == "cover":
        circle(im, 70, 60, 210, "Беслан Терекбаев")
        y = s.get("y", 760)
        y = center(d, y, s["title1"], font(OSW, 100, 700), YEL)
        y = center(d, y + 4, s["title2"], font(OSW, 72, 700), WHITE)
        if s.get("title3"):
            y = center(d, y + 4, s["title3"], font(OSW, 72, 700), YEL)
        y = center(d, y + 22, s["sub"], font(ROB, 36, 500), (235, 235, 235), maxw=900, lh=1.3)
        f = font(OSW, 34, 600)
        t = "ЛИСТАЙ  ›››"
        w = d.textlength(t, font=f)
        d.rounded_rectangle(((W - w) / 2 - 36, y + 26, (W + w) / 2 + 36, y + 96), radius=35, fill=YEL)
        d.text(((W - w) / 2, y + 36), t, font=f, fill=(15, 15, 15))

    elif s["kind"] == "point":
        gold_number(im, s["num"], 60, 20, 260)
        d = ImageDraw.Draw(im)
        y = s.get("y", 790)
        y = center(d, y, s["title"], font(OSW, 76, 700), YEL)
        y = center(d, y + 22, s["text"], font(ROB, 37, 500), WHITE, maxw=920, lh=1.32)
        if s.get("phrase"):
            f = font(ROB, 36, 700)
            lines = wrap(d, "«" + s["phrase"] + "»", f, 860)
            bh = len(lines) * 48 + 46
            overlay_box(im, (70, y + 26, W - 70, y + 26 + bh), 22, 140, outline=YEL + (255,))
            d = ImageDraw.Draw(im)
            yy = y + 48
            for ln in lines:
                w = d.textlength(ln, font=f)
                d.text(((W - w) / 2, yy), ln, font=f, fill=YEL)
                yy += 48
        footer(d, s.get("foot", "Практика брокера · @terekbaev"))

    elif s["kind"] == "checklist":
        y = s.get("y", 280)
        y = center(d, y, s["title"], font(OSW, 84, 700), YEL)
        f = font(ROB, 38, 500)
        y += 40
        hh = sum(len(wrap(d, it, f, 800)) * 50 + 28 for it in s["items"])
        overlay_box(im, (80, y - 24, W - 80, y + hh), 26, 165)
        d = ImageDraw.Draw(im)
        for item in s["items"]:
            d.ellipse((110, y + 6, 150, y + 46), fill=YEL)
            d.line([(120, y + 26), (128, y + 35), (142, y + 16)], fill=(15, 15, 15), width=5)
            yy = y
            for ln in wrap(d, item, f, 800):
                d.text((178, yy), ln, font=f, fill=WHITE)
                yy += 50
            y = yy + 28
        f2 = font(OSW, 46, 600)
        t = s.get("cta", "НАПИШИТЕ «БРОКЕР» В DIRECT")
        w = d.textlength(t, font=f2)
        d.rounded_rectangle(((W - w) / 2 - 40, y + 30, (W + w) / 2 + 40, y + 116), radius=18, fill=YEL)
        d.text(((W - w) / 2, y + 42), t, font=f2, fill=(15, 15, 15))

    elif s["kind"] == "subscribe":
        y = 150
        y = center(d, y, "ОБУЧЕНИЕ ДЛЯ БРОКЕРОВ", font(OSW, 84, 700), YEL)
        y = center(d, y, "КАЖДЫЙ ВЕЧЕР", font(OSW, 84, 700), WHITE)
        circle(im, (W - 300) // 2, y + 70, 300, "Беслан Терекбаев")
        d = ImageDraw.Draw(im)
        y = y + 70 + 300 + 90
        y = center(d, y, "Практика брокера в Дубае без воды: фразы, чек-листы, разбор ошибок", font(ROB, 36, 500), (235, 235, 235), maxw=880, lh=1.3)
        f = font(OSW, 46, 600)
        t = "ПОДПИСАТЬСЯ  +"
        w = d.textlength(t, font=f)
        d.rounded_rectangle(((W - w) / 2 - 50, y + 40, (W + w) / 2 + 50, y + 130), radius=45, fill=YEL)
        d.text(((W - w) / 2, y + 52), t, font=f, fill=(15, 15, 15))
        footer(d, "@terekbaev")

    im.convert("RGB").save(os.path.join(odir, f"slide-{n:02d}.jpg"), quality=92)
    print("ok", n)

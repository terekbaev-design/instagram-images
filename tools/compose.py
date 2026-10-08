#!/usr/bin/env python3
"""Compose StepDream morning carousel slides (1080x1350 JPEG).

Usage: python3 compose.py SPEC.json FONTS_DIR LOGO_REF PHOTOS_DIR OUT_DIR [PORTRAIT]
Photos: PHOTOS_DIR/pN.png (N = slide number). Text is rendered from real fonts,
so the Russian text is always exact.

PORTRAIT = refs/beslan-circle.jpg (photo de Беслан avec le logo STEP DREAM).
Règle de l'utilisateur (07/10/2026) : la slide 1 porte TOUJOURS le rond avec
cette photo et le nom « Беслан Терекбаев » dessous, et la dernière slide est
TOUJOURS la slide d'abonnement ("kind": "subscribe").
"""
import json, os, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1350
BG_TOP, BG_BOT = (247, 244, 253), (236, 231, 250)
INK = (17, 17, 20)
PURPLE = (59, 31, 168)
PURPLE_2 = (88, 54, 214)
GREY = (104, 100, 122)
MARGIN = 72

spec_path, fonts_dir, logo_ref, photos_dir, out_dir = sys.argv[1:6]
portrait_path = sys.argv[6] if len(sys.argv) > 6 else os.path.join(os.path.dirname(os.path.abspath(logo_ref)), "beslan-circle.jpg")
os.makedirs(out_dir, exist_ok=True)

# Rond photo de la slide 1 (fixe, validé le 07/10/2026)
CIRCLE_X, CIRCLE_Y, CIRCLE_D = 640, 196, 380
PORTRAIT_NAME = "Беслан Терекбаев"


def vfont(name, size, **axes):
    f = ImageFont.truetype(os.path.join(fonts_dir, name), size)
    try:
        cur = f.get_variation_axes()
        vals = []
        for a in cur:
            key = a.get("name", b"")
            key = key.decode() if isinstance(key, bytes) else key
            k = {"Weight": "wght", "Width": "wdth"}.get(key, key)
            vals.append(axes.get(k, a.get("default", a["minimum"])))
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def title_font(size):
    return vfont("Oswald[wght].ttf", size, wght=700)


def body_font(size, weight=400):
    return vfont("Roboto[wdth,wght].ttf", size, wght=weight, wdth=100)


def background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    # faint dot grid top-right, like the references
    for gx in range(0, 7):
        for gy in range(0, 5):
            x, y = W - 60 - gx * 22, 70 + gy * 22
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(200, 190, 232))
    return bg.convert("RGBA")


def grade(photo):
    """Purple-blue grading so every photo matches the brand."""
    photo = photo.convert("RGB")
    tint = Image.new("RGB", photo.size, (92, 64, 210))
    graded = Image.blend(photo, ImageChops.multiply(photo, Image.new("RGB", photo.size, (225, 215, 255))), 0.55)
    graded = Image.blend(graded, tint, 0.10)
    return graded


def cover_fit(img, w, h, fx=0.5, fy=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    x = int((img.width - w) * fx)
    y = int((img.height - h) * fy)
    return img.crop((x, y, x + w, y + h))


def place_photo(canvas, slide):
    p = os.path.join(photos_dir, f"p{slide['n']}.png")
    photo = grade(Image.open(p))
    lay = slide.get("layout", "right")
    if lay == "right":
        x0 = slide.get("photo_x", 430)
        w, h = W - x0, H
        ph = cover_fit(photo, w, h, slide.get("fx", 0.5), slide.get("fy", 0.5))
        mask = Image.new("L", (w, h))
        md = ImageDraw.Draw(mask)
        fade = int(w * 0.42)
        for x in range(w):
            a = 255 if x >= fade else int(255 * (x / fade) ** 1.6)
            md.line([(x, 0), (x, h)], fill=a)
        top = Image.new("L", (w, h), 255)
        td = ImageDraw.Draw(top)
        for y in range(0, 260):
            td.line([(0, y), (w, y)], fill=int(255 * (y / 260) ** 1.4))
        mask = ImageChops.multiply(mask, top)
        canvas.paste(ph, (x0, 0), mask)
    else:  # bottom
        y0 = slide.get("photo_y", 760)
        w, h = W, H - y0
        ph = cover_fit(photo, w, h, slide.get("fx", 0.5), slide.get("fy", 0.5))
        mask = Image.new("L", (w, h))
        md = ImageDraw.Draw(mask)
        fade = int(h * 0.45)
        for y in range(h):
            a = 255 if y >= fade else int(255 * (y / fade) ** 1.5)
            md.line([(0, y), (w, y)], fill=a)
        canvas.paste(ph, (0, y0), mask)


_logo = None


def logo():
    global _logo
    if _logo is None:
        ref = Image.open(logo_ref).convert("RGB").crop((58, 52, 262, 222))
        bg = (236, 233, 244)
        px = ref.load()
        out = Image.new("RGBA", ref.size)
        op = out.load()
        for y in range(ref.height):
            for x in range(ref.width):
                r, g, b = px[x, y]
                dist = math.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)
                a = max(0, min(255, int((dist - 18) * 3.2)))
                if a > 0:
                    k = a / 255.0
                    # un-mix the light background to keep crisp dark text
                    rr = int(max(0, min(255, (r - bg[0] * (1 - k)) / k)))
                    gg = int(max(0, min(255, (g - bg[1] * (1 - k)) / k)))
                    bb = int(max(0, min(255, (b - bg[2] * (1 - k)) / k)))
                    op[x, y] = (rr, gg, bb, a)
        _logo = out
    return _logo


def header(canvas, n, total):
    lg = logo()
    canvas.alpha_composite(lg, (MARGIN - 12, 48))
    d = ImageDraw.Draw(canvas)
    ly = 48 + 122
    lx0 = MARGIN - 12 + lg.width + 26
    d.ellipse([lx0 - 8, ly - 8, lx0 + 8, ly + 8], fill=PURPLE)
    d.line([(lx0, ly), (lx0 + 300, ly)], fill=PURPLE, width=3)
    # page pill
    f = body_font(30, 500)
    txt = f"{n:02d} / {total:02d}"
    tw = d.textlength(txt, font=f)
    pw, ph = tw + 48, 58
    x1, y1 = W - MARGIN, 66
    pill = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([x1 - pw, y1, x1, y1 + ph], radius=ph // 2, fill=(120, 116, 138, 210))
    canvas.alpha_composite(pill)
    d = ImageDraw.Draw(canvas)
    d.text((x1 - pw / 2, y1 + ph / 2), txt, font=f, fill=(255, 255, 255), anchor="mm")


def footer(canvas):
    f = body_font(24, 500)
    band = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    y = H - 64
    for txt, anchor_x, right in [("STEP DREAM / ПРАКТИКА БРОКЕРА", MARGIN, False), ("@terekbaev", W - MARGIN, True)]:
        tw = bd.textlength(txt, font=f)
        x0 = anchor_x - tw - 22 if right else anchor_x - 22
        bd.rounded_rectangle([x0, y - 22, x0 + tw + 44, y + 22], radius=22, fill=(255, 255, 255, 215))
        bd.text((x0 + 22, y), txt, font=f, fill=GREY, anchor="lm")
    canvas.alpha_composite(band)


NBSP = " "
SHORT = {"а", "в", "и", "к", "о", "с", "у", "я", "во", "на", "по", "за", "до", "не", "из", "от", "об", "со", "ко"}


def typo(text):
    """Russian typesetting: no dash at line start, no short word left at line end."""
    text = text.replace(" — ", NBSP + "— ")
    words = text.split(" ")
    out = []
    for i, w_ in enumerate(words):
        out.append(w_)
        if i < len(words) - 1:
            out.append(NBSP if w_.lower().strip("«»") in SHORT else " ")
    return "".join(out)


def wrap(d, text, font, width):
    out = []
    for para in typo(text).split("\n"):
        words, line = para.split(" "), ""
        for w_ in words:
            test = (line + " " + w_).strip()
            if d.textlength(test, font=font) <= width:
                line = test
            else:
                if line:
                    out.append(line)
                line = w_
        out.append(line)
    return out


def draw_title(canvas, x, y, lines, size, gap=0.98, max_w=None):
    d = ImageDraw.Draw(canvas)
    f = title_font(size)
    max_w = max_w or (W - 2 * MARGIN)
    for item in lines:
        txt, col = item["t"], PURPLE if item.get("c") == "p" else INK
        s = item.get("s", size)
        ff = title_font(s) if s != size else f
        while d.textlength(txt, font=ff) > max_w and s > 40:
            s -= 2
            ff = title_font(s)
        d.text((x, y), txt, font=ff, fill=col)
        bbox = d.textbbox((x, y), txt, font=ff)
        y = bbox[3] + int(s * (gap - 0.82))
    return y


def draw_text(canvas, x, y, text, size, width, color=INK, weight=400, lh=1.32):
    d = ImageDraw.Draw(canvas)
    f = body_font(size, weight)
    for line in wrap(d, text, f, width):
        d.text((x, y), line, font=f, fill=color)
        y += int(size * lh)
    return y


def icon_circle(canvas, cx, cy, r, kind):
    circ = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    grad = Image.new("RGBA", (2 * r, 2 * r))
    gd = ImageDraw.Draw(grad)
    for yy in range(2 * r):
        t = yy / (2 * r)
        c = tuple(int(PURPLE_2[i] + (40 - PURPLE_2[i] if i == 0 else (20 - PURPLE_2[i] if i == 1 else 120 - PURPLE_2[i])) * t) for i in range(3))
        gd.line([(0, yy), (2 * r, yy)], fill=c + (255,))
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    circ.paste(grad, (0, 0), m)
    canvas.alpha_composite(circ, (cx - r, cy - r))
    d = ImageDraw.Draw(canvas)
    s = r * 0.5
    wcol = (255, 255, 255)
    lw = max(3, r // 11)
    if kind == "chat":
        d.rounded_rectangle([cx - s, cy - s * 0.75, cx + s, cy + s * 0.45], radius=int(s * 0.35), outline=wcol, width=lw)
        d.polygon([(cx - s * 0.45, cy + s * 0.40), (cx - s * 0.55, cy + s * 0.95), (cx - s * 0.05, cy + s * 0.42)], fill=wcol)
        for k in (-0.45, 0, 0.45):
            d.ellipse([cx + s * k - lw * 0.8, cy - s * 0.15 - lw * 0.8, cx + s * k + lw * 0.8, cy - s * 0.15 + lw * 0.8], fill=wcol)
    elif kind == "check":
        d.line([(cx - s * 0.6, cy), (cx - s * 0.15, cy + s * 0.45), (cx + s * 0.65, cy - s * 0.45)], fill=wcol, width=lw + 2, joint="curve")
    elif kind == "chart":
        bw = s * 0.36
        for i_, hh in enumerate((0.5, 0.85, 1.2)):
            x = cx - s * 0.75 + i_ * (bw + s * 0.2)
            d.rectangle([x, cy + s * 0.6 - s * hh, x + bw, cy + s * 0.6], outline=wcol, width=lw)
    elif kind == "pin":
        d.ellipse([cx - s * 0.55, cy - s * 0.9, cx + s * 0.55, cy + s * 0.2], outline=wcol, width=lw)
        d.polygon([(cx - s * 0.42, cy - s * 0.05), (cx + s * 0.42, cy - s * 0.05), (cx, cy + s * 0.85)], fill=wcol)
        d.ellipse([cx - s * 0.18, cy - s * 0.53, cx + s * 0.18, cy - s * 0.17], fill=PURPLE)
    elif kind == "building":
        d.rectangle([cx - s * 0.55, cy - s * 0.85, cx + s * 0.55, cy + s * 0.75], outline=wcol, width=lw)
        for row in range(3):
            for col in range(2):
                x = cx - s * 0.3 + col * s * 0.38
                y = cy - s * 0.6 + row * s * 0.42
                d.rectangle([x, y, x + s * 0.18, y + s * 0.2], fill=wcol)
    elif kind == "calendar":
        d.rounded_rectangle([cx - s * 0.75, cy - s * 0.6, cx + s * 0.75, cy + s * 0.75], radius=6, outline=wcol, width=lw)
        d.line([(cx - s * 0.75, cy - s * 0.2), (cx + s * 0.75, cy - s * 0.2)], fill=wcol, width=lw)
        for k in (-0.4, 0.4):
            d.line([(cx + s * k, cy - s * 0.85), (cx + s * k, cy - s * 0.45)], fill=wcol, width=lw)
    elif kind == "mail":
        d.rectangle([cx - s * 0.8, cy - s * 0.55, cx + s * 0.8, cy + s * 0.55], outline=wcol, width=lw)
        d.line([(cx - s * 0.8, cy - s * 0.55), (cx, cy + s * 0.1), (cx + s * 0.8, cy - s * 0.55)], fill=wcol, width=lw)
    elif kind == "heart":
        d.ellipse([cx - s * 0.8, cy - s * 0.6, cx, cy + s * 0.15], outline=wcol, width=lw)
        d.ellipse([cx, cy - s * 0.6, cx + s * 0.8, cy + s * 0.15], outline=wcol, width=lw)
    elif kind == "x":
        d.line([(cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy + s * 0.5)], fill=wcol, width=lw + 2)
        d.line([(cx + s * 0.5, cy - s * 0.5), (cx - s * 0.5, cy + s * 0.5)], fill=wcol, width=lw + 2)


def card(canvas, x, y, w, text, size=34, icon="chat", weight=400):
    d = ImageDraw.Draw(canvas)
    f = body_font(size, weight)
    pad, ir = 34, 40
    tx = x + pad + 2 * ir + 26
    lines = wrap(d, text, f, w - (tx - x) - pad)
    lh = int(size * 1.34)
    h = max(2 * pad + len(lines) * lh - (lh - size) + 6, 2 * pad + 2 * ir)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x, y + 10, x + w, y + h + 10], radius=30, fill=(60, 30, 150, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(sh)
    ImageDraw.Draw(layer).rounded_rectangle([x, y, x + w, y + h], radius=30, fill=(255, 255, 255, 242), outline=(214, 202, 245), width=2)
    canvas.alpha_composite(layer)
    icon_circle(canvas, x + pad + ir, y + pad + ir, ir, icon)
    d = ImageDraw.Draw(canvas)
    ty = y + pad + 2
    for line in lines:
        d.text((tx, ty), line, font=f, fill=INK)
        ty += lh
    return y + h


def rows(canvas, x, y, items, width, size=36, r=40, gap=34, bold=False):
    for it in items:
        d = ImageDraw.Draw(canvas)
        f = body_font(size, 700 if bold else 400)
        fb = body_font(size, 700)
        tx = x + 2 * r + 28
        head, rest = it.get("b", ""), it.get("t", "")
        lines = []
        if head:
            lines.append((head, fb, PURPLE))
        for ln in wrap(d, rest, f, width - (tx - x)):
            lines.append((ln, f, PURPLE if bold else INK))
        lh = int(size * 1.3)
        block = len(lines) * lh
        cy = y + max(block, 2 * r) // 2
        icon_circle(canvas, x + r, cy, r, it.get("i", "check"))
        ty = cy - block // 2
        for ln, ff, col in lines:
            d.text((tx, ty), ln, font=ff, fill=col)
            ty += lh
        y += max(block, 2 * r) + gap
    return y


def button(canvas, x, y, text, plus=False):
    d = ImageDraw.Draw(canvas)
    f = body_font(44, 500)
    tw = d.textlength(text, font=f)
    h = 104
    w = int(tw + 60 + 84 + 30)
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x, y + 10, x + w, y + h + 10], radius=h // 2, fill=(59, 31, 168, 70))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=PURPLE)
    d.text((x + 50, y + h / 2), text, font=f, fill=(255, 255, 255), anchor="lm")
    cx, cy, r = x + w - 16 - 42, y + h // 2, 38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    if plus:
        d.line([(cx - 15, cy), (cx + 15, cy)], fill=PURPLE, width=6)
        d.line([(cx, cy - 15), (cx, cy + 15)], fill=PURPLE, width=6)
    else:
        d.line([(cx - 16, cy), (cx + 14, cy)], fill=PURPLE, width=6)
        d.line([(cx + 2, cy - 13), (cx + 15, cy), (cx + 2, cy + 13)], fill=PURPLE, width=6, joint="curve")


def brush(canvas, x, y, w, h, text, size=46):
    rnd = random.Random(7)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(26):
        yy = y + rnd.uniform(0, h * 0.85)
        th = rnd.uniform(h * 0.18, h * 0.42)
        xs = x + rnd.uniform(-20, 30)
        xe = x + w - rnd.uniform(-25, 40)
        d.rounded_rectangle([xs, yy, xe, yy + th], radius=int(th / 2), fill=(66, 36, 178, 235))
    for i in range(70):  # dry-brush streaks at both ends
        yy = y + rnd.uniform(0, h)
        side = rnd.choice([0, 1])
        ln = rnd.uniform(20, 90)
        xx = (x - ln * 0.6) if side == 0 else (x + w - ln * 0.4)
        d.line([(xx, yy), (xx + ln, yy)], fill=(66, 36, 178, 200), width=rnd.randint(2, 6))
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    canvas.alpha_composite(layer)
    d = ImageDraw.Draw(canvas)
    f = body_font(size, 700)
    d.text((x + w / 2, y + h / 2), text, font=f, fill=(255, 255, 255), anchor="mm")


def portrait(canvas):
    """Rond avec la photo de Беслан (logo STEP DREAM dedans) + nom dessous."""
    x, y, D = CIRCLE_X, CIRCLE_Y, CIRCLE_D
    inner = D - 32          # disque blanc
    photo_d = inner - 20    # photo (bordure blanche de 10 px)
    ox, oy = x + (D - inner) // 2, y + (D - inner) // 2
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([ox, oy + 18, ox + inner, oy + inner + 18], fill=(40, 20, 110, 95))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(canvas)
    d.ellipse([x, y, x + D - 1, y + D - 1], outline=PURPLE, width=4)
    d.ellipse([ox, oy, ox + inner - 1, oy + inner - 1], fill=(255, 255, 255))
    ph = cover_fit(Image.open(portrait_path).convert("RGB"), photo_d * 2, photo_d * 2)
    m = Image.new("L", (photo_d * 2, photo_d * 2), 0)
    ImageDraw.Draw(m).ellipse([0, 0, photo_d * 2 - 1, photo_d * 2 - 1], fill=255)
    ph = ph.resize((photo_d, photo_d), Image.LANCZOS)
    m = m.resize((photo_d, photo_d), Image.LANCZOS)
    canvas.paste(ph, (ox + 10, oy + 10), m)
    # nom sous le rond
    f = vfont("Oswald[wght].ttf", 32, wght=500)
    tw = d.textlength(PORTRAIT_NAME, font=f)
    pw, phh = int(tw + 56), 58
    px0, py0 = x + D // 2 - pw // 2, y + D + 22
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([px0, py0 + 8, px0 + pw, py0 + phh + 8], radius=phh // 2, fill=(40, 20, 110, 60))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + phh], radius=phh // 2, fill=(255, 255, 255))
    d.text((px0 + pw / 2, py0 + phh / 2), PORTRAIT_NAME, font=f, fill=PURPLE, anchor="mm")


# Dernière slide : abonnement (fixe, validée le 07/10/2026). Le texte ne change pas.
SUBSCRIBE = {
    "layout": "right", "photo_x": 560, "fx": 0.5, "title_y": 250, "title_size": 96, "title_w": 620, "text_w": 600,
    "title": [{"t": "ПОДПИШИСЬ,"}, {"t": "ЧТОБЫ НЕ", "c": "p"}, {"t": "ПРОПУСТИТЬ", "c": "p"}],
    "blocks": [
        {"k": "text", "t": "Каждый день здесь выходит новое бесплатное обучение для брокеров.", "size": 36, "w": 600, "pad": 34},
        {"k": "rows", "pad": 34, "size": 34, "r": 26, "gap": 16, "w": 640, "bold": True, "items": [
            {"i": "check", "t": "Бесплатно"},
            {"i": "check", "t": "Новый урок каждое утро"},
            {"i": "check", "t": "Практика, а не теория"}
        ]},
        {"k": "button", "t": "Подписаться", "y": 1110, "plus": True}
    ]
}


def render(slide, total):
    if slide.get("kind") == "subscribe":
        slide = dict(SUBSCRIBE, n=slide["n"], **{k: v for k, v in slide.items() if k in ("photo_x", "fx", "fy")})
    c = background()
    place_photo(c, slide)
    header(c, slide["n"], total)
    first = slide["n"] == 1
    if first:
        portrait(c)
    y = slide.get("title_y", 300)
    tw = slide.get("text_w", W - 2 * MARGIN)
    y = draw_title(c, MARGIN, y, slide["title"], slide.get("title_size", 92),
                   max_w=slide.get("title_w", CIRCLE_X - MARGIN - 30 if first else None))
    for blk in slide.get("blocks", []):
        y += blk.get("pad", 34)
        k = blk["k"]
        if k == "text":
            y = draw_text(c, MARGIN, y, blk["t"], blk.get("size", 38), blk.get("w", tw), PURPLE if blk.get("c") == "p" else INK, blk.get("weight", 400))
        elif k == "card":
            y = card(c, MARGIN, y, blk.get("w", W - 2 * MARGIN), blk["t"], blk.get("size", 34), blk.get("i", "chat"), blk.get("weight", 400))
        elif k == "rows":
            y = rows(c, MARGIN, y, blk["items"], blk.get("w", tw), blk.get("size", 36), blk.get("r", 40), blk.get("gap", 30), blk.get("bold", False))
        elif k == "button":
            button(c, MARGIN, blk.get("y", y), blk["t"], blk.get("plus", False))
        elif k == "brush":
            brush(c, MARGIN - 10, blk.get("y", y), blk.get("w", 760), 130, blk["t"])
    footer(c)
    out = c.convert("RGB")
    path = os.path.join(out_dir, f"slide-{slide['n']:02d}.jpg")
    out.save(path, "JPEG", quality=92, optimize=True, progressive=True)
    return path


spec = json.load(open(spec_path, encoding="utf-8"))
total = len(spec["slides"])
if spec["slides"][-1].get("kind") != "subscribe":
    sys.exit("ERREUR : la dernière slide doit être {\"kind\": \"subscribe\"} (règle du 07/10/2026).")
if not os.path.exists(portrait_path):
    sys.exit("ERREUR : photo du rond introuvable : " + portrait_path + " (refs/beslan-circle.jpg).")
for s in spec["slides"]:
    if os.path.exists(os.path.join(photos_dir, f"p{s['n']}.png")):
        print(render(s, total))

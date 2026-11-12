#!/usr/bin/env python3
"""Renderer de colagem jornal-meme, 1080x1920."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops

W, H, FPS = 1080, 1920, 30
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
ASSETS = _os.environ.get("PLANTAO_ASSETS") or _os.path.join(_os.path.dirname(_HERE), "assets")
WORK = _os.environ.get("PLANTAO_WORK") or _os.path.join(_os.getcwd(), "work")
F = f"{ASSETS}/fonts"
EMO = f"{ASSETS}/emoji"
OUT = f"{WORK}/cout"
MASTHEAD = _os.environ.get("PLANTAO_NOME", "MAPA SUJO")
_os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

PAPER = (241, 234, 218)
INK = (22, 19, 16)
RED = (198, 16, 46)
BLUE = (32, 68, 186)
YEL = (255, 213, 58)
GREY = (118, 112, 101)
MAG = (226, 0, 132)
CYA = (0, 174, 230)
ORG = (255, 116, 20)
LIM = (172, 234, 60)
WHT = (255, 255, 255)

_rng = np.random.default_rng(7)


# ------------------------------------------------------------------ fontes
def fnt(name, size, weight=None):
    f = ImageFont.truetype(f"{F}/{name}", max(8, int(size)))
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


# ------------------------------------------------------------------ papel
FAKE = ("O Primeiro Comando da Capital e o Comando Vermelho aparecem agora na lista de "
        "organizacoes terroristas estrangeiras do governo dos Estados Unidos. A medida foi "
        "anunciada em Washington e reacende a discussao sobre seguranca publica no Brasil. "
        "O ministerio da Justica informou que novas acoes de recuperacao de ativos estao em "
        "andamento em cinco estados. Investigadores apontam que o crime organizado movimenta "
        "bilhoes por ano em contrabando, armas e lavagem de dinheiro. O texto aprovado no "
        "congresso americano abre caminho para sancoes economicas e congelamento de bens. "
        "Especialistas divergem sobre o efeito pratico da medida. A defesa nega as acusacoes. ")


def wrap_col(d, text, x, y, w, h, font, fill, lead):
    words = text.split()
    line, cur = "", y
    i = 0
    while cur < y + h:
        wd = words[i % len(words)]
        test = (line + " " + wd).strip()
        if d.textlength(test, font=font) > w:
            d.text((x, cur), line, font=font, fill=fill)
            cur += lead
            line = wd
        else:
            line = test
        i += 1
    return cur


def make_paper(seed):
    rng = np.random.default_rng(seed)
    arr = np.ones((H, W, 3), dtype=np.float32) * np.array(PAPER, dtype=np.float32)
    arr += rng.normal(0, 3.4, (H, W, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).convert("RGBA")

    stains = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(stains)
    for _ in range(6):
        cx, cy = int(rng.integers(0, W)), int(rng.integers(0, H))
        r = int(rng.integers(90, 280))
        d.ellipse([cx - r, cy - r * .7, cx + r, cy + r * .7], fill=(148, 118, 66, int(rng.integers(5, 12))))
    stains = stains.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img, stains)

    # colunas de texto falso
    d = ImageDraw.Draw(img)
    col_w = 296
    x0 = 56
    for c in range(3):
        wrap_col(d, FAKE[c * 90:], x0 + c * (col_w + 40), 300, col_w, 1250,
                 fnt("Oswald.ttf", 11, 300), (163, 156, 143), 13.2)
        d.line([x0 + c * (col_w + 40) - 20, 290, x0 + c * (col_w + 40) - 20, 1560],
               fill=(0, 0, 0, 18), width=1)

    # masthead
    mt = MASTHEAD
    mf = fnt("Playfair.ttf", 116, 900)
    tw = d.textlength(mt, font=mf)
    if tw > W - 120:                      # nome longo: encolhe até caber no cabeçalho
        mf = fnt("Playfair.ttf", int(116 * (W - 120) / tw), 900)
        tw = d.textlength(mt, font=mf)
    d.text(((W - tw) / 2, 62), mt, font=mf, fill=INK)
    d.line([56, 214, W - 56, 214], fill=INK, width=4)
    d.line([56, 224, W - 56, 224], fill=INK, width=1)
    df = fnt("Oswald.ttf", 21, 400)
    dt = "EDIÇÃO EXTRA  ·  BRASÍLIA  ·  QUINTA-FEIRA, 12 DE NOVEMBRO DE 2026"
    d.text(((W - d.textlength(dt, font=df)) / 2, 236), dt, font=df, fill=(90, 84, 74))
    d.line([56, 268, W - 56, 268], fill=(0, 0, 0, 60), width=1)

    # dobras
    fold = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fold)
    fd.rectangle([W // 2 - 3, 0, W // 2 + 3, H], fill=(0, 0, 0, 8))
    fd.rectangle([0, int(H * .44) - 3, W, int(H * .44) + 3], fill=(0, 0, 0, 7))
    fold = fold.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, fold)

    d = ImageDraw.Draw(img)
    d.line([56, 1786, W - 56, 1786], fill=(0, 0, 0, 70), width=1)
    ff = fnt("Oswald.ttf", 19, 400)
    d.text((56, 1798), f"{MASTHEAD}  ·  EDIÇÃO EXTRA  ·  SEGURANÇA PÚBLICA", font=ff, fill=(120, 113, 101))
    pt = "PÁGINA 1"
    d.text((W - 56 - d.textlength(pt, font=ff), 1798), pt, font=ff, fill=(120, 113, 101))
    return img.convert("RGB")


# ------------------------------------------------------------------ fotos
_imgs = {}
def load(path):
    if path not in _imgs:
        _imgs[path] = Image.open(path).convert("RGB")
    return _imgs[path]


def cover(im, w, h):
    iw, ih = im.size
    s = max(w / iw, h / ih)
    n = im.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    l = (n.width - w) // 2
    t = (n.height - h) // 2
    return n.crop((l, t, l + w, t + h))


def print_photo(im, w, h, tint=(1.05, 1.0, .92), color=False, bright=1.0):
    if color:
        c = cover(im, w, h)
        c = ImageEnhance.Color(c).enhance(0.82)
        c = ImageEnhance.Contrast(c).enhance(1.16)
        arr = np.array(c).astype(np.float32) * np.array(tint, dtype=np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        dots = (np.sin(xx * math.pi / 4.0) ** 2) * (np.sin(yy * math.pi / 4.0) ** 2)
        arr *= (0.9 + 0.1 * dots)[..., None]
        arr += np.random.normal(0, 2.4, arr.shape)
        return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    g = ImageOps.grayscale(cover(im, w, h))
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.22)
    arr = np.array(Image.merge("RGB", (g, g, g))).astype(np.float32) * np.array(tint, dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    dots = (np.sin(xx * math.pi / 4.0) ** 2) * (np.sin(yy * math.pi / 4.0) ** 2)
    arr *= (0.88 + 0.12 * dots)[..., None]
    arr = arr * bright + 10 * (bright - 1)
    arr += np.random.normal(0, 2.6, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def torn_mask(w, h, seed, sides=("bottom",)):
    rng = random.Random(seed)
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    if "bottom" in sides:
        step = 16
        pts = [(0, h)]
        for x in range(0, w + step, step):
            pts.append((x, h - rng.randint(0, 18)))
        pts.append((w, h))
        d.polygon(pts, fill=0)
    if "top" in sides:
        step = 18
        pts = [(0, 0)]
        for x in range(0, w + step, step):
            pts.append((x, rng.randint(0, 12)))
        pts.append((w, 0))
        d.polygon(pts, fill=0)
    return m


def paper_cut(photo, seed=0, border=13, torn=("bottom",), shadow=26, tape_corner=None, tape_color=None):
    w, h = photo.size
    bw, bh = w + border * 2, h + border * 2
    card = Image.new("RGBA", (bw, bh), (252, 248, 238, 255))
    card.paste(photo.convert("RGB"), (border, border))
    card.putalpha(torn_mask(bw, bh, seed, torn))
    # sombra
    sh = Image.new("RGBA", (bw + shadow * 2, bh + shadow * 2), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (shadow, shadow), card.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    out = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    out.alpha_composite(sh)
    out.alpha_composite(card, (shadow, shadow))
    if tape_corner:
        t = tape_strip(int(bw * (.34 if tape_color else .42)), 46 if tape_color else 54,
                       tape_corner[0], tape_color or (231, 219, 184), 92 if tape_color else 152)
        ty = tape_corner[2] + (34 if tape_color else 0)
        out.alpha_composite(t, (tape_corner[1], ty))
    return out


def tape_strip(w, h, angle, color=(231, 219, 184), alpha=152):
    im = Image.new("RGBA", (w, h), color + (alpha,))
    d = ImageDraw.Draw(im)
    edge = tuple(max(0, int(c * .86)) for c in color)
    d.rectangle([0, 0, w - 1, h - 1], outline=edge + (min(255, alpha + 18),), width=2)
    arr = np.array(im).astype(np.int16)
    arr[..., :3] += _rng.normal(0, 5, (h, w, 3)).astype(np.int16)
    im = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


# ------------------------------------------------------------------ tipografia colada
def text_block(lines, size, color=INK, font="Playfair.ttf", weight=900,
               leading=.92, align="center", spacing=0, maxw=940):
    fs = size
    while fs > 20:
        f = fnt(font, fs, weight)
        widest = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f) for l in lines)
        if widest <= maxw:
            break
        fs -= 2
    f = fnt(font, fs, weight)
    lh = int(fs * leading)
    widths = [ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f) for l in lines]
    bw = int(max(widths)) + 40
    bh = lh * len(lines) + 30 + spacing * (len(lines) - 1)
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 14
    for i, l in enumerate(lines):
        x = (bw - widths[i]) / 2 if align == "center" else 20
        d.text((x, y), l, font=f, fill=color + (255,))
        y += lh + spacing
    return im


PLATE = (249, 244, 232)


def with_plate(im, padx=26, pady=16, color=PLATE):
    w, h = im.width + padx * 2, im.height + pady * 2
    plate = Image.new("RGBA", (w + 26, h + 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rectangle([13, 13, 13 + w - 1, 13 + h - 1], fill=color + (255,))
    sh = Image.new("RGBA", plate.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 70), (13, 15), plate)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    out = Image.new("RGBA", plate.size, (0, 0, 0, 0))
    out.alpha_composite(sh)
    out.alpha_composite(plate)
    arr = np.array(out).astype(np.int16)
    noise = _rng.normal(0, 3, (out.height, out.width, 1)).astype(np.int16)
    arr[..., :3] += noise
    out = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    out.alpha_composite(im, (13 + padx, 13 + pady))
    return out


def stamp(text, size, color=RED, ang=-8, alpha=228):
    f = fnt("Anton.ttf", size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(d0.textlength(text, font=f))
    bbox = f.getbbox(text)
    th = bbox[3] - bbox[1]
    pad = int(size * .34)
    im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([5, 5, im.width - 6, im.height - 6], outline=color + (int(alpha * .85),), width=max(4, size // 14))
    d.rectangle([14, 14, im.width - 15, im.height - 15], outline=color + (int(alpha * .45),), width=2)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=color + (alpha,))
    # grunge
    a = np.array(im.split()[3]).astype(np.float32)
    noise = _rng.random(a.shape)
    a *= (noise > .09).astype(np.float32)
    a = np.array(Image.fromarray(a.astype("uint8")).filter(ImageFilter.GaussianBlur(.6))).astype(np.float32)
    im.putalpha(Image.fromarray(np.clip(a, 0, 255).astype("uint8")))
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def marker(text, size, color=RED, ang=-5, highlight=None):
    f = fnt("PermanentMarker.ttf", size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(d0.textlength(text, font=f))
    bbox = f.getbbox(text)
    th = bbox[3] - bbox[1]
    pad = int(size * .45)
    ch = int(th * 1.18) + pad * 2
    ty = (ch - th) / 2 - bbox[1]
    im = Image.new("RGBA", (tw + pad * 2, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if highlight:
        hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        y0 = ty + bbox[1] + th * .05
        y1 = ty + bbox[1] + th * .93
        ImageDraw.Draw(hl).polygon([(pad * .55, y0), (tw + pad * 1.45, y0 - 5),
                                    (tw + pad * 1.4, y1 + 4), (pad * .6, y1)], fill=highlight + (135,))
        hl = hl.filter(ImageFilter.GaussianBlur(4))
        im = Image.alpha_composite(im, hl)
        d = ImageDraw.Draw(im)
    d.text((pad - bbox[0], ty), text, font=f, fill=color + (242,))
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def marker_arrow(w, h, color=RED, ang=-2):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    th = h * .30
    y = h / 2
    d.polygon([(w * .04, y - th / 2), (w * .68, y - th / 2), (w * .68, y - th * 1.5),
               (w * .97, y), (w * .68, y + th * 1.5), (w * .68, y + th / 2), (w * .04, y + th / 2)],
              fill=color + (238,))
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def marker_circle(rx, ry, color=RED, width=9, ang=-6):
    im = Image.new("RGBA", (int(rx * 2.3), int(ry * 2.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = [im.width * .1, im.height * .1, im.width * .9, im.height * .9]
    for k in range(2):
        b2 = [box[0] + k * 3, box[1] + k * 2, box[2] - k * 4, box[3] - k * 3]
        d.ellipse(b2, outline=color + (230,), width=width - k * 3)
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def emoji_sticker(code, size, outline=13):
    e = Image.open(f"{EMO}/{code}.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    a = e.split()[3].filter(ImageFilter.MaxFilter(outline * 2 + 1))
    white = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    white.putalpha(a)
    pad = 22
    out = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 80), (pad + 5, pad + 9), white.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    out.alpha_composite(sh)
    out.alpha_composite(white, (pad, pad))
    out.alpha_composite(e, (pad, pad))
    return out


# ------------------------------------------------------------------ motion
def crop_zoom(img, zoom, dx=0.0, dy=0.0):
    bw, bh = img.size
    cw, ch = bw / zoom, bh / zoom
    cx = bw / 2 + dx * bw
    cy = bh / 2 + dy * bh
    x0 = min(max(cx - cw / 2, 0), bw - cw)
    y0 = min(max(cy - ch / 2, 0), bh - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


# ------------------------------------------------------------------ cor / dopamina
def sunburst(size, color, rays=15, alpha=64, ang=0.0):
    S = int(size)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    pts = []
    for i in range(rays * 2):
        a = ang + i * math.pi / rays
        r = c if i % 2 == 0 else c * .58
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    d.polygon(pts, fill=color + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(1.1))


def disc(r, color, alpha=255):
    im = Image.new("RGBA", (int(r * 2) + 8, int(r * 2) + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([4, 4, im.width - 5, im.height - 5], fill=color + (alpha,))
    return im


def tilt(im, ang):
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


TICKER_TXT = ("  URGENTE  •  PCC E CV NA LISTA DE TERRORISTAS  •  R$ 190,3 MILHÕES NA MIRA"
              "  •  CV EM 26 DE 27 ESTADOS  •  1/3 DO RIO É ÁREA DE FACÇÃO"
              "  •  A BARRICADA CONTINUA  •  ")
_tick = {}


def ticker_strip(color, h=60):
    if color in _tick:
        return _tick[color]
    fg = INK if color == YEL else WHT
    f = fnt("Oswald.ttf", 34, 600)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(d0.textlength(TICKER_TXT, font=f))
    im = Image.new("RGBA", (tw + 60, h), color + (255,))
    d = ImageDraw.Draw(im)
    d.text((30, h / 2 + 1), TICKER_TXT, font=f, fill=fg + (255,), anchor="lm")
    d.rectangle([0, 0, im.width - 1, h - 1], outline=(0, 0, 0, 110), width=4)
    _tick[color] = im
    return im


def confetti(lt, seed, colors, n=20, cx=540, cy=950):
    if lt > .58:
        return None
    rnd = random.Random(seed)
    fade = 255 if lt < .34 else int(255 * max(0.0, 1 - (lt - .34) / .24))
    if fade <= 2:
        return None
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(n):
        ang = rnd.uniform(-math.pi, math.pi)
        spd = rnd.uniform(520, 1080)
        col = colors[i % len(colors)]
        s = rnd.uniform(11, 24)
        rot = rnd.uniform(0, math.pi) + lt * 7
        x = cx + math.cos(ang) * spd * lt
        y = cy + math.sin(ang) * spd * lt + 1400 * lt * lt
        w2, h2 = s, s * .44
        ca, sa = math.cos(rot), math.sin(rot)
        pts = [(x + ca * w2 / 2 - sa * h2 / 2, y + sa * w2 / 2 + ca * h2 / 2),
               (x - ca * w2 / 2 - sa * h2 / 2, y - sa * w2 / 2 + ca * h2 / 2),
               (x - ca * w2 / 2 + sa * h2 / 2, y - sa * w2 / 2 - ca * h2 / 2),
               (x + ca * w2 / 2 + sa * h2 / 2, y + sa * w2 / 2 - ca * h2 / 2)]
        d.polygon(pts, fill=col + (fade,))
    return lay


# ------------------------------------------------------------------ motion
def crop_zoom(img, zoom, dx=0.0, dy=0.0):
    bw, bh = img.size
    cw, ch = bw / zoom, bh / zoom
    cx = bw / 2 + dx * bw
    cy = bh / 2 + dy * bh
    x0 = min(max(cx - cw / 2, 0), bw - cw)
    y0 = min(max(cy - ch / 2, 0), bh - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


# ------------------------------------------------------------------ cena
def build():
    papers = [make_paper(s) for s in (11, 27, 41)]
    P = [p.convert("RGBA") for p in papers]

    rio_files = sorted(os.listdir(f"{WORK}/frames"))
    rio_a = load(f"{ROOT}/work/frames/{rio_files[10]}")
    rio_b = load(f"{ROOT}/work/frames/{rio_files[95]}")
    img = lambda n: load(f"{ROOT}/img/{n}")

    B = []

    # B1a — carimbo URGENTE
    B.append(dict(t0=0.00, t1=0.90, p=0, accent=YEL, burst=True, shake=16, zoom=.06, layers=[
        (stamp("URGENTE", 210, RED, -7), 540, 830, 0.0),
        (with_plate(tilt(text_block(["EDIÇÃO EXTRA"], 52, INK, "Oswald.ttf", 600, spacing=4), 2.5), 14, 10,
                    color=YEL), 540, 1210, 0.10),
        (emoji_sticker("1f4a5", 190), 815, 545, 0.04, 6.0),
        (emoji_sticker("1f6a8", 150), 200, 1230, 0.16, 5.0),
    ]))

    # B1b — manchete de capa
    B.append(dict(t0=0.90, t1=5.45, p=1, accent=MAG, burst=True, shake=13, zoom=.13,
                  punches=[(1.30, .085, .34), (2.85, .075, .30)], layers=[
        (with_plate(text_block(["PCC E CV NA LISTA", "DE TERRORISTAS"], 99, INK, leading=.92, maxw=850)), 540, 385, 0.02),
        (with_plate(marker("os EUA decidiram", 44, INK, -4, highlight=YEL), 18, 10), 540, 560, 0.50),
        (paper_cut(print_photo(rio_a, 640, 640, bright=1.22), 3, torn=("bottom",),
                   tape_corner=(-8, 40, 34), tape_color=MAG), 540, 1085, 0.26),
        (stamp("URGENTE", 74, RED, -11), 805, 745, 0.60),
        (emoji_sticker("1f4a5", 150), 245, 780, 0.68, 5.0),
        (with_plate(text_block(["Imagem ilustrativa · Complexo da Penha, Rio"], 24, GREY, "Oswald.ttf", 400), 20, 8),
         540, 1495, 0.44),
    ]))

    # B2 — escudo das américas
    B.append(dict(t0=5.45, t1=7.30, p=2, accent=CYA, shake=11, zoom=.11,
                  punches=[(0.55, .07, .26)], layers=[
        (with_plate(text_block(["ESCUDO DAS", "AMÉRICAS"], 108, INK)), 540, 375, 0.0),
        (with_plate(marker("EUA", 54, INK, -4, highlight=YEL), 14, 8), 330, 630, 0.30),
        (marker_arrow(115, 54, RED, -1), 532, 630, 0.34),
        (with_plate(marker("BRASIL", 54, INK, 2, highlight=YEL), 14, 8), 735, 630, 0.38),
        (with_plate(marker("entrou junto", 36, BLUE, -3), 12, 6), 520, 720, 0.46),
        (paper_cut(print_photo(img("radar_room.png"), 600, 600, bright=1.18), 7,
                   tape_corner=(7, 380, 8), tape_color=CYA), 540, 1105, 0.18),
        (stamp("ATIVADO", 58, BLUE, 7), 705, 1215, 0.68),
        (emoji_sticker("1f440", 124), 168, 1235, 0.86, 6.0),
    ]))

    # B3 — lei antifacção / 190 milhões
    B.append(dict(t0=7.30, t1=8.90, p=0, accent=YEL, burst=True, shake=14, zoom=.12,
                  punches=[(0.28, .075, .24)], layers=[
        (with_plate(text_block(["LEI ANTIFACÇÃO"], 104, INK)), 540, 420, 0.0),
        (with_plate(tilt(text_block(["R$ 190 MILHÕES NA MIRA"], 62, RED, "Oswald.ttf", 600), -2.0), 22, 12,
                    color=YEL), 540, 575, 0.10),
        (paper_cut(print_photo(img("gavel.png"), 420, 450), 11, tape_corner=(-6, 26, -18), tape_color=MAG),
         350, 1055, 0.08),
        (paper_cut(print_photo(img("cash_table.png"), 420, 450, color=True), 12,
                   tape_corner=(9, 290, -14), tape_color=CYA), 745, 1120, 0.18),
        (stamp("CONFISCO", 62, RED, -9), 760, 1455, 0.52),
        (emoji_sticker("1f4b0", 150), 902, 712, 0.62, 6.0),
    ]))

    # B4 — 26 de 27 estados
    B.append(dict(t0=8.90, t1=13.70, p=1, accent=MAG, burst=True, shake=13, zoom=.14,
                  punches=[(1.55, .08, .32), (3.05, .07, .28)], layers=[
        (with_plate(text_block(["O CV TÁ EM", "26 DE 27", "ESTADOS"], 106, INK, leading=.90)), 540, 400, 0.0),
        (paper_cut(print_photo(img("brazil_map.png"), 590, 780, color=True), 21,
                   tape_corner=(-7, 34, -18), tape_color=YEL), 540, 1145, 0.12),
        (with_plate(tilt(marker("26/27", 96, WHT, -7), 3.0), 18, 10, color=RED), 306, 900, 1.95),
        (stamp("EXCLUSIVO", 58, RED, 6), 250, 1520, 2.30),
        (emoji_sticker("1f525", 124), 936, 706, 1.55, 6.0),
    ]))

    # B5 — um terço do rio
    B.append(dict(t0=13.70, t1=17.40, p=2, accent=ORG, shake=12, zoom=.13,
                  punches=[(1.20, .08, .30), (2.60, .06, .24)], layers=[
        (with_plate(text_block(["UM TERÇO DO RIO", "É ÁREA DE FACÇÃO"], 88, INK, leading=.95)), 540, 375, 0.0),
        (paper_cut(print_photo(rio_b, 615, 660, bright=1.22), 31,
                   tape_corner=(6, 46, 10), tape_color=ORG), 540, 1085, 0.14),
        (with_plate(tilt(marker("1/3", 150, WHT, -9), 3.5), 16, 8, color=RED), 356, 786, 1.50),
        (with_plate(text_block(["Fonte: Fogo Cruzado / UFF — via FT"], 24, GREY, "Oswald.ttf", 400), 18, 8),
         540, 1480, 0.34),
        (emoji_sticker("1f3af", 122), 872, 760, 1.62, 6.0),
    ]))

    # B6 — tá na lista, mas a barricada continua
    B.append(dict(t0=17.40, t1=20.70, p=0, accent=RED, burst=True, shake=14, zoom=.12,
                  punches=[(0.90, .07, .30), (2.20, .06, .26)], layers=[
        (with_plate(text_block(["TÁ NA LISTA DE", "TERRORISTA..."], 96, INK, leading=.92)), 540, 360, 0.0),
        (paper_cut(print_photo(img("prison.png"), 450, 500, bright=1.30), 41,
                   tape_corner=(-6, 18, -18), tape_color=MAG), 320, 880, 0.08),
        (paper_cut(print_photo(img("barricade.png"), 530, 540, bright=1.25), 42,
                   tape_corner=(8, 370, -14), tape_color=YEL), 725, 1015, 0.20),
        (with_plate(tilt(text_block(["...MAS A BARRICADA", "CONTINUA NA ESQUINA"], 80, WHT, leading=.95), 1.8),
                    24, 14, color=RED), 540, 1428, 0.86),
        (emoji_sticker("1f631", 128), 172, 1180, 1.02, 6.0),
    ]))

    # B7 — RESOLVE?
    B.append(dict(t0=20.70, t1=21.60, p=2, accent=MAG, burst=True, shake=15, zoom=.10, layers=[
        (with_plate(tilt(text_block(["RESOLVE?"], 118, WHT, maxw=700), -2.5), 30, 16, color=MAG), 540, 790, 0.0),
        (emoji_sticker("1f914", 178), 828, 1085, 0.06, 7.0),
    ]))

    # B8 — ou é só foto pra eleição?
    B.append(dict(t0=21.60, t1=23.90, p=1, accent=CYA, shake=11, zoom=.12,
                  punches=[(0.70, .07, .26)], layers=[
        (with_plate(text_block(["OU É SÓ FOTO", "PRA ELEIÇÃO?"], 100, INK)), 540, 655, 0.0),
        (paper_cut(print_photo(img("urna.png"), 460, 380, bright=1.12), 51,
                   tape_corner=(5, 20, -12), tape_color=CYA), 470, 1175, 0.16),
        (emoji_sticker("1f921", 152), 878, 1118, 0.26, 6.0),
    ]))

    # B9 — CTA
    B.append(dict(t0=23.90, t1=27.90, p=2, accent=YEL, burst=True, shake=12, zoom=.10, layers=[
        (with_plate(tilt(text_block(["COMENTA AÍ"], 112, INK, maxw=700), -2.0), 34, 22, color=YEL), 540, 540, 0.0),
        (disc(122, MAG), 540, 792, 0.08),
        (marker_arrow(128, 82, WHT, -1).rotate(-90, expand=True), 540, 792, 0.10, 5.0),
        (paper_cut(print_photo(rio_a, 250, 250, bright=1.22), 61, border=10,
                   tape_corner=(-9, 18, -14), tape_color=MAG), 215, 1205, 0.20),
        (paper_cut(print_photo(img("cash_table.png"), 250, 250, color=True), 62, border=10,
                   tape_corner=(8, 175, -14), tape_color=CYA), 540, 1245, 0.27),
        (paper_cut(print_photo(img("barricade.png"), 250, 250), 63, border=10,
                   tape_corner=(-7, 18, -14), tape_color=ORG), 865, 1212, 0.34),
        (with_plate(text_block(["FONTES: AGU · GOV.BR · BBC/FT · MJSP"], 30, GREY, "Oswald.ttf", 400), 18, 8),
         540, 1562, 0.46),
    ]))
    return P, B


try:
    PAPERS, BEATS = build()
except Exception as _e:   # importado como biblioteca
    PAPERS, BEATS = [], []
    print('collage: build() ignorado (%s)' % _e)
def render(t):
    beat = BEATS[-1]
    for b in BEATS:
        if b["t0"] <= t < b["t1"]:
            beat = b
            break
    comp = PAPERS[beat["p"]].copy()
    lt = t - beat["t0"]
    accent = beat.get("accent", YEL)

    if beat.get("burst"):
        cf = confetti(lt, int(beat["t0"] * 100) + 3, [accent, RED, MAG, CYA, WHT], n=30)
        if cf is not None:
            comp.alpha_composite(cf)

    for layer in beat["layers"]:
        im, x, y, pop = layer[0], layer[1], layer[2], layer[3]
        wob = layer[4] if len(layer) > 4 else 0.0
        if lt < pop:
            continue
        age = lt - pop
        if age < 0.13:
            s = 1.46 - 0.46 * ease(age / 0.13)
        else:
            k = age - 0.13
            s = 1.0 + 0.055 * math.sin(k * 44) * math.exp(-9 * k)
        im2 = im
        if wob:
            im2 = im2.rotate(wob * math.sin(age * 4.4), resample=Image.BILINEAR, expand=True)
        if abs(s - 1) > 0.003:
            im2 = im2.resize((max(1, int(im2.width * s)), max(1, int(im2.height * s))), Image.BILINEAR)
        comp.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))

    # câmera: push-in + punch + shake de impacto
    p = lt / max(1e-3, beat["t1"] - beat["t0"])
    z = 1.035 + beat.get("zoom", .10) * p
    for (tm, amt, dur) in beat.get("punches", []):
        k = lt - tm
        if 0 <= k < dur:
            z += amt * (1 - k / dur)
    sh = beat.get("shake", 10) * max(0.0, 1 - lt / 0.24) ** 2
    dx = (sh * math.sin(lt * 96)) / W
    dy = -(1 - 1 / z) * .46 + (sh * math.cos(lt * 71)) / H
    out = crop_zoom(comp, z, dx, dy)

    if lt < 0.09:  # página descendo
        off = int(-46 * (1 - ease(lt / 0.09)))
        canvas = Image.new("RGBA", (W, H), (22, 20, 18, 255))
        canvas.paste(out, (0, off))
        out = canvas

    if lt < 0.07:  # flash colorido + aberração cromática
        a = int(96 * (1 - lt / 0.07))
        out = Image.alpha_composite(out, Image.new("RGBA", (W, H), (255, 252, 244, a)))
        k = max(1, int(5 * (1 - lt / 0.07)))
        r, g, b = out.convert("RGB").split()
        r = ImageChops.offset(r, k, 0)
        b = ImageChops.offset(b, -k, 0)
        out = (Image.merge("RGB", (r, g, b)).crop((13, 13, W - 13, H - 13))
               .resize((W, H), Image.BILINEAR).convert("RGBA"))

    # ticker de notícia
    tick = ticker_strip(accent)
    period = tick.width
    x = -int((t * 235) % period)
    y = H - tick.height
    out.alpha_composite(tick, (x, y))
    out.alpha_composite(tick, (x + period, y))
    return out.convert("RGB")


if __name__ == "__main__":
    total = int(BEATS[-1]["t1"] * FPS)
    print("frames", total, flush=True)
    for i in range(total):
        render(i / FPS).save(f"{OUT}/f_{i:05d}.jpg", quality=91, subsampling=2)
        if i % 60 == 0:
            print(i, flush=True)
    print("done", flush=True)

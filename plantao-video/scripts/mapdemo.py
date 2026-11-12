#!/usr/bin/env python3
"""Demo 8s: mapa animado (map explainer) + colagem, sem página quadrada."""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import collage as C

W, H, FPS = 1080, 1920, 30
DUR = 8.0
OUT = f"{C.OUT}/map"
os.makedirs(OUT, exist_ok=True)

DARK = (11, 14, 12)
LAND = (33, 45, 38)
BORDER = (92, 114, 100)
HOT = (206, 16, 44)
YEL, RED, WHT, INK, PAPER = C.YEL, C.RED, C.WHT, C.INK, C.PAPER

# ---------------------------------------------------------------- geo
LON0, LON1, LAT0, LAT1 = -74.6, -32.6, 5.8, -34.6
KMID = math.cos(math.radians((LAT0 + LAT1) / 2))
MW = MH = 1600
_sx = (LON1 - LON0) * KMID
_sy = LAT0 - LAT1
_SC = min(MW / _sx, MH / _sy) * 0.94
_OX = (MW - _sx * _SC) / 2
_OY = (MH - _sy * _SC) / 2


def proj(lon, lat):
    return ((lon - LON0) * KMID * _SC + _OX, (LAT0 - lat) * _SC + _OY)


def load_geo():
    d = json.load(open(f"{C.ASSETS}/geo/br_states.geojson"))
    out = []
    for f in d["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = [[proj(p[0], p[1]) for p in poly[0]] for poly in polys]
        out.append((f["properties"]["sigla"], rings))
    return out


STATES = load_geo()
ORDER = sorted(range(len(STATES)), key=lambda i: -min(p[1] for r in STATES[i][1] for p in r))
DARK_UF = "RR"


def build_map():
    land = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    d = ImageDraw.Draw(land)
    for sig, rings in STATES:
        for r in rings:
            d.polygon(r, fill=LAND + (255,))
    bd = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    db = ImageDraw.Draw(bd)
    for sig, rings in STATES:
        for r in rings:
            db.line(r + [r[0]], fill=BORDER + (175,), width=3, joint="curve")
    masks = {}
    for sig, rings in STATES:
        m = Image.new("L", (MW, MH), 0)
        dm = ImageDraw.Draw(m)
        for r in rings:
            dm.polygon(r, fill=255)
        masks[sig] = np.array(m) > 120
    return land, bd, masks


LAND_IMG, BORDER_IMG, MASKS = build_map()

# ---------------------------------------------------------------- fundo
def make_bg():
    bg = Image.new("RGBA", (W, H), DARK + (255,))
    d = ImageDraw.Draw(bg)
    for x in range(-H, W + H, 96):
        d.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 7), width=2)
    arr = np.array(bg).astype(np.int16)
    arr[..., :3] += np.random.default_rng(4).normal(0, 3.5, (H, W, 1)).astype(np.int16)
    bg = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    vy = np.linspace(-1, 1, H)[:, None]
    vx = np.linspace(-1, 1, W)[None, :]
    v = np.clip(1 - 0.62 * (vx ** 2 + vy ** 2) ** 1.15, 0, 1)[..., None]
    a = np.array(bg).astype(np.float32)
    a[..., :3] *= v
    return Image.fromarray(a.astype("uint8"))


BG = make_bg()

# ---------------------------------------------------------------- cartão
CARD = (760, 950)
CARD_POS = (472, 1010)
ROT = -4.5


def torn_rect(w, h, seed=1, amp=13):
    rnd = random.Random(seed)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    pts = []
    step = 18
    for x in range(0, w, step):
        pts.append((x, rnd.uniform(0, amp)))
    for y in range(0, h, step):
        pts.append((w - rnd.uniform(0, amp), y))
    for x in range(w, 0, -step):
        pts.append((x, h - rnd.uniform(0, amp)))
    for y in range(h, 0, -step):
        pts.append((rnd.uniform(0, amp), y))
    d.polygon(pts, fill=255)
    return m


def map_frame(lit, zoom, cx, cy):
    cw = MW / zoom
    ch = cw * CARD[1] / CARD[0]
    x0 = min(max(cx - cw / 2, 0), MW - cw)
    y0 = min(max(cy - ch / 2, 0), MH - ch)
    img = LAND_IMG.copy()
    if lit:
        acc = np.zeros((MH, MW), dtype=np.float32)
        for sig, a in lit:
            if a > .01:
                acc += MASKS[sig] * a
        acc = np.clip(acc, 0, 1)
        red = np.zeros((MH, MW, 4), dtype=np.uint8)
        red[..., 0], red[..., 1], red[..., 2] = HOT
        red[..., 3] = (acc * 232).astype(np.uint8)
        glow = Image.fromarray((acc * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(16))
        gl = Image.new("RGBA", (MW, MH), HOT + (0,))
        gl.putalpha(glow.point(lambda v: int(v * .5)))
        img = Image.alpha_composite(img, Image.fromarray(red, "RGBA"))
        img = Image.alpha_composite(gl, img)
    img = Image.alpha_composite(img, BORDER_IMG)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize(CARD, Image.BILINEAR), (x0, y0, cw, ch)


def to_card(lon, lat, cam):
    x, y = proj(lon, lat)
    x0, y0, cw, ch = cam
    return ((x - x0) / cw * CARD[0], (y - y0) / ch * CARD[1])


CITIES = dict(RIO=(-43.2, -22.9), SP=(-46.6, -23.5), BH=(-43.9, -19.9), SAL=(-38.5, -12.97),
              REC=(-34.9, -8.05), BEL=(-48.5, -1.45), MAN=(-60.0, -3.1), CUI=(-56.1, -15.6),
              PVH=(-63.9, -8.76), FOR=(-38.5, -3.7))

_xs = [p[0] for _, rs in STATES for r in rs for p in r]
_ys = [p[1] for _, rs in STATES for r in rs for p in r]
BB = (min(_xs), min(_ys), max(_xs), max(_ys))


def view(box, margin=1.06):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    need_w = max((x1 - x0) * margin, (y1 - y0) * margin * CARD[0] / CARD[1])
    return cx, cy, MW / need_w


FULL = view(BB)
SE = view((proj(-49.6, 0)[0], proj(0, -16.2)[1], proj(-39.4, 0)[0], proj(0, -25.8)[1]))
SHOTS = [
    dict(t0=0.0, t1=2.70, z0=FULL[2], z1=FULL[2] * 1.16, c0=(FULL[0], FULL[1]), c1=(FULL[0], FULL[1])),
    dict(t0=2.70, t1=5.40, z0=SE[2] * .92, z1=SE[2] * 1.22, c0=(SE[0], SE[1]), c1=(SE[0] + 10, SE[1] + 30)),
    dict(t0=5.40, t1=8.00, z0=SE[2] * 1.22, z1=FULL[2] * 1.04, c0=(SE[0] + 10, SE[1] + 30), c1=(FULL[0], FULL[1])),
]
CUTS = [0.0, 2.70, 5.40]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lit_at(t):
    lit = []
    for k, i in enumerate(ORDER):
        sig = STATES[i][0]
        if sig == DARK_UF:
            continue
        t_on = 0.42 + 0.052 * k
        if t > t_on:
            lit.append((sig, min(1.0, (t - t_on) / 0.16)))
    return lit


def pin(size=44, col=RED):
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([s * .5 - size * .40, s * .5 - size * .40, s * .5 + size * .40, s * .5 + size * .40],
              fill=col + (255,), outline=WHT + (250,), width=max(4, size // 7))
    d.ellipse([s * .5 - size * .12, s * .5 - size * .12, s * .5 + size * .12, s * .5 + size * .12],
              fill=WHT + (255,))
    return im


def ring(r, alpha, col=RED, wid=6):
    s = int(r * 2 + 10)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([5, 5, s - 6, s - 6], outline=col + (int(alpha),), width=wid)
    return im


PINS = [(3.00, "RIO", "RIO"), (3.34, "SP", "SÃO PAULO"), (3.66, "BH", "MINAS")]


def build(t):
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break
    p = (t - shot["t0"]) / max(1e-3, shot["t1"] - shot["t0"])
    e = ease(p)
    zoom = shot["z0"] + (shot["z1"] - shot["z0"]) * e
    cx = shot["c0"][0] + (shot["c1"][0] - shot["c0"][0]) * e
    cy = shot["c0"][1] + (shot["c1"][1] - shot["c0"][1]) * e

    frame = BG.copy()
    mimg, cam = map_frame(lit_at(t), zoom, cx, cy)

    # cartão: moldura de papel + borda rasgada + rotação
    mat = 16
    card = Image.new("RGBA", (CARD[0] + mat * 2, CARD[1] + mat * 2), PAPER + (255,))
    card.alpha_composite(mimg, (mat, mat))
    card.putalpha(torn_rect(card.width, card.height, 9, 12))
    card = card.rotate(ROT, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 210), (0, 0), card.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    ox, oy = CARD_POS[0] - card.width // 2, CARD_POS[1] - card.height // 2
    frame.alpha_composite(sh, (ox + 10, oy + 20))
    frame.alpha_composite(card, (ox, oy))

    # fitas
    tp = C.tape_strip(int(card.width * .30), 46, -7, YEL, 210)
    frame.alpha_composite(tp, (ox + 10, oy - 14))
    tp2 = C.tape_strip(int(card.width * .26), 44, 6, RED, 200)
    frame.alpha_composite(tp2, (ox + card.width - tp2.width - 30, oy + card.height - 40))

    # coordenadas cartão -> frame
    ang = math.radians(ROT)
    cw2, ch2 = card.width / 2, card.height / 2

    def c2f(px, py):
        px += mat
        py += mat
        dx, dy = px - cw2, py - ch2
        return (ox + dx * math.cos(ang) - dy * math.sin(ang) + cw2,
                oy + dx * math.sin(ang) + dy * math.cos(ang) + ch2)

    # pontinhos nas capitais (cena 1)
    if t < 2.7:
        for k, (nm, ll) in enumerate(CITIES.items()):
            t_on = 1.2 + 0.12 * k
            if t < t_on:
                continue
            a = min(1.0, (t - t_on) / 0.2)
            fx, fy = c2f(*to_card(ll[0], ll[1], cam))
            rr = ring(8 + 26 * (1 - a) + 6, 120 * a, WHT, 4)
            frame.alpha_composite(rr, (int(fx - rr.width / 2), int(fy - rr.height / 2)))

    # pinos (cena 2)
    for (tp_, nm, label) in PINS:
        if t < tp_ or t > 5.5:
            continue
        age = t - tp_
        px, py = to_card(*CITIES[nm], cam)
        fx, fy = c2f(px, py)
        drop = 1 - ease(min(1, age / 0.2))
        fy -= 190 * drop
        rr = ring(30 + 110 * min(1, age / .85), max(0, 200 * (1 - age / .85)))
        frame.alpha_composite(rr, (int(fx - rr.width / 2), int(fy - rr.height / 2)))
        pm = pin(24)
        sc = 1.0 + 0.6 * drop
        pm = pm.resize((int(pm.width * sc), int(pm.height * sc)), Image.BILINEAR)
        frame.alpha_composite(pm, (int(fx - pm.width / 2), int(fy - pm.height / 2)))
        if age > .16:
            lab = C.with_plate(C.text_block([label], 28, INK, "Oswald.ttf", 600), 12, 5, color=PAPER)
            lab = lab.rotate(-5, expand=True, resample=Image.BICUBIC)
            frame.alpha_composite(lab, (int(fx + 14), int(fy - lab.height + 6)))

    # anotação de caneta apontando o Rio
    if 4.2 < t < 5.45:
        px, py = to_card(*CITIES["RIO"], cam)
        fx, fy = c2f(px, py)
        a = ease(min(1, (t - 4.2) / 0.3))
        circ = C.marker_circle(int(70 * a), int(70 * a), RED, 7, -6)
        frame.alpha_composite(circ, (int(fx - circ.width / 2), int(fy - circ.height / 2)))
        ar = C.marker_arrow(120, 62, RED, -18)
        frame.alpha_composite(ar, (int(fx + 60), int(fy - 120)))

    # ---------------- títulos
    if t < 5.4:
        strip = C.with_plate(C.text_block(["ONDE ELES", "ESTÃO"], 70, INK, leading=1.0), 24, 14, color=PAPER)
        strip = strip.rotate(-3.0, expand=True, resample=Image.BICUBIC)
        k = ease(min(1, t / 0.45))
        frame.alpha_composite(strip, (int(-14 + 18 * k), int(240 - strip.height / 2 + 24 * (1 - k))))
        n = sum(1 for s, a in lit_at(t) if a > .5)
        cnt = C.with_plate(C.text_block([f"{n:02d}/27"], 88, WHT, "Anton.ttf"), 20, 10, color=RED)
        cnt = cnt.rotate(5, expand=True, resample=Image.BICUBIC)
        frame.alpha_composite(cnt, (int(W - cnt.width - 26), 262))
        cap = C.with_plate(C.text_block(["estados com CV"], 22, INK, "Oswald.ttf", 400), 12, 5)
        frame.alpha_composite(cap, (int(W - cap.width - 20), 262 + cnt.height - 10))
    else:
        a = ease(min(1, (t - 5.4) / .3))
        big = C.with_plate(C.text_block(["O CV TÁ EM", "26 DE 27", "ESTADOS"], 86, INK, leading=.94), 24, 14, color=YEL)
        big = big.rotate(-2.5, expand=True, resample=Image.BICUBIC)
        sc = .84 + .16 * a
        big = big.resize((int(big.width * sc), int(big.height * sc)), Image.BILINEAR)
        frame.alpha_composite(big, (int(-30 + 20 * a), int(150 - 30 * (1 - a))))
        cap = C.with_plate(C.text_block(["mapa ilustrativo · fonte: relatórios de inteligência"], 20, INK,
                                        "Oswald.ttf", 400), 12, 5)
        frame.alpha_composite(cap, (int(60), H - 190))

    # ---------------- ticker
    tick = C.ticker_strip(YEL)
    x = -int((t * 235) % tick.width)
    frame.alpha_composite(tick, (x, H - tick.height))
    frame.alpha_composite(tick, (x + tick.width, H - tick.height))

    # grão + flash
    arr = np.array(frame).astype(np.int16)
    arr[..., :3] += np.random.default_rng(int(t * 997) % 9999).normal(0, 3.0, (H, W, 1)).astype(np.int16)
    frame = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    for c in CUTS:
        k = t - c
        if 0 <= k < .07:
            al = int(72 * (1 - k / .07))
            frame = Image.alpha_composite(frame, Image.new("RGBA", (W, H), (255, 252, 244, al)))
            off = max(1, int(6 * (1 - k / .07)))
            r, g, b = frame.convert("RGB").split()
            frame = Image.merge("RGB", (ImageChops.offset(r, off, 0), g, ImageChops.offset(b, -off, 0)))
            frame = frame.crop((12, 12, W - 12, H - 12)).resize((W, H)).convert("RGBA")
    return frame.convert("RGB")


if __name__ == "__main__":
    total = int(DUR * FPS)
    print("frames", total, flush=True)
    for i in range(total):
        build(i / FPS).save(f"{OUT}/f_{i:05d}.jpg", quality=91, subsampling=2)
        if i % 40 == 0:
            print(i, flush=True)
    print("done", flush=True)

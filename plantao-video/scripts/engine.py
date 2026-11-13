#!/usr/bin/env python3
"""Motor de render da série: colagem de jornal + mapa animado, 1080x1920.

O conteúdo de cada episódio vive num módulo separado (conteudo_*.py) que expõe:
    ACCENT[i]        cor do ticker por bloco
    MAP_BLOCKS[i]    função (frame, lt) -> frame  para blocos de mapa
    layers(i)        lista de cartelas/fotos que entram no bloco de papel
    base(i)          imagem de fundo do bloco de papel
    TAG              texto do selo nos blocos de mapa
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import collage as C          # noqa: E402
import mapdemo as M          # noqa: E402

W, H, FPS = 1080, 1920, 30
WORK = C.WORK
OUT = os.environ.get("PLANTAO_OUT") or os.path.join(WORK, "frames_out")
os.makedirs(OUT, exist_ok=True)

BEATS_PATH = os.environ.get("PLANTAO_BEATS") or os.path.join(os.getcwd(), "beats.json")
if not os.path.exists(BEATS_PATH):
    raise SystemExit(f"beats.json não encontrado em {BEATS_PATH}: rode edit_vo.py primeiro")
_B = json.load(open(BEATS_PATH))
CUTS = _B["cuts"]
DUR = _B["dur"]
T0 = CUTS
T1 = CUTS[1:] + [DUR]

PAPER, INK, RED, YEL, BLUE, MAG, CYA, ORG, LIM, WHT, GREY = (
    C.PAPER, C.INK, C.RED, C.YEL, C.BLUE, C.MAG, C.CYA, C.ORG, C.LIM, C.WHT, C.GREY)

MOD = None


def load(path):
    """Carrega o módulo de conteúdo do episódio."""
    global MOD
    if not os.path.exists(path):
        raise SystemExit(f"conteúdo não encontrado: {path}")
    spec = importlib.util.spec_from_file_location("conteudo", path)
    MOD = importlib.util.module_from_spec(spec)
    sys.modules["conteudo"] = MOD
    spec.loader.exec_module(MOD)
    return MOD


# ------------------------------------------------------------------ tipografia
def TB(lines, size, color=INK, font="Playfair.ttf", weight=900, lead=1.0, maxw=900):
    """Bloco de texto que encolhe sozinho para caber em maxw. lead>=1.0 (senão corta o til)."""
    return C.text_block(lines, size, color, font, weight, leading=lead, maxw=maxw)


def PL(im, padx=30, pady=22, color=PAPER, border=True):
    """Cartela de papel colada: sombra + borda de 3px."""
    out = C.with_plate(im, padx, pady, color=color)
    if border:
        d = ImageDraw.Draw(out)
        d.rectangle([13, 13, 13 + im.width + padx * 2 - 1, 13 + im.height + pady * 2 - 1],
                    outline=(26, 22, 18, 190), width=3)
    return out


def st(im, ang=0.0):
    return C.tilt(im, ang)


_P = {}


def paper(seed):
    if seed not in _P:
        _P[seed] = C.make_paper(seed).convert("RGBA")
    return _P[seed].copy()


def photo(path, w, h, color=True, bright=1.0):
    """Foto com meio-tom de jornal."""
    return C.print_photo(C.load(path), w, h, color=color, bright=bright)


def cut(im, seed=1, torn=("bottom",), tape=None):
    """Recorte com borda rasgada e sombra (a foto colada na página)."""
    return C.paper_cut(im, seed, 13, torn, 24, tape)


def xmark(size, color=RED, wdt=13, ang=0):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([size * .13, size * .13, size * .87, size * .87], fill=color + (238,), width=wdt)
    d.line([size * .87, size * .13, size * .13, size * .87], fill=color + (238,), width=wdt)
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def L(im, x, y, pop, wob=0.0, s=1.0):
    """Camada: imagem, centro (x,y), instante em que entra (pop), balanço, escala."""
    return dict(im=im, x=x, y=y, pop=pop, wob=wob, s=s)


# ------------------------------------------------------------------ mapa
class MapCard:
    """Moldura de papel rasgada e torta em volta do mapa. Sombra/fitas estáticas."""

    def __init__(self, w, h, rot, pos, seed=9, tape=True):
        self.mat = 14
        self.w, self.ch0 = w, h
        cw, ch = w + self.mat * 2, h + self.mat * 2
        self.core_w, self.core_h = cw, ch
        self.rot, self.pos = rot, pos
        self.mask = M.torn_rect(cw, ch, seed, 12)
        rs = Image.new("L", (cw, ch)).rotate(rot, expand=True).size
        self.pad = 44
        self.canvas = (rs[0] + self.pad * 2, rs[1] + self.pad * 2)
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 200), (0, 0), self.mask)
        sh = sh.filter(ImageFilter.GaussianBlur(16)).rotate(rot, expand=True, resample=Image.BICUBIC)
        self.shadow = Image.new("RGBA", self.canvas, (0, 0, 0, 0))
        self.shadow.alpha_composite(sh, (self.pad + 3, self.pad + 14))
        self.tapes = []
        if tape:
            self.tapes.append((C.tape_strip(int(cw * .28), 44, -7, YEL, 215), -cw * .34, -ch * .465))
            self.tapes.append((C.tape_strip(int(cw * .22), 42, 6, RED, 200), cw * .33, ch * .455))

    def draw(self, frame, mimg):
        core = mimg.resize((self.w, self.ch0), Image.BILINEAR)
        card = Image.new("RGBA", (self.core_w, self.core_h), PAPER + (255,))
        card.alpha_composite(core, (self.mat, self.mat))
        card.putalpha(self.mask)
        card = card.rotate(self.rot, expand=True, resample=Image.BICUBIC)
        out = self.shadow.copy()
        out.alpha_composite(card, (self.pad, self.pad))
        px, py = self.pos
        frame.alpha_composite(out, (int(px - out.width / 2), int(py - out.height / 2)))
        a = math.radians(self.rot)
        for tp, dx, dy in self.tapes:
            rx = dx * math.cos(a) - dy * math.sin(a) + px
            ry = dx * math.sin(a) + dy * math.cos(a) + py
            frame.alpha_composite(tp, (int(rx - tp.width / 2), int(ry - tp.height / 2)))
        return card

    def c2f(self, mx, my, cam):
        """Coordenada do mapa -> coordenada do frame (para pinos, X, setas)."""
        px = (mx - cam[0]) / cam[2] * (self.core_w - self.mat * 2) + self.mat
        py = (my - cam[1]) / cam[3] * (self.core_h - self.mat * 2) + self.mat
        dx, dy = px - self.core_w / 2, py - self.core_h / 2
        a = math.radians(self.rot)
        return (self.pos[0] + dx * math.cos(a) - dy * math.sin(a),
                self.pos[1] + dx * math.sin(a) + dy * math.cos(a))


def lit_seq(lt, t0=0.22, step=0.10, fade=0.15, alpha=1.0):
    """Estados acendendo em sequência (norte -> sul)."""
    out = []
    for k, i in enumerate(M.ORDER):
        sig = M.STATES[i][0]
        if sig == M.DARK_UF:
            continue
        on = t0 + step * k
        if lt > on:
            out.append((sig, alpha * min(1.0, (lt - on) / fade)))
    return out


def lit_static(sigs, lt, fade=0.4, alpha=1.0):
    return [(s, alpha * min(1.0, max(0.0, lt / fade))) for s in sigs]


# ------------------------------------------------------------------ render
def beat_at(t):
    for i in range(len(T0)):
        if T0[i] <= t < T1[i]:
            return i
    return len(T0) - 1


_CAP = {}


def _cap(i, n, words):
    key = (i, n)
    if key not in _CAP:
        _CAP[key] = PL(TB([" ".join(words[:n])], 44, WHT, "Oswald.ttf", 700, maxw=930), 22, 12, INK)
    return _CAP[key]


def render(t):
    i = beat_at(t)
    lt = t - T0[i]
    dur = T1[i] - T0[i]
    p = lt / max(1e-3, dur)
    accent = MOD.ACCENT.get(i, YEL)

    if i in MOD.MAP_BLOCKS:
        frame = M.BG.copy()
        frame = MOD.MAP_BLOCKS[i](frame, lt)
        z = 1.02 + .055 * p + .005 * math.sin(t * 1.9)
        sh = 13 * max(0.0, 1 - lt / .26) ** 2
        dx = (sh * math.sin(lt * 90)) / W
        dy = (sh * math.cos(lt * 67)) / H
        out = C.crop_zoom(frame, z, dx, dy)
    else:
        comp = MOD.base(i)
        ref = getattr(MOD, "REF", {}).get(i)
        kr = (dur / ref) if ref else 1.0        # pops foram escritos p/ outra duração
        lt_c = lt / kr
        z = 1.035 + .085 * p + .006 * math.sin(t * 2.1)
        for l in MOD.layers(i):
            if lt_c < l["pop"]:
                continue
            age = lt - l["pop"] * kr
            if age < .13:
                s = 1.42 - .42 * C.ease(age / .13)
            else:
                k = age - .13
                s = 1.0 + .05 * math.sin(k * 46) * math.exp(-9 * k)
            im2 = l["im"]
            if l["wob"]:
                im2 = im2.rotate(l["wob"] * math.sin(age * 4.2), resample=Image.BILINEAR,
                                 expand=True)
            s *= l.get("s", 1.0)
            if abs(s - 1) > .004:
                im2 = im2.resize((max(1, int(im2.width * s)), max(1, int(im2.height * s))),
                                 Image.BILINEAR)
            comp.alpha_composite(im2, (int(l["x"] - im2.width / 2), int(l["y"] - im2.height / 2)))
            if age < .17:                      # soco de câmera em cada elemento que entra
                z += .032 * (1 - age / .17)
        pf = getattr(MOD, "PER_FRAME", {}).get(i)
        if pf:
            pf(comp, lt_c)
        sh = 15 * max(0.0, 1 - lt / .24) ** 2
        dx = (sh * math.sin(lt * 96)) / W
        dy = -(1 - 1 / z) * .46 + (sh * math.cos(lt * 71)) / H
        out = C.crop_zoom(comp, z, dx, dy)

    # flash + aberração cromática no corte
    for c in CUTS:
        k = t - c
        if 0 <= k < .09:
            al = int(96 * (1 - k / .09))
            out = Image.alpha_composite(out, Image.new("RGBA", (W, H), (255, 252, 244, al)))
            off = max(1, int(7 * (1 - k / .07)))
            r, g, b = out.convert("RGB").split()
            out = Image.merge("RGB", (ImageChops.offset(r, off, 0), g, ImageChops.offset(b, -off, 0)))
            out = out.crop((14, 14, W - 14, H - 14)).resize((W, H), Image.BILINEAR).convert("RGBA")

    # grão de filme
    arr = np.array(out).astype(np.int16)
    arr[..., :3] += np.random.default_rng(int(t * 997) % 9999).normal(
        0, 3.0, (H, W, 1)).astype(np.int16)
    out = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))

    # ticker
    tick = C.ticker_strip(accent)
    x = -int((t * 235) % tick.width)
    out.alpha_composite(tick, (x, H - tick.height))
    out.alpha_composite(tick, (x + tick.width, H - tick.height))

    if i in MOD.MAP_BLOCKS:                # marca da série nos blocos de mapa
        tag = PL(TB([MOD.TAG], 24, WHT, "Oswald.ttf", 600), 12, 6, INK)
        out.alpha_composite(tag, (26, 40))
    return out.convert("RGB")

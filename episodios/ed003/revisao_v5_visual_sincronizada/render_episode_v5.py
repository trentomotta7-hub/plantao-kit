#!/usr/bin/env python3
"""MAPA SUJO — edição 003, revisão V5 fotográfica e sincronizada.

O storyboard usa palavras/timecodes de beats.json; fotos entram 100 ms antes do
nome pronunciado. Mantém papel, recortes, carimbos e ticker da série, com layout
mais limpo e fotográfico. Não usa mapa nesta edição porque nenhuma localidade é
nomeada na locução.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path
import unicodedata

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
ED003 = HERE.parent
V32 = ED003 / "revisao_v3_cortes_visuais"
PLANTAO = HERE.parents[2]
FRAME_DIR = HERE / "work" / "frames_v5"
SMOKE_DIR = HERE / "work" / "smoke_v5"
OUTDIR = HERE / "out"
OUT = OUTDIR / "ed003_v5_sincronizada.mp4"
CONTACT = OUTDIR / "check" / "contact_storyboard_v5.jpg"
PLAN_FILE = HERE / "storyboard_v5.json"
BEATS_FILE = V32 / "beats.json"
FPS, W, H = 30, 1080, 1920
LEAD_S = 0.10
ENTRY_S = 0.10

# Inicializar o kit original e reaproveitar textura, fonte, recortes e ticker.
os.environ["PLANTAO_WORK"] = str(V32 / "work")
os.environ["PLANTAO_OUT"] = str(V32 / "work" / "frames_out")
os.environ["PLANTAO_BEATS"] = str(BEATS_FILE)
os.environ["PLANTAO_EDICAO"] = "3"
os.environ["PLANTAO_NOME"] = "MAPA SUJO"
os.environ["PLANTAO_DATA"] = "CONTEXTO E INFERÊNCIA"
os.environ["PLANTAO_TICKER"] = (
    "CASO BANCO MASTER  •  MENSAGEM ATRIBUÍDA  •  RELATÓRIOS EM REVISÃO  •  "
    "PARECER DA PGR NÃO É DECISÃO DO STF  •  "
)
sys.path.insert(0, str(V32))
sys.path.insert(0, str(PLANTAO / "plantao-video" / "scripts"))
import engine_ritmo as E  # noqa: E402
import collage as C  # noqa: E402

PLAN = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
AUDIO = json.loads(BEATS_FILE.read_text(encoding="utf-8"))
BEATS = PLAN["beats"]
DURATION = float(PLAN["duration_s"])
CUTS = [float(x) for x in AUDIO["cuts"]]
SPEECH_STARTS = [float(x) for x in AUDIO["starts"]]

PAPER = tuple(C.PAPER)
INK = tuple(C.INK)
RED = tuple(C.RED)
YELLOW = tuple(C.YEL)
WHITE = tuple(C.WHT)
NAVY = (18, 26, 34)
PALE = (248, 244, 232)

PHOTO_FILES = {
    "daniel": V32 / "assets" / "photos" / "daniel_vorcaro_claudio_gatti.webp",
    "moraes": V32 / "assets" / "photos" / "alexandre_moraes_victor_piemonte_stf.jpg",
    "gonet": V32 / "assets" / "photos" / "paulo_gonet_agencia_senado.jpg",
}
PHOTO_LABELS = {
    "daniel": ("DANIEL VORCARO", "Arquivo · Claudio Gatti/Divulgação"),
    "moraes": ("ALEXANDRE DE MORAES", "Victor Piemonte/STF · domínio público"),
    "gonet": ("PAULO GONET", "Agência Senado"),
}

SOURCE_BY_BEAT = {
    1: "UOL · reportagem de 13/11/2026",
    2: "UOL · reportagem de 13/11/2026",
    3: "UOL · trecho citado pela reportagem",
    4: "UOL · reportagem de 13/11/2026",
    5: "UOL · contexto reportado",
    6: "UOL · reportagem de 13/11/2026",
    7: "UOL · reportagem sobre revisão dos relatórios",
    8: "UOL · reportagem de 13/11/2026",
    9: "Agência Brasil · 11/11/2026",
    10: "Fontes: UOL · Agência Brasil",
}

TEXT_OVERRIDES = {
    (1, "mensagem"): "MENSAGEM",
    (1, "atribuida"): "MENSAGEM ATRIBUÍDA",
    (1, "isso"): "ISSO PROVA?",
    (1, "nao"): "NÃO PROVA",
    (2, "segundo"): "SEGUNDO O UOL",
    (2, "fevereiro"): "FEVEREIRO DE 2024",
    (2, "previsao"): "PREVISÃO REPORTADA",
    (2, "exsocio"): "A UM EX-SÓCIO",
    (3, "cita"): "TRECHO CITADO",
    (3, "kassio"): "CITAÇÃO REPORTADA",
    (3, "vai"): "CONTINUA A CITAÇÃO",
    (4, "master"): "BANCO MASTER",
    (4, "credor"): "CREDOR DA MANTENEDORA",
    (4, "ulbra"): "ULBRA · MANTENEDORA",
    (4, "maio"): "MAIO · 2024",
    (4, "pedidos"): "REGRA DE TRANSIÇÃO",
    (5, "interesse"): "INTERESSE ECONÔMICO",
    (5, "prova"): "NÃO PROVA",
    (6, "outro"): "OUTRO LIMITE",
    (6, "uol"): "SEGUNDO O UOL",
    (6, "recuperou"): "MENSAGENS NÃO RECUPERADAS",
    (6, "imagens"): "IMAGENS DE TEXTOS",
    (7, "cupula"): "CÚPULA DA PF",
    (7, "refazer"): "RELATÓRIOS EM REVISÃO",
    (7, "excesso"): "EXCESSO DE ESCOPO",
    (7, "isso"): "NÃO CONFIRMA · NEM AFASTA",
    (8, "pf"): "SEM RESPOSTA DA PF",
    (8, "13"): "ATÉ 13 DE NOVEMBRO",
    (8, "fabio"): "FÁBIO FARIA · SEM RELAÇÃO COM O TEMA",
    (9, "separadamente"): "SEPARADAMENTE",
    (9, "parecer"): "PARECER DA PGR  ≠  DECISÃO DO STF",
    (9, "supremo"): "A DECISÃO CABE AO SUPREMO",
    (10, "mensagem"): "MENSAGEM RELATADA",
    (10, "relatorio"): "RELATÓRIO EM REVISÃO",
    (10, "duvidas"): "DÚVIDAS EM ABERTO",
    (10, "nova"): "O QUE PRECISA ESCLARECER?",
}


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return "".join(ch for ch in text.casefold() if ch.isalnum())


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


@lru_cache(maxsize=64)
def font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    return C.fnt(name, size, weight)


def wrap_lines(text: str, fnt: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 3) -> list[str]:
    words = str(text).replace("\n", " ").split()
    draw = ImageDraw.Draw(Image.new("L", (2, 2)))
    lines: list[str] = []
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if line and draw.textlength(trial, font=fnt) > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        # Preserve content but reduce font size at caller when possible; this
        # fallback keeps complete labels instead of silently dropping words.
        mid = (len(lines) + 1) // 2
        lines = [" ".join(lines[:mid]), " ".join(lines[mid:])]
    return lines


def center_layer(canvas: Image.Image, layer: Image.Image, x: float, y: float,
                 scale: float = 1.0, angle: float = 0.0, opacity: float = 1.0) -> None:
    w = max(1, round(layer.width * scale))
    h = max(1, round(layer.height * scale))
    im = layer.resize((w, h), Image.Resampling.LANCZOS)
    if abs(angle) > 0.05:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if opacity < 0.999:
        im.putalpha(im.getchannel("A").point(lambda a: round(a * clamp(opacity))))
    canvas.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))


def build_background(beat_index: int) -> Image.Image:
    # Mesmo papel de jornal do kit original, mas com cabeçalho/footer próprios.
    base = E.paper(181 + beat_index * 13).convert("RGBA")
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rectangle((0, 282, W, 1710), fill=PAPER + (218,))
    base.alpha_composite(veil)
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 280), fill=PAPER + (255,))
    d.rectangle((0, 1710, W, H), fill=PAPER + (255,))
    # Wordmark em destaque, sem localização geográfica fixa no masthead.
    mast = font("Playfair.ttf", 158, 900)
    mast_w = d.textlength("MAPA SUJO", font=mast)
    if mast_w > W - 70:
        mast = font("Playfair.ttf", int(158 * (W - 70) / mast_w), 900)
    d.text((W / 2, 10), "MAPA SUJO", font=mast, fill=INK, anchor="mt")
    sub = "EDIÇÃO 003  ·  CONTEXTO E INFERÊNCIA"
    sf = font("Oswald.ttf", 24, 500)
    d.text((W / 2, 166), sub, font=sf, fill=(86, 80, 72), anchor="mt")
    d.rectangle((56, 205, W - 56, 211), fill=RED + (255,))
    d.rectangle((56, 218, W - 56, 221), fill=INK + (180,))
    # Filete editorial discreto: papel + acento, sem colagem excessiva.
    d.rectangle((56, 1710, W - 56, 1713), fill=INK + (120,))
    return base


def find_person(event: dict, beat_number: int) -> str | None:
    trigger = norm(event.get("trigger_word", ""))
    source = norm(event.get("asset_or_source", ""))
    if "paulogonet" in source or trigger == "paulo":
        return "gonet"
    if "alexandremoraes" in source or trigger == "moraes":
        return "moraes"
    if "danielvorcaro" in source or trigger in {"daniel", "vorcaro"}:
        return "daniel"
    return None


def make_photo_panel(person: str, seed: int) -> Image.Image:
    path = PHOTO_FILES[person]
    raw = C.load(str(path))
    if person == "daniel":
        photo_w, photo_h = 930, 590
    else:
        photo_w, photo_h = 790, 850
    # Reproduce o meio-tom colorido do jornal, sem alterar a identidade/expressão.
    photo = C.print_photo(raw, photo_w, photo_h, color=True, bright=1.01)
    card_w = photo_w + 44
    name, credit = PHOTO_LABELS[person]
    bar_h, credit_h, top = 78, 56, 20
    card_h = photo_h + top + bar_h + credit_h + 34
    card = Image.new("RGB", (card_w, card_h), PALE)
    card.paste(photo, (22, top))
    d = ImageDraw.Draw(card)
    ybar = top + photo_h + 12
    d.rectangle((22, ybar, card_w - 22, ybar + bar_h), fill=NAVY)
    f = font("Oswald.ttf", 40 if person != "moraes" else 36, 700)
    while d.textlength(name, font=f) > card_w - 72:
        f = font("Oswald.ttf", f.size - 2, 700)
    d.text((card_w / 2, ybar + bar_h / 2 + 1), name, font=f, fill=WHITE, anchor="mm")
    cf = font("Oswald.ttf", 22, 500)
    d.text((card_w / 2, ybar + bar_h + 29), credit, font=cf, fill=(47, 48, 45), anchor="mm")
    # Borda clara + sombra/torn edge, numa rotação quase imperceptível.
    return C.paper_cut(card, seed=seed, border=13, torn=("bottom",), shadow=20,
                       tape_corner=None)


def accent_for(beat_number: int, event_number: int) -> tuple[int, int, int]:
    palette = [YELLOW, RED, (0, 112, 158), (42, 53, 65), (218, 224, 218)]
    return palette[(beat_number * 2 + event_number) % len(palette)]


def card_label(event: dict, beat_number: int) -> str:
    key = (beat_number, norm(event.get("trigger_word", "")))
    if key in TEXT_OVERRIDES:
        return TEXT_OVERRIDES[key]
    text = event.get("on_screen_text", "")
    text = text.split("\n")[0]
    text = text.replace("Aos ", "").strip()
    if len(text) > 70:
        text = text[:67].rsplit(" ", 1)[0] + "…"
    return text or event.get("trigger_word", "").upper()


def make_general_card(event: dict, beat_number: int, event_number: int) -> Image.Image:
    title = card_label(event, beat_number)
    accent = accent_for(beat_number, event_number)
    if (beat_number, norm(event.get("trigger_word", ""))) == (4, "credor"):
        return make_relation_card(accent)
    if (beat_number, norm(event.get("trigger_word", ""))) == (4, "maio"):
        return make_timeline_card(accent)
    if (beat_number, norm(event.get("trigger_word", ""))) == (9, "parecer"):
        return make_verdict_card(accent)

    is_stamp = title in {"NÃO PROVA", "MENSAGEM ATRIBUÍDA", "RELATÓRIOS EM REVISÃO"}
    if is_stamp:
        ink = RED if title in {"NÃO PROVA", "RELATÓRIOS EM REVISÃO"} else INK
        stamp = C.stamp(title, 82 if len(title) < 18 else 62, ink, -5, 235)
        canvas = Image.new("RGBA", (1000, 410), (0, 0, 0, 0))
        center_layer(canvas, stamp, 500, 205, 1.0)
        return canvas

    plate = PALE if accent in {RED, (42, 53, 65)} else accent
    fg = WHITE if plate in {RED, (42, 53, 65)} else INK
    size = 120 if len(title) < 18 else 96
    f = font("Anton.ttf", size, 800)
    lines = wrap_lines(title, f, 850, 3)
    # Avoid overflowing long labels: shrink only as much as needed.
    while max(ImageDraw.Draw(Image.new("L", (2, 2))).textlength(line, font=f) for line in lines) > 850 and f.size > 54:
        f = font("Anton.ttf", f.size - 4, 800)
    text = C.text_block(lines, f.size, fg, "Anton.ttf", 800, leading=0.98, maxw=860)
    card_w = 960
    card_h = max(250, text.height + 112)
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((18, 20, card_w - 12, card_h - 8), radius=18,
                                               fill=(0, 0, 0, 72))
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((10, 10, card_w - 10, card_h - 15), radius=18,
                        fill=plate + (255,), outline=INK + (220,), width=3)
    d.rectangle((28, 34, 42, card_h - 38), fill=accent + (255,))
    card.alpha_composite(text, ((card_w - text.width) // 2, 28))
    small = font("Oswald.ttf", 22, 600)
    label = "TRECHO REPORTADO" if beat_number in {1, 2, 3, 4, 6, 7, 8} else "CONTEXTO · EDIÇÃO 003"
    if beat_number == 9:
        label = "PGR / STF · DISTINÇÃO INSTITUCIONAL"
    sw = d.textlength(label, font=small)
    d.text(((card_w - sw) / 2, card_h - 47), label, font=small, fill=INK + (230,))
    # Acento retangular curto, sem rabisco ou seta ornamental.
    d.rectangle((card_w - 155, 22, card_w - 35, 29), fill=accent + (255,))
    return card


def make_relation_card(accent: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGBA", (1000, 510), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((28, 35, 972, 475), radius=20, fill=PALE + (255,), outline=INK + (220,), width=4)
    # Relação financeira explícita no texto: sem seta causal ou ligação a pessoas.
    d.rectangle((90, 160, 430, 370), fill=YELLOW + (255,), outline=INK + (220,), width=3)
    d.rectangle((570, 160, 910, 370), fill=(238, 235, 222, 255), outline=INK + (220,), width=3)
    f1, f2, fm = font("Anton.ttf", 42, 800), font("Anton.ttf", 38, 800), font("Oswald.ttf", 28, 700)
    d.text((260, 265), "BANCO MASTER", font=f1, fill=INK, anchor="mm")
    d.text((740, 265), "MANTENEDORA\nDA ULBRA", font=f2, fill=INK, anchor="mm", align="center", spacing=6)
    d.line((430, 265, 570, 265), fill=accent + (255,), width=8)
    d.text((500, 215), "CREDOR DE", font=fm, fill=INK, anchor="mm")
    d.text((500, 435), "RELAÇÃO REPORTADA · UOL", font=font("Oswald.ttf", 24, 500), fill=INK, anchor="mm")
    return canvas


def make_timeline_card(accent: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGBA", (960, 390), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((22, 24, 938, 366), radius=18, fill=PALE + (255,), outline=INK + (220,), width=4)
    d.text((480, 155), "MAIO", font=font("Anton.ttf", 132, 800), fill=INK, anchor="mm")
    d.line((245, 255, 715, 255), fill=accent + (255,), width=7)
    d.ellipse((465, 243, 495, 273), fill=accent + (255,), outline=INK + (255,), width=2)
    d.text((480, 315), "2024  ·  REFERÊNCIA TEMPORAL", font=font("Oswald.ttf", 28, 700), fill=INK, anchor="mm")
    return canvas


def make_verdict_card(accent: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGBA", (1000, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((22, 25, 978, 495), radius=18, fill=PALE + (255,), outline=INK + (220,), width=4)
    d.rectangle((70, 110, 450, 385), fill=YELLOW + (255,))
    d.rectangle((550, 110, 930, 385), fill=(230, 232, 229, 255))
    d.text((260, 246), "PARECER\nDA PGR", font=font("Anton.ttf", 62, 800), fill=INK, anchor="mm", align="center")
    d.text((740, 246), "DECISÃO\nDO STF", font=font("Anton.ttf", 62, 800), fill=INK, anchor="mm", align="center")
    d.ellipse((442, 205, 558, 321), fill=accent + (255,), outline=INK + (255,), width=3)
    d.text((500, 263), "≠", font=font("Playfair.ttf", 62, 900), fill=INK, anchor="mm")
    d.text((500, 438), "PARECER NÃO É DECISÃO", font=font("Oswald.ttf", 28, 700), fill=INK, anchor="mm")
    return canvas


def build_event_layer(event: dict, beat_number: int) -> tuple[Image.Image, str | None]:
    person = find_person(event, beat_number)
    if person:
        layer = make_photo_panel(person, seed=beat_number * 17 + int(event["event_number"]))
        return layer, person
    return make_general_card(event, beat_number, int(event["event_number"])), None


@lru_cache(maxsize=10)
def background_for(beat_index: int) -> Image.Image:
    return build_background(beat_index)

EVENT_LAYERS: dict[tuple[int, int], tuple[Image.Image, str | None]] = {}
EVENT_TIMES: list[list[float]] = []


def prepare_layers() -> None:
    for beat in BEATS:
        n = int(beat["beat_number"])
        ts = []
        for event in beat["events"]:
            idx = int(event["event_number"])
            EVENT_LAYERS[(n, idx)] = build_event_layer(event, n)
            ts.append(float(event["time_s"]))
        EVENT_TIMES.append(ts)


def active_word(beat_index: int, t: float) -> tuple[int, list[dict]] | None:
    local = t - SPEECH_STARTS[beat_index]
    if local < 0:
        return None
    words = AUDIO["words"][beat_index]
    starts = [float(w["t"]) for w in words]
    k = bisect_right(starts, local) - 1
    if k < 0 or k >= len(words):
        return None
    if local > float(words[k]["e"]) + 0.46:
        return None
    # Keep a short, growing phrase from the current sentence. No future words.
    begin = max(0, k - 4)
    for p in range(k - 1, max(-1, k - 5), -1):
        if any(ch in words[p]["w"] for ch in ".!?;:"):
            begin = p + 1
            break
    return k, words[begin:k + 1]


def wrap_caption(items: list[dict], active_index: int, fnt: ImageFont.FreeTypeFont,
                 max_width: int) -> list[list[tuple[str, bool]]]:
    measure = ImageDraw.Draw(Image.new("L", (2, 2)))
    gap = int(measure.textlength(" ", font=fnt))
    lines: list[list[tuple[str, bool]]] = [[]]
    width = 0
    for item in items:
        token = item["w"]
        tw = int(measure.textlength(token, font=fnt))
        if lines[-1] and width + gap + tw > max_width and len(lines) < 2:
            lines.append([])
            width = 0
        if lines[-1]:
            width += gap
        lines[-1].append((token, int(item["_idx"]) == active_index))
        width += tw
    return lines


def draw_caption(frame: Image.Image, beat_index: int, t: float) -> None:
    active = active_word(beat_index, t)
    if active is None:
        return
    k, selected = active
    indexed = []
    first_global = max(0, k - len(selected) + 1)
    # Rebuild actual indices from the known contiguous beat word list.
    for offset, item in enumerate(selected):
        indexed.append({**item, "_idx": first_global + offset})
    f = font("Oswald.ttf", 48, 600)
    lines = wrap_caption(indexed, k, f, 940)
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((55, 1490, W - 55, 1697), radius=16, fill=(16, 22, 28, 228))
    d.rectangle((82, 1490, W - 82, 1497), fill=YELLOW + (255,))
    line_h = 58
    total_h = line_h * len(lines)
    y = 1596 - total_h // 2
    measure = ImageDraw.Draw(Image.new("L", (2, 2)))
    for line in lines:
        line_width = sum(measure.textlength(txt, font=f) for txt, _ in line) + measure.textlength(" ", font=f) * (len(line) - 1)
        x = (W - line_width) / 2
        for txt, is_active in line:
            color = YELLOW + (255,) if is_active else WHITE + (255,)
            d.text((x, y), txt, font=f, fill=color, stroke_width=1, stroke_fill=INK + (255,))
            x += measure.textlength(txt, font=f) + measure.textlength(" ", font=f)
        y += line_h


def draw_source_and_ticker(frame: Image.Image, beat_number: int, t: float) -> None:
    d = ImageDraw.Draw(frame)
    source = SOURCE_BY_BEAT.get(beat_number, "UOL · reportagem")
    sf = font("Oswald.ttf", 23, 500)
    d.text((W / 2, 1738), source.upper(), font=sf, fill=(59, 57, 52), anchor="mm")
    ticker = C.ticker_strip(YELLOW, h=72)
    x = -int((t * 190) % ticker.width)
    y = 1800
    while x < W:
        frame.alpha_composite(ticker, (x, y))
        x += ticker.width


def draw_event(frame: Image.Image, beat: dict, event: dict, t: float,
               next_time: float | None, beat_index: int) -> None:
    age = max(0.0, t - float(event["time_s"]))
    p = smooth(age / ENTRY_S)
    layer, person = EVENT_LAYERS[(int(beat["beat_number"]), int(event["event_number"]))]
    # Distinct entry direction per event; cards sit on an independent depth plane.
    direction = -1 if (int(beat["beat_number"]) + int(event["event_number"])) % 2 == 0 else 1
    x_offset = direction * 245 * (1.0 - p) + 8.0 * math.sin(age * 1.15 + beat_index)
    target_y = 890 if person else 915
    y_offset = 64 * (1.0 - p) + 5.5 * math.sin(age * 0.9 + int(event["event_number"]))
    scale = (0.94 + 0.06 * p) * (1.0 + min(age, 4.0) * 0.002)
    angle = direction * (1.0 - p) * 1.2 + 0.22 * math.sin(age * 0.8)
    center_layer(frame, layer, W / 2 + x_offset, target_y + y_offset,
                 scale=scale, angle=angle, opacity=p)


def render_frame(t: float) -> Image.Image:
    t = max(0.0, min(DURATION - 1 / FPS, t))
    bi = max(0, min(len(BEATS) - 1, bisect_right(CUTS, t) - 1))
    beat = BEATS[bi]
    n = int(beat["beat_number"])
    frame = background_for(bi).copy()
    ts = EVENT_TIMES[bi]
    idx = bisect_right(ts, t) - 1
    if idx >= 0:
        event = beat["events"][idx]
        next_time = ts[idx + 1] if idx + 1 < len(ts) else float(beat["end_s"])
        draw_event(frame, beat, event, t, next_time, bi)
    draw_caption(frame, bi, t)
    draw_source_and_ticker(frame, n, t)
    return frame.convert("RGB")


def smoke_times() -> list[tuple[float, str]]:
    samples: list[tuple[float, str]] = [(0.0, "abertura")]
    for beat in BEATS:
        n = int(beat["beat_number"])
        for event in beat["events"]:
            ts = float(event["time_s"])
            samples.append((min(DURATION - 0.02, ts + 0.16), f"b{n:02d}_e{int(event['event_number']):02d}_{ts:.2f}s"))
    samples.append((DURATION - 0.08, "encerramento"))
    return samples


def save_contact_sheet(samples: list[tuple[float, str]]) -> None:
    thumbs = []
    for t, label in samples:
        im = render_frame(t)
        im.thumbnail((270, 480), Image.Resampling.LANCZOS)
        thumbs.append((im.copy(), label))
    cols = 5
    cell_w, cell_h, title_h = 270, 480, 30
    rows = math.ceil(len(thumbs) / cols)
    board = Image.new("RGB", (cols * cell_w, rows * (cell_h + title_h)), (229, 229, 229))
    bd = ImageDraw.Draw(board)
    labelf = font("Inter.ttf", 18, 500)
    for i, (im, label) in enumerate(thumbs):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + title_h)
        bd.text((x + 6, y + 5), label, font=labelf, fill=(12, 16, 19))
        board.paste(im.convert("RGB"), (x, y + title_h))
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    board.save(CONTACT, quality=92)
    print(f"Contact sheet: {CONTACT}")


def render_smoke() -> None:
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    for old in SMOKE_DIR.glob("*.jpg"):
        old.unlink()
    samples = smoke_times()
    for i, (t, label) in enumerate(samples):
        render_frame(t).save(SMOKE_DIR / f"{i:03d}_{label}.jpg", quality=92, subsampling=0)
    save_contact_sheet(samples)
    print(f"Smoke test: {len(samples)} quadros de eventos em {SMOKE_DIR}")


def render_full(keep_frames: bool = False) -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for old in FRAME_DIR.glob("frame_*.jpg"):
        old.unlink()
    frame_count = math.ceil(DURATION * FPS)
    for n in range(frame_count):
        t = min(DURATION - 1 / FPS, n / FPS)
        render_frame(t).save(FRAME_DIR / f"frame_{n:06d}.jpg", quality=91, subsampling=0)
        if (n + 1) % 180 == 0 or n + 1 == frame_count:
            print(f"Frames V5: {n + 1}/{frame_count} ({100*(n+1)/frame_count:.1f}%)", flush=True)
    audio_path = V32 / "mix_ln.wav"
    if not audio_path.exists():
        raise FileNotFoundError(f"Locução/trilha final não encontrada: {audio_path}")
    command = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-framerate", str(FPS), "-start_number", "0", "-i", str(FRAME_DIR / "frame_%06d.jpg"),
        "-i", str(audio_path), "-t", f"{DURATION:.3f}",
        "-map", "0:v:0", "-map", "1:a:0", "-vf", "hqdn3d=1:1:4:4",
        "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(OUT),
    ]
    subprocess.run(command, check=True)
    print(f"MP4 V5: {OUT}")
    if not keep_frames:
        shutil.rmtree(FRAME_DIR, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="renderizar folha de contato, sem MP4 completo")
    parser.add_argument("--keep-frames", action="store_true", help="manter JPEGs do render completo")
    args = parser.parse_args()
    prepare_layers()
    if args.smoke:
        render_smoke()
    else:
        render_full(keep_frames=args.keep_frames)


if __name__ == "__main__":
    main()

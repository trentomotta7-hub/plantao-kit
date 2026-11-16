#!/usr/bin/env python3
"""MAPA SUJO — edição 003, revisão V6 com fotos contextuais.

A V6 preserva imagem, narração e trilha da V5 e substitui o foco visual em
janelas editoriais específicas por duas fotos reais, com crédito visível,
painel rasgado e movimento 2.5D discreto. O vídeo da V5 nunca é sobrescrito.
Uso: python3 render_episode_v6.py --smoke
     python3 render_episode_v6.py --render
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ED003 = HERE.parent
V5_PATH = ED003 / "revisao_v5_visual_sincronizada" / "render_episode_v5.py"
V5_VIDEO = ED003 / "revisao_v5_visual_sincronizada" / "out" / "ed003_v5_sincronizada.mp4"
ASSETS = HERE / "assets"
WORK = HERE / "work" / "v6_overlays"
SMOKE_DIR = HERE / "work" / "v6_smoke"
OUT_DIR = HERE / "out"
OUT = OUT_DIR / "ed003_v6_fotos_contextuais.mp4"
CONTACT = SMOKE_DIR / "contact_v6.jpg"
FPS, W, H = 30, 1080, 1920

# Posições do manifesto V5, calculadas a partir de beats.json (fala + word.t).
BANK_START, BANK_END = 22.04, 26.40
STF_START, STF_END = 68.58, 72.12
CENTER_Y = 920
ENTRY_S, EXIT_S = 0.10, 0.10


def load_v5():
    if not V5_PATH.exists():
        raise FileNotFoundError(f"Renderer V5 ausente: {V5_PATH}")
    spec = importlib.util.spec_from_file_location("plantao_v5_base", V5_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar o renderer-base: {V5_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def fit_size(draw: ImageDraw.ImageDraw, text: str, family: str, initial: int,
             max_width: int, weight: int = 600, min_size: int = 17):
    size = initial
    f = V5.font(family, size, weight)
    while draw.textlength(text, font=f) > max_width and size > min_size:
        size -= 1
        f = V5.font(family, size, weight)
    return f


def make_context_panel(image_path: Path, title: str, detail: str, credit: str,
                       photo_w: int, photo_h: int, seed: int) -> Image.Image:
    if not image_path.is_file():
        raise FileNotFoundError(f"Foto contextual ausente: {image_path}")
    # O enquadramento de cada ativo acompanha sua proporção original para não
    # cortar conteúdo. A pequena granulação é aplicada uma vez ao painel, não
    # refeita a cada frame.
    np.random.seed(seed)
    raw = V5.C.load(str(image_path))
    photo = V5.C.print_photo(raw, photo_w, photo_h, color=True, bright=1.01)

    pad = 22
    card_w = photo_w + pad * 2
    top = 20
    title_h, detail_h, credit_h = 70, 47, 48
    gap = 8
    card_h = top + photo_h + 12 + title_h + gap + detail_h + gap + credit_h + 16
    card = Image.new("RGB", (card_w, card_h), (248, 244, 232))
    card.paste(photo, (pad, top))
    d = ImageDraw.Draw(card)
    y = top + photo_h + 12
    navy = (18, 26, 34)
    ink = (22, 19, 16)
    white = (255, 255, 255)
    d.rectangle((pad, y, card_w - pad, y + title_h), fill=navy)
    title_font = fit_size(d, title, "Oswald.ttf", 39, card_w - 72, 700)
    d.text((card_w / 2, y + title_h / 2), title, font=title_font,
           fill=white, anchor="mm")
    y += title_h + gap
    detail_font = fit_size(d, detail, "Oswald.ttf", 27, card_w - 56, 600)
    d.text((card_w / 2, y + detail_h / 2), detail, font=detail_font,
           fill=ink, anchor="mm")
    y += detail_h + gap
    credit_font = fit_size(d, credit, "Oswald.ttf", 22, card_w - 46, 500)
    d.text((card_w / 2, y + credit_h / 2), credit, font=credit_font,
           fill=(55, 52, 47), anchor="mm")

    # Recorte de papel e sombra são os componentes da própria identidade da série.
    return V5.C.paper_cut(card, seed=seed, border=13, torn=("bottom",),
                          shadow=20, tape_corner=None)


def context_specs():
    return [
        {
            "name": "banco_master",
            "start": BANK_START,
            "end": BANK_END,
            "direction": -1,
            "seed": 603,
            "panel": make_context_panel(
                ASSETS / "fachada_banco_master_rovena_rosa_ebc.jpg",
                "BANCO MASTER",
                "FACHADA · ITAIM BIBI, SÃO PAULO",
                "Rovena Rosa / Agência Brasil · 19/11/2025",
                970, 485, 603,
            ),
        },
        {
            "name": "edificio_stf",
            "start": STF_START,
            "end": STF_END,
            "direction": 1,
            "seed": 1408,
            "panel": make_context_panel(
                ASSETS / "stf_edificio_dasfour2022_commons.jpg",
                "EDIFÍCIO DO STF · FOTO DE ARQUIVO",
                "PARECER DA PGR ≠ DECISÃO DO STF",
                "Dasfour2022 · Wikimedia Commons · CC BY-SA 4.0 · recorte/movimento",
                970, 648, 1408,
            ),
        },
    ]


def overlay_frame(spec: dict, t: float) -> Image.Image:
    """Create one transparent, time-driven photo-card overlay frame."""
    rel = max(0.0, t - float(spec["start"]))
    duration = float(spec["end"]) - float(spec["start"])
    entry = smooth(rel / ENTRY_S)
    exit_alpha = smooth((duration - rel) / EXIT_S)
    alpha = min(entry, exit_alpha)
    direction = int(spec["direction"])
    x = W / 2 + direction * 132 * (1.0 - entry) + 5 * math.sin(rel * 0.95)
    y = CENTER_Y + 30 * (1.0 - entry) + 3 * math.sin(rel * 0.75)
    scale = (0.955 + 0.045 * entry) * (1.0 + min(rel, 4.0) * 0.003)
    angle = direction * (1.0 - entry) * 1.4 + 0.12 * math.sin(rel * 0.65)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    V5.center_layer(canvas, spec["panel"], x, y, scale=scale,
                    angle=angle, opacity=alpha)
    return canvas


def overlay_on_base(base: Image.Image, spec: dict, t: float) -> Image.Image:
    frame = base.convert("RGBA")
    frame.alpha_composite(overlay_frame(spec, t))
    return frame.convert("RGB")


def render_smoke() -> None:
    global V5
    V5 = load_v5()
    V5.prepare_layers()
    specs = context_specs()
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    for old in SMOKE_DIR.glob("*.jpg"):
        old.unlink()
    samples = [
        (21.98, "antes_fachada"),
        (22.18, "entrada_master"),
        (23.70, "fachada_hold"),
        (26.22, "antes_maio"),
        (26.50, "cartela_maio"),
        (68.54, "antes_stf"),
        (68.72, "entrada_stf"),
        (70.00, "distincao_pgr_stf"),
        (71.55, "supremo"),
        (72.18, "saida_stf"),
    ]
    thumbs = []
    for t, label in samples:
        base = V5.render_frame(t)
        spec = next((s for s in specs if s["start"] <= t < s["end"]), None)
        im = overlay_on_base(base, spec, t) if spec else base
        path = SMOKE_DIR / f"{label}_{t:.2f}.jpg"
        im.save(path, quality=93, subsampling=0)
        thumb = im.copy()
        thumb.thumbnail((270, 480), Image.Resampling.LANCZOS)
        thumbs.append((thumb, label))
    cols, cell_w, cell_h, title_h = 5, 270, 480, 30
    board = Image.new("RGB", (cols * cell_w, 2 * (cell_h + title_h)), (229, 229, 229))
    d = ImageDraw.Draw(board)
    labelf = V5.font("Inter.ttf", 18, 500)
    for i, (im, label) in enumerate(thumbs):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + title_h)
        d.text((x + 6, y + 5), label, font=labelf, fill=(12, 16, 19))
        board.paste(im, (x, y + title_h))
    board.save(CONTACT, quality=92)
    print(f"Smoke test: {len(samples)} quadros em {CONTACT}")


def render_overlay_sequence(spec: dict, destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    for old in destination.glob("frame_*.png"):
        old.unlink()
    frame_count = math.ceil((float(spec["end"]) - float(spec["start"])) * FPS)
    for i in range(frame_count):
        rel = i / FPS
        t = float(spec["start"]) + rel
        overlay_frame(spec, t).save(destination / f"frame_{i:04d}.png", optimize=True)
        if (i + 1) % 60 == 0 or i + 1 == frame_count:
            print(f"Overlay {spec['name']}: {i + 1}/{frame_count}", flush=True)
    return frame_count


def render_full() -> None:
    global V5
    V5 = load_v5()
    if not V5_VIDEO.is_file():
        raise FileNotFoundError(f"Vídeo-base V5 ausente: {V5_VIDEO}")
    specs = context_specs()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bank_dir = WORK / "bank_master"
    stf_dir = WORK / "edificio_stf"
    render_overlay_sequence(specs[0], bank_dir)
    render_overlay_sequence(specs[1], stf_dir)

    # Os PNGs têm alpha; cada overlay começa no timestamp editorial original.
    # O áudio AAC é copiado bit a bit do master V5 para não alterar sync nem mix.
    graph = (
        f"[1:v]format=rgba,setpts=PTS+{BANK_START:.3f}/TB[bank];"
        f"[2:v]format=rgba,setpts=PTS+{STF_START:.3f}/TB[stf];"
        f"[0:v][bank]overlay=0:0:eof_action=pass:repeatlast=0:"
        f"enable='between(t,{BANK_START:.3f},{BANK_END - 0.001:.3f})'[v1];"
        f"[v1][stf]overlay=0:0:eof_action=pass:repeatlast=0:"
        f"enable='between(t,{STF_START:.3f},{STF_END - 0.001:.3f})'[v]"
    )
    command = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-i", str(V5_VIDEO),
        "-framerate", str(FPS), "-start_number", "0", "-i", str(bank_dir / "frame_%04d.png"),
        "-framerate", str(FPS), "-start_number", "0", "-i", str(stf_dir / "frame_%04d.png"),
        "-filter_complex", graph,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-fps_mode", "cfr",
        "-c:a", "copy", "-movflags", "+faststart",
        str(OUT),
    ]
    print("Executando FFmpeg para criar a V6 sem alterar o áudio-base...", flush=True)
    subprocess.run(command, check=True)
    print(f"MP4 V6 de revisão: {OUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true", help="gerar amostras de composição, sem MP4 completo")
    group.add_argument("--render", action="store_true", help="gerar a V6 completa a partir do master V5")
    args = parser.parse_args()
    if args.render:
        render_full()
    else:
        render_smoke()


if __name__ == "__main__":
    main()

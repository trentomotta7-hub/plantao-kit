#!/usr/bin/env python3
"""Confere o episodio pronto: corte x fala, respiros, duracao e loudness.

    python3 qa.py --video out/ed02.mp4 --beats beats.json

Roda antes de publicar. Sai com codigo 1 se houver FALHA (corrija antes de subir).
"""
import argparse
import json
import re
import subprocess
import sys

OK, WARN, FAIL = "ok", "ATENCAO", "FALHA"
rows = []


def add(nivel, item, detalhe):
    rows.append((nivel, item, detalhe))


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_name,width,height,r_frame_rate,codec_type",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)


def loudness(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                        "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r'"input_i"\s*:\s*"(-?[\d.]+)".*?"input_tp"\s*:\s*"(-?[\d.]+)"',
                   p.stderr, re.S)
    if not m:
        return None, None
    return float(m[0][0]), float(m[0][1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--beats", default="beats.json")
    ap.add_argument("--min-dur", type=float, default=62.0)
    ap.add_argument("--max-dur", type=float, default=75.0)
    ap.add_argument("--max-gap", type=float, default=1.20)
    a = ap.parse_args()

    B = json.load(open(a.beats))
    starts, cuts, dur, words = B["starts"], B["cuts"], B["dur"], B.get("words")

    info = probe(a.video)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    vdur = float(info["format"]["duration"])

    if not v:
        add(FAIL, "video", "sem stream de video")
    else:
        num, den = (v.get("r_frame_rate") or "0/1").split("/")
        fps = float(num) / max(1e-9, float(den))
        if (v.get("width"), v.get("height")) != (1080, 1920):
            add(FAIL, "formato", f"{v.get('width')}x{v.get('height')} (esperado 1080x1920)")
        else:
            add(OK, "formato", "1080x1920")
        add(OK if abs(fps - 30) < .01 else FAIL, "fps", f"{fps:.2f}")
    add(OK if au else FAIL, "audio", au["codec_name"] if au else "ausente")

    if not (a.min_dur <= vdur <= a.max_dur):
        add(FAIL, "duracao", f"{vdur:.2f}s fora da faixa {a.min_dur:.0f}-{a.max_dur:.0f}s")
    else:
        add(OK, "duracao", f"{vdur:.2f}s")

    if abs(vdur - dur) > 0.25:
        add(WARN, "audio x video", f"beats {dur:.2f}s vs mp4 {vdur:.2f}s")

    if words:
        folga = min(starts[k] - cuts[k] for k in range(1, len(starts)))
        add(OK if 0.06 <= folga <= 0.20 else WARN, "lead do corte",
            f"{folga:.2f}s entre imagem e voz (ideal 0.10-0.15)")
        primeiro = words[0][0]["t"] if words[0] else 0
        real = starts[0] + primeiro
        add(OK if real <= 0.30 else WARN, "primeira palavra",
            f"{real:.2f}s (hook deve falar antes de 0.30s)")

        print(f"{'bloco':>6} {'corte':>7} {'voz':>7} {'lead':>6} {'fim fala':>9} {'respiro':>8}")
        for k in range(len(starts)):
            ini = starts[k]
            fim = starts[k + 1] if k + 1 < len(starts) else dur
            ultimo = ini + max([w["e"] for w in words[k]], default=0)
            respiro = fim - ultimo
            lead = ini - cuts[k]
            print(f"B{k+1:02d} {cuts[k]:7.2f} {ini:7.2f} {lead:6.2f} {ultimo:9.2f} {respiro:8.2f}")
            if k < len(starts) - 1 and respiro > a.max_gap:
                add(WARN, f"respiro B{k+1:02d}", f"{respiro:.2f}s sem fala antes do corte")
        print()

    if au:
        i, tp = loudness(a.video)
        if i is None:
            add(WARN, "loudness", "nao foi possivel medir")
        else:
            add(OK if abs(i + 14) <= 0.6 else WARN, "loudness", f"{i:.1f} LUFS (alvo -14)")
            add(OK if tp <= -0.9 else FAIL, "true peak", f"{tp:.1f} dBTP (teto -1.0)")

    larg = max(len(r[0]) for r in rows)
    print("=== CONTROLE DE QUALIDADE ===")
    for nivel, item, det in rows:
        print(f"[{nivel:>{larg}}] {item:<16} {det}")
    falhas = sum(1 for r in rows if r[0] == FAIL)
    print(f"\n{len(rows)} checagens · {falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Transforma a narração crua do TTS em narração final + beats.json.

O TTS sai rápido demais para vídeo (fala corrida, sem respiro). Este script:
 1. desacelera (atempo, padrão 0.87) — melhora dicção e aumenta a duração;
 2. insere respiros entre os blocos (padrão 0.4–0.75s, maiores nas viradas);
 3. grava beats.json com o instante exato de cada bloco (o corte cai 0.10s antes da voz).

Uso:
    python3 edit_vo.py --wav vo_raw.wav --bounds 7.70,11.74,17.12,... \
        --gaps 0.75,0.45,0.70,0.40,0.55,0.65,0.40,0.75,0.75

`--bounds` são as fronteiras entre blocos em segundos no áudio CRU (use dips.py para achar).
"""
import argparse
import json
import subprocess

import numpy as np

SR = 48000


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--bounds", required=True, help="fronteiras em s, separadas por vírgula")
    ap.add_argument("--gaps", default="", help="respiro depois de cada bloco (n-1 valores)")
    ap.add_argument("--tempo", type=float, default=0.87)
    ap.add_argument("--lead", type=float, default=0.15)
    ap.add_argument("--out-wav", default="vo_edit.wav")
    ap.add_argument("--out-json", default="beats.json")
    a = ap.parse_args()

    bounds = [float(x) for x in a.bounds.split(",") if x.strip()]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.wav, "-filter:a",
                    f"atempo={a.tempo}", "-ac", "1", "-ar", str(SR), "vo_slow.wav"], check=True)
    x = load("vo_slow.wav")

    # duração crua = fim do áudio; fronteiras + fim
    dur_raw = len(x) / SR * a.tempo
    edges = [0.0] + bounds + [dur_raw]
    n_blocos = len(edges) - 1
    gaps = [float(g) for g in a.gaps.split(",") if g.strip()] if a.gaps else [0.55] * (n_blocos - 1)
    if len(gaps) < n_blocos - 1:
        gaps += [gaps[-1]] * (n_blocos - 1 - len(gaps))

    st = 1.0 / a.tempo
    segs = []
    for i in range(n_blocos):
        x0 = int(min(edges[i] * st * SR, len(x)))
        x1 = int(min(edges[i + 1] * st * SR, len(x)))
        segs.append(x[x0:x1])

    out = [np.zeros(int(a.lead * SR))]
    starts, t = [], a.lead
    for i, s in enumerate(segs):
        starts.append(t)
        out.append(s)
        t += len(s) / SR
        if i < n_blocos - 1:
            out.append(np.zeros(int(gaps[i] * SR)))
            t += gaps[i]
    y = np.concatenate(out)
    fo = int(0.25 * SR)
    y[-fo:] *= np.linspace(1, 0, fo) ** 1.5

    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", a.out_wav], input=pcm.tobytes(), check=True)

    cuts = [0.0] + [round(s - 0.10, 3) for s in starts[1:]]
    json.dump({"dur": round(len(y) / SR, 3), "starts": [round(s, 3) for s in starts],
               "cuts": cuts}, open(a.out_json, "w"), indent=1)
    print("duração final %.2f s (%d blocos)" % (len(y) / SR, n_blocos))
    for i, s in enumerate(starts):
        print("B%02d  %.2f" % (i + 1, s))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Acha as fronteiras entre os blocos da narração por vales de energia.

O TTS emenda os parágrafos sem silêncio audível, então detectamos onde a energia
afunda perto da posição esperada (proporcional ao tamanho de cada bloco).

    python3 dips.py --wav vo_raw.wav --textos roteiro.txt

`roteiro.txt` = uma linha por bloco (o texto falado). Imprime as fronteiras em
segundos, prontas para passar em edit_vo.py --bounds.
"""
import argparse
import subprocess

import numpy as np

SR = 48000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--textos", required=True)
    ap.add_argument("--janela", type=float, default=1.4, help="busca em ±s ao redor do esperado")
    a = ap.parse_args()

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.wav, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    hop = int(0.01 * SR)
    m = len(x) // hop
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(m)])
    e /= (e.max() + 1e-12)

    textos = [l.strip() for l in open(a.textos, encoding="utf-8") if l.strip()]
    w = np.array([len(t) for t in textos], dtype=float)
    w /= w.sum()
    exp = np.cumsum(w)[:-1] * (m - 1)

    jan = int(a.janela * 100)
    bounds = []
    for p in exp:
        lo, hi = max(0, int(p - jan)), min(m - 1, int(p + jan))
        bounds.append((lo + int(np.argmin(e[lo:hi]))) / 100.0)

    print("duração %.2f s · %d blocos" % (len(x) / SR, len(textos)))
    print(",".join("%.2f" % b for b in bounds))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Mixa narração + trilha com ducking e drop em cada corte.

    python3 mix.py --vo vo_edit.wav --bgm trilha.mp3 --start 50 --big 0,3,5,7,8,9

--start  : segundo da trilha onde começa o trecho mais agressivo (ela entra em loop)
--big    : índices de bloco cujo corte leva impacto cheio (boom + riser); os outros levam 62%
Saída: mix_raw.wav e mix_ln.wav (normalizado a -14 LUFS, padrão de plataforma).
"""
import argparse
import json
import subprocess

import numpy as np

SR = 48000


def load(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def env(x, atk=0.004, rel=0.18):
    mono = np.abs(x).max(axis=1)
    a_a, a_r = np.exp(-1.0 / (atk * SR)), np.exp(-1.0 / (rel * SR))
    out = np.empty(len(mono))
    prev = 0.0
    for i, v in enumerate(mono):
        prev = a_a * prev + (1 - a_a) * v if v > prev else a_r * prev + (1 - a_r) * v
        out[i] = prev
    return out


def smooth_gain(g, ms=6):
    a = np.exp(-1.0 / (ms / 1000.0 * SR))
    out = np.empty_like(g)
    prev = g[0]
    for i, v in enumerate(g):
        prev = a * prev + (1 - a) * v
        out[i] = prev
    return out


def loop_to(x, n, xf=1.2):
    if len(x) >= n:
        return x[:n]
    out = x.copy()
    while len(out) < n:
        k = int(xf * SR)
        w = np.linspace(0, 1, k)[:, None]
        seam = out[-k:] * (1 - w) + x[:k] * w
        out = np.concatenate([out[:-k], seam, x[k:]])
    return out[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", default="vo_edit.wav")
    ap.add_argument("--bgm", required=True)
    ap.add_argument("--beats", default="beats.json")
    ap.add_argument("--start", type=float, default=50.0)
    ap.add_argument("--big", default="0")
    ap.add_argument("--duck", type=float, default=0.64)
    ap.add_argument("--bg", type=float, default=0.30)
    a = ap.parse_args()

    B = json.load(open(a.beats))
    DUR, CUTS = B["dur"], B["cuts"]
    big_idx = {int(x) for x in a.big.split(",") if x.strip()}
    BIG = {CUTS[i] for i in big_idx if i < len(CUTS)}

    vo = load(a.vo)
    bg = load(a.bgm)[int(a.start * SR):]
    n = int(DUR * SR)
    vo = np.pad(vo, ((0, max(0, n - len(vo))), (0, 0)))[:n]
    bg = loop_to(bg, n)
    vo *= 0.94 / max(1e-9, np.abs(vo).max())
    bg *= a.bg / max(1e-9, np.abs(bg).max())

    e = env(vo, 0.004, 0.16)
    e = e / max(1e-9, np.percentile(e, 99.5))
    gain = smooth_gain(1.0 - a.duck * np.clip(e, 0, 1) ** 0.7, 8)

    boom = np.zeros(n)
    crack = np.zeros(n)
    rng = np.random.default_rng(3)
    for c in CUTS:
        i0 = int(c * SR)
        pre = int(0.04 * SR)
        for k in range(max(0, i0 - pre), min(n, i0)):
            p = (k - (i0 - pre)) / pre
            gain[k] *= max(0.08, 1 - p * 0.92)
        ov = int(0.26 * SR)
        for k in range(i0, min(n, i0 + ov)):
            gain[k] *= 1.0 + 0.22 * np.exp(-(k - i0) / ov * 5.0)
        amp = 1.0 if c in BIG else 0.62
        seg = np.arange(min(int(0.55 * SR), n - i0)) / SR
        f = 52 + 26 * np.exp(-seg * 9)
        boom[i0:i0 + len(seg)] += amp * 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-seg * 7.5)
        Lc = min(int(0.05 * SR), n - i0)
        nz = rng.normal(0, 1, Lc) * np.exp(-np.arange(Lc) / (0.012 * SR))
        crack[i0:i0 + len(nz)] += amp * 0.16 * nz

    riser = np.zeros(n)
    for c in sorted(BIG):
        if c == 0:
            continue
        Lr = int(0.34 * SR)
        i0 = max(0, int(c * SR) - Lr)
        m = int(c * SR) - i0
        seg = np.arange(m) / SR
        f = 190 * (1500 / 190) ** (seg / (Lr / SR))
        hiss = np.diff(np.concatenate([[0.0], rng.normal(0, 1, m)]))
        riser[i0:i0 + m] += (seg / (Lr / SR)) ** 2.2 * (
            0.055 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.030 * hiss)

    fi = int(0.06 * SR)
    bg[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(1.6 * SR)
    bg[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.4

    speech = e > 0.35
    print("VO  rms %.1f dB" % (20 * np.log10(np.sqrt(np.mean(vo[speech] ** 2)) + 1e-9)))
    print("BGM rms %.1f dB" % (20 * np.log10(np.sqrt(np.mean((bg * gain[:, None])[speech] ** 2)) + 1e-9)))

    mix = vo + bg * gain[:, None] + boom[:, None] + crack[:, None] + riser[:, None]
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    mix *= 0.94 / max(1e-9, np.abs(mix).max())

    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-c:a", "pcm_s16le", "mix_raw.wav"], input=pcm.tobytes(), check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "mix_raw.wav", "-af",
                    "loudnorm=I=-14:TP=-1.0:LRA=9", "-c:a", "pcm_s16le", "mix_ln.wav"], check=True)
    print("ok", mix.shape)


if __name__ == "__main__":
    main()

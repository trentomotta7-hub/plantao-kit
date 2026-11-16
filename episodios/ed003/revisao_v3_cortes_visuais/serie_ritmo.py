#!/usr/bin/env python3
"""Renderiza o episódio. Uso:

    python3 serie.py conteudo_ep01.py            # todos os frames -> work/frames_out
    python3 serie.py conteudo_ep01.py --test     # 13 frames de conferência
    python3 serie.py conteudo_ep01.py --from 900 --to 1200   # refazer um trecho
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_ritmo as E  # noqa: E402

args = [a for a in sys.argv[1:]]
conteudo = next((a for a in args if a.endswith(".py")), "conteudo_ep01.py")
E.load(conteudo)

if "--test" in args:
    # Amostra toda a duração, inclusive o último bloco de vídeos explicadores.
    fractions = (0.005, 0.04, 0.09, 0.16, 0.24, 0.33, 0.43, 0.54, 0.65, 0.76, 0.87, 0.95, 0.995)
    for t in sorted({round(max(0.0, min(E.DUR - 0.01, E.DUR * f)), 2) for f in fractions}):
        E.render(t).save(f"{E.OUT}/t_{t:05.1f}.jpg", quality=90)
        print("ok", t, flush=True)
    raise SystemExit(0)

ini, fim = 0, int(E.DUR * E.FPS)
if "--from" in args:
    ini = int(args[args.index("--from") + 1])
if "--to" in args:
    fim = int(args[args.index("--to") + 1])

print("frames", fim - ini, flush=True)
for n in range(ini, fim):
    E.render(n / E.FPS).save(f"{E.OUT}/f_{n:05d}.jpg", quality=92, subsampling=2)
    if n % 60 == 0:
        print(n, flush=True)
print("done", flush=True)

#!/usr/bin/env python3
"""Renderiza o episódio. Uso:

    python3 serie.py conteudo_ep01.py            # todos os frames -> work/frames_out
    python3 serie.py conteudo_ep01.py --test     # 13 frames de conferência
    python3 serie.py conteudo_ep01.py --from 900 --to 1200   # refazer um trecho
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E  # noqa: E402

args = [a for a in sys.argv[1:]]
conteudo = next((a for a in args if a.endswith(".py")), "conteudo_ep01.py")
E.load(conteudo)

if "--test" in args:
    for t in (0.2, 3.0, 6.0, 10.5, 16.0, 23.0, 27.5, 35.0, 40.0, 45.0, 49.0, 55.0, 62.0):
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

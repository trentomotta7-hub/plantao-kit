#!/usr/bin/env python3
"""Gera beats.json a partir dos timestamps de PALAVRA da narracao.

Substitui o chute por vale de energia (dips.py) por ancoragem real: cada bloco
comeca na primeira palavra que a voz fala, e o corte visual entra `--lead`
antes dela.

    manus-speech-to-text vo_edit.wav --granularity word > vo.json
    python3 timing.py --stt vo.json --textos roteiro.txt --wav vo_edit.wav

Saida (beats.json):
    dur      duracao do audio final
    starts   instante em que cada bloco comeca a ser falado
    cuts     instante do corte visual (starts - lead)
    words    para cada bloco, [{t, e, w}] com tempos RELATIVOS ao bloco,
             usados pelo engine para ancorar cada elemento visual na palavra.

O motor (engine.py) consome `words` para nao precisar mais de REF (retiming
proporcional): o pop de cada cartela cai na palavra que ele ilustra.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata

TOKEN = re.compile(r"[0-9a-z]+")


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return TOKEN.findall(s.lower())


def load_words(path):
    """Aceita o JSON do manus-speech-to-text ou o texto com [mm:ss.s - mm:ss.s]."""
    if path.lower().endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        out = [(float(w["start"]), float(w.get("end", w["start"])), w["text"]) for w in d["words"]]
        dur = d.get("duration")
    else:
        txt = open(path, encoding="utf-8").read()
        out, dur = [], None
        for m in re.finditer(r"\[(\d+):(\d+\.\d+) - (\d+):(\d+\.\d+)\] (.+)", txt):
            a, b, c, d2, w = m.groups()
            out.append((int(a) * 60 + float(b), int(c) * 60 + float(d2), w.strip()))
        # a saida do CLI as vezes ecoa o bloco de resultados duas vezes
        vistos, unicos = set(), []
        for t in out:
            if t not in vistos:
                vistos.add(t)
                unicos.append(t)
        out = unicos
    out.sort()
    return out, dur


def find_anchor(tokens, flat, cursor, max_len=4):
    """Mantido por compatibilidade: nao e mais o caminho principal."""
    for n in range(min(max_len, len(tokens)), 0, -1):
        needle = tokens[:n]
        for i in range(cursor, len(flat) - n + 1):
            if [f[0] for f in flat[i:i + n]] == needle:
                return i, n
    return None, 0


def align(linhas, flat):
    """Alinha o roteiro inteiro com a transcricao e devolve o 1o token de cada bloco.

    Alinhamento global (difflib) tolera palavra trocada, omitida ou inserida pelo
    TTS — o que a busca por prefixo nao tolera. Tambem mede a semelhanca, para
    avisar quando o roteiro do arquivo nao e o texto que foi realmente narrado.
    """
    roteiro, bloco_de = [], []
    for k, linha in enumerate(linhas):
        for t in norm(linha):
            roteiro.append(t)
            bloco_de.append(k)
    transc = [f[0] for f in flat]
    sm = difflib.SequenceMatcher(None, roteiro, transc, autojunk=False)
    mapa = {}
    for bloco in sm.get_matching_blocks():
        for d in range(bloco.size):
            mapa[bloco.a + d] = bloco.b + d
    semelhanca = sm.ratio()
    inicios = {}
    for i, k in enumerate(bloco_de):
        if i in mapa and k not in inicios:
            inicios[k] = mapa[i]
    return inicios, semelhanca


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stt", required=True, help="json/texto com timestamps de palavra")
    ap.add_argument("--textos", required=True, help="roteiro: uma linha por bloco")
    ap.add_argument("--wav", help="audio final; usado para a duracao exata")
    ap.add_argument("--lead", type=float, default=0.10, help="corte visual antes da voz")
    ap.add_argument("--out", default="beats.json")
    a = ap.parse_args()

    words, dur = load_words(a.stt)
    if a.wav and os.path.exists(a.wav):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", a.wav], capture_output=True, text=True)
        dur = float(r.stdout.strip())
    if not dur:
        dur = words[-1][1] + 0.3

    linhas = [l.strip() for l in open(a.textos, encoding="utf-8") if l.strip()]
    flat = []
    for i, (s, e, w) in enumerate(words):
        for t in norm(w):
            flat.append((t, i))
    if not flat:
        sys.exit("transcricao vazia")

    starts, idxs, falhas = [], [], []
    inicios, semelhanca = align(linhas, flat)
    for k, linha in enumerate(linhas):
        pos = inicios.get(k)
        if pos is None:
            falhas.append((k + 1, " ".join(norm(linha)[:4])))
            pos = inicios.get(k + 1, len(flat) - 1)
        wi = flat[pos][1]
        starts.append(round(words[wi][0], 3))
        idxs.append(wi)

    if semelhanca < 0.85:
        print(f"AVISO: roteiro e audio batem apenas {semelhanca:.0%}. "
              f"O arquivo de texto provavelmente nao e o que foi narrado.",
              file=sys.stderr)

    cuts = []
    for k, s in enumerate(starts):
        c = round(s - a.lead, 3)
        if k == 0:
            c = 0.0
        c = max(c, 0.0 if k == 0 else cuts[-1] + 0.5)
        cuts.append(round(min(c, s - 0.02), 3))

    blocos = []
    for k in range(len(starts)):
        ini = idxs[k]
        fim = idxs[k + 1] if k + 1 < len(starts) else len(words)
        blocos.append([{"t": round(max(0.0, words[j][0] - starts[k]), 3),
                        "e": round(max(0.0, words[j][1] - starts[k]), 3),
                        "w": words[j][2]} for j in range(ini, fim)])

    json.dump({"dur": round(dur, 3), "starts": starts, "cuts": cuts,
               "lead": a.lead, "words": blocos}, open(a.out, "w", encoding="utf-8"), indent=1)

    print("duracao %.2f s · %d blocos · lead %.2f s" % (dur, len(starts), a.lead))
    for k, s in enumerate(starts):
        fim = starts[k + 1] if k + 1 < len(starts) else dur
        print("B%02d  voz %6.2f  corte %6.2f  dur %5.2f  %s" % (
            k + 1, s, cuts[k], fim - s, " ".join(w["w"] for w in blocos[k][:4])))
    if falhas:
        print("\nATENCAO: ancora nao encontrada nestes blocos (revise a transcricao):")
        for k, t in falhas:
            print("  B%02d  %s" % (k, t))


if __name__ == "__main__":
    main()

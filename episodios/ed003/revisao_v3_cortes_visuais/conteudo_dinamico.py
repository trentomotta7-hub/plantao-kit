#!/usr/bin/env python3
"""MAPA SUJO — V3.2: microcenas editoriais dentro de cada fala.

O módulo original da edição 003 é usado apenas como biblioteca de componentes.
Cada beat recebe novas composições em palavras-chave; não há looping de um único
quadro de mapa ou de uma página. Retratos continuam como recortes impressos e
as telas sobre mensagens/relatórios são esquemas editoriais, nunca evidências.
"""
from bisect import bisect_right
from functools import lru_cache
import math
from pathlib import Path

import engine_ritmo as E
import conteudo_ed003 as BASE

C, M = E.C, E.M
ACCENT = BASE.ACCENT
TAG = BASE.TAG
MAP_BLOCKS = BASE.MAP_BLOCKS
base = BASE.base
layers = BASE.layers
PER_FRAME = {}

# Âncoras locais a palavras realmente faladas. Cada lista tem um estado inicial
# (None) e cortes internos ligados a uma frase/termo da narração.
CUES = {
    0: [None, "Daniel", "Isso prova", "Não"],
    1: [None, "2024", "ex-sócio", "medicina"],
    2: [None, "Kássio", "Moraes", "apertado"],
    3: [None, "mantenedora", "maio", "transição"],
    4: [None, "interesse", "não", "combinou"],
    5: [None, "recuperou", "identificadas", "enviadas"],
    6: [None, "refazer", "excesso", "confirma"],
    7: [None, "Moraes", "não responderam", "Fábio"],
    8: [None, "manter", "Parecer", "Supremo"],
    9: [None, "mensagem", "relatório", "dúvidas", "nova versão"],
}


def _cue_times(i):
    out = [0.0]
    for cue in CUES[i][1:]:
        t = E.AT(i, cue)
        if t - out[-1] >= .82:
            out.append(t)
    return out


SCENE_TIMES = {i: _cue_times(i) for i in CUES}
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "context"
PHOTO_SHOTS = {
    (1, 2): str(ASSET_DIR / "gavel.jpg"),
}
DARK_SHOTS = {
    (1, 1), (2, 0), (3, 1), (4, 2), (5, 0), (5, 3),
    (6, 3), (7, 1), (8, 1), (9, 2),
}


def _center(frame, im, x, y):
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _page(i, variant):
    # Variar sutilmente a folha/tinta a cada microcena; preservar masthead e papel.
    frame = E.paper(701 + i * 31 + variant * 17).convert("RGBA")
    veil = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    E.ImageDraw.Draw(veil).rectangle((0, 292, E.W, E.H - 132), fill=E.PAPER + (194,))
    frame.alpha_composite(veil)
    return frame


def _brand_tag(frame):
    tag = E.PL(E.TB(["MAPA SUJO · EDIÇÃO 003"], 23, E.WHT, "Oswald.ttf", 700,
                    maxw=460), 13, 7, E.INK)
    frame.alpha_composite(tag, (24, 30))
    return frame


def _board():
    # Fundo preto diagonal usado nos blocos de mapa da identidade aprovada.
    return _brand_tag(M.BG.copy())


def _photo_background(path):
    frame = E.photo(path, E.W, E.H, color=True, bright=.86).convert("RGBA")
    shade = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 72))
    frame.alpha_composite(shade)
    return _brand_tag(frame)


def _plate(lines, size=64, bg=E.YEL, fg=E.INK, font="Anton.ttf", angle=-1.5, maxw=890):
    im = E.PL(E.TB(lines, size, fg, font, 800, maxw=maxw), 24, 15, bg)
    return E.st(im, angle)


def _source(frame, text="UOL · 13/11/2026", y=1530):
    im = E.PL(E.TB([text], 22, E.INK, "Oswald.ttf", 500, maxw=920), 12, 6, E.PAPER)
    _center(frame, im, 540, y)


def _photo_credit(frame, text, y=1465):
    im = E.PL(E.TB([text], 21, E.INK, "Oswald.ttf", 500, maxw=850), 11, 5, E.PAPER)
    _center(frame, im, 540, y)


def _stamp(frame, text, x, y, size=54, color=E.RED, angle=-8):
    _center(frame, C.stamp(text, size, color, angle), x, y)


def _marker(frame, text, x, y, size=38, color=E.BLUE, angle=-3, highlight=E.YEL):
    _center(frame, C.marker(text, size, color, angle, highlight=highlight), x, y)


def _arrow(frame, x, y, length=140, angle=-90, color=E.RED):
    _center(frame, C.marker_arrow(length, max(52, int(length * .55)), color, angle), x, y)


def _icon(kind, color=E.INK, accent=E.RED):
    """Desenho editorial simples, feito à mão; não representa local real."""
    im = E.Image.new("RGBA", (360, 300), (0, 0, 0, 0))
    d = E.ImageDraw.Draw(im)
    w = 9
    if kind in ("bank", "school", "court"):
        d.line([(35, 105), (180, 30), (325, 105)], fill=color + (255,), width=w, joint="curve")
        d.line([(52, 112), (308, 112)], fill=accent + (255,), width=7)
        for x in (82, 148, 214, 280):
            d.line([(x, 120), (x, 235)], fill=color + (255,), width=14)
        d.line([(46, 242), (314, 242)], fill=color + (255,), width=11)
        d.line([(32, 264), (328, 264)], fill=accent + (255,), width=7)
        if kind == "school":
            d.rectangle((151, 38, 209, 92), outline=accent + (255,), width=8)
            d.line([(180, 47), (180, 82)], fill=accent + (255,), width=8)
            d.line([(162, 64), (198, 64)], fill=accent + (255,), width=8)
        if kind == "court":
            d.ellipse((156, 36, 204, 84), outline=accent + (255,), width=7)
    elif kind == "file":
        d.polygon([(42, 95), (142, 95), (172, 125), (320, 125), (302, 253), (58, 253)],
                  outline=color + (255,), fill=(E.PAPER[0], E.PAPER[1], E.PAPER[2], 255))
        d.line([(42, 95), (142, 95), (172, 125), (320, 125)], fill=accent + (255,), width=10)
        d.line([(78, 167), (285, 167)], fill=color + (230,), width=6)
        d.line([(78, 198), (250, 198)], fill=color + (230,), width=6)
        d.line([(78, 229), (270, 229)], fill=color + (230,), width=6)
    elif kind == "calendar":
        d.rounded_rectangle((55, 40, 305, 262), radius=8, outline=color + (255,), width=9)
        d.rectangle((55, 40, 305, 95), fill=accent + (230,))
        for x in (112, 180, 248):
            d.line([(x, 112), (x, 236)], fill=color + (180,), width=4)
        for y in (145, 185, 225):
            d.line([(72, y), (288, y)], fill=color + (180,), width=4)
        d.ellipse((162, 153, 197, 188), fill=E.RED + (255,))
    elif kind == "question":
        f = C.fnt("Anton.ttf", 250)
        d.text((70, -5), "?", font=f, fill=accent + (255,))
    return im


def _map_card(frame):
    M.CARD = (580, 610)
    cx, cy, z = M.FULL
    mimg, cam = M.map_frame([("DF", 1.0)], z * 1.04, cx, cy)
    card = E.MapCard(580, 610, -3.4, (540, 1005), seed=47, tape=True)
    card.draw(frame, mimg)
    px, py = card.c2f(*M.proj(-47.8825, -15.7942), cam)
    _center(frame, C.marker_circle(38, 38, E.RED, 9, -4), px, py)
    _center(frame, E.PL(E.TB(["STF · BRASÍLIA"], 28, E.INK, "Oswald.ttf", 700,
                              maxw=410), 12, 7, E.PAPER), px + 120, py - 93)
    return frame


def _draw(i, k):
    if (i, k) in PHOTO_SHOTS:
        frame = _photo_background(PHOTO_SHOTS[(i, k)])
    elif (i, k) in DARK_SHOTS:
        frame = _board()
    else:
        frame = _page(i, k)
    source = "UOL · reportagem de 13/11/2026"

    if i == 0:
        if k == 0:
            _center(frame, _plate(["MORAES VAI", "VOTAR A FAVOR?"], 82, maxw=900), 540, 540)
            _center(frame, E.st(BASE._photo_cut(BASE.DANIEL, 930, 660, 410, E.RED, 1.04), -1.1), 540, 1040)
            _center(frame, _plate(["DANIEL VORCARO"], 32, bg=E.PAPER, maxw=370), 240, 750)
            _stamp(frame, "MENSAGEM ATRIBUÍDA", 690, 1280, 43)
            _photo_credit(frame, "Arquivo · Claudio Gatti/Divulgação", 1430)
            _source(frame, source, 1510)
        elif k == 1:
            _center(frame, E.st(BASE._photo_cut(BASE.DANIEL, 850, 610, 411, E.RED, 1.04), -1.1), 540, 980)
            _center(frame, _plate(["DANIEL VORCARO"], 49, bg=E.PAPER, maxw=750), 540, 520)
            _stamp(frame, "MENSAGEM ATRIBUÍDA", 700, 1245, 43)
            _photo_credit(frame, "Arquivo · Claudio Gatti/Divulgação", 1405)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, _plate(["“MORAES VAI", "VOTAR A FAVOR?”"], 76, bg=E.PAPER, maxw=860), 540, 740)
            _marker(frame, "ISSO PROVA?", 540, 1180, 58, E.RED, -4, E.YEL)
            _source(frame, source, 1510)
        else:
            _stamp(frame, "NÃO É PROVA", 540, 820, 106, E.RED, -5)
            _center(frame, E.st(BASE._photo_cut(BASE.DANIEL, 540, 350, 412, E.YEL, 1.0), 1.5), 540, 1190)
            _center(frame, _plate(["DANIEL VORCARO"], 32, bg=E.PAPER, maxw=420), 540, 970)
            _source(frame, source, 1510)

    elif i == 1:
        if k == 0:
            _center(frame, _plate(["FEVEREIRO", "DE 2024"], 94, bg=E.RED, fg=E.WHT, maxw=820), 540, 760)
            _center(frame, C.marker_arrow(250, 86, E.RED, 0), 540, 1120)
            _source(frame, source, 1510)
        elif k == 1:
            _map_card(frame)
            _center(frame, _plate(["LOCALIZAÇÃO DO STF"], 45, bg=E.YEL, maxw=800), 540, 1430)
            _photo_credit(frame, "Mapa ilustrativo · não representa trajeto ou contato", 1505)
        elif k == 2:
            _center(frame, _plate(["UMA AÇÃO", "NO STF"], 69, bg=E.PAPER, maxw=790), 540, 760)
            _center(frame, _plate(["CURSOS DE MEDICINA"], 49, bg=E.YEL, maxw=800), 540, 1080)
            _marker(frame, "IMAGEM ILUSTRATIVA", 540, 1370, 34, E.WHT, -2, E.RED)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["CURSOS DE", "MEDICINA"], 83, bg=E.CYA, maxw=780), 540, 840)
            _marker(frame, "AÇÃO CITADA PELO UOL", 540, 1170, 38, E.BLUE)
            _source(frame, source, 1510)

    elif i == 2:
        if k == 0:
            _center(frame, _plate(["“CÁSSIO VAI VOTAR", "A FAVOR.”"], 69, bg=E.YEL, maxw=890), 540, 760)
            _stamp(frame, "TRECHO ATRIBUÍDO", 540, 1160, 49)
            _source(frame, source, 1510)
        elif k == 1:
            _center(frame, _plate(["“E MORAES.”"], 101, bg=E.PAPER, maxw=840), 540, 770)
            _center(frame, E.st(BASE._photo_cut(BASE.DANIEL, 620, 390, 413, E.CYA, 1.0), -1.4), 540, 1180)
            _center(frame, _plate(["DANIEL VORCARO"], 34, bg=E.PAPER, maxw=420), 285, 1010)
            _photo_credit(frame, "Foto de arquivo · Claudio Gatti/Divulgação", 1430)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, _plate(["VAI SER", "APERTADO"], 92, bg=E.RED, fg=E.WHT, maxw=830), 540, 760)
            _marker(frame, "“MAS VAMOS.”", 540, 1190, 52, E.BLUE, -2, E.YEL)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["CITAÇÃO", "REPORTADA"], 79, bg=E.PAPER, maxw=800), 540, 760)
            _stamp(frame, "NÃO É CAPTURA", 540, 1120, 43, E.BLUE, 5)
            _source(frame, source, 1510)

    elif i == 3:
        if k == 0:
            _center(frame, E.st(_icon("bank", E.INK, E.RED), -1.5), 540, 785)
            _center(frame, _plate(["BANCO MASTER"], 83, bg=E.YEL, maxw=830), 540, 1150)
            _source(frame, source, 1510)
        elif k == 1:
            _center(frame, _plate(["ERA CREDOR DA"], 69, bg=E.PAPER, maxw=850), 540, 710)
            _arrow(frame, 540, 960, 190, -90)
            _center(frame, _plate(["MANTENEDORA", "DA ULBRA"], 65, bg=E.CYA, maxw=830), 540, 1220)
            _marker(frame, "VÍNCULO DE CRÉDITO", 540, 1430, 33)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, E.st(_icon("school", E.INK, E.CYA), 1.2), 540, 790)
            _center(frame, _plate(["MANTENEDORA", "DA ULBRA"], 64, bg=E.PAPER, maxw=840), 540, 1190)
            _source(frame, source, 1510)
        else:
            _center(frame, E.st(_icon("calendar", E.INK, E.RED), -1.0), 540, 730)
            _center(frame, _plate(["MAIO/2024"], 78, bg=E.RED, fg=E.WHT, maxw=720), 540, 1110)
            _marker(frame, "STF · REGRA DE TRANSIÇÃO", 540, 1360, 34, E.BLUE)
            _source(frame, source, 1510)

    elif i == 4:
        if k == 0:
            _center(frame, E.st(BASE._photo_cut(BASE.MORAES, 690, 690, 414, E.CYA, 1.02), -1.4), 390, 920)
            _center(frame, _plate(["ALEXANDRE DE MORAES"], 34, bg=E.PAPER, maxw=500), 390, 520)
            _center(frame, _plate(["CONTEXTO"], 72, bg=E.YEL, maxw=430), 800, 870)
            _photo_credit(frame, "Victor Piemonte/STF · domínio público", 1430)
            _source(frame, source, 1510)
        elif k == 1:
            _center(frame, _plate(["INTERESSE", "ECONÔMICO"], 86, bg=E.YEL, maxw=840), 540, 800)
            _marker(frame, "PODE INDICAR", 540, 1150, 46)
            _source(frame, source, 1510)
        elif k == 2:
            _stamp(frame, "NÃO PROVA", 540, 820, 112, E.RED, -5)
            _center(frame, _icon("question", E.INK, E.RED), 540, 1190)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["ANTECIPOU O VOTO?"], 64, bg=E.PAPER, maxw=870), 540, 690)
            _center(frame, _plate(["COMBINOU ALGO?"], 64, bg=E.CYA, maxw=820), 540, 1120)
            _stamp(frame, "NÃO COMPROVADO", 540, 1390, 40, E.RED, 4)
            _source(frame, source, 1510)

    elif i == 5:
        if k == 0:
            _center(frame, _plate(["MENSAGENS DE", "MORAES"], 66, bg=E.PAPER, maxw=860), 540, 720)
            _stamp(frame, "NÃO RECUPERADAS", 540, 1110, 63, E.RED, -5)
            _marker(frame, "ESQUEMA EDITORIAL · UOL", 540, 1370, 30)
            _source(frame, source, 1510)
        elif k == 1:
            _center(frame, E.st(_icon("file", E.INK, E.RED), -1.5), 540, 770)
            _stamp(frame, "NÃO RECUPERADAS", 540, 1190, 53, E.RED, -6)
            _marker(frame, "SEM RECRIAR CONVERSAS", 540, 1400, 31)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, _plate(["IMAGENS DE TEXTOS"], 66, bg=E.CYA, maxw=880), 540, 700)
            _center(frame, _plate(["ENVIADAS POR VORCARO"], 53, bg=E.PAPER, maxw=900), 540, 1030)
            _stamp(frame, "IDENTIFICADAS", 540, 1290, 58, E.BLUE, -4)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["NÃO RECUPERADAS"], 54, bg=E.RED, fg=E.WHT, maxw=850), 540, 710)
            _center(frame, C.marker_arrow(115, 62, E.BLUE, -90), 540, 950)
            _center(frame, _plate(["IMAGENS DE TEXTOS", "ENVIADAS POR VORCARO"], 48, bg=E.CYA, maxw=880), 540, 1210)
            _marker(frame, "ESQUEMA EDITORIAL · UOL", 540, 1430, 30)
            _source(frame, source, 1510)

    elif i == 6:
        if k == 0:
            _center(frame, E.st(_icon("file", E.INK, E.RED), -1.4), 540, 780)
            _center(frame, _plate(["RELATÓRIOS DA PF"], 62, bg=E.PAPER, maxw=850), 540, 1160)
            _source(frame, source, 1510)
        elif k == 1:
            _stamp(frame, "EM REVISÃO", 540, 790, 93, E.RED, -7)
            _center(frame, _plate(["MANDOU REFAZER"], 67, bg=E.YEL, maxw=840), 540, 1170)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, _plate(["EXCESSO DE ESCOPO"], 59, bg=E.PAPER, maxw=900), 540, 750)
            _marker(frame, "E DESCRIÇÃO", 540, 1110, 54, E.RED, -4)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["NÃO CONFIRMA", "NEM AFASTA"], 72, bg=E.RED, fg=E.WHT, maxw=850), 540, 820)
            _marker(frame, "A SUSPEITA", 540, 1210, 50, E.BLUE)
            _source(frame, source, 1510)

    elif i == 7:
        if k == 0:
            rows = [("MORAES", E.YEL, -2.0), ("DEFESA", E.PAPER, 1.5), ("PF", E.CYA, -1.2)]
            for n, (txt, color, angle) in enumerate(rows):
                _center(frame, E.st(E.PL(E.TB([txt], 56, E.INK, "Anton.ttf", 800,
                                              maxw=700), 24, 14, color), angle),
                        540 + (26 if n % 2 else -22), 620 + n * 245)
            _source(frame, source, 1510)
        elif k == 1:
            _stamp(frame, "SEM RESPOSTA", 540, 790, 91, E.RED, -6)
            _center(frame, _plate(["ATÉ 13/11"], 74, bg=E.YEL, maxw=700), 540, 1160)
            _source(frame, source, 1510)
        elif k == 2:
            _center(frame, _plate(["FÁBIO FARIA"], 70, bg=E.CYA, maxw=800), 540, 710)
            _marker(frame, "DISSE QUE NÃO TINHA", 540, 1040, 42, E.BLUE)
            _center(frame, _plate(["RELAÇÃO COM O TEMA"], 58, bg=E.PAPER, maxw=870), 540, 1280)
            _source(frame, source, 1510)
        else:
            _center(frame, _plate(["RESPOSTA", "ATRIBUÍDA"], 78, bg=E.PAPER, maxw=800), 540, 760)
            _stamp(frame, "FÁBIO FARIA", 540, 1180, 57, E.BLUE, 5)
            _source(frame, source, 1510)

    elif i == 8:
        if k == 0:
            _center(frame, E.st(BASE._photo_cut(BASE.GONET, 740, 560, 418, E.CYA, 1.02), -1.2), 540, 930)
            _center(frame, _plate(["PAULO GONET"], 56, bg=E.PAPER, maxw=700), 540, 520)
            _photo_credit(frame, "Agência Senado", 1400)
            _source(frame, "Agência Brasil · manifestação da PGR", 1510)
        elif k == 1:
            _stamp(frame, "PGR", 540, 760, 112, E.RED, -7)
            _center(frame, _plate(["OPINOU POR"], 72, bg=E.YEL, maxw=780), 540, 1110)
            _source(frame, "Agência Brasil · manifestação da PGR", 1510)
        elif k == 2:
            _center(frame, _plate(["MANTER A PRISÃO", "PREVENTIVA"], 72, bg=E.PAPER, maxw=890), 540, 780)
            _marker(frame, "PARECER DA PGR", 540, 1160, 45, E.BLUE)
            _source(frame, "Agência Brasil · manifestação da PGR", 1510)
        else:
            _center(frame, _plate(["PARECER ≠ DECISÃO"], 71, bg=E.RED, fg=E.WHT, maxw=870), 540, 720)
            _arrow(frame, 540, 1010, 155, -90, E.BLUE)
            _center(frame, _plate(["CABE AO SUPREMO"], 61, bg=E.YEL, maxw=830), 540, 1280)
            _source(frame, "Agência Brasil · STF · Agência Senado", 1510)

    else:  # i == 9 · síntese e pergunta final
        if k == 0:
            _center(frame, _plate(["MENSAGEM", "RELATADA"], 68, bg=E.PAPER, maxw=840), 540, 850)
            _source(frame, "Fontes: UOL · Agência Brasil · STF", 1510)
        elif k == 1:
            _stamp(frame, "RELATÓRIO", 540, 730, 91, E.RED, -6)
            _center(frame, _plate(["EM REVISÃO"], 67, bg=E.YEL, maxw=760), 540, 1110)
            _source(frame, "Fontes: UOL · Agência Brasil · STF", 1510)
        elif k == 2:
            _center(frame, _plate(["DÚVIDAS", "EM ABERTO"], 84, bg=E.CYA, maxw=820), 540, 850)
            _center(frame, _icon("question", E.INK, E.RED), 540, 1230)
            _source(frame, "Fontes: UOL · Agência Brasil · STF", 1510)
        elif k == 3:
            _center(frame, _plate(["O QUE A NOVA", "VERSÃO PRECISA", "ESCLARECER?"], 73,
                                  bg=E.YEL, maxw=880), 540, 850)
            _marker(frame, "MAPA SUJO · EDIÇÃO 003", 540, 1290, 35, E.BLUE)
            _source(frame, "Fontes: UOL · Agência Brasil · STF · Agência Senado", 1510)
        else:
            _center(frame, _plate(["UMA MENSAGEM", "UM RELATÓRIO", "DÚVIDAS EM ABERTO"], 60,
                                  bg=E.PAPER, maxw=870), 540, 850)
            _source(frame, "Fontes: UOL · Agência Brasil · STF · Agência Senado", 1510)

    return frame


@lru_cache(maxsize=64)
def _scene_image(i, k):
    return _draw(i, k)


def _render_beat(i, lt):
    starts = SCENE_TIMES[i]
    idx = min(len(starts) - 1, max(0, bisect_right(starts, lt) - 1))
    age = max(0.0, lt - starts[idx])
    end = starts[idx + 1] if idx + 1 < len(starts) else E.T1[i] - E.T0[i]
    duration = max(.2, end - starts[idx])
    return _scene_image(i, idx), age, duration, idx


DYNAMIC_BEATS = {i: (lambda lt, i=i: _render_beat(i, lt)) for i in range(10)}

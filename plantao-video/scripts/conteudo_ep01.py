#!/usr/bin/env python3
"""CONTEÚDO DO EPISÓDIO — copie este arquivo e reescreva os 10 blocos.

Mapa dos blocos (o beat sheet vem do beats.json):
   0 gancho        1 mapa        2 dinheiro    3 mapa (contagem)
   4 origem        5 número      6 lista       7 mapa (fronteira)
   8 resposta      9 CTA
Cada bloco de papel recebe uma base() e uma lista de camadas layers(i).
Cada bloco de mapa recebe uma função em MAP_BLOCKS.
"""
import os

import engine as E
from engine import (TB, PL, st, paper, photo, cut, xmark, L, MapCard,
                    lit_seq, lit_static, INK, RED, YEL, BLUE, CYA, WHT, PAPER, C, M)

IMG = f"{E.C.ASSETS}/img"
TAG = f"{E.C.MASTHEAD}  ·  EDIÇÃO {E.C.EDICAO:03d}"

ACCENT = {0: YEL, 1: RED, 2: YEL, 3: YEL, 4: YEL, 5: RED, 6: CYA, 7: RED, 8: YEL, 9: YEL}

_CACHE = {}


# ------------------------------------------------------------------ blocos de papel
def base(i):
    if i == 5:                      # número forte: foto sangrada + vinheta
        im = C.cover(C.load(f"{IMG}/barricade.jpg"), E.W, E.H).convert("RGBA")
        ov = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
        d = E.ImageDraw.Draw(ov)
        for y in range(E.H):
            k = max(0.0, (y - 900) / 1020.0)
            d.line([(0, y), (E.W, y)], fill=(8, 8, 10, int(150 * k ** 1.4)))
        for y in range(0, 620):
            k = 1 - y / 620.0
            d.line([(0, y), (E.W, y)], fill=(8, 8, 10, int(140 * k ** 1.3)))
        return E.Image.alpha_composite(im, ov)
    b = paper(11 + i * 7)
    veil = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    E.ImageDraw.Draw(veil).rectangle([0, 292, E.W, E.H], fill=PAPER + (205,))
    b.alpha_composite(veil)
    return b


def layers(i):
    if i in _CACHE:
        return _CACHE[i]

    if i == 0:                      # GANCHO: manchete + foto + carimbo + caneta
        head = PL(TB(["EUA BOTAM", "O PCC E O CV", "NA LISTA DE", "TERRORISTAS"], 92), 34, 26)
        head = st(head, -1.4)
        ph = cut(photo(f"{IMG}/barricade.jpg", 790, 460, bright=1.12), 3, ("bottom",), (2, 0, 0))
        ph = st(ph, 1.8)
        out = [L(head, 540, 600, 0.0, .6),
               L(ph, 540, 1170, 0.25, 1.2),
               L(st(C.stamp("CONFIRMADO", 66, RED, -12), 0), 700, 940, 1.9),
               L(st(C.marker("e na prática, nada mudou", 44, RED, -4, YEL), 0), 540, 1540, 6.2, 1.5),
               L(C.emoji_sticker("1f525", 140), 900, 340, 3.4, 7)]

    elif i == 2:                    # DINHEIRO: cartela amarela + foto + carimbo
        ph = cut(photo(f"{IMG}/cash_table.jpg", 720, 470), 5, ("bottom",), (1, 0, 0))
        ph = st(ph, -1.6)
        big = PL(TB(["R$ 190,3", "MILHÕES"], 118, INK, "Anton.ttf"), 30, 14, YEL)
        big = st(big, -3.2)
        sub = PL(TB(["que a AGU quer confiscar", "AGORA"], 38, INK, "Oswald.ttf", 600), 20, 12)
        sub = st(sub, 1.4)
        out = [L(ph, 540, 690, .2, 1.0),
               L(sub, 545, 1470, 3.3, 1.0),
               L(st(C.stamp("CONFISCO", 58, RED, -13), 0), 800, 1010, 4.5),
               L(C.emoji_sticker("1f4b0", 168), 210, 960, 5.2, 6)]

    elif i == 4:                    # ORIGEM: presídio + dois cartões de ano
        title = st(PL(TB(["COMEÇOU NO", "PRESÍDIO"], 84), 26, 14), -1.2)
        ph = st(cut(photo(f"{IMG}/prison.jpg", 660, 430), 7, ("bottom",), (2, 1, 0)), 1.5)
        a = st(PL(TB(["PCC", "1993"], 74, INK, "Anton.ttf"), 26, 10, YEL), -5)
        b = st(PL(TB(["CV", "1979"], 74, WHT, "Anton.ttf"), 26, 10, RED), 4)
        out = [L(title, 540, 470, .15, .5),
               L(ph, 540, 930, 1.9, 1.0),
               L(a, 330, 1330, 3.7, 3),
               L(b, 760, 1360, 5.2, 3),
               L(st(C.marker("a rua é consequência", 42, BLUE, -3), 0), 540, 1580, 6.6)]

    elif i == 5:                    # NÚMERO: 1/3 em disco amarelo
        disc = C.disc(215, YEL, 240)
        one = TB(["1/3"], 210, INK, "Anton.ttf")
        disc.alpha_composite(one, ((disc.width - one.width) // 2,
                                   (disc.height - one.height) // 2 - 8))
        lab = st(PL(TB(["DO RIO É ÁREA", "DE FACÇÃO"], 62, WHT, "Anton.ttf"), 22, 10, RED), 1.4)
        out = [L(st(disc, -7), 400, 760, .6, 3.0),
               L(lab, 560, 1240, 1.6, 1.2),
               L(C.marker_circle(250, 250, RED, 11, -5), 400, 760, 2.5, 2.0),
               L(C.emoji_sticker("1f440", 140), 890, 560, 1.1, 7)]

    elif i == 6:                    # LISTA: quatro mordidas numeradas
        title = st(PL(TB(["A LISTA COMEÇA", "A MORDER"], 66, INK, "Anton.ttf"), 26, 12), -1.6)
        rows = [("BANCO CONGELA", YEL, INK, 2.0, -2.0),
                ("DOAÇÃO VIRA CRIME", WHT, INK, 3.8, 1.8),
                ("PASSAGEM SOME", CYA, INK, 5.6, -1.4),
                ("EXTRADIÇÃO FICA FÁCIL", RED, WHT, 7.2, 1.2)]
        out = [L(title, 540, 400, .2, .5)]
        for k, (txt, bg, fg, pop, ang) in enumerate(rows):
            bar = PL(TB([txt], 52, fg, "Oswald.ttf", 600, maxw=740), 22, 12, bg)
            dnum = C.disc(40, INK, 255)
            nn = TB([f"{k + 1}"], 46, WHT, "Anton.ttf")
            dnum.alpha_composite(nn, ((dnum.width - nn.width) // 2,
                                      (dnum.height - nn.height) // 2 - 6))
            row = E.Image.new("RGBA", (bar.width + dnum.width - 18, max(bar.height, dnum.height)),
                              (0, 0, 0, 0))
            row.alpha_composite(bar, (dnum.width - 18, 0))
            row.alpha_composite(dnum, (0, (row.height - dnum.height) // 2))
            out.append(L(st(row, ang), 540 + (18 if k % 2 else -14), 740 + k * 250, pop, 2.0))

    elif i == 9:                    # CTA
        big = st(PL(TB(["COMENTA AÍ"], 124, INK, "Anton.ttf"), 30, 12, YEL), -2.2)
        q = st(PL(TB(["o que VOCÊ faria?"], 66), 24, 12), 1.5)
        nxt = PL(TB(["PARTE 2 AMANHÃ", "· MESMA HORA ·"], 34, WHT, "Oswald.ttf", 600), 20, 12, INK)
        out = [L(big, 540, 620, .2, 1.2),
               L(q, 540, 880, .9, 1.0),
               L(st(C.marker_arrow(300, 90, RED, 0), -90), 540, 1180, 1.6, 3),
               L(nxt, 540, 1520, 2.6, 0.8),
               L(C.emoji_sticker("1f440", 130), 850, 1060, 3.4, 6)]

    else:
        out = []
    _CACHE[i] = out
    return out


# ------------------------------------------------------------------ blocos de mapa
_MAPS = {}


def m1(frame, lt):                  # mapa apagado + X no Rio
    z, cx, cy = M.FULL[2] * 1.02, M.FULL[0], M.FULL[1]
    M.CARD = (840, 780)
    mimg, cam = M.map_frame([], z, cx, cy)
    card = _MAPS.get(1) or MapCard(840, 780, -4.0, (540, 1120), 4)
    _MAPS[1] = card
    card.draw(frame, mimg)
    a = C.ease(min(1, max(0, (lt - .5) / .3)))
    X = xmark(int(180 * (.6 + .4 * a)), RED, 15, 6)
    px, py = card.c2f(*M.proj(-42.4, -22.4), cam)
    frame.alpha_composite(X, (int(px - X.width / 2), int(py - X.height / 2)))
    ttl = PL(TB(["NÃO ATACA", "ONDE VOCÊ", "PENSA"], 78), 24, 12, RED)
    frame.alpha_composite(st(ttl, -2.0), (int(60 - 20 * (1 - a)), 300))
    cap = PL(TB(["área de atuação do CV · mapa ilustrativo"], 24, INK, "Oswald.ttf", 500), 12, 6)
    frame.alpha_composite(cap, (70, 1660))
    return frame


def m3(frame, lt):                  # 26 de 27 acendendo com contador
    M.CARD = (900, 840)
    lit = lit_seq(lt, .18, .105, .15)
    mimg, cam = M.map_frame(lit, 1.03 * M.FULL[2], M.FULL[0], M.FULL[1])
    card = _MAPS.get(3) or MapCard(900, 840, -3.5, (540, 1140), 6)
    _MAPS[3] = card
    card.draw(frame, mimg)
    n = sum(1 for s, a in lit if a > .5)
    cnt = PL(TB([f"{n:02d}/27"], 84, WHT, "Anton.ttf"), 18, 8, RED)
    frame.alpha_composite(st(cnt, 5), (int(E.W - cnt.width - 24), 296))
    cap = PL(TB(["estados com CV"], 22, INK, "Oswald.ttf", 400), 10, 4)
    frame.alpha_composite(cap, (int(E.W - cap.width - 16), 296 + cnt.height - 8))
    ttl = PL(TB(["26 DE 27", "ESTADOS"], 62, INK, "Anton.ttf"), 22, 10, YEL)
    k = C.ease(min(1, lt / .4))
    frame.alpha_composite(st(ttl, -2.4), (int(22 + 14 * k), 292))
    return frame


def m7(frame, lt):                  # fronteira: seta entrando da Bolívia
    e = C.ease(min(1, lt / 6.0))
    z = 2.15 + .30 * e
    cx, cy = M.proj(-55.2, -19.8)
    M.CARD = (880, 900)
    mimg, cam = M.map_frame(lit_static(["MS", "MT", "RO", "AC", "AM"], lt, alpha=.55), z, cx, cy)
    card = _MAPS.get(7) or MapCard(880, 900, 2.4, (540, 1010), 8)
    _MAPS[7] = card
    card.draw(frame, mimg)
    a = C.ease(min(1, max(0, (lt - .35) / .35)))
    if lt > .45:
        frame.alpha_composite(C.marker("BOLÍVIA", 46, BLUE, -9), (96, 1240))
    ar = C.marker_arrow(430, 120, RED, -8)
    frame.alpha_composite(ar, (int(card.pos[0] - 470 + 120 * a), int(card.pos[1] + 30)))
    if lt > 2.5:
        t1 = PL(TB(["O FUZIL VEM", "DA FRONTEIRA"], 64, WHT, "Anton.ttf"), 22, 10, RED)
        frame.alpha_composite(st(t1, -2.2), (34, 286))
    if lt > 4.1:
        t2 = PL(TB(["E CONTINUA ABERTA"], 54, INK, "Anton.ttf"), 20, 8, YEL)
        frame.alpha_composite(st(t2, 1.8), (70, 1500))
    return frame


def m8(frame, lt):                  # resposta: mapa cheio apagado + as duas frases
    e = C.ease(min(1, lt / 6.4))
    z = M.FULL[2] * (1.22 - .16 * e)
    M.CARD = (940, 880)
    mimg, cam = M.map_frame(lit_seq(lt, .0, .0, .01, alpha=.22), z, M.FULL[0], M.FULL[1])
    card = _MAPS.get(8) or MapCard(940, 880, -2.0, (540, 1160), 10)
    _MAPS[8] = card
    card.draw(frame, mimg)
    if lt > 1.8:
        t1 = PL(TB(["NÃO É A ESQUINA."], 62, INK, "Anton.ttf"), 22, 10, PAPER)
        frame.alpha_composite(st(t1, -1.6), (50, 320))
    if lt > 3.7:
        t2 = PL(TB(["É O DINHEIRO", "QUE PAGA A ESQUINA."], 58, INK, "Anton.ttf", lead=1.02),
                22, 10, YEL)
        frame.alpha_composite(st(t2, 1.4), (40, 1470))
    return frame


def _counter(comp, lt):             # contador: o valor sobe de 0 até 190,3
    if lt < 1.1:
        return
    v = 190.3 * C.ease(min(1, (lt - 1.1) / 1.35))
    big = st(PL(TB([("R$ %.1f" % v).replace(".", ","), "MILHÕES"], 118, INK, "Anton.ttf"), 30, 14, YEL), -3.2)
    comp.alpha_composite(big, (520 - big.width // 2, 1200 - big.height // 2))


# duração de cada bloco na gravação ORIGINAL desta versão do conteúdo.
# Se você regravar a narração, o motor reescala estes tempos sozinho.
REF = {0: 9.601, 2: 6.884, 4: 8.021, 5: 4.535, 6: 8.630, 9: 5.636}

PER_FRAME = {2: _counter}

CAPTIONS = {
    0: ["os EUA botaram o PCC e o CV", "na lista de terroristas", "e na esquina não mudou nada"],
    1: ["eles não atacam onde você pensa"],
    2: ["190 milhões que a AGU quer confiscar"],
    3: ["26 estados de 27"],
    4: ["começou no presídio", "PCC 93, CV 79"],
    5: ["1 em cada 3 metros do Rio"],
    6: ["banco congela", "doação vira crime", "passagem some", "extradição fácil"],
    7: ["o fuzil vem da fronteira"],
    8: ["não é a esquina", "é o dinheiro que paga a esquina"],
    9: ["pega o dinheiro ou a manchete?"],
}

MAP_BLOCKS = {1: m1, 3: m3, 7: m7, 8: m8}

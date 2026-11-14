#!/usr/bin/env python3
"""CONTEÚDO — EDIÇÃO 002: o aluguel do crime.

Todos os pops são ancorados na palavra falada (W), nunca em segundo fixo:
se a narração mudar, a imagem continua entrando junto com a fala.

   0 gancho     1 mapa (PB)    2 dinheiro   3 mapa (13 estados)  4 origem
   5 mapa (250) 6 lista        7 receita    8 mapa (resposta)    9 CTA
"""
import os

import engine as E
from engine import (TB, PL, st, paper, photo, cut, xmark, L, MapCard,
                    lit_static, AT, INK, RED, YEL, BLUE, CYA, WHT, PAPER, C, M)

IMG = f"{E.C.ASSETS}/img"
ED = os.path.dirname(os.path.abspath(__file__))
TAG = f"{E.C.MASTHEAD}  ·  EDIÇÃO {E.C.EDICAO:03d}"

ACCENT = {0: YEL, 1: RED, 2: YEL, 3: YEL, 4: CYA, 5: RED, 6: YEL, 7: RED, 8: YEL, 9: YEL}

# 13 estados com operações contra o CV (Folha, jan-out 2026)
UFS = ["AC", "BA", "CE", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "RJ", "RN", "SP"]

_CACHE = {}


def base(i):
    if i == 7:                       # RECEITA: dinheiro sangrado + vinheta
        im = C.cover(C.load(f"{IMG}/cash_table.jpg"), E.W, E.H).convert("RGBA")
        ov = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
        d = E.ImageDraw.Draw(ov)
        for y in range(E.H):
            k = max(0.0, (y - 820) / 1100.0)
            d.line([(0, y), (E.W, y)], fill=(8, 8, 10, int(165 * k ** 1.3)))
        for y in range(0, 560):
            k = 1 - y / 560.0
            d.line([(0, y), (E.W, y)], fill=(8, 8, 10, int(150 * k ** 1.3)))
        return E.Image.alpha_composite(im, ov)
    b = paper(21 + i * 7)
    veil = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    E.ImageDraw.Draw(veil).rectangle([0, 292, E.W, E.H], fill=PAPER + (205,))
    b.alpha_composite(veil)
    return b


def layers(i):
    if i in _CACHE:
        return _CACHE[i]

    if i == 0:                       # GANCHO
        head = st(PL(TB(["DESPEJO", "EM DEZ", "MINUTOS"], 108), 36, 26), -1.4)
        ph = st(cut(photo(f"{ED}/casa.jpg", 800, 470, bright=1.08), 3, ("bottom",), (2, 0, 0)), 1.6)
        out = [L(head, 540, 610, 0.0, .6),
               L(ph, 540, 1180, 0.18, 1.2),
               L(st(C.stamp("250 FAMÍLIAS", 52, RED, -11), 0), 690, 930, AT(0, "250"), 1.4),
               L(st(C.marker("o motivo não era droga", 42, BLUE, -3), 0),
                 540, 1545, AT(0, "droga"), 1.5),
               L(C.emoji_sticker("1f6a8", 140), 900, 350, AT(0, "sacolas"), 7)]

    elif i == 2:                     # O NÚMERO
        ph = st(cut(photo(f"{IMG}/cash_table.jpg", 730, 460), 5, ("bottom",), (1, 0, 0)), -1.6)
        big = st(PL(TB(["R$ 7", "BILHÕES"], 118, INK, "Anton.ttf"), 30, 14, YEL), -3.0)
        sub = st(PL(TB(["bloqueados na Bahia", "em dez meses"], 36, INK, "Oswald.ttf", 600), 20, 12), 1.4)
        out = [L(ph, 540, 700, .15, 1.0),
               L(big, 540, 1180, AT(2, "sete"), 1.0),
               L(sub, 545, 1490, AT(2, "bloqueados"), 1.0),
               L(st(C.stamp("BLOQUEADO", 54, RED, -12), 0), 800, 1020, AT(2, "Bahia")),
               L(C.emoji_sticker("1f4b0", 160), 215, 980, AT(2, "bens"), 6)]

    elif i == 4:                     # ORIGEM: a taxa que cresce
        title = st(PL(TB(["A TAXA", "QUE CRESCE"], 78), 26, 14), -1.2)
        rows = [("1", "TAXA DO GÁS", YEL, INK, AT(4, "gás"), -2.2),
                ("2", "INTERNET", CYA, INK, AT(4, "internet"), 1.8),
                ("3", "ALUGUEL DA CASA", RED, WHT, AT(4, "aluguel"), -1.4)]
        out = [L(title, 540, 470, .15, .5)]
        for k, (num, txt, bg, fg, pop, ang) in enumerate(rows):
            out.append(L(st(PL(TB([txt], 58, fg, "Anton.ttf", maxw=820), 22, 12, bg), ang),
                         540 + (10 if k % 2 else -10), 800 + k * 270, pop, 1.6))
        out += [L(st(C.marker("a mesma lógica, cada vez maior", 40, BLUE, -3), 0),
                 540, 1600, AT(4, "lógica"), 1.4)]

    elif i == 6:                     # LISTA
        title = st(PL(TB(["A CONTA", "DO MÊS"], 74, INK, "Anton.ttf"), 26, 12), -1.6)
        rows = [("ALUGUEL PRA MORAR", YEL, INK, AT(6, "morar"), -1.8),
                ("TAXA PRA TRABALHAR", WHT, INK, AT(6, "trabalhar"), 1.6),
                ("PROVEDOR NÃO OPERA", CYA, INK, AT(6, "provedor"), -1.2),
                ("OBRA SÓ PAGANDO", RED, WHT, AT(6, "obra"), 1.4)]
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

    elif i == 7:                     # VIRADA: é receita
        big = st(PL(TB(["É RECEITA."], 128, INK, "Anton.ttf"), 30, 10, YEL), -2.4)
        mk = st(C.marker("não cai com viatura", 52, WHT, -4, RED), 0)
        kick = st(PL(TB(["NÃO É BRIGA DE RUA"], 44, WHT, "Oswald.ttf", 600), 18, 10, RED), -2.0)
        out = [L(kick, 540, 430, AT(7, "briga"), 0.9),
               L(big, 540, 720, AT(7, "receita"), 1.2),
               L(mk, 540, 1320, AT(7, "viatura"), 1.5),
               L(C.emoji_sticker("1f4b8", 150), 880, 1000, AT(7, "receita") + 0.5, 6)]

    elif i == 9:                     # CTA — a pergunta abre a cena, o comando entra na palavra
        q = st(PL(TB(["você paga taxa pra", "trabalhar onde mora?"], 58), 24, 12), 1.5)
        big = st(PL(TB(["COMENTA AÍ"], 116, INK, "Anton.ttf"), 30, 12, YEL), -2.2)
        ass = PL(TB([f"{E.C.MASTHEAD} · EDIÇÃO {E.C.EDICAO:03d}"], 30, WHT, "Oswald.ttf", 600),
                 20, 12, INK)
        out = [L(q, 540, 900, 0.10, 0.9),
               L(big, 540, 520, AT(9, "paga"), 1.2),
               L(st(C.marker_arrow(300, 90, RED, 0), -90), 540, 1310, AT(9, "mora"), 3),
               L(ass, 540, 1560, AT(9, "Comenta"), 0.8),
               L(C.emoji_sticker("1f440", 130), 862, 1180, AT(9, "Comenta") + 0.2, 6)]

    else:
        out = []
    _CACHE[i] = out
    return out


# ------------------------------------------------------------------ mapas
_MAPS = {}


def m1(frame, lt):                   # Paraíba: onde os despejos aconteceram
    z = M.FULL[2] * 1.03
    M.CARD = (860, 800)
    mimg, cam = M.map_frame([], z, M.FULL[0], M.FULL[1])
    card = _MAPS.get(1) or MapCard(860, 800, -4.0, (540, 1130), 4)
    _MAPS[1] = card
    card.draw(frame, mimg)
    a = C.ease(min(1, max(0, (lt - AT(1, "chegou")) / .3)))
    X = xmark(int(190 * (.55 + .45 * a)), RED, 15, 6)
    px, py = card.c2f(*M.proj(-34.86, -7.12), cam)
    frame.alpha_composite(X, (int(px - X.width / 2), int(py - X.height / 2)))
    ttl = PL(TB(["NÃO É", "TRÁFICO.", "É COBRANÇA."], 66, WHT, "Anton.ttf"), 24, 12, RED)
    frame.alpha_composite(st(ttl, -2.0), (56, 300))
    cap = PL(TB(["Paraíba · Bayeux · 250 famílias (MP-PB)"], 24, INK, "Oswald.ttf", 500), 12, 6)
    frame.alpha_composite(cap, (70, 1660))
    return frame


def m3(frame, lt):                   # 13 estados acendendo, contador fecha na fala
    fim = max(0.8, AT(3, "estados"))  # o 13º estado acende quando a voz diz "estados"
    step = (fim - 0.15) / len(UFS)
    lit = []
    for k, sig in enumerate(UFS):
        on = 0.10 + step * k
        if lt > on:
            lit.append((sig, min(1.0, (lt - on) / .15)))
    M.CARD = (900, 840)
    mimg, cam = M.map_frame(lit, 1.03 * M.FULL[2], M.FULL[0], M.FULL[1])
    card = _MAPS.get(3) or MapCard(900, 840, -3.5, (540, 1140), 6)
    _MAPS[3] = card
    card.draw(frame, mimg)
    n = sum(1 for s, a in lit if a > .5)
    cnt = PL(TB([f"{n:02d}/27"], 84, WHT, "Anton.ttf"), 18, 8, RED)
    frame.alpha_composite(st(cnt, 5), (int(E.W - cnt.width - 24), 296))
    cap = PL(TB(["estados com operação"], 22, INK, "Oswald.ttf", 400), 10, 4)
    frame.alpha_composite(cap, (int(E.W - cap.width - 16), 296 + cnt.height - 8))
    ttl = PL(TB(["16 OPERAÇÕES", "13 ESTADOS"], 54, INK, "Anton.ttf"), 22, 10, YEL)
    k = C.ease(min(1, lt / .4))
    frame.alpha_composite(st(ttl, -2.4), (int(22 + 14 * k), 292))
    return frame


def m5(frame, lt):                   # zoom em Bayeux: uma cidade, 250 famílias
    e = C.ease(min(1, lt / 4.5))
    z = 1.48 + 0.52 * e
    cx, cy = M.proj(-36.2, -7.6)
    M.CARD = (900, 880)
    mimg, cam = M.map_frame(lit_static(["PB"], lt, alpha=.75), z, cx, cy)
    card = _MAPS.get(5) or MapCard(900, 880, 2.2, (540, 1050), 8)
    _MAPS[5] = card
    card.draw(frame, mimg)
    if lt > 0.15:
        frame.alpha_composite(C.marker("Bayeux", 46, BLUE, -9), (96, 1240))
    d = C.disc(150, YEL, 245)
    num = TB(["250"], 118, INK, "Anton.ttf")
    d.alpha_composite(num, ((d.width - num.width) // 2, (d.height - num.height) // 2 - 8))
    if lt > AT(5, "250"):
        frame.alpha_composite(st(d, -6), (90, 300))
    if lt > AT(5, "famílias"):
        lab = PL(TB(["FAMÍLIAS", "EXPULSAS"], 46, WHT, "Anton.ttf"), 18, 8, RED)
        frame.alpha_composite(st(lab, 1.6), (56, 640))
    cap = PL(TB(["estimativa do MP-PB · mapa ilustrativo"], 22, INK, "Oswald.ttf", 500), 10, 4)
    frame.alpha_composite(cap, (70, 1660))
    return frame


def m8(frame, lt):                   # resposta: a casa não, a renda sim
    e = C.ease(min(1, lt / 6.0))
    z = M.FULL[2] * (1.20 - .14 * e)
    M.CARD = (940, 880)
    mimg, cam = M.map_frame(lit_static(UFS, lt, fade=.4, alpha=.30), z, M.FULL[0], M.FULL[1])
    card = _MAPS.get(8) or MapCard(940, 880, -2.0, (540, 1160), 10)
    _MAPS[8] = card
    card.draw(frame, mimg)
    if lt > AT(8, "casa"):
        t1 = PL(TB(["NÃO QUEREM", "A SUA CASA."], 58, INK, "Anton.ttf"), 22, 10, PAPER)
        frame.alpha_composite(st(t1, -1.6), (50, 320))
    if lt > AT(8, "renda"):
        t2 = PL(TB(["QUEREM", "A SUA RENDA."], 58, INK, "Anton.ttf"), 22, 10, YEL)
        frame.alpha_composite(st(t2, 1.4), (40, 1480))
    return frame


MAP_BLOCKS = {1: m1, 3: m3, 5: m5, 8: m8}

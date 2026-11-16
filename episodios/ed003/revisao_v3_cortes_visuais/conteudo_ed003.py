#!/usr/bin/env python3
"""Edição 003 — revisão V3 com a identidade visual aprovada de MAPA SUJO.

Usa o motor original (engine.py): papel de jornal, recortes com borda rasgada,
cartelas inclinadas, carimbos, quadros de mapa/diagrama e ticker. Fotografias
reais aparecem como recortes editoriais com identificação e crédito visíveis.
"""
import os
from functools import lru_cache

import engine_ritmo as E
from engine_ritmo import TB, PL, st, paper, photo, L, PAPER, INK, RED, YEL, BLUE, CYA, WHT

C, M = E.C, E.M
HERE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(HERE, "assets", "photos")
DANIEL = os.path.join(PHOTOS, "daniel_vorcaro_claudio_gatti.webp")
MORAES = os.path.join(PHOTOS, "alexandre_moraes_victor_piemonte_stf.jpg")
GONET = os.path.join(PHOTOS, "paulo_gonet_agencia_senado.jpg")

TAG = f"{C.MASTHEAD} · EDIÇÃO {C.EDICAO:03d}"
ACCENT = {0: YEL, 1: RED, 2: CYA, 3: YEL, 4: RED,
          5: CYA, 6: RED, 7: YEL, 8: CYA, 9: YEL}
MAP_BLOCKS = {}


def _center(frame, im, x, y):
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _photo_cut(path, w, h, seed, tape_color=YEL, bright=1.0):
    raw = photo(path, w, h, color=True, bright=bright)
    return C.paper_cut(raw, seed=seed, border=14, torn=("bottom",), shadow=26,
                       tape_corner=(-7 if seed % 2 else 7, int(w * .34), -12),
                       tape_color=tape_color)


def _source(text, size=23):
    return PL(TB([text], size, INK, "Oswald.ttf", 500, maxw=920), 12, 6, PAPER)


def _paper_card(lines, size, color=INK, plate=PAPER, font="Playfair.ttf", maxw=850,
                padx=28, pady=18, angle=0):
    im = PL(TB(lines, size, color, font, 900, maxw=maxw), padx, pady, plate)
    return st(im, angle) if angle else im


def base(i):
    """Página-base da série, preservando o cabeçalho e suavizando texto de fundo."""
    frame = paper(181 + i * 13).convert("RGBA")
    veil = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    E.ImageDraw.Draw(veil).rectangle((0, 292, E.W, E.H - 125), fill=PAPER + (190,))
    frame.alpha_composite(veil)
    return frame


@lru_cache(maxsize=10)
def layers(i):
    """Recortes e cartelas por bloco; entradas ancoradas às palavras do áudio."""
    if i == 0:
        headline = _paper_card(["MORAES VAI", "VOTAR A FAVOR?"], 100, maxw=870,
                               padx=30, pady=23, angle=-1.4)
        portrait = st(_photo_cut(DANIEL, 790, 470, 301, RED, 1.05), -1.2)
        stamp = C.stamp("MENSAGEM ATRIBUÍDA", 47, RED, -8)
        not_proof = st(PL(TB(["NÃO É PROVA"], 50, WHT, "Anton.ttf", 800, maxw=600),
                          18, 10, RED), 2.0)
        return [
            L(headline, 540, 510, 0.0, 0.8),
            L(_source("UOL · reportagem de 13/11/2026", 24), 540, 665, 0.04, 0.5),
            L(portrait, 540, 1135, 0.24, 1.0),
            L(stamp, 720, 880, E.AT(0, "mensagem"), 1.2),
            L(not_proof, 540, 1510, E.AT(0, "Não"), 0.7),
            L(_source("Arquivo · Claudio Gatti/Divulgação", 22), 540, 1648,
              E.AT(0, "Daniel") + 0.25, 0.4),
        ]

    if i == 2:
        quote = st(_paper_card(["“CÁSSIO VAI VOTAR", "A FAVOR. E MORAES.”"], 67,
                               maxw=860, padx=25, pady=18, angle=-1.8), -1.0)
        tail = st(PL(TB(["“VAI SER APERTADO, MAS VAMOS.”"], 37, INK,
                        "Oswald.ttf", 700, maxw=790), 20, 12, YEL), 1.7)
        label = C.stamp("TRECHO ATRIBUÍDO", 50, RED, -7)
        source = _source("Segundo reportagem do UOL · 13/11/2026", 23)
        return [
            L(quote, 540, 610, 0.05, 0.6),
            L(tail, 540, 950, E.AT(2, "apertado"), 0.8),
            L(label, 540, 1185, E.AT(2, "reportagem") + 0.35, 1.0),
            L(st(_photo_cut(DANIEL, 570, 280, 302, CYA, 1.0), 1.0), 540, 1370,
              E.AT(2, "Moraes") + 0.25, 0.5),
            L(source, 540, 1595, E.AT(2, "reportagem") + 0.5, 0.4)
        ]

    if i == 4:
        portrait = st(_photo_cut(MORAES, 400, 560, 401, CYA, 1.02), 1.0)
        headline = st(_paper_card(["INTERESSE", "NÃO É PROVA"], 76, maxw=430,
                                  padx=23, pady=17, plate=YEL, font="Anton.ttf", angle=-2.0), -1.0)
        label = C.marker("CONTEXTO ≠ CONCLUSÃO", 34, RED, -4, highlight=YEL)
        return [
            L(headline, 790, 555, E.AT(4, "Esse contexto"), 0.7),
            L(portrait, 260, 1050, E.AT(4, "Moraes") - 0.12, 0.8),
            L(label, 780, 1095, E.AT(4, "prova") - 0.08, 0.7),
            L(_source("Victor Piemonte/STF · domínio público", 21), 540, 1570,
              E.AT(4, "Moraes") + 0.35, 0.4),
        ]

    if i == 6:
        headline = st(_paper_card(["PF MANDA REFAZER", "RELATÓRIOS"], 87, maxw=850,
                                  padx=28, pady=18, plate=YEL, font="Anton.ttf", angle=-1.3), -1.2)
        sub = st(PL(TB(["EXCESSO DE ESCOPO E DESCRIÇÃO"], 41, WHT,
                       "Oswald.ttf", 700, maxw=850), 19, 11, RED), 1.3)
        stamp = C.stamp("EM REVISÃO", 68, RED, -8)
        caution = _source("A revisão não confirma nem afasta a suspeita · UOL", 22)
        return [
            L(headline, 540, 580, E.AT(6, "A cúpula"), 0.8),
            L(sub, 540, 950, E.AT(6, "escopo") - 0.12, 0.7),
            L(stamp, 540, 1240, E.AT(6, "relatórios") + 0.35, 1.1),
            L(st(C.marker("NÃO É CONCLUSÃO", 41, INK, -3, highlight=YEL), -1),
              540, 1455, E.AT(6, "suspeita") - 0.12, 0.6),
            L(caution, 540, 1660, E.AT(6, "PF") + 0.25, 0.4),
        ]

    if i == 7:
        headline = st(_paper_card(["QUEM RESPONDEU?"], 91, maxw=820, padx=28, pady=18,
                                  plate=YEL, font="Anton.ttf", angle=-1.7), -1.4)
        rows = [
            st(PL(TB(["MORAES · DEFESA · PF"], 38, INK, "Oswald.ttf", 700, maxw=820),
                  18, 10, PAPER), -1.2),
            st(PL(TB(["SEM RESPOSTA ATÉ 13/11"], 40, WHT, "Anton.ttf", 700, maxw=850),
                  20, 12, RED), 1.0),
            st(PL(TB(["FÁBIO FARIA: “NÃO TINHA RELAÇÃO”"], 32, INK,
                     "Oswald.ttf", 700, maxw=850), 18, 10, CYA), -1.5),
        ]
        return [
            L(headline, 540, 485, 0.0, 0.7),
            L(rows[0], 540, 850, E.AT(7, "Moraes") - 0.1, 0.6),
            L(rows[1], 540, 1110, E.AT(7, "não") - 0.08, 0.7),
            L(rows[2], 540, 1390, E.AT(7, "Fábio") - 0.08, 0.6),
            L(_source("UOL · publicação de 13/11/2026", 22), 540, 1648,
              E.AT(7, "UOL") + 0.28, 0.4),
        ]

    if i == 9:
        headline = st(_paper_card(["O QUE A NOVA VERSÃO", "PRECISA ESCLARECER?"], 75,
                                  maxw=875, padx=28, pady=20, plate=YEL,
                                  font="Anton.ttf", angle=-1.4), -1.2)
        tags = [
            st(PL(TB(["MENSAGEM RELATADA"], 38, INK, "Oswald.ttf", 700, maxw=800),
                  20, 12, PAPER), -2.0),
            st(PL(TB(["RELATÓRIO EM REVISÃO"], 38, WHT, "Anton.ttf", 700, maxw=800),
                  20, 12, RED), 1.5),
            st(PL(TB(["DÚVIDAS EM ABERTO"], 38, INK, "Oswald.ttf", 700, maxw=800),
                  20, 12, CYA), -1.0),
        ]
        arrow = C.marker_arrow(130, 75, RED, -90)
        return [
            L(headline, 540, 490, 0.0, 0.7),
            L(tags[0], 540, 845, E.AT(9, "mensagem") - 0.1, 0.6),
            L(tags[1], 540, 1090, E.AT(9, "relatório") - 0.1, 0.6),
            L(tags[2], 540, 1335, E.AT(9, "dúvidas") - 0.1, 0.6),
            L(arrow, 540, 1490, E.AT(9, "esclarecer") - 0.1, 0.6),
            L(_source("Fontes: UOL · Agência Brasil · STF · Agência Senado", 21),
              540, 1595, E.AT(9, "versão") + 0.3, 0.4),
        ]

    # Blocos que têm visual de mapa/processo recebem seu desenho em MAP_BLOCKS.
    return []


def _map_title(lines, size=72, color=INK, plate=YEL, y=315, font="Anton.ttf"):
    art = st(PL(TB(lines, size, color, font, 800, maxw=900), 25, 15, plate), -1.5)
    return art, (540, y)


def _paper_tear(w, h, seed=1, angle=-2.5):
    raw = E.Image.new("RGBA", (w, h), PAPER + (255,))
    d = E.ImageDraw.Draw(raw)
    d.rectangle((3, 3, w - 4, h - 4), outline=INK + (95,), width=3)
    # A blank newsprint scrap leaves hierarchy to the cutout headline and stamps.
    return st(C.paper_cut(raw, seed=seed, border=10, torn=("bottom",), shadow=18,
                          tape_corner=(-7, int(w * .36), -10), tape_color=YEL), angle)


def _map_places(frame, lt):
    M.CARD = (830, 780)
    cx, cy, z = M.FULL
    img, cam = M.map_frame([("DF", 1.0)], z * 1.02, cx, cy)
    card = E.MapCard(830, 780, -3.2, (540, 1110), seed=82, tape=True)
    card.draw(frame, img)
    px, py = card.c2f(*M.proj(-47.8825, -15.7942), cam)
    mark = C.marker_circle(35, 35, RED, 9, -5)
    _center(frame, mark, px, py)
    pin_label = st(PL(TB(["STF · BRASÍLIA"], 31, INK, "Oswald.ttf", 700,
                         maxw=490), 15, 9, PAPER), -2)
    _center(frame, pin_label, px + 160, py - 100)
    title, pos = _map_title(["FEVEREIRO DE 2024"], 76, y=330)
    _center(frame, title, *pos)
    context = PL(TB(["Ação sobre cursos de medicina"], 29, INK,
                    "Oswald.ttf", 600, maxw=830), 18, 10, PAPER)
    _center(frame, context, 540, 1650)
    src = PL(TB(["Localização do STF · mapa ilustrativo"], 21, INK,
                "Oswald.ttf", 500, maxw=830), 12, 6, PAPER)
    _center(frame, src, 540, 1740)
    return frame


def _map_credit(frame, lt):
    title, pos = _map_title(["O VÍNCULO ECONÔMICO"], 72, y=330)
    _center(frame, title, *pos)
    # Relação descrita pela reportagem; as setas significam vínculo de crédito,
    # não comunicação, favorecimento ou interferência judicial.
    top = st(PL(TB(["BANCO MASTER"], 57, INK, "Anton.ttf", 800, maxw=720),
                25, 15, YEL), -2)
    middle = st(PL(TB(["ERA CREDOR DA"], 39, INK,
                      "Oswald.ttf", 700, maxw=800), 22, 12, PAPER), 1)
    bottom = st(PL(TB(["MANTENEDORA DA ULBRA"], 46, INK, "Anton.ttf", 800, maxw=780),
                   25, 15, CYA), -1.5)
    _center(frame, top, 540, 740)
    _center(frame, C.marker_arrow(100, 62, RED, -90), 540, 890)
    _center(frame, middle, 540, 1050)
    _center(frame, C.marker_arrow(100, 62, RED, -90), 540, 1215)
    _center(frame, bottom, 540, 1385)
    note = st(PL(TB(["MAIO/2024 · STF cria regra de transição", "para pedidos já avançados"],
                    31, INK, "Oswald.ttf", 700, maxw=850), 20, 12, PAPER), 1.2)
    _center(frame, note, 540, 1615)
    src = PL(TB(["UOL · contexto, não prova de combinação"], 21, WHT,
                "Oswald.ttf", 500, maxw=850), 12, 6, INK)
    _center(frame, src, 540, 1740)
    return frame


def _map_messages(frame, lt):
    title, pos = _map_title(["O QUE FOI RECUPERADO?"], 70, y=330)
    _center(frame, title, *pos)
    sheet = _paper_tear(900, 1070, seed=91, angle=-2.2)
    _center(frame, sheet, 540, 1110)

    first = st(TB(["MENSAGENS DE MORAES"], 50, INK,
                  "Anton.ttf", 700, maxw=790), -1.2)
    first_stamp = C.stamp("NÃO RECUPERADAS", 44, RED, -7)
    second = st(TB(["IMAGENS DE TEXTOS ENVIADAS", "POR VORCARO"], 40, INK,
                   "Anton.ttf", 700, maxw=790), 1.0)
    second_stamp = C.stamp("IDENTIFICADAS", 48, BLUE, 6)
    _center(frame, first, 455, 790)
    _center(frame, first_stamp, 620, 990)
    _center(frame, second, 600, 1220)
    _center(frame, second_stamp, 480, 1430)

    note = PL(TB(["ESQUEMA EDITORIAL · SEGUNDO O UOL"], 25, INK,
                 "Oswald.ttf", 600, maxw=850), 16, 9, YEL)
    _center(frame, note, 540, 1610)
    source = PL(TB(["As interações identificadas eram imagens de textos enviadas por Vorcaro"],
                   21, WHT, "Oswald.ttf", 500, maxw=900), 12, 6, INK)
    _center(frame, source, 540, 1710)
    return frame


def _map_pgr(frame, lt):
    title, pos = _map_title(["PARECER NÃO É DECISÃO"], 71, y=330)
    _center(frame, title, *pos)
    portrait = _photo_cut(GONET, 570, 390, 98, CYA, 1.02)
    _center(frame, st(portrait, -1.0), 370, 1010)
    credit = PL(TB(["Paulo Gonet · Agência Senado"], 21, INK,
                   "Oswald.ttf", 500, maxw=540), 12, 6, PAPER)
    _center(frame, credit, 370, 1265)
    pgr = st(PL(TB(["PGR"], 54, INK, "Anton.ttf", 800, maxw=410),
                20, 12, YEL), -1.0)
    opinion = st(PL(TB(["OPINA POR MANTER", "A PRISÃO PREVENTIVA"], 31,
                       INK, "Oswald.ttf", 700, maxw=420), 18, 12, PAPER), 1.0)
    supreme = st(PL(TB(["STF DECIDE"], 49, WHT, "Anton.ttf", 800, maxw=410),
                     20, 12, RED), -1.5)
    _center(frame, pgr, 790, 790)
    _center(frame, opinion, 790, 1030)
    _center(frame, C.marker_arrow(95, 58, RED, -90), 790, 1275)
    _center(frame, supreme, 790, 1450)
    note = PL(TB(["Parecer da PGR · não é decisão judicial"], 22, WHT,
                 "Oswald.ttf", 500, maxw=870), 12, 6, INK)
    _center(frame, note, 540, 1700)
    return frame


# As sequências alternam papel e quadros-objeto, como nas edições 001/002.
MAP_BLOCKS = {1: _map_places, 3: _map_credit, 5: _map_messages, 8: _map_pgr}

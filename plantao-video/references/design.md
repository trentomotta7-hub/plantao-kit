# Gramática visual

## Tela
1080×1920. Margem segura: nada importante acima de y=60 (a marca d'água do TikTok cobre) nem abaixo de y=1800 (ticker ocupa 60px no pé). Texto grande entre y=280 e y=1600.

## Paleta
| Uso | Cor | RGB |
|---|---|---|
| Papel | `PAPER` | 241,234,218 |
| Tinta | `INK` | 22,19,16 |
| Urgência | `RED` | 198,16,46 |
| Destaque | `YEL` | 255,213,58 |
| Frio/dado | `CYA` | 0,174,230 |
| Caneta | `BLUE` | 32,68,186 |
| Fundo de mapa | `M.DARK` | 11,14,12 |

Regra: cada bloco tem **uma** cor de acento (a do ticker). Papel claro = informação; fundo escuro = mapa.

## Tipografia
| Papel | Fonte | Tamanho | Onde |
|---|---|---|---|
| Manchete | Playfair 900 | 84–96 | blocos 1, 5 |
| Grito | Anton | 52–124 | cartelas, números, CTA |
| Legenda/dado | Oswald 400–600 | 22–52 | listas, legendas, ticker |
| Caneta | PermanentMarker | 40–46 | anotações à mão |

`TB(lines, size, ...)` encolhe sozinho para caber em `maxw`. **Sempre `lead >= 1.0`** em texto com Ã/Õ.

## Componentes

**Cartela (`PL`)** — papel colado: `with_plate` (sombra + ruído) + borda de 3px escura. É o tijolo de todo texto. `PL(TB([...]), padx=30, pady=22, color=YEL)`.

**Foto (`cut`)** — `photo()` dá meio-tom de jornal; `cut()` acrescenta borda branca, base rasgada, sombra e fita crepe opcional. Sempre torta (−2° a +2°).

**Carimbo (`C.stamp`)** — texto em Anton com moldura dupla e grunge. Vermelho, −12° a −8°. Usar 1 por bloco, no máximo.

**Caneta (`C.marker`)** — texto manuscrito com marca-texto amarelo opcional. É onde entra a opinião/emoji verbal ("e na prática, nada mudou"). 1 por bloco.

**Emoji (`C.emoji_sticker`)** — Twemoji com contorno branco e sombra. 1–2 por bloco, tamanho 130–190.

**Ticker** — faixa de 60px no pé, correndo a 235px/s, cor do bloco. É o que dá cara de "plantão".

**MapCard** — cartão de papel rasgado e torto em volta do mapa, com duas fitas. O mapa é renderizado em 1600×1600 e cortado na proporção do cartão (defina `M.CARD = (w, h)` **antes** de `M.map_frame`).

## Mapa: como dirigir
- `M.FULL` = enquadramento do Brasil inteiro; `M.SE` = sudeste.
- `M.map_frame(lit, zoom, cx, cy)` devolve `(imagem, cam)`; `cam` serve para `MapCard.c2f()` converter coordenada geográfica em pixel de tela (pinos, X, setas).
- `lit` é lista de `(sigla, alpha)`: `lit_seq(lt, t0, step)` acende em sequência (norte→sul), `lit_static([...])` acende fixo.
- `RR` fica apagado de propósito (`M.DARK_UF`): é o estado que falta para "26 de 27".
- Zoom 1.0 = Brasil inteiro; 2,1–2,5 = fronteira; 3+ = cidade.

## Movimento (o que dá dopamina)
1. **Pop**: cada elemento entra com escala 1,42→1,0 em 0,13s + tremida amortecida. É `L(im, x, y, pop, wob)`.
2. **Soco de câmera**: cada pop soma +0,032 de zoom por 0,17s (o motor faz sozinho).
3. **Push-in**: 1,035→1,12 ao longo do bloco, sempre devagar.
4. **Flash + aberração cromática** nos 0,07s de cada corte.
5. **Shake** de 9–11px nos primeiros 0,22s do bloco.

Sem esses cinco, o vídeo "fica parado" mesmo com texto bom.

## Ritmo de entrada por bloco
Bloco de 4s → 3 elementos (pops em 0,2 / 1,6 / 3,2). Bloco de 8s → 5 elementos. Nunca deixar 2,5s sem nada entrando. Os pops devem cair **na sílaba da informação**, não no meio da frase: alinhe com `beats.json` (`starts[i]` + deslocamento).

## Composição que funciona
- Papel: manchete no topo (y≈300–650), foto no meio (y≈900–1200), caneta/carimbo por cima das bordas.
- Mapa: cartão no centro-baixo (y≈1010–1160), título no topo (y≈290–420), legenda no pé (y≈1660).
- Nunca centralizar tudo: alternar esquerda/direita e rotação ±2° para parecer colado à mão.

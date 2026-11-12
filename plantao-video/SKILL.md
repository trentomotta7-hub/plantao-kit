---
name: plantao-video
description: Produz episódios verticais 9:16 em PT-BR de notícia criminal e crime organizado (break news) na estética colagem de jornal + mapa animado do Brasil, montados para retenção e monetização no TikTok. Use para criar vídeo de notícia policial, série de episódios sobre facções/PCC/Comando Vermelho, mapa explicativo animado com dados de estados, vídeo com cara de jornal colado, narração TTS com beat sheet, corte curto de 30s para Reels/Shorts.
---

# O PLANTÃO — fábrica de episódios

Vídeo vertical de 62–75s, 1080×1920, 30fps, em 10 blocos que alternam **página de jornal colada** e **mapa animado do Brasil**. O corte é a batida: flash + drop de áudio em cada virada. Custo padrão: **1 crédito por episódio** (só a narração; o resto é render determinístico).

## Edição, não capítulo
A série **não numera episódios** (MAPA 01, 02…). Notícia não é novela: numeração cria a sensação de "perdi os anteriores" em quem chega frio, e 80–90% do TikTok chega frio.
- O selo é de **edição**: `EDIÇÃO 007` na linha de data do jornal e no canto dos mapas. Coleção sem prometer continuação.
- Numere só quando a história **realmente** continua, e no título: `O DINHEIRO DO PCC · PARTE 2`. No máximo 3 partes, e o vídeo 2 re-explica o essencial nos 2 primeiros segundos.
- Proporção: 3 notícias soltas para cada continuação.
- No TikTok, a série mora na **playlist** do app, não no título.

Variáveis de edição (defina antes de renderizar):
| variável | efeito |
|---|---|
| `PLANTAO_NOME` | cabeçalho do jornal (padrão `MAPA SUJO`, encolhe sozinho se for longo) |
| `PLANTAO_EDICAO` | número da edição (padrão `1` → `EDIÇÃO 001`) |
| `PLANTAO_DATA` | data da linha de rosto (padrão a data do ep. 01) |

## Gancho: os 2 primeiros segundos
Manchete entra em **0.0** e a foto em **0.25** — a página nunca aparece vazia no primeiro frame. Carimbo em 1.9, emoji em 3.4. Só o `marker` (a frase que dói) fica ancorado no áudio.

## Regra de ouro
O Creator Rewards do TikTok exige vídeo com **mais de 1 minuto**. O mestre é sempre 62–75s. Corte de 30s é peça de alcance, não de monetização.

## Fluxo

### 1. Pauta (15 min)
Buscar notícia recente de crime organizado com **número forte** (valor confiscado, nº de estados, % de território, ano de fundação). Sem número, não vira episódio. Fontes e cuidados: `references/roteiro.md` §1.

### 2. Roteiro em 10 blocos
Escrever o texto falado em `roteiro.txt`, **uma linha por bloco**. A arquitetura (gancho → promessa → dinheiro → mapa → origem → número → consequências → fronteira → resposta → CTA) está em `references/roteiro.md` §2, com o exemplo real do ep. 01.

### 3. Narração (1 crédito)
Chamar `generate_speech` (voice `pt-br-techagent-4`, `pt-BR`, um turn por bloco, style `urgent, clear, conversational`; o último bloco pode ir `slower, emphatic`). Salvar como `vo_raw.wav`. O TTS sai rápido demais — **nunca use cru**.

### 4. Beat sheet (2 min)
```bash
python3 <skill>/scripts/dips.py --wav vo_raw.wav --textos roteiro.txt      # fronteiras
python3 <skill>/scripts/edit_vo.py --wav vo_raw.wav --bounds 7.70,11.74,... \
        --gaps 0.75,0.45,0.70,0.40,0.55,0.65,0.40,0.75,0.75                  # vo_edit.wav + beats.json
```
`--gaps` são os respiros: maiores (0.7–0.75) nas viradas de história, menores (0.4) entre blocos irmãos. O corte de imagem cai 0.10s antes da voz.

### 5. Conteúdo visual
```bash
cp <skill>/scripts/conteudo_ep01.py conteudo_ep02.py
```
Reescrever os 10 blocos: textos, fotos, cores e pops de cada cartela. Gramática visual, coordenadas e tempos em `references/design.md`. O motor (`engine.py`) não se mexe.

### 6. Render, mix e encode
```bash
python3 <skill>/scripts/serie.py conteudo_ep02.py --test      # 13 frames de conferência
python3 <skill>/scripts/serie.py conteudo_ep02.py             # ~6 fps, 4–6 min
python3 <skill>/scripts/mix.py --bgm trilha.mp3 --start 50 --big 0,3,5,7,8,9
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -vf "hqdn3d=1.5:1.5:5:5" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/ep02.mp4
```
Detalhes, tempos medidos e erros comuns: `references/pipeline.md`.

### 7. Publicação
Título, legenda, hashtags e horário: `references/monetizacao.md`.

## Os 10 blocos

| # | Função | Tipo | O que precisa ter |
|---|---|---|---|
| 1 | Gancho | papel | manchete + foto + carimbo + caneta (a frase que dói) |
| 2 | Promessa | mapa | "não é onde você pensa" — mapa apagado, X no alvo |
| 3 | O número | papel | valor gigante em cartela colorida |
| 4 | Escala | mapa | estados acendendo + contador |
| 5 | Origem | papel | foto + dois cartões de ano |
| 6 | Impacto | papel | 1 número em disco amarelo sobre foto sangrada |
| 7 | Consequências | papel | 4 cartelas numeradas entrando em sequência |
| 8 | Virada | mapa | fronteira, seta entrando de fora |
| 9 | Resposta | mapa | a pergunta mestra é respondida SÓ aqui |
| 10 | CTA | papel | pergunta + seta + "parte 2 amanhã" |

## Regras que não se quebram
- 9:16, 1080×1920, 30fps. Encode `crf 25` **com** `hqdn3d` (sem isso o grão estoura o arquivo: 128 MB → 18 MB).
- Texto com Ã/Õ: `leading >= 1.0` no `TB()`, senão o til é cortado.
- Nenhum bloco pode ficar mais de ~2,5s sem um elemento novo entrando. Cada `pop` também dá um soco de zoom na câmera.
- A resposta da pergunta mestra só aparece no bloco 9. Blocos 2–8 abrem loops, não fecham.
- Mapa sempre com dado verificável; quando for projeção, legenda "mapa ilustrativo".
- Nunca afirmar crime a pessoa nomeada. Usar "segundo", "de acordo com", "a investigação aponta".
- Trilha gerada (nunca música de catálogo) para não tomar claim.

## Arquivos
```
scripts/engine.py          motor: colagem, mapa, câmera, flash, ticker, grão (NÃO EDITAR)
scripts/collage.py         helpers de papel, cartela, carimbo, caneta, emoji, ticker
scripts/mapdemo.py         projeção, máscaras por UF, câmera, cartão rasgado
scripts/conteudo_ep01.py   CONTEÚDO do ep. 01 — molde para os próximos
scripts/serie.py           renderiza (--test, --from, --to)
scripts/dips.py            acha as fronteiras dos blocos no áudio cru
scripts/edit_vo.py         desacelera, abre respiros, gera beats.json
scripts/mix.py             ducking + drop nos cortes + loudnorm -14 LUFS
scripts/bootstrap.sh       confere/baixa fontes, emojis e malha do IBGE
assets/fonts|emoji|geo|img  Playfair, Anton, Oswald, Bebas, Marker, Twemoji, UFs, fotos
```

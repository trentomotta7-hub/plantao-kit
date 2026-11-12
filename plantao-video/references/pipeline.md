# Pipeline técnico

Tempos medidos no ep. 01 (sandbox 4 vCPU): narração ~40s, beat sheet 3s, render 1962 frames ≈ 8 min, mix 7s, encode 1,5 min.

## 0. Preparar
```bash
bash <skill>/scripts/bootstrap.sh      # confere fontes, emojis, malha IBGE, pillow/numpy/ffmpeg
mkdir -p meu_ep && cd meu_ep           # a pasta do episódio: roteiro.txt, audio/, out/, work/
```

## 1. Narração
`generate_speech` (MCP) com:
- `voice_name: pt-br-techagent-4`, `language_code: pt-BR`
- um turn por bloco, `style: "urgent, clear, conversational"` (bloco 9 pode ser `"slower, emphatic"`)
- salvar em `vo_raw.wav`

O áudio sai ~52s para 10 blocos (rápido demais) e **sem silêncio entre os parágrafos** — por isso os passos 2 e 3.

## 2. Fronteiras
```bash
python3 <skill>/scripts/dips.py --wav vo_raw.wav --textos roteiro.txt
# 52.08 s · 10 blocos
# 7.70,11.74,17.12,20.29,26.79,30.17,37.33,42.01,47.17
```
Funciona por vale de energia perto da posição esperada (proporcional ao tamanho do bloco). Se um valor cair no meio de uma frase, ajuste à mão ±0,5s.

## 3. Narração final + beat sheet
```bash
python3 <skill>/scripts/edit_vo.py --wav vo_raw.wav --bounds 7.70,11.74,... \
   --gaps 0.75,0.45,0.70,0.40,0.55,0.65,0.40,0.75,0.75 --tempo 0.87
# duração final 65.40 s (10 blocos) → grava vo_edit.wav e beats.json
```
`beats.json` = `{dur, starts[], cuts[]}`. `cuts[i] = starts[i] - 0.10` (imagem entra um fio antes da voz). **Todo o resto do pipeline lê esse arquivo** — é a única fonte de verdade de tempo.

## 4. Render
```bash
python3 <skill>/scripts/serie.py conteudo_ep02.py --test     # 13 frames, confira ANTES
python3 <skill>/scripts/serie.py conteudo_ep02.py            # work/frames_out/f_00000.jpg...
python3 <skill>/scripts/serie.py conteudo_ep02.py --from 900 --to 1200   # refazer um trecho
```
~4–6 fps (blocos de mapa custam o dobro). `PLANTAO_OUT` muda a pasta de saída; `PLANTAO_NOME` muda o nome no cabeçalho do jornal; `PLANTAO_BEATS` aponta outro beat sheet.

## 5. Áudio
```bash
python3 <skill>/scripts/mix.py --vo vo_edit.wav --bgm trilha.mp3 --start 50 --big 0,3,5,7,8,9
```
- `--start`: segundo da trilha onde começa o trecho mais forte (a trilha entra em loop com crossfade).
- `--big`: blocos cujo corte leva impacto cheio (boom + riser). Os outros levam 62%.
- `--duck 0.64`: quanto a trilha abaixa sob a voz (0.64 = −9 dB). Menos que isso a voz some no celular.
- Saída `mix_ln.wav` a −14 LUFS (padrão TikTok/YouTube).

Trilha: gerar com `generate_music` (phonk/funk 140–150 BPM, 90s+) ou usar faixa própria. **Nunca** catálogo comercial — claim derruba o alcance.

## 6. Encode
```bash
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -vf "hqdn3d=1.5:1.5:5:5" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/ep02.mp4
```
O `hqdn3d` é obrigatório: o grão de filme é ruído aleatório e sem ele o arquivo vai a 128 MB em 65s. Com ele: **18 MB** sem perda visível no celular.

Conferência final:
```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 out/ep02.mp4   # 65.4
ffmpeg -ss 3 -i out/ep02.mp4 -frames:v 1 capa.jpg                          # capa 9:16
```

## Erros comuns

| Sintoma | Causa | Conserto |
|---|---|---|
| Til do "Ã" cortado | `leading < 1.0` | usar `lead=1.0` no `TB()` |
| Vídeo "parado" | pops concentrados no começo do bloco | distribuir os pops na duração |
| Mapa com margem branca enorme | `M.CARD` com proporção diferente do cartão | definir `M.CARD` antes de `map_frame` |
| Arquivo de 100 MB+ | encode sem `hqdn3d` | refazer com o filtro |
| Voz sumindo no celular | `--duck` alto ou `--bg` alto | duck 0.6–0.7, bg 0.28–0.32 |
| Cartelas sem contraste | cartela da mesma cor do papel | usar YEL/CYA/RED/WHT ou borda escura |
| Fala atropelada | usou `vo_raw` | sempre `vo_edit` (atempo 0.87 + gaps) |
| Áudio e imagem fora de fase | `beats.json` de outro episódio | regerar com `edit_vo.py` |

## Custo por episódio
| Item | Créditos |
|---|---|
| Narração (TTS) | 1 |
| Trilha (reaproveitar a mesma) | 0 |
| Fotos (reaproveitar `assets/img` ou buscar) | 0–7 |
| Render/encode | 0 |

Com trilha e banco de imagens fixos, cada episódio novo custa **1 crédito**.

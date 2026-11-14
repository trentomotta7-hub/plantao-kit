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
python3 <skill>/scripts/edit_vo.py --wav vo_raw.wav --bounds 7.70,11.74,... \
   --gaps 0.75,0.45,0.70,0.40,0.55,0.65,0.40,0.75,0.75 --tempo 0.87
```
`--bounds` vem do `dips.py` **só como chute** (vale de energia perto da posição esperada, proporcional ao tamanho do bloco):
```bash
python3 <skill>/scripts/dips.py --wav vo_raw.wav --textos roteiro.txt
# 52.08 s · 10 blocos
# 7.70,11.74,17.12,20.29,26.79,30.17,37.33,42.01,47.17
```
O `edit_vo.py` desacelera (atempo 0.87), abre os respiros e emite um `beats.json` provisório. Esse arquivo **é substituído no passo 3** pela versão ancorada em palavra.

## 3. Beat sheet por palavra (fonte de verdade)
```bash
manus-speech-to-text vo_edit.wav --granularity word > vo.json
python3 <skill>/scripts/timing.py --stt vo.json --textos roteiro.txt --wav vo_edit.wav
```
`beats.json` = `{dur, starts[], cuts[], words[][]}`. `cuts[i] = starts[i] - 0.10` (a imagem entra um fio antes da voz) e `words[i]` traz o tempo de cada palavra **relativo ao bloco**. Todo o resto do pipeline lê esse arquivo.

O `timing.py` alinha o roteiro inteiro com a transcrição, então tolera palavra que o TTS trocou, cortou ou inseriu — e avisa quando roteiro e áudio batem menos de 85% (sinal de que o arquivo de texto não é o narrado). Sem esse passo, o `REF` de cada módulo de conteúdo volta a esticar os pops proporcionalmente, e cartela de número passa a entrar depois da fala.

Verificação rápida do alinhamento: `starts` deve começar em ~0.40 e cada corte cair 0.10s antes dele. Se algum bloco cair no meio da frase anterior, a linha do roteiro não corresponde ao parágrafo do TTS.

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

## 7. QA automatizado (antes de publicar)
```bash
python3 <skill>/scripts/qa.py --video out/ep02.mp4 --beats beats.json
```
Checa 1080×1920/30fps, duração 62–75s, lead do corte (0.06–0.20s), primeira palavra antes de 0.30s, respiro entre blocos (≤1.2s), loudness (−14 ±0.6 LUFS) e true peak (≤−1 dBTP) **medidos no MP4**, não no WAV. Falha ⇒ conserta antes de subir.

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

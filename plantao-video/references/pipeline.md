# Pipeline técnico

Tempos medidos no ep. 01 (sandbox 4 vCPU): narração ~40s, beat sheet 3s, render 1962 frames ≈ 8 min, mix 7s, encode 1,5 min.

## 0. Preparar
```bash
bash <skill>/scripts/bootstrap.sh      # confere fontes, emojis, malha IBGE, pillow/numpy/ffmpeg
mkdir -p meu_ep && cd meu_ep           # a pasta do episódio: roteiro.txt, audio/, out/, work/
```

## 1. Narração
`generate_speech` (MCP) com `voice_name: pt-br-techagent-4`, `language_code: pt-BR` e **um único turn** com o texto completo, abaixo de 6000 caracteres. Use uma direção de voz curta e constante. Novo turn só para mudança intencional de locutor/interpretação. Salvar em `vo_raw.wav`.

O áudio sai como `vo_raw.wav`. Preserve o WAV gerado: aparar por limiar de volume pode cortar fricativas e consoantes, e `atempo` altera a articulação. Ajuste o texto/voz ouvindo uma nova geração, não cortando fonemas.

## 2. Beat sheet por palavra (fonte de verdade)
```bash
manus-speech-to-text vo_raw.wav --granularity word > vo_transcription.txt
STT=$(ls -t vo_raw_transcription_*.json | head -1)
python3 <skill>/scripts/timing.py --stt "$STT" --textos roteiro.txt --wav vo_raw.wav --out beats.json
```
`beats.json` = `{dur, starts[], cuts[], words[][]}`. `cuts[i] = starts[i] - 0.10` (a imagem entra um fio antes da voz) e `words[i]` traz o tempo de cada palavra **relativo ao bloco**. Todo o resto do pipeline lê esse arquivo.

O `timing.py` alinha o roteiro inteiro com a transcrição, então tolera palavra que o TTS trocou, cortou ou inseriu — e avisa quando roteiro e áudio batem menos de 85% (sinal de que o arquivo de texto não é o narrado). Sem esse passo, o `REF` de cada módulo de conteúdo volta a esticar os pops proporcionalmente, e cartela de número passa a entrar depois da fala.

Verificação rápida: confira se a primeira palavra e as 10 aberturas de bloco correspondem à narração. As imagens entram 0.10 s antes da palavra; não se divide nem se desloca o WAV.

## 4. Render
```bash
python3 <skill>/scripts/serie.py conteudo_ep02.py --test     # 13 frames, confira ANTES
python3 <skill>/scripts/serie.py conteudo_ep02.py            # work/frames_out/f_00000.jpg...
python3 <skill>/scripts/serie.py conteudo_ep02.py --from 900 --to 1200   # refazer um trecho
```
~4–6 fps (blocos de mapa custam o dobro). `PLANTAO_OUT` muda a pasta de saída; `PLANTAO_NOME` muda o nome no cabeçalho do jornal; `PLANTAO_BEATS` aponta outro beat sheet.

## 5. Áudio
```bash
python3 <skill>/scripts/mix.py --vo vo_raw.wav --beats beats.json --bgm trilha.mp3 --start 50 --impacts 0
```
- `--start`: segundo da trilha onde começa o trecho mais forte (a trilha entra em loop com crossfade).
- `--impacts`: efeitos de corte são opt-in (0–1) e ficam desligados por padrão para não mascarar a primeira sílaba.
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
Checa 1080×1920/30fps, duração 45–75s (não se deve alongar a voz com silêncio para atingir uma duração artificial), lead do corte (0.06–0.20s), primeira palavra antes de 0.30s, respiro entre blocos (≤1.2s), loudness (−14 ±0.6 LUFS) e true peak (≤−1 dBTP) **medidos no MP4**, não no WAV. Falha ⇒ conserta antes de subir.

Em seguida, usar `plantao-video-autoreview`: comparar STT word-level com o roteiro, ouvir toda a voz seca e o MP4 completo, e conferir cada emenda/transição. A entrega fica bloqueada até que não haja palavras cortadas, mudança vocal não intencional ou revisão humana pendente.

## Erros comuns

| Sintoma | Causa | Conserto |
|---|---|---|
| Til do "Ã" cortado | `leading < 1.0` | usar `lead=1.0` no `TB()` |
| Vídeo "parado" | pops concentrados no começo do bloco | distribuir os pops na duração |
| Mapa com margem branca enorme | `M.CARD` com proporção diferente do cartão | definir `M.CARD` antes de `map_frame` |
| Arquivo de 100 MB+ | encode sem `hqdn3d` | refazer com o filtro |
| Voz sumindo no celular | `--duck` alto ou `--bg` alto | duck 0.6–0.7, bg 0.28–0.32 |
| Cartelas sem contraste | cartela da mesma cor do papel | usar YEL/CYA/RED/WHT ou borda escura |
| Palavra cortada | `trim`/limiar ou corte de áudio atravessou um fonema | restaurar `vo_raw.wav`; não aparar; refazer beats por palavra |
| Áudio e imagem fora de fase | `beats.json` de outro episódio | regerar transcrição e `beats.json` com `timing.py`; manter o WAV intacto |

## Custo por episódio
| Item | Créditos |
|---|---|
| Narração (TTS) | 1 |
| Trilha (reaproveitar a mesma) | 0 |
| Fotos (reaproveitar `assets/img` ou buscar) | 0–7 |
| Render/encode | 0 |

Com trilha e banco de imagens fixos, cada episódio novo custa **1 crédito**.

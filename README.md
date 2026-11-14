# MAPA SUJO — kit de produção

Fábrica de episódios verticais (9:16) de notícia criminal em PT-BR: colagem de jornal + mapa animado do Brasil, montados para retenção e monetização no TikTok.

Cada episódio novo custa **1 crédito** (só a narração). O resto é render determinístico.

A série se chama **MAPA SUJO** e numera os episódios (MAPA 01, MAPA 02…). O kit/motor continua com o nome interno `plantao-video`; para trocar o nome no vídeo use `PLANTAO_NOME`.

**Regra obrigatória para agentes:** leia `AGENTS.md` antes de qualquer tarefa. Para vídeo narrado, ele exige carregar `skills/plantao-video-autoreview/SKILL.md` e seguir seu gate de liberação.

## O que tem aqui

- `plantao-video/`: skill de produção, referências visuais e motor/renderização.
- `skills/plantao-video-autoreview/`: skill obrigatória, auditor técnico e checklist humano pré-entrega.
- `assets/`: fontes, Twemoji, malha IBGE (27 UFs) e fotos base.

## Instalar em outra conta Manus

```bash
git clone <este-repo> ~/plantao-kit
cp -r ~/plantao-kit/plantao-video ~/skills/          # a skill fica disponível
cp -r ~/plantao-kit/skills/plantao-video-autoreview ~/skills/  # revisão pré-entrega
bash ~/skills/plantao-video/scripts/bootstrap.sh     # confere dependências
```

Depois é só pedir: *"faz o episódio 2 do plantão sobre X"* — a skill dispara sozinha.

## Rodar um episódio na mão

```bash
mkdir -p ep02 && cd ep02
# 1. roteiro.txt (10 linhas = texto EXATO) + vo_raw.wav (uma tomada TTS contínua)
cp vo_raw.wav vo_final.wav                         # preservar a voz: sem trim/atempo
manus-speech-to-text vo_final.wav --granularity word > vo_transcription.txt
STT=$(ls -t vo_final_transcription_*.json | head -1) # JSON word-level estruturado
python3 ~/skills/plantao-video/scripts/timing.py --stt "$STT" --textos roteiro.txt --wav vo_final.wav --out beats.json
cp ~/skills/plantao-video/scripts/conteudo_ep01.py conteudo_ed002.py   # reescrever os 10 blocos
python3 ~/skills/plantao-video/scripts/serie.py conteudo_ed002.py --test
python3 ~/skills/plantao-video/scripts/serie.py conteudo_ed002.py
python3 ~/skills/plantao-video/scripts/mix.py --vo vo_final.wav --beats beats.json --bgm trilha.mp3 --impacts 0
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -vf "hqdn3d=1.5:1.5:5:5" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/ed002.mp4
python3 ~/skills/plantao-video/scripts/qa.py --video out/ed002.mp4 --beats beats.json
python3 ../skills/plantao-video-autoreview/scripts/audit_video.py --video out/ed002.mp4 --beats beats.json --script roteiro.txt --stt "$STT" --tts-turns 1 --report qa_report.md
```

`roteiro.txt` tem que ser **o mesmo texto** enviado ao TTS. O episódio de referência em `exemplos/ep01` foi narrado a partir de `ROTEIRO_VO.txt`, uma versão mais curta e falada de `roteiro.txt` — o `timing.py` avisa quando os dois não batem.

## Episódio de referência

`conteudo_ep01.py` é o episódio "A lista que ataca o dinheiro" (EUA listam PCC e CV como terroristas; AGU pede R$ 190,3 milhões; CV em 26 de 27 estados). Serve de molde: mesma estrutura, conteúdo novo.

## Licenças dos assets

- Fontes: Playfair Display, Oswald, Anton, Bebas Neue, Permanent Marker, Montserrat, Inter, Archivo Black — SIL Open Font License.
- Emojis: Twemoji (Twitter/X) — CC-BY 4.0.
- Malha dos estados: IBGE — domínio público.
- Fotos em `assets/img`: geradas por IA para o projeto.

## Licença
Código sob MIT (`LICENSE`). Fontes, Twemoji, malha do IBGE e fotos têm licenças próprias — `CREDITOS.md`.
Repositório público: pode clonar, forkar e adaptar. Se publicar uma versão, mantenha os créditos.
A série se chama **MAPA SUJO** e usa número de **EDIÇÃO** (`EDIÇÃO 001`, `002`…), não de episódio: notícia não é novela e numeração faz quem chega frio achar que perdeu os anteriores. O kit/motor continua com o nome interno `plantao-video`; para trocar o nome no vídeo use `PLANTAO_NOME`.

## Episódios

| pasta | edição | pauta | fontes |
|---|---|---|---|
| `exemplos/ep01` | 001 | EUA listam PCC e CV como terroristas; AGU pede R$ 190,3 mi | AGU · gov.br · BBC |
| `episodios/ed002` | 002 | O aluguel do crime: CV cobra moradia, comércio e internet | Folha (25/10/2026) · MP-PB · SSP-BA |

O `ed002` iniciou o pipeline ancorado em palavra (`timing.py` + `AT()`), mas a versão de vídeo atual está reprovada para entrega por problemas de continuidade da narração; não use como modelo de locução final.

# Revisão da edição 001 quadro a quadro — e o que mudou no kit

Método: medi o MP4 final, não o projeto. `ffprobe` (formato), `loudnorm` (loudness e
true peak), transcrição com timestamp de **palavra**, diferença de luminância quadro a
quadro a 10 fps para achar cortes e entradas de elemento, e folhas de contato em
resolução cheia nos instantes críticos. Depois cruzei cada evento visual com a palavra
falada naquele exato momento.

## O que estava errado na edição 001

1. **O primeiro quadro nascia estourado.** Em 0,00 s o motor aplicava o efeito de corte
   (flash + aberração cromática) sobre a manchete. Como o TikTok usa o primeiro quadro
   como capa do vídeo e do perfil, a peça se apresentava borrada. `mapa_sujo_ep01.mp4`,
   frame 0, comparado lado a lado com o novo.
2. **O relógio do conteúdo era proporcional, não real.** Cada módulo de conteúdo declara
   uma duração de projeto (`REF`) e o motor esticava os pops por `dur/REF`. No bloco 6 o
   `REF` era 4,535 s para um bloco de 6,9 s — fator **1,52**. Resultado: pop desenhado
   para 2,0 s entrava em 3,0 s, e o disco do contador saía de cima do número.
3. **Cartelas de resposta entravam depois da fala.** Onde o bloco real passou do previsto
   — B03 1,15×, B05 1,07×, B06 1,52×, B07 1,07× — todo pop era esticado na mesma
   proporção, e a frase na tela chegava depois da frase na voz. No bloco 10 foi o
   contrário: o bloco encolheu (0,90×) e as cartelas entraram antes da hora.
4. **O contador de estados fechava atrasado.** No bloco 6, com fator 1,52, um pop previsto
   para 2,2 s entrava em 3,35 s: o "26/27" completava mais de 1 s depois de a narração
   dizer o número.
5. **Pico de áudio acima do teto.** Medido no MP4: **−14,0 LUFS** (certo) com true peak
   **−0,3 dBTP**. O teto é −1,0 dBTP; acima disso a recompressão da plataforma distorce.
   O `qa.py` marca isso como falha no arquivo antigo.
6. **CTA não batia com a voz.** A narração pergunta "essa lista pega o dinheiro ou pega só
   a manchete?" e a cartela na tela dizia "o que VOCÊ faria?". Além disso o selo anunciava
   "PARTE 2 AMANHÃ · MESMA HORA" — uma parte 2 que não existe.
7. **Documentação contraditória.** `SKILL.md` mandava numerar por edição ("EDIÇÃO 001"),
   `README` dizia "MAPA 01, MAPA 02". E o áudio do ep. 01 foi narrado a partir de
   `ROTEIRO_VO.txt`, que é mais curto que o `roteiro.txt` do projeto — daí qualquer
   alinhamento automático por texto errar.

## O que mudou no kit

| arquivo | mudança |
|---|---|
| `scripts/timing.py` (novo) | escreve `beats.json` com `starts`, `cuts` e **`words`** (tempo de cada palavra dentro do bloco), alinhando o roteiro inteiro com a transcrição; avisa se a semelhança cair abaixo de 85% |
| `scripts/engine.py` | `AT(bloco, "palavra")` ancora qualquer elemento na fala; com `words` no beat sheet o motor **ignora o `REF`** (fim do retiming proporcional); sem efeito de corte no primeiro quadro |
| `scripts/qa.py` (novo) | confere formato, fps, duração, lead do corte, primeira palavra, respiro entre blocos, loudness e true peak medidos no MP4; sai com erro se falhar |
| `scripts/mix.py` | normalização em duas passagens lineares: entrega −14 LUFS com teto de pico respeitado |
| `scripts/edit_vo.py` | corta o silêncio que o TTS deixa no fim de cada parágrafo (era a causa dos buracos antes do corte) e preserva 0,12 s do ataque, para não comer a primeira consoante |
| `scripts/collage.py` | `PLANTAO_TICKER` define o texto do rodapé por episódio — antes o vídeo novo herdava a manchete do 001 |
| `SKILL.md` / `README.md` | fluxo com `timing.py` + `qa.py`, regra "pop ancorado em palavra", numeração por edição, áreas seguras 900×1400, aviso de que `roteiro.txt` tem que ser o texto narrado |

## A edição 002

Pauta: **o aluguel do crime** — o CV cobrando moradia, comércio e internet além do tráfico.
Fontes e checagem em `episodios/ed002/FONTES.md`.

| | ed. 001 | ed. 002 |
|---|---|---|
| duração | 66,63 s | 64,17 s |
| lead imagem→voz | 0,05 s | **0,10 s** em todos os 10 blocos |
| primeira palavra | não mensurável (o beat sheet do 001 não tem palavras) | 0,30 s |
| pops | proporcionais (REF até 1,52×) | **ancorados na palavra** (0,08 s antes) |
| loudness | −14,0 LUFS | −14,1 LUFS |
| true peak | −0,3 dBTP (falha) | **−1,2 dBTP** |
| primeiro quadro | com aberração | limpo |
| QA | 1 falha | **0 falhas**, 6 avisos de respiro |

Os seis avisos são pausas de 1,0–1,6 s antes de um corte: é a respiração desenhada entre
blocos (a trilha e o ticker seguem correndo). Se quiser mais denso, reduza `--gaps` no
`edit_vo.py` (cada 0,1 s a menos em cada bloco tira ~1 s do total).

## Como repetir

```bash
cd episodios/ed002
manus-speech-to-text vo_raw.wav --granularity word
python3 ../../plantao-video/scripts/timing.py --stt vo_raw_transcription_*.json \
        --textos roteiro.txt --wav vo_raw.wav --out raw_beats.json      # fronteiras
python3 ../../plantao-video/scripts/edit_vo.py --wav vo_raw.wav --bounds ... --gaps ...
manus-speech-to-text vo_edit.wav --granularity word
python3 ../../plantao-video/scripts/timing.py --stt vo_edit_transcription_*.json \
        --textos roteiro.txt --wav vo_edit.wav                          # beats com palavras
python3 ../../plantao-video/scripts/serie.py conteudo_ed002.py --test
python3 ../../plantao-video/scripts/serie.py conteudo_ed002.py
python3 ../../plantao-video/scripts/mix.py --vo vo_edit.wav --bgm trilha.mp3 --start 26 --big 0,3,5,7,8,9
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav -vf "hqdn3d=1.5:1.5:5:5" \
  -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p -c:a aac -b:a 192k \
  -movflags +faststart -shortest out/ed002.mp4
python3 ../../plantao-video/scripts/qa.py --video out/ed002.mp4 --beats beats.json
```

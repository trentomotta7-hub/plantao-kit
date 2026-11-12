# MAPA SUJO — kit de produção

Fábrica de episódios verticais (9:16) de notícia criminal em PT-BR: colagem de jornal + mapa animado do Brasil, montados para retenção e monetização no TikTok.

Cada episódio novo custa **1 crédito** (só a narração). O resto é render determinístico.

A série se chama **MAPA SUJO** e numera os episódios (MAPA 01, MAPA 02…). O kit/motor continua com o nome interno `plantao-video`; para trocar o nome no vídeo use `PLANTAO_NOME`.

## O que tem aqui

```
plantao-video/            a skill (copie para a pasta de skills da conta)
├── SKILL.md              o fluxo de 7 passos
├── references/
│   ├── roteiro.md        arquitetura de 10 blocos + como apurar e escrever
│   ├── design.md         paleta, tipografia, componentes, movimento, coordenadas
│   ├── pipeline.md       comandos, tempos medidos, erros comuns
│   └── monetizacao.md    regras de TikTok/Shorts/Reels e o que olhar no analytics
├── scripts/
│   ├── engine.py         motor de render (não editar)
│   ├── collage.py        papel, cartela, carimbo, caneta, emoji, ticker
│   ├── mapdemo.py        projeção, máscaras por UF, câmera, cartão rasgado
│   ├── conteudo_ep01.py  CONTEÚDO do ep. 01 — molde dos próximos
│   ├── serie.py          renderiza (--test, --from, --to)
│   ├── dips.py           acha as fronteiras dos blocos no áudio
│   ├── edit_vo.py        desacelera, abre respiros, gera beats.json
│   ├── mix.py            ducking + drop nos cortes + loudnorm -14 LUFS
│   └── bootstrap.sh      confere/baixa fontes, emojis, malha do IBGE
└── assets/               fontes, Twemoji, malha IBGE (27 UFs), fotos base
```

## Instalar em outra conta Manus

```bash
git clone <este-repo> ~/plantao-kit
cp -r ~/plantao-kit/plantao-video ~/skills/          # a skill fica disponível
bash ~/skills/plantao-video/scripts/bootstrap.sh     # confere dependências
```

Depois é só pedir: *"faz o episódio 2 do plantão sobre X"* — a skill dispara sozinha.

## Rodar um episódio na mão

```bash
mkdir -p ep02 && cd ep02
# 1. roteiro.txt (10 linhas) + vo_raw.wav (narração do TTS)
python3 ~/skills/plantao-video/scripts/dips.py --wav vo_raw.wav --textos roteiro.txt
python3 ~/skills/plantao-video/scripts/edit_vo.py --wav vo_raw.wav --bounds 7.70,... --gaps 0.75,...
cp ~/skills/plantao-video/scripts/conteudo_ep01.py conteudo_ep02.py   # reescrever os 10 blocos
python3 ~/skills/plantao-video/scripts/serie.py conteudo_ep02.py --test
python3 ~/skills/plantao-video/scripts/serie.py conteudo_ep02.py
python3 ~/skills/plantao-video/scripts/mix.py --bgm trilha.mp3 --big 0,3,5,7,8,9
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -vf "hqdn3d=1.5:1.5:5:5" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/ep02.mp4
```

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

# MAPA SUJO — kit de produção

Fábrica de episódios verticais (9:16) de notícia criminal em PT-BR: colagem de jornal + mapa animado do Brasil, montados para retenção e monetização no TikTok.

Cada episódio novo custa **1 crédito** (só a narração). O resto é render determinístico.

A série se chama **MAPA SUJO** e usa numeração de edição, não de capítulo. O kit/motor continua com o nome interno `plantao-video`; para trocar o nome no vídeo use `PLANTAO_NOME`.

**Regra obrigatória para agentes:** leia `AGENTS.md` antes de qualquer tarefa. Para vídeo narrado, ele exige carregar `skills/plantao-video-autoreview/SKILL.md` e seguir seu gate de liberação.

## Retomada rápida — Edição 003 V6

Para continuar este trabalho em uma nova sessão, clone o repositório e comece por [`episodios/ed003/revisao_v6_imagens_variadas/HANDOFF_V6.md`](episodios/ed003/revisao_v6_imagens_variadas/HANDOFF_V6.md). O handoff reúne as preferências do usuário, decisões editoriais, estado da V5/V6, gatilhos por palavra, limitações, direitos pendentes e próximos passos. Em seguida, leia `AGENTS.md`, `README.md` da pasta V6, `PRODUCAO_V6.md`, `storyboard_v6.md` e `review_checklist_v6.md`.

O renderer reproduzível é `episodios/ed003/revisao_v6_imagens_variadas/render_episode_v6.py`. A V6 completa foi gerada e passou por 8 checagens de QA sem falhas, mas ainda está **NEEDS REVIEW**: falta escuta/revisão humana integral e confirmação dos direitos de imagem. O MP4 e os quadros são mídia local ignorada pelo Git, não fazem parte deste clone. Não publique até resolver as pendências documentadas.

## O que tem aqui

- `plantao-video/`: skill de produção, referências visuais e motor/renderização.
- `skills/plantao-video-autoreview/`: skill obrigatória, auditor técnico e checklist humano pré-entrega.
- `assets/`: fontes, Twemoji, malha IBGE (27 UFs) e fotos base.
- `plantao-video/references/formatos.md`: seis estruturas narrativas, ganchos e testes editoriais.
- `plantao-video/templates/briefing_editorial.json`: modelo para ganchos, alegações e fontes.
- `plantao-video/templates/publication_metrics.csv`: registro de desempenho por publicação, plataforma e janela.
- `plantao-video/scripts/validate_brief.py`, `check_hook.py` e `analyze_metrics.py`: verificações estruturais e métricas normalizadas.

## Instalar em outra conta Manus

```bash
git clone <este-repo> ~/plantao-kit
cp -r ~/plantao-kit/plantao-video ~/skills/          # a skill fica disponível
cp -r ~/plantao-kit/skills/plantao-video-autoreview ~/skills/  # revisão pré-entrega
bash ~/skills/plantao-video/scripts/bootstrap.sh     # confere dependências
```

Depois é só pedir: *"faz o episódio 2 do plantão sobre X"* — a skill dispara sozinha.

## Fluxo editorial atualizado

1. Escolha uma estrutura em `plantao-video/references/formatos.md` e uma faixa de duração que a pauta sustenta: `quick` (20–45s), `standard` (60–75s) ou `explainer` (75–90s).
2. Copie `plantao-video/templates/briefing_editorial.json`, registre três ganchos, fontes diretas e cada alegação. Rode `python3 plantao-video/scripts/validate_brief.py briefing.json`; depois confira manualmente se cada fonte sustenta o que será dito.
3. Use `python3 plantao-video/scripts/check_hook.py --script roteiro.txt --beats beats.json` para checar bloco inicial e tempo da primeira palavra. Clareza e fidelidade do gancho continuam dependendo de revisão humana.
4. Após publicar, preencha uma linha por plataforma e janela no CSV de métricas. Rode `python3 plantao-video/scripts/analyze_metrics.py --input publication_metrics.csv` e compare publicações de pauta e janela semelhantes.

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
python3 ~/skills/plantao-video/scripts/qa.py --video out/ed002.mp4 --beats beats.json --preset standard
python3 ../skills/plantao-video-autoreview/scripts/audit_video.py --video out/ed002.mp4 --beats beats.json --script roteiro.txt --stt "$STT" --preset standard --tts-turns 1 --report qa_report.md
```

`roteiro.txt` tem que ser **o mesmo texto** enviado ao TTS. O episódio de referência em `exemplos/ep01` foi narrado a partir de `ROTEIRO_VO.txt`, uma versão mais curta e falada de `roteiro.txt` — o `timing.py` avisa quando os dois não batem.

## Episódio de referência

`conteudo_ep01.py` é o episódio "A lista que ataca o dinheiro" (EUA listam PCC e CV como terroristas; AGU pede R$ 190,3 milhões; CV em 26 de 27 estados). Serve de molde: mesma estrutura, conteúdo novo.

## Licenças dos assets

- Fontes: Playfair Display, Oswald, Anton, Bebas Neue, Permanent Marker, Montserrat, Inter, Archivo Black — SIL Open Font License.
- Emojis: Twemoji (Twitter/X) — CC-BY 4.0.
- Malha dos estados: IBGE — domínio público.
- Fotos em `plantao-video/assets/img`: geradas por IA para o projeto; fotos reais de pauta/episódio têm atribuição e licença próprias em `CREDITOS.md` e na documentação da edição.

## Licença
Código sob MIT (`LICENSE`). Fontes, Twemoji, malha do IBGE e fotos têm licenças próprias — `CREDITOS.md`.
Repositório público: pode clonar, forkar e adaptar. Se publicar uma versão, mantenha os créditos.
A série se chama **MAPA SUJO** e usa número de **EDIÇÃO** (`EDIÇÃO 001`, `002`…), não de episódio: notícia não é novela e numeração faz quem chega frio achar que perdeu os anteriores. O kit/motor continua com o nome interno `plantao-video`; para trocar o nome no vídeo use `PLANTAO_NOME`.

## Episódios

| pasta | edição | pauta | fontes |
|---|---|---|---|
| `exemplos/ep01` | 001 | EUA listam PCC e CV como terroristas; AGU pede R$ 190,3 mi | AGU · gov.br · BBC |
| `episodios/ed002` | 002 | O aluguel do crime: CV cobra moradia, comércio e internet | Folha (25/10/2026) · MP-PB · SSP-BA |
| `episodios/ed003` | 003 | Daniel Vorcaro: parecer da PGR, defesa e estilo de vida | Agência Brasil · g1 · BBC (revisão humana pendente) |
| `episodios/ed003/revisao_v3_mapa_sujo` | 003 (V3, prévia) | Mensagem atribuída a Vorcaro, relatório da PF em revisão e parecer da PGR | UOL · Agência Brasil · STF · Agência Senado |
| `episodios/ed003/revisao_v3_cortes_visuais` | 003 (V3.2, prévia) | Mesma pauta; 41 estados visuais internos, revisão humana pendente | UOL · Agência Brasil · STF · Agência Senado |
| `episodios/ed003/revisao_v5_visual_sincronizada` | 003 (V5, prévia) | 47 eventos visuais sincronizados à fala; revisão humana e direitos pendentes | UOL · Agência Brasil · STF · Agência Senado |
| `episodios/ed003/revisao_v6_imagens_variadas` | 003 (V6, prévia local) | Vídeo completo com duas fotos contextuais novas; QA técnico passa, revisão humana/direitos pendentes | Agência Brasil · Wikimedia Commons |

**Revisões visuais da edição 003:** V1 e V2 permanecem arquivadas e não aprovadas visualmente. `episodios/ed003/revisao_v3_mapa_sujo/` restaura o motor e a gramática visual de MAPA SUJO das edições 001/002; a V3.2 em `episodios/ed003/revisao_v3_cortes_visuais/` acrescenta cortes internos e movimento, preservando essa identidade e sem sobrescrever as versões anteriores. Ambas são prévias independentes. A revisão humana completa e a autorização para publicar a foto de Vorcaro continuam pendentes.

O `ed002` iniciou o pipeline ancorado em palavra (`timing.py` + `AT()`), mas a versão de vídeo atual está reprovada para entrega por problemas de continuidade da narração; não use como modelo de locução final. Cada corte de duração é uma versão independente e precisa de QA e revisão humana próprios.

Para retomar a revisão de variedade fotográfica da edição 003 em outra sessão, comece por `episodios/ed003/revisao_v6_imagens_variadas/HANDOFF_V6.md`. O handoff registra as preferências do usuário, o estado da V5, os novos ativos e os próximos passos sem incluir quadros de renderização.

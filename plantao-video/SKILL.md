---
name: plantao-video
description: Produz episódios verticais 9:16 em PT-BR de notícia criminal e crime organizado (break news) na estética colagem de jornal + mapa animado do Brasil, montados para retenção e monetização no TikTok. Use para criar vídeo de notícia policial, série de episódios sobre facções/PCC/Comando Vermelho, mapa explicativo animado com dados de estados, vídeo com cara de jornal colado, narração TTS com beat sheet, corte curto de 30s para Reels/Shorts.
---

# O PLANTÃO — fábrica de episódios

Vídeo vertical 9:16, 1080×1920, 30fps. O padrão editorial é 62–75s; consulte `references/formatos.md` para versões `quick` e `explainer`. O corte é a batida: flash + drop de áudio em cada virada. Custo padrão informado no projeto: **1 crédito por episódio** (narração; o resto é render determinístico).

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

## Legenda queimada: desligada
Testamos legenda palavra por palavra no rodapé e o resultado não ficou bom na colagem (briga com o ticker e com o papel). O bloco de legenda foi removido do `engine.py`. Se quiser reativar, o desenho era um `PL(TB([...]))` composto antes do ticker, em y≈1586.

## Gancho: os 2 primeiros segundos
Manchete entra em **0.0** e a foto em **0.25** — a página nunca aparece vazia no primeiro frame. O primeiro frame é a capa do vídeo e do perfil: **nada de flash, aberração cromática ou imagem desfocada nele**. Se a voz abrir com silêncio, mantenha o WAV intacto e sincronize o primeiro visual à primeira palavra; **nunca apare o WAV por limiar de volume**, pois isso pode cortar consoantes e fricativas.

Carimbo e emoji entram ancorados na palavra (`W(0, "terroristas")`), nunca em tempo fixo. O `marker` (a frase que dói) entra junto com a palavra que ele repete.

## Regra de ouro
O programa Creator Rewards exige vídeo com **mais de 1 minuto**, conforme regras e elegibilidade vigentes da conta/região. A versão `standard` fica em 60–75s; `explainer`, em 75–90s. Um corte `quick` pode servir ao alcance, mas não atende ao requisito de duração desse programa.

## Formatos e experimentação
Os 10 blocos são o formato padrão, não uma obrigação para cada pauta. Consulte `references/formatos.md` para estruturas narrativas alternativas e faixas `quick` (20–45s), `standard` (60–75s) e `explainer` (75–90s). Não alongue ou acelere a locução para preencher uma faixa; cada versão deve ter roteiro e narração contínua próprios.

Antes de roteirizar, copie `templates/briefing_editorial.json`, escreva três candidatos de gancho e registre fontes e alegações. Rode `scripts/validate_brief.py` e revise manualmente cada fonte. O validador confirma completude e referências, não verifica a veracidade das alegações. Use `scripts/check_hook.py` para checar o primeiro bloco e o timestamp da primeira palavra.

Depois de publicar, registre métricas por plataforma e janela em `templates/publication_metrics.csv` e use `scripts/analyze_metrics.py` para comparar taxas normalizadas. Compare publicações semelhantes e mude uma variável por teste; métricas não provam causalidade.

## Fluxo

### 1. Pauta e briefing
Escolher acontecimento atual com pergunta clara e evidência acessível; número forte ajuda, mas não é requisito. Registrar fonte, data, atribuição e classificação de cada alegação no briefing. Fontes e cuidados: `references/roteiro.md`.

### 2. Roteiro em 10 blocos
Escrever o texto falado em `roteiro.txt`, uma linha por bloco quando usar o formato de 10 blocos. Estruturas alternativas e suas durações estão em `references/formatos.md`. O texto deve responder à promessa inicial e distinguir fatos de alegações.

### 3. Narração (1 crédito)
Chamar `generate_speech` (voice `pt-br-techagent-4`, `pt-BR`) com **um único turn para a locução contínua**, style curto e constante. Abrir turnos separados só para troca intencional de locutor/interpretação. Salvar como `vo_raw.wav`. **Preserve a narração original**: não apare por energia, não segmente frases e não use `atempo` por padrão; corrija o texto ou regenere a passagem inteira.

### 4. Beat sheet — alinhamento obrigatório por palavra
Não inferir fronteiras por silêncio: pausa interna pode ser maior que a pausa entre blocos. Transcrever o áudio final com timestamps de palavra e deixar o `timing.py` escrever o beat sheet:
```bash
manus-speech-to-text vo_raw.wav --granularity word > vo_transcription.txt
STT=$(ls -t vo_raw_transcription_*.json | head -1)
python3 <skill>/scripts/timing.py --stt "$STT" --textos roteiro.txt --wav vo_raw.wav --out beats.json
```
O `timing.py` alinha o roteiro inteiro com a transcrição (tolerando palavra trocada ou omitida), grava `beats.json` com `starts`, `cuts` (0.10s antes da voz) e `words` (tempo de cada palavra dentro do bloco). Se a semelhança entre roteiro e áudio ficar abaixo de 85%, ele avisa: o arquivo de texto não é o que foi narrado — corrija antes de seguir. `dips.py` fica só como chute quando não há transcrição.

### 5. Conteúdo visual
```bash
cp <skill>/scripts/conteudo_ep01.py conteudo_ep02.py
```
Reescrever os 10 blocos: textos, fotos, cores e pops de cada cartela. **Cada pop é ancorado na palavra que ele ilustra**, com `AT(bloco, "palavra")` — nunca em segundo fixo nem em proporção da duração:
```python
   L(big, 540, 700, AT(2, "milhões"), 1.0)    # a cartela entra junto com "milhões"
   ```
Gramática visual, coordenadas e tempos em `references/design.md`. O motor (`engine.py`) não se mexe. O antigo `REF` (retiming proporcional) está desativado: quando o beat sheet tem `words`, o motor ignora `REF`.

Varie entre retratos, fachadas, ambientes e outros registros reais que expliquem a fala; não repita o mesmo retrato por conveniência nem use imagem genérica como prova de um fato. Registre fonte, autor, licença, crédito e palavra-gatilho de cada foto. Use mapa apenas quando a geografia for relevante. A referência `references/design.md` detalha essa regra e a revisão de amostras antes do render integral.

### 6. Render, mix e encode
```bash
python3 <skill>/scripts/serie.py conteudo_ep02.py --test      # 13 frames de conferência
python3 <skill>/scripts/serie.py conteudo_ep02.py             # ~6 fps, 4–6 min
python3 <skill>/scripts/mix.py --vo vo_raw.wav --beats beats.json --bgm trilha.mp3 --start 50 --impacts 0
ffmpeg -y -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -vf "hqdn3d=1.5:1.5:5:5" -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/ep02.mp4
```
Detalhes, tempos medidos e erros comuns: `references/pipeline.md`.

### 7. Controle de qualidade (obrigatório)
```bash
python3 <skill>/scripts/qa.py --video out/ep02.mp4 --beats beats.json --preset standard
```
Confere formato, fps, duração, lead do corte, primeira palavra, respiro entre blocos, loudness (−14 LUFS) e true peak (−1 dBTP). Depois, ler e seguir `skills/plantao-video-autoreview/SKILL.md` para transcrição comparada, escuta do WAV e do MP4 completos, inspeção das emendas e dos cortes visuais. QA numérico sozinho não aprova entrega: qualquer corte audível bloqueia publicação.

### 8. Publicação
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
| 10 | CTA | papel | pergunta genuína, relacionada à pauta, sem engajamento artificial |

## Regras que não se quebram
- 9:16, 1080×1920, 30fps. Encode `crf 25` **com** `hqdn3d` (sem isso o grão estoura o arquivo: 128 MB → 18 MB).
- Texto com Ã/Õ: `leading >= 1.0` no `TB()`, senão o til é cortado.
- Nenhum bloco pode ficar mais de ~2,5s sem um elemento novo entrando. Cada `pop` também dá um soco de zoom na câmera.
- Todo `pop` é ancorado em palavra (`AT()`), nunca em segundo fixo. Números na tela (contador, "26 de 27", "1/3") fecham **na palavra que os diz**, não depois.
- Respiro entre o fim da fala de um bloco e o corte do próximo: **até 1,2s**. Acima disso é buraco, não pausa dramática.
- O texto na tela do CTA tem que ser o que a voz pergunta. Se a voz diz "pega o dinheiro ou a manchete?", a cartela não pode dizer "o que você faria?".
- Nada de "parte 2 amanhã" quando não existe parte 2: o selo é de edição.
- A resposta da pergunta mestra só aparece no bloco 9. Blocos 2–8 abrem loops, não fecham.
- Mapa sempre com dado verificável; quando for projeção, legenda "mapa ilustrativo".
- Nunca afirmar crime a pessoa nomeada. Usar "segundo", "de acordo com", "a investigação aponta".
- Trilha gerada (nunca música de catálogo) para não tomar claim.
- Entregar a **−14 LUFS / −1 dBTP** medidos no MP4 final (`qa.py`), não só na etapa de mix.

## Arquivos
```
scripts/engine.py          motor: colagem, mapa, câmera, flash, ticker, grão (NÃO EDITAR)
scripts/collage.py         helpers de papel, cartela, carimbo, caneta, emoji, ticker
scripts/mapdemo.py         projeção, máscaras por UF, câmera, cartão rasgado
scripts/conteudo_ep01.py   CONTEÚDO do ep. 01 — molde para os próximos
scripts/serie.py           renderiza (--test, --from, --to)
scripts/timing.py          escreve beats.json a partir dos timestamps de PALAVRA
scripts/qa.py              confere sincronia, respiros, formato e loudness do MP4
scripts/validate_brief.py  confere campos, ganchos e referências de fontes
scripts/check_hook.py      confere o primeiro bloco e horário da primeira palavra
scripts/analyze_metrics.py resume taxas normalizadas do CSV pós-publicação
scripts/dips.py            acha as fronteiras dos blocos no áudio cru
scripts/edit_vo.py         utilitário legado; não usar para aparar/acelerar voz
scripts/mix.py             ducking + loudnorm -14 LUFS; impactos desligados por padrão
scripts/bootstrap.sh       confere/baixa fontes, emojis e malha do IBGE
assets/fonts|emoji|geo|img  Playfair, Anton, Oswald, Bebas, Marker, Twemoji, UFs, fotos
```
| `PLANTAO_TICKER` | texto da faixa do rodapé (padrão: manchete do ep. 01 — sempre definir num episódio novo) |
Manchete entra em **0.0** e a foto em **0.25** — a página nunca aparece vazia no primeiro frame. O primeiro frame é a capa do vídeo e do perfil: **nada de flash, aberração cromática ou imagem desfocada nele**. Se a voz abrir com silêncio, mantenha o áudio intacto e sincronize o primeiro visual à primeira palavra; **nunca apare o WAV por limiar de volume** (pode cortar consoantes/fricativas).
scripts/edit_vo.py         utilitário legado; não usar para aparar a fala

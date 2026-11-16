# Produção V5 — revisão fotográfica sincronizada

## Exportação

- Arquivo: `out/ed003_v5_sincronizada.mp4` (9.651.248 bytes; aproximadamente 9,65 MB).
- H.264, 1080×1920, 30 fps; AAC estéreo, 48 kHz; duração 79,333 s.
- Compressão: CRF 25, preset `slow`, `hqdn3d=1:1:4:4`, `yuv420p` e `+faststart`, para reprodução em celular.
- Mix reutilizado: `revisao_v3_cortes_visuais/mix_ln.wav`, com locução e trilha já mixadas. QA mediu −14,1 LUFS e −1,2 dBTP.

## Verificações

O QA técnico do Plantão Kit passou em 8 checagens, sem falhas. O MP4 decodificou integralmente; foram extraídas 49 amostras pós-encode, cobrindo a abertura, os 47 eventos visuais e o encerramento. A auditoria de alinhamento mediu 0,10 s de antecipação para todos os gatilhos do manifesto; o relatório de pré-entrega registrou 10 beats e 79,33 s contra 79,32 s do mapa de beats.

O relatório automatizado permanece **NEEDS REVIEW** porque a escuta/revisão humana não foi concluída; também assinala que o número de turnos TTS não foi informado. O roteiro versus ASR registra WER 4,1% e variações de grafia/numeração, incluindo a citação do beat 3. Isso precisa ser conferido contra a fonte antes de publicação; não foi presumida uma aprovação humana.

## Sincronização e imagem

O manifesto `storyboard_v5.json` usa os timestamps palavra-a-palavra de `revisao_v3_cortes_visuais/beats.json`. Para cada evento: `tempo_da_palavra = starts[i] + words[i][k].t`; `tempo_visual = max(cut[i], tempo_da_palavra − 0,10s)`. `timing_audit_v5.md` registra a checagem individual. A legenda progressiva apresenta somente palavras já iniciadas na locução.

As fotos provêm dos arquivos locais do episódio e mantêm identificação e crédito na cartela. O mapa geográfico foi omitido porque a locução desta edição não menciona uma localidade relevante; Brasília não é inserida como padrão.

## Reproduzir

Na raiz desta pasta:

```bash
python3 prepare_v5.py
python3 render_episode_v5.py --smoke
python3 render_episode_v5.py
```

O smoke test cria `out/check/contact_storyboard_v5.jpg`. O render completo usa `work/frames_v5/` temporariamente e remove os quadros intermediários após o encode, a menos que seja chamado com `--keep-frames`.

## Estado de liberação

Esta é uma prévia para revisão, não uma liberação para publicação. A revisão humana de conteúdo, ritmo, legibilidade em celular e áudio permanece obrigatória. A autorização pública/comercial da foto de Daniel Vorcaro não está confirmada; confirmar os direitos de todas as imagens antes de publicar. Ver `review_checklist_v5.md` e `FONTES.md`.

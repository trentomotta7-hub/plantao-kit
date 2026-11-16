# Produção V6 — dados e reprodução

## Origem e transformação

- Base: `../revisao_v5_visual_sincronizada/out/ed003_v5_sincronizada.mp4`.
- Renderer: `render_episode_v6.py`.
- Imagens: `assets/fachada_banco_master_rovena_rosa_ebc.jpg` e `assets/stf_edificio_dasfour2022_commons.jpg`.
- Áudio: AAC da V5 copiado sem re-encode; não houve alteração de locução, música, ganho nem timing.
- A V6 acrescenta sobreposições PNG com alpha em duas janelas; o vídeo-base e a V5 não são sobrescritos.
- A base V5 já recebeu hqdn3d; o encode final V6 não reaplica denoise. CRF 25, H.264, yuv420p, 30 fps e `+faststart`.

## Sincronização calculada

- Beat 4: corte 21,94 s; visual/fachada 22,04 s; “Master” 22,14 s; visual da foto termina na entrada visual do cartão “MAIO”, 26,40 s; a palavra “maio” é falada em 26,50 s.
- Beat 9: corte 64,04 s; visual do edifício 68,58 s; “Parecer” 68,68 s; “Supremo” 71,10 s; foto termina no corte para o beat seguinte, 72,12 s.
- O render é limitado a frames de 30 fps, então a apresentação física pode ser quantizada ao quadro mais próximo; o beat sheet e os gatilhos continuam registrados em milissegundos.

## Comando

```bash
python3 render_episode_v6.py --smoke
python3 render_episode_v6.py --render
```

QA e auditoria executados:

```bash
python3 /home/ubuntu/plantao-kit/plantao-video/scripts/qa.py \
  --video out/ed003_v6_fotos_contextuais.mp4 \
  --beats ../revisao_v3_cortes_visuais/beats.json \
  --preset explainer

python3 /home/ubuntu/plantao-kit/skills/plantao-video-autoreview/scripts/audit_video.py \
  --video out/ed003_v6_fotos_contextuais.mp4 \
  --beats ../revisao_v3_cortes_visuais/beats.json \
  --script ../revisao_v3_cortes_visuais/roteiro.txt \
  --stt ../revisao_v3_cortes_visuais/vo_raw_transcription_20261115_222947.json \
  --preset explainer --report out/audit_report_v6.md
```

## Resultado medido

- `ffprobe`: H.264 1080×1920 a 30 fps, AAC estéreo 48 kHz; 79,333 s.
- Tamanho: 9.938.630 bytes (cerca de 9,94 MB).
- Decode integral FFmpeg: concluído sem erro.
- QA do kit: 8 checagens, 0 falhas. Loudness −14,1 LUFS; true peak −1,2 dBTP.
- Auditoria automática: **NEEDS REVIEW**, código de saída 2. Passam duração, dimensões, fps, áudio, beats, lead visual 0,10 s, primeira palavra a 0,28 s, respiros e comparação aproximada roteiro/ASR (WER 4,1%).
- Aviso da auditoria: `--tts-turns` não informado. O número real de turnos deve ser confirmado no registro original e a auditoria reexecutada com o número correto.
- Checklist de escuta e revisão humana integral não foi preenchido. Uma inspeção automatizada de frames não equivale a assistir/escutar ao vídeo completo.

## Direitos

A Agência Brasil identifica Rovena Rosa como autora da foto da fachada, mas é necessário reconfirmar se a foto específica está abrangida pelas condições de uso antes de qualquer publicação. A imagem do STF é CC BY-SA 4.0; cumprir crédito, link da licença, indicação de recorte/movimento e ShareAlike na adaptação distribuída. O retrato de Daniel Vorcaro que já estava na V5 permanece com autorização pública/comercial não confirmada. Ver `IMAGENS_E_DIREITOS.md` e `review_checklist_v6.md`.

**Conclusão:** arquivo é prévia técnica de revisão; não aprovado para distribuição/publicação.

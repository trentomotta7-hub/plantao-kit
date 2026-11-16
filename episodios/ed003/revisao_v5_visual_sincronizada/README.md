# MAPA SUJO — Edição 003 · V5 sincronizada

A V5 repagina os dez beats com papel de jornal, masthead ampliado no topo, recortes fotográficos e movimento 2.5D. O foco visual muda 47 vezes; retratos aparecem 0,10 s antes da palavra correspondente, e legendas progressivas acompanham a locução sem mostrar palavras futuras. Não há mapa geográfico nesta edição porque a locução não nomeia uma localidade que o justifique.

## Resultado técnico

| Item | Resultado |
|---|---|
| Arquivo | `out/ed003_v5_sincronizada.mp4` |
| Vídeo | H.264, 1080×1920, 30 fps |
| Áudio | AAC, estéreo, 48 kHz; locução e trilha do mix do projeto |
| Duração / tamanho | 79,33 s / 9,65 MB |
| Compressão | CRF 25, `hqdn3d=1:1:4:4`, `yuv420p`, `+faststart` |
| Loudness / pico verdadeiro | −14,1 LUFS / −1,2 dBTP |
| QA do projeto | 8 checagens, 0 falhas; decodificação integral concluída |
| Pré-entrega | NEEDS REVIEW; depende de escuta e revisão humana completas |

A lista completa de eventos e a auditoria dos timestamps estão em `storyboard_v5.md` e `timing_audit_v5.md`. O manifesto JSON, o briefing e as fontes permanecem no repositório para conferência. MP4, WAVs, quadros e fotos locais não são versionados; reproduzir exige obter novamente os ativos de mídia com direitos confirmados.

## Arquivos principais

- Vídeo: `out/ed003_v5_sincronizada.mp4`
- Folha de contato pós-encode: `out/check/contact_final_v5.jpg`
- Storyboard de leitura: `storyboard_v5.md`
- Manifesto completo: `storyboard_v5.json`
- Sincronização palavra a palavra: `timing_audit_v5.md`
- Auditoria pré-entrega: `out/audit_report_v5.md`
- Fontes e créditos: `FONTES.md`
- Briefing factual: `briefing_editorial.json`
- Direção visual: `DIRECAO_VISUAL_V5.md`
- Checklist pendente: `review_checklist_v5.md`
- Renderer: `render_episode_v5.py`

## Reproduzir

```bash
python3 prepare_v5.py
python3 render_episode_v5.py --smoke
python3 render_episode_v5.py
```

## Antes de publicar

A auditoria automatizada **não** atesta a qualidade da fala nem a veracidade das afirmações. O relatório continua `NEEDS REVIEW`: falta assistir ao vídeo completo, conferir a citação do beat 3 contra a fonte e preencher o checklist humano. Também falta confirmar os direitos/licença da fotografia de Daniel Vorcaro; não publicar antes dessa confirmação. Ver `review_checklist_v5.md`.

# MAPA SUJO — Edição 003 · V6 com fotos contextuais

Prévia vertical V6 gerada a pedido do usuário, incorporando duas fotos contextuais reais à montagem V5. Mantém o jornal colado, o masthead centralizado, o ticker, as legendas sincronizadas por palavra e o áudio existente. Nenhum mapa decorativo foi acrescentado.

## Arquivo de revisão

- MP4 local: `out/ed003_v6_fotos_contextuais.mp4`
- H.264/AAC · 1080×1920 · 30 fps · 79,33 s · 9.938.630 bytes (~9,94 MB)
- CRF 25, `+faststart`; o master V5 já estava denoised, por isso a V6 não reaplica denoise.
- O AAC é copiado do V5 sem alteração, preservando narração, trilha e sincronização.

## O que mudou

| Janela | Foto/uso editorial | Sincronização |
|---|---|---|
| Beat 4, 22,04–26,40 s | Fachada do Banco Master, identificada como fachada em Itaim Bibi/SP e foto do local; crédito Rovena Rosa/Agência Brasil | Entra 0,10 s antes de “Master”; a cartela temporal de maio reaparece no seu gatilho |
| Beat 9, 68,58–72,12 s | Edifício do STF identificado como foto de arquivo; texto explícito diferencia parecer da PGR e decisão do STF | Entra 0,10 s antes de “Parecer”; sai no limite do beat |

Os cartões mantêm proporção próxima à das fotos, exibem os créditos e se movem com entrada lateral/zoom discreto. A V5 permanece intacta.

## Verificações

- QA do projeto: **8 checagens, 0 falhas**.
- Decodificação integral do MP4: concluída.
- Especificações confirmadas por `ffprobe`: H.264/AAC, 1080×1920, 30 fps, 79,33 s.
- Auditoria: **NEEDS REVIEW**; aviso de número de turnos TTS não informado e checklist humano pendente.
- Folha pós-encode: `out/check/post_frames/contact_final_v6.jpg`.
- Relatório: `out/audit_report_v6.md`.

## Reproduzir

```bash
python3 render_episode_v6.py --smoke
python3 render_episode_v6.py --render
```

O renderer usa o MP4 V5 local, o beat sheet e as fotos em `assets/`. Áudio original e vídeo-base não são versionados pelo GitHub público; sem esses arquivos locais, a clonagem do código sozinha não basta para re-renderizar.

## Não publicar ainda

A V6 é apenas uma prévia. Ainda é necessária escuta humana integral e revisão visual/factual. Confirmar os direitos da foto específica da Agência Brasil e do retrato de Daniel Vorcaro. Para a imagem do STF do Wikimedia Commons, cumprir integralmente CC BY-SA 4.0 (crédito, link, alterações e ShareAlike para a adaptação distribuída). Consulte `IMAGENS_E_DIREITOS.md` e `review_checklist_v6.md`.

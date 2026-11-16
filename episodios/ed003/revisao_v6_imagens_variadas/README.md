# MAPA SUJO — Edição 003 · V6 com fotos contextuais

**Status: prévia pública de revisão**, publicada no GitHub a pedido explícito do usuário em 16/11/2026. A presença pública do arquivo não significa aprovação editorial nem confirmação dos direitos das imagens.

## Vídeo

- [Abrir/baixar o MP4 V6](out/ed003_v6_fotos_contextuais.mp4)
- 9.938.630 bytes (~9,94 MB) · 79,33 s · 1080×1920 · 30 fps · H.264/AAC
- SHA-256: `e08d4a5a411ecd6ef30db7ccdad65d3f090462d81ae3e23216450323bd11be63`
- CRF 25, `+faststart`; a base V5 já tinha denoise, então não foi aplicado denoise duplo.
- O AAC foi copiado bit a bit do V5, preservando voz, trilha, ganho e sincronização.

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
- Relatório incluído neste clone: [`audit_report_v6.md`](audit_report_v6.md).
- A folha de contato e os frames isolados ficam locais, não versionados.

## Reproduzir/modificar

```bash
python3 render_episode_v6.py --smoke
python3 render_episode_v6.py --render
```

O renderer precisa do MP4-base V5 e de ativos locais de áudio/episódio que não foram incluídos neste commit. O clone atual permite ver o MP4 V6, o código e o contexto, mas **não permite re-renderizar** sem fornecer essas dependências.

## Direitos e revisão

O usuário autorizou expressamente armazenar este MP4 em repositório público mesmo com pendências registradas. A foto da fachada atribuída a Rovena Rosa/Agência Brasil ainda precisa de confirmação de uso para o caso concreto; a imagem do STF está sob CC BY-SA 4.0 e exige atribuição, link da licença, indicação das alterações e ShareAlike na adaptação distribuída; a autorização do retrato de Daniel Vorcaro que já aparece no vídeo não foi confirmada. Consulte [`IMAGENS_E_DIREITOS.md`](IMAGENS_E_DIREITOS.md).

**Não trate o upload público no GitHub como liberação editorial/comercial do vídeo.** A revisão humana integral de áudio e imagem continua pendente. A licença MIT do código não substitui as licenças específicas das fotografias ou do material audiovisual.

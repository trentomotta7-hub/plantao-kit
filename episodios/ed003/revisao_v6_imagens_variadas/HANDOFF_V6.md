# Retomada de sessão — MAPA SUJO, edição 003, V6

## Direção do usuário

O usuário gostou da V5 em relação às versões anteriores, mas quer uma edição mais interessante com **mais imagens e fotos variadas**. Preserve a identidade MAPA SUJO: masthead grande e centralizado no topo, papel de jornal, recortes fotográficos, carimbos e ticker. Mantenha a sincronização visual por palavra. Mapas só devem aparecer quando geografia for realmente relevante — não como abertura padrão nem como único recurso visual. Não reescrever a narração sem pedido.

A V4 foi rejeitada por desenhos/elementos abstratos rústicos e retratos atrasados. A V5 aproximou-se da direção certa; o usuário agora pediu gerar um vídeo com as atualizações V6. A V5 foi preservada e usada como master.

## V6 gerada

- **MP4 de revisão local:** `out/ed003_v6_fotos_contextuais.mp4`.
- Duração 79,33 s; 1080×1920; 30 fps; H.264/AAC; 9.938.630 bytes (~9,94 MB); `+faststart`.
- O encode usa CRF 25. A V5 já tinha passado pelo denoise; a V6 não reaplica denoise para evitar suavização dupla.
- O AAC foi copiado bit a bit da V5: locução, trilha, volume e timing de áudio não foram alterados.
- QA técnico do kit: 8 checagens, 0 falhas.  −14,1 LUFS e −1,2 dBTP; corte/voz, dimensões, fps e duração passam.
- Decodificação integral por FFmpeg concluída; foram inspecionados quadros pós-encode nas duas janelas.
- Auditoria pré-entrega: **NEEDS REVIEW**, saída 2. `WARN` por não informar `--tts-turns`; revisão/escuta humana continua pendente. WER 4,1% entre texto/ASR, com variações de números e nomes listadas no relatório. O relatório não aprova a versão para publicação.
- Relatório: `out/audit_report_v6.md`; folha de contato final: `out/check/post_frames/contact_final_v6.jpg`.

## Novas fotos contextuais e sincronização

1. **Fachada do Banco Master**, entra em 22,04 s, 100 ms antes da palavra “Master” (22,14 s), e cede à cartela de maio em 26,40 s. Crédito visível: `Rovena Rosa / Agência Brasil · 19/11/2025`. É foto do local, não evidência de evento investigado.
2. **Edifício do STF**, entra em 68,58 s, 100 ms antes de “Parecer” (68,68 s), e termina no início do beat seguinte, em 72,12 s. Cartela deixa explícito `PARECER DA PGR ≠ DECISÃO DO STF`; identifica a imagem como foto de arquivo. Crédito visível: `Dasfour2022 · Wikimedia Commons · CC BY-SA 4.0 · recorte/movimento`.

Fotos, fontes e detalhes de licença: `IMAGENS_E_DIREITOS.md` e `assets/`. O renderer V6 aplica cartão editorial rasgado, slide/zoom 2.5D discreto e créditos; nenhuma fotografia foi gerada por IA ou alterada semanticamente. A V5 segue preservada.

## Direitos e liberação

**Esta V6 é uma prévia de revisão, não uma versão aprovada para publicação.** Confirmar o direito de uso específico da foto da Agência Brasil. Respeitar a licença CC BY-SA 4.0 da foto do STF, incluindo atribuição, link da licença, indicação de alterações e a exigência ShareAlike na adaptação distribuída. A autorização comercial/pública do retrato de Daniel Vorcaro que já aparece na V5 também continua não confirmada. Revisão humana integral continua pendente.

## Retomada e arquivos

- Renderer reprodutível: `render_episode_v6.py`; usa o MP4 V5 como base e acrescenta dois segmentos transparentes.
- Executar smoke test: `python3 render_episode_v6.py --smoke`.
- Re-renderizar a V6: `python3 render_episode_v6.py --render`.
- Base/áudio: `../revisao_v5_visual_sincronizada/out/ed003_v5_sincronizada.mp4` e `../revisao_v3_cortes_visuais/beats.json`.
- Produção e comandos: `PRODUCAO_V6.md`; checklist humano: `review_checklist_v6.md`.
- O MP4, PNGs de overlay e quadros de conferência são mídia local e não devem entrar no GitHub público. O código/documentação V6 podem ser versionados separadamente.

## Próximas ações

1. Assistir ao MP4 inteiro em velocidade normal, com áudio, e ouvir o WAV seco conforme o checklist.
2. Revisar em celular todos os cortes, créditos, legibilidade, datas e sincronização visual, além da citação do beat 3 contra a fonte.
3. Confirmar quantos turnos TTS compõem a fala original e reexecutar a auditoria com `--tts-turns` correto.
4. Confirmar direitos de todas as fotos antes de qualquer publicação. Só então decidir se esta V6 precisa de polimento adicional ou se pode ser liberada.

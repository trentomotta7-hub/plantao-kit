# Produção V3.2 — cortes visuais

Esta revisão responde ao problema de planos longos e alternância mecânica observado na V3.1. Mantém o visual MAPA SUJO das edições 001/002 — papel de jornal, recortes, cartelas, carimbos, mapas e ticker — sem migrar para a estética digital de tela cheia.

## O que mudou

- 41 estados visuais internos, ancorados aos dez beats falados, com cortes curtos em vez de uma única composição parada durante cada bloco.
- Alternância de página editorial, painel escuro hachurado, mapa rasgado, fotografia documental creditada e fotografia contextual explicitamente marcada como ilustrativa.
- Zoom e pan mais perceptíveis, reiniciados em cada composição; os flashes não foram adicionados a cada microcorte.
- Narração, trilha/mix, roteiro e timings mantidos da revisão anterior.

## Render e QA

- 2.379 quadros; 1080×1920; 30 fps; duração-alvo/medida 79,30 s.
- QA do projeto: 8 checagens, zero falhas; −14,1 LUFS e −1,2 dBTP.
- Auditoria: WER roteiro–ASR 4,1%; revisão humana permanece pendente.
- Exportação entregue como **prévia**, não aprovada para publicação. É necessário assistir e ouvir o arquivo integralmente, e confirmar direitos de uso da foto de Vorcaro.

Para reproduzir a renderização/codificação, usar `./render_v32.sh` nesta pasta.

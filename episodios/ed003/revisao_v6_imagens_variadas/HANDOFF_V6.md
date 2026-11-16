# Retomada de sessão — MAPA SUJO, edição 003, V6

## Direção já confirmada pelo usuário

O usuário gostou da V5 em relação às versões anteriores, mas quer deixá-la mais interessante com **mais imagens e fotos variadas**. Ele escolheu isso ao ser perguntado se queria variar fotos ou margens/enquadramentos. Portanto, priorize variedade de imagens reais/contextuais; não interprete a resposta como pedido principal por margens diferentes. Preserve a identidade MAPA SUJO: masthead grande e centralizado no topo, página de jornal, recortes, carimbos e ticker. Mantenha a sincronização visual palavra a palavra. Mapa só entra quando localização for realmente relevante — não é uma abertura padrão nem o único recurso visual.

O usuário rejeitou a V4 por desenhos/elementos abstratos rústicos e por retratos atrasados em relação à fala. A V5 ficou mais próxima da direção desejada, mas ainda repete retratos/cartelas em alguns pontos. A orientação desta retomada é variar as imagens, não redesenhar a marca nem reescrever o roteiro.

## Estado da V5 existente

- Prévia local: `../revisao_v5_visual_sincronizada/out/ed003_v5_sincronizada.mp4`.
- Especificações medidas: 1080×1920, 30 fps, H.264/AAC, 79,33 s, 9.651.248 bytes, aproximadamente 9,65 MB.
- QA do kit: 8 checagens, zero falhas; o arquivo decodificou por inteiro. Lead visual de 0,10 s, primeira palavra em 0,28 s, áudio −14,1 LUFS e −1,2 dBTP.
- Auditoria automatizada: `NEEDS REVIEW`. Não foi registrada escuta humana integral; há aviso sobre quantidade de turnos TTS não informada. O relatório também pede conferir a citação do beat 3. A foto de Daniel Vorcaro tem autorização pública/comercial não confirmada. Não tratar a versão como aprovada ou pronta para publicação.
- A V5 não foi substituída por este estudo. O MP4, áudio e quadros de render são arquivos de mídia e não devem ser colocados no GitHub público sem pedido explícito; respeite também `AGENTS.md`.

## Fotos novas salvas para o estudo

As duas fotos foram copiadas para `assets/` desta pasta. Foram selecionadas por busca de imagens e checadas nas páginas-fonte. Não são imagens geradas por IA.

1. `assets/fachada_banco_master_rovena_rosa_ebc.jpg` — fachada do Banco Master na rua Elvira Ferraz, Itaim Bibi, São Paulo; foto de Rovena Rosa/Agência Brasil, 19/11/2025. A Agência Brasil e o serviço oficial do gov.br indicam banco gratuito com crédito obrigatório, com exceções para imagens de parceiros marcadas como direitos reservados. Reproduza o crédito na imagem: `Rovena Rosa/Agência Brasil`. Confirmar que a imagem específica está coberta pelas condições de uso para a publicação pretendida.
2. `assets/stf_edificio_dasfour2022_commons.jpg` — edifício do STF, Praça dos Três Poderes, Brasília; foto de Dasfour2022, 14/08/2010. Wikimedia Commons indica CC BY-SA 4.0. Crédito: `Dasfour2022 · Wikimedia Commons · CC BY-SA 4.0`; indicar recorte/movimento e cumprir CompartilhaIgual na distribuição da adaptação.

A lista de URLs, os créditos completos e as condições estão em [`IMAGENS_E_DIREITOS.md`](IMAGENS_E_DIREITOS.md). Atribuições também foram adicionadas a `CREDITOS.md`.

## Amostra planejada — não renderizada ainda

Criar primeiro uma prova curta e não substituir a V5:

- **Beat 4 — Banco Master:** o gatilho `master` entra em 22,04 s (100 ms antes da palavra em 22,14 s). Mostrar a fachada a partir desse gatilho, com crédito visível, e manter a foto durante o trecho relevante até o marco temporal `maio` em 26,40 s. Movimento lateral/zoom muito leve sobre o cartão fotográfico rasgado, sem ligar a foto a pessoas.
- **Beat 9 — PGR/STF:** a comparação começa em 68,58 s; o termo “Supremo” aparece em 71,00 s. Usar a foto do edifício do STF como arquivo institucional em uma janela curta dessa comparação, com crédito/licença visíveis. Não sugerir que a foto registra uma sessão ou a decisão mencionada.
- Para uma prova rápida, montar dois trechos originais não contíguos, 21,94–31,10 s e 64,04–72,12 s, deixando explícito que é uma montagem de demonstração. Dentro de cada trecho, preservar áudio e timestamps originais. A legenda palavra a palavra continua no renderer V5.
- Revisar a amostra em tela pequena e verificar que os créditos estão legíveis. Só então propor a integração dessas imagens no episódio inteiro. Manter a versão V5 intacta até aprovação visual.

Evitar as imagens genéricas existentes `cash_table.jpg`, `gavel.jpg` e `prison.jpg` nesta nova direção: podem sugerir apreensão, ato judicial ou encarceramento específicos, sem comprovação no trecho. Não usar o mapa como decoração.

## Arquivos e retomada

- Renderer-base e planos V5: `../revisao_v5_visual_sincronizada/render_episode_v5.py`, `storyboard_v5.json`, `storyboard_v5.md` e `timing_audit_v5.md`.
- Fonte dos tempos palavra a palavra: `../revisao_v3_cortes_visuais/beats.json`.
- Regras obrigatórias do repo: ler `AGENTS.md`, `skills/plantao-video-autoreview/SKILL.md` e `plantao-video/SKILL.md` antes de editar/renderizar.
- Esta pasta documenta o estudo V6. A prova curta ainda não foi renderizada; os dois assets de contexto e as fontes já estão salvos.
- Não fazer uma versão completa antes da prova curta ser vista pelo usuário. Depois de eventual integração, executar QA numérico, auditoria e revisão humana integral; checar direitos de todas as fotos antes de publicar.

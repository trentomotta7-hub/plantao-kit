# Direção visual V5 — MAPA SUJO, edição 003

## Assinatura fixa

- O masthead **MAPA SUJO** aparece grande, centralizado no topo, acompanhado de “Edição 003 · Contexto e inferência”.
- Papel de jornal, recortes fotográficos, créditos junto às fotos, cartelas de alto contraste e ticker móvel preservam a identidade da série.
- O acabamento é editorial e fotográfico, com menos rabiscos, selos e ilustrações abstratas do que a V4; 2.5D vem do movimento independente entre fundo, cartão/recorte e fotografia impressa.
- Fotos de pessoas reais são recortes de arquivo: não são geradas, retocadas para sugerir expressão, nem animadas como se a pessoa agisse.

## Regra de mapas

O nome da marca contém “MAPA”, mas isso não obriga a inserir um mapa geográfico em todo episódio. Nesta edição, a locução não nomeia uma cidade/localidade que necessite cartografia; portanto, **a V5 não usa mapa**. Não aparece mapa por hábito, como fundo, abertura ou decoração. Se uma edição futura tratar de um local nomeado e relevante, o mapa entra apenas nesse trecho e identifica o lugar efetivamente falado.

## Variação narrativa entre beats

1. Gancho editorial e pergunta; retratos entram em palavras distintas.
2. Data em cartela dominante, atribuição ao UOL e contexto do destinatário.
3. Citação apresentada como trecho reportado, sem simular conversa original.
4. Relação financeira e linha cronológica; a ligação visual é apenas entre instituições, com rótulo “credor de”, sem seta causal ou referência a pessoas.
5. “Interesse econômico” e “não prova”; fotos de Moraes e Vorcaro em composições independentes.
6. Diferença entre mensagens não recuperadas e imagens de textos identificadas; sem interface de chat ou documento fabricado.
7. Relatórios em revisão e ressalva “não confirma nem afasta”.
8. Respostas/ausências atribuídas, data-limite e declaração de Fábio Faria sem retrato inventado.
9. Retrato de Paulo Gonet; distinção visual explícita entre parecer da PGR e decisão do Supremo.
10. Síntese em faixas e encerramento com pergunta.

## Sincronização

O plano final é calculado com `beats.starts[i] + words[i][k].t`, porque os `t` são relativos ao início da fala, não ao corte do beat. Cada entrada visual começa 0,10 segundo antes da palavra correspondente, limitada ao corte do próprio beat. A transcrição aparece como legenda progressiva: somente palavras já iniciadas são mostradas, com destaque para a palavra atual.

## Rigor factual e direitos

“Mensagem atribuída/relatada”, “não prova”, “relatórios em revisão” e “parecer não é decisão” permanecem explícitos. Não se desenham linhas entre Vorcaro e Moraes. Os créditos das imagens acompanham os retratos. A autorização pública/comercial da fotografia de Daniel Vorcaro não está confirmada; a exportação V5 é um rascunho para revisão, não uma autorização de publicação.

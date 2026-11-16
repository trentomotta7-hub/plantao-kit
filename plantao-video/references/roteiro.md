# Roteiro, retenção e responsabilidade editorial

## 1. Escolha da pauta e do formato

Não há uma fórmula de viralização. Escolha pauta com relevância atual, pergunta clara, evidências acessíveis e consequência compreensível. Um número forte pode ajudar, mas só entra se sua fonte, período e significado estiverem claros.

Fontes a priorizar: documentos e comunicados de órgãos públicos, decisões judiciais, dados oficiais e reportagens identificadas de veículos confiáveis. Registre cada afirmação em `briefing_editorial.json`, com classificação (`confirmed`, `attributed` ou `uncertain`), fonte e atribuição. O validador verifica campos e referências, não confirma a verdade da informação.

Escolha uma estrutura adequada à pauta em `formatos.md`: número explicativo, fluxo de dinheiro, atualização, mito versus fato, lacunas ainda abertas ou mapa de alcance. Os 10 blocos seguem disponíveis como padrão compatível, não são obrigatórios para todo corte.

Regras de apuração:
- Número sem fonte direta não entra. Exiba ou fale quem publicou o dado e de que período ele é.
- Dado geográfico deve mostrar período e metodologia; se for esquemático, marcar “mapa ilustrativo”.
- Alegações devem ser atribuídas. Diferencie investigação, indiciamento, denúncia, decisão cautelar e condenação.
- Procure a resposta da pessoa/instituição citada e inclua-a quando disponível.
- Não use estilo de vida, riqueza ou relações pessoais como prova de crime.
- Não apresente imagem gerada por IA como fotografia documental. Identifique reconstruções/ilustrações quando houver risco de confusão.
- Para notícia que não seja do dia, confira o desdobramento mais recente antes de publicar.

## 2. Arquitetura-padrão de 10 blocos

O formato pode ser adaptado ou substituído por um esqueleto de `formatos.md`. Se usar 10 blocos, cada bloco deve acrescentar uma informação real; não crie perguntas artificiais só para aumentar tempo.

| # | Bloco | Função editorial | Imagem sugerida |
|---|---|---|---|
| 1 | Gancho | fato específico + por que importa | manchete e elemento principal |
| 2 | Promessa | pergunta que o vídeo responderá | mapa ou cartão que estabelece a dúvida |
| 3 | Dado | número/ato central com contexto | cartela legível com período e fonte |
| 4 | Escala | dimensão do acontecimento | mapa ou comparação com limites declarados |
| 5 | Contexto | origem/antecedente necessário | linha do tempo ou documento |
| 6 | Impacto | consequência humana/institucional comprovada | imagem ilustrativa devidamente marcada |
| 7 | Evidências | o que sustenta a afirmação | recortes, fontes e explicação |
| 8 | Contraponto | resposta, defesa ou dado que limita a tese | cartela “o que se sabe / o que não se sabe” |
| 9 | Resposta | conclusão proporcional à evidência | síntese visual da promessa |
| 10 | CTA | pergunta genuína sobre o tema | convite curto, sem induzir engajamento artificial |

A pergunta do início precisa ser respondida no próprio vídeo. Não reservar a informação essencial para uma parte futura.

## 3. Escrita falada

- Uma ideia por frase e vocabulário falado, mas sem sacrificar precisão.
- Escreva nomes e números como devem ser pronunciados pelo TTS.
- Explique siglas na primeira ocorrência.
- Evite “supostamente” solto: diga quem alega, em qual investigação ou documento.
- Evite afirmações categóricas sobre culpa de pessoa identificável quando o caso está em investigação.
- O roteiro de produção deve ser exatamente o texto narrado. Para outra duração, escreva outra versão e gere outra tomada contínua.
- Não use cortes automáticos por silêncio, `atempo` ou locução por blocos para encaixar duração. Se a tomada não funcionar, ajuste o texto e gere novamente.

## 4. Gancho e primeira tela

Antes de completar o roteiro, escreva três aberturas para o mesmo fato. Cada uma deve ter uma fonte rastreável e uma recompensa informativa que o vídeo realmente entrega. Prefira especificidade, contraste verificável e pergunta concreta. Evite rumor, adjetivo de choque ou clickbait.

O primeiro quadro deve comunicar o assunto sem áudio, e a primeira palavra deve começar até 0,30s segundo os beats. Fala, texto e imagem devem apontar para o mesmo fato. Rode:

```bash
python3 <skill>/scripts/check_hook.py --script roteiro.txt --beats beats.json
```

A ferramenta só verifica itens mecânicos; o time ainda precisa julgar clareza, adequação, legibilidade e suporte documental.

## 5. Duração e variantes

A duração depende da pauta e da finalidade: `quick` 20–45s, `standard` 60–75s ou `explainer` 75–90s. Use 60–75s quando houver conteúdo suficiente e isso servir à estratégia; a duração, isoladamente, não assegura monetização nem distribuição. Para o programa Creator Rewards, confirme as regras e disponibilidade vigentes antes de prometer elegibilidade.

Cada variante tem roteiro, narração, transcrição, beats, render, QA e checklist próprios. Nunca cortar ou acelerar o mestre para fabricar uma versão curta e nunca alongar com silêncio.

QA técnico por perfil, por exemplo:

```bash
python3 <skill>/scripts/qa.py --video out/edicao.mp4 --beats beats.json --preset quick
python3 <skill>/scripts/qa.py --video out/edicao.mp4 --beats beats.json --preset standard
```

## 6. Aprendizado após publicação

Registrar métricas nativas por plataforma em `templates/publication_metrics.csv`, incluindo janela uniforme. Medir tempo médio assistido relativo à duração, conclusão quando disponível, compartilhamentos e salvamentos por mil visualizações, comentários e seguidores gerados.

```bash
python3 <skill>/scripts/analyze_metrics.py --input publication_metrics.csv
```

Comparar múltiplos vídeos de pauta e janela próximas. Alterar uma hipótese criativa por vez quando possível. Métricas são sinais, não provam causalidade; visualizações isoladas não explicam o desempenho.

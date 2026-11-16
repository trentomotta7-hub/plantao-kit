# Auditoria de sincronização — V5

Os eventos abaixo usam os timestamps palavra-a-palavra de `beats.json`. Para cada gatilho, a imagem/texto entra 100 ms antes do início acústico do token (lead visual → fala), limitado ao início do beat. Se a fala começa 100 ms após o corte, o primeiro token pode ter entrada exatamente no corte.

| Beat | Evento | Token reconhecido | Visual | Palavra falada | Lead |
|---:|---|---|---:|---:|---:|
| 01 · Gancho: mensagem atribuída e pergunta | mensagem | mensagem | 0.340s | 0.440s | 0.100s |
| 01 · Gancho: mensagem atribuída e pergunta | atribuída | atribuída | 0.860s | 0.960s | 0.100s |
| 01 · Gancho: mensagem atribuída e pergunta | Daniel | Daniel | 1.480s | 1.580s | 0.100s |
| 01 · Gancho: mensagem atribuída e pergunta | Moraes | "Moraes | 2.700s | 2.800s | 0.100s |
| 01 · Gancho: mensagem atribuída e pergunta | Isso | Isso | 5.000s | 5.100s | 0.100s |
| 01 · Gancho: mensagem atribuída e pergunta | Não. | Não. | 7.500s | 7.600s | 0.100s |
| 02 · Data e contexto da previsão | Segundo | Segundo | 8.460s | 8.560s | 0.100s |
| 02 · Data e contexto da previsão | fevereiro | fevereiro | 9.600s | 9.700s | 0.100s |
| 02 · Data e contexto da previsão | Vorcaro | Vorcaro | 11.300s | 11.400s | 0.100s |
| 02 · Data e contexto da previsão | previsão | previsão | 12.240s | 12.340s | 0.100s |
| 02 · Data e contexto da previsão | ex-sócio | ex-sócio | 12.980s | 13.080s | 0.100s |
| 03 · Trecho de citação reportada | cita: | cita: | 16.760s | 16.860s | 0.100s |
| 03 · Trecho de citação reportada | "Kássio | "Kássio | 17.440s | 17.540s | 0.100s |
| 03 · Trecho de citação reportada | Moraes. | Moraes. | 18.840s | 18.940s | 0.100s |
| 03 · Trecho de citação reportada | Vai | Vai | 19.580s | 19.680s | 0.100s |
| 04 · Vínculo financeiro e regra de transição | master | master | 22.040s | 22.140s | 0.100s |
| 04 · Vínculo financeiro e regra de transição | credor | credor | 22.680s | 22.780s | 0.100s |
| 04 · Vínculo financeiro e regra de transição | Ulbra, | Ulbra, | 24.080s | 24.180s | 0.100s |
| 04 · Vínculo financeiro e regra de transição | maio, | maio, | 26.400s | 26.500s | 0.100s |
| 04 · Vínculo financeiro e regra de transição | pedidos | pedidos | 29.240s | 29.340s | 0.100s |
| 05 · Contexto não é prova | interesse | interesse | 32.240s | 32.340s | 0.100s |
| 05 · Contexto não é prova | prova | prova | 33.840s | 33.940s | 0.100s |
| 05 · Contexto não é prova | Moraes | Moraes | 34.300s | 34.400s | 0.100s |
| 05 · Contexto não é prova | Vorcaro. | Vorcaro. | 36.680s | 36.780s | 0.100s |
| 06 · Mensagens não recuperadas | Outro | Outro | 37.740s | 37.840s | 0.100s |
| 06 · Mensagens não recuperadas | UOL | UOL | 38.860s | 38.960s | 0.100s |
| 06 · Mensagens não recuperadas | recuperou | recuperou | 40.060s | 40.160s | 0.100s |
| 06 · Mensagens não recuperadas | imagens | imagens | 44.180s | 44.280s | 0.100s |
| 06 · Mensagens não recuperadas | Vorcaro. | Vorcaro. | 46.000s | 46.100s | 0.100s |
| 07 · Relatórios da PF em revisão | cúpula | cúpula | 47.320s | 47.420s | 0.100s |
| 07 · Relatórios da PF em revisão | refazer | refazer | 48.480s | 48.580s | 0.100s |
| 07 · Relatórios da PF em revisão | excesso | excesso | 50.700s | 50.800s | 0.100s |
| 07 · Relatórios da PF em revisão | Isso | Isso | 52.720s | 52.820s | 0.100s |
| 08 · Respostas e ausência de resposta | Moraes, | Moraes, | 56.420s | 56.520s | 0.100s |
| 08 · Respostas e ausência de resposta | Vorcaro | Vorcaro | 57.540s | 57.640s | 0.100s |
| 08 · Respostas e ausência de resposta | PF | PF | 58.300s | 58.400s | 0.100s |
| 08 · Respostas e ausência de resposta | 13 | 13 | 59.780s | 59.880s | 0.100s |
| 08 · Respostas e ausência de resposta | Fábio | Fábio | 61.100s | 61.200s | 0.100s |
| 09 · Parecer da PGR não é decisão | Separadamente, | Separadamente, | 64.040s | 64.140s | 0.100s |
| 09 · Parecer da PGR não é decisão | Paulo | Paulo | 65.020s | 65.120s | 0.100s |
| 09 · Parecer da PGR não é decisão | Vorcaro. | Vorcaro. | 67.620s | 67.720s | 0.100s |
| 09 · Parecer da PGR não é decisão | Parecer | Parecer | 68.580s | 68.680s | 0.100s |
| 09 · Parecer da PGR não é decisão | Supremo. | Supremo. | 71.000s | 71.100s | 0.100s |
| 10 · Síntese e pergunta final | mensagem | mensagem | 73.060s | 73.160s | 0.100s |
| 10 · Síntese e pergunta final | relatório | relatório | 74.420s | 74.520s | 0.100s |
| 10 · Síntese e pergunta final | dúvidas | dúvidas | 75.880s | 75.980s | 0.100s |
| 10 · Síntese e pergunta final | nova | nova | 77.480s | 77.580s | 0.100s |

**Verificação automática:** 47 entradas; todos os leads = 0.10s; tolerância ±0,001s; gatilhos sem correspondência = 0.
**Definição usada:** os tempos `t` em `beats.json` são locais ao início da fala `starts[i]`, não ao corte `cuts[i]`. Portanto `t_global = starts[i] + t` e `visual = max(cuts[i], t_global − 0,10)`.

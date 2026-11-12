# Roteiro e retenção

## 1. Pauta: o que vira episódio

Critério único: **um número forte + uma contradição**. Exemplo do ep. 01: número = R$ 190,3 milhões; contradição = "puseram na lista de terroristas e nada mudou na esquina".

Onde procurar (sempre checar data e fonte primária):
- **AGU / gov.br / MJSP / PF**: apreensões, ações civis, operações, perdimento.
- **BBC Brasil, Folha, UOL, G1, Poder360**: cobertura com contexto e números.
- **Fogo Cruzado, ISP-RJ, Atlas da Violência, FBSP**: território, mortes, % de área.
- **Reuters/FT**: quando a notícia é fora do Brasil (lista de terroristas, sanções).

Regras de apuração:
- Número sem fonte = número cortado. Legenda de fonte no rodapé do bloco (`FONTES: AGU · GOV.BR · BBC`).
- Dado de território é sempre estimativa: dizer "segundo o estudo" e usar "mapa ilustrativo".
- Não nomear pessoa como criminosa sem condenação. "A investigação aponta", "segundo a denúncia".
- Se o fato tem mais de 10 dias, procure o desdobramento (é o que rende segunda parte).

## 2. Arquitetura de 10 blocos

O vídeo é um **loop aberto**: a pergunta mestra é feita no bloco 1 e só respondida no 9. Cada bloco entrega uma informação nova **e** uma pergunta nova. Ninguém sai no meio porque sempre falta uma peça.

| # | Bloco | O que a voz faz | O que a imagem faz |
|---|---|---|---|
| 1 | Gancho | fato + consequência que dói ("não mudou nada na esquina") | manchete, foto, carimbo, caneta |
| 2 | Promessa | "não é onde você pensa" | mapa apagado, X no alvo |
| 3 | O número | "ela ataca o dinheiro: R$ X" | cartela gigante |
| 4 | Escala | "olha o mapa: 26 de 27" | estados acendendo, contador |
| 5 | Origem | "não começou na rua, começou no presídio: 1993 / 1979" | foto + dois cartões |
| 6 | Impacto | "1/3 do território" | número em disco sobre foto |
| 7 | Consequências | lista de 4 ("banco congela, doação vira crime…") | 4 cartelas numeradas |
| 8 | Virada | "só que o fuzil não vem da lista, vem da fronteira" | mapa na fronteira, seta de fora |
| 9 | Resposta | "a lista não é sobre a esquina, é sobre o dinheiro que paga a esquina" | mapa cheio apagado + 2 frases |
| 10 | CTA | pergunta direta + "parte 2 amanhã" | cartela + seta |

### Como escrever cada linha
- **Frases de 6 a 12 palavras.** Uma ideia por frase. Ponto final é respiro.
- **Número sempre falado por extenso**: "cento e noventa milhões", "vinte e seis dos vinte e sete".
- **Repetição de impacto**: repetir a palavra-chave ("Um terço. Um TERÇO.") — o TTS entrega ênfase em maiúscula.
- **Nada de advérbio de jornalista** ("supostamente", "de certa forma"). Fala de gente: "tá", "pra", "aí".
- **Última frase do bloco abre o próximo**: "mas pra entender o tamanho disso…", "só que…".
- 10 blocos somam **150–170 palavras** (~65s depois do ajuste de ritmo).

### Roteiro do ep. 01 (referência de tom)
```
1 Os Estados Unidos botaram o PCC e o Comando Vermelho na lista de terroristas. E na prática, não mudou NADA na esquina.
2 E não é porque a lista é fraca. É porque ela não ataca onde você tá pensando.
3 Ela ataca o dinheiro. Cento e noventa milhões de reais que a AGU quer confiscar agora.
4 Mas pra entender o tamanho disso, olha o mapa: vinte e seis dos vinte e sete estados.
5 E isso não começou na rua. Começou no presídio: PCC em noventa e três, Comando Vermelho em setenta e nove.
6 Hoje, no Rio, um terço do território tá sob influência de facção. Um TERÇO.
7 Aí a lista começa a morder: banco congela, doação vira crime, passagem some, extradição fica mais fácil.
8 Só que o fuzil não vem da lista. Vem da fronteira. E a fronteira continua aberta.
9 Então a resposta é essa: a lista não é sobre a esquina. É sobre o dinheiro que paga a esquina.
10 E enquanto o dinheiro não secar, a barricada continua. Comenta aí o que você faria.
```

## 3. Ritmo de fala

- O TTS entrega ~3,2 palavras/s. Isso é rápido demais para leitura de notícia pesada.
- `edit_vo.py` aplica `atempo 0.87` (≈13% mais lento) + respiros. Resultado: ~2,4 palavras/s.
- Se o vídeo passar de 75s, **corte texto**, não acelere de novo.
- Se ficar abaixo de 62s, aumente os `--gaps` antes de inventar conteúdo.

## 4. Gancho: os 3 primeiros segundos

O primeiro frame precisa responder "por que eu paro de rolar?" sem áudio:
1. Manchete em caixa alta ocupando o terço superior.
2. Carimbo vermelho torto (CONFIRMADO / URGENTE / EXCLUSIVO).
3. A frase que dói escrita à mão, em vermelho com marca-texto.

Nunca abrir com logo, vinheta, "olá pessoal" ou pergunta genérica.

## 5. Loop de rewatch
A última frase deve poder emendar na primeira: "…a barricada continua" → "Os Estados Unidos botaram o PCC…". Quem reassiste conta como retenção.

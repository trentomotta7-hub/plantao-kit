# Relatório pré-entrega

**Status: NEEDS REVIEW**

| Estado | Checagem | Resultado |
|---|---|---|
| PASS | vídeo stream | h264 |
| PASS | áudio stream | aac |
| PASS | quadro | 1080×1920 (esperado 1080×1920) |
| PASS | fps | 30.000 |
| PASS | duração | 79.33s (preset explainer: 75–90s) |
| PASS | loudness | -14.1 LUFS (alvo operacional −14 ±0,6) |
| PASS | true peak | -1.2 dBTP (limite −1,0) |
| PASS | beat sheet | 10 blocos; tempos por palavra=sim |
| PASS | MP4 × beats | 79.33s vs 79.32s |
| PASS | lead visual | min–max 0.10–0.10s; alvo 0,06–0,20s |
| PASS | primeira palavra | 0.28s |
| PASS | respiros | nenhuma pausa acima do limite |
| WARN | continuidade TTS | informe `--tts-turns`; uma única voz deve ser uma tomada contínua salvo mudança intencional |
| PASS | roteiro × ASR | WER 4.1%; dois → 2024; mil → [ausente]; e → [ausente]; vinte → [ausente]; e → [ausente]; quatro → [ausente]; cassio → kassio; para → pra; treze → 13 |
| PENDING | escuta/revisão humana | complete e marque o checklist humano; automação não certifica entonação, dicção ou clareza visual |

## Checklist humano obrigatório

- [ ] Ouvir o WAV seco inteiro antes da música.
- [ ] Ouvir o MP4 inteiro uma vez em velocidade normal, sem pular trechos.
- [ ] Ouvir cada emenda com pelo menos 1,5 s de contexto dos dois lados.
- [ ] Conferir consoantes/finais, entonação, pausas, pronúncia e música/SFX mascarando fala.
- [ ] Inspecionar primeiro/último quadro, cada corte, entradas de dado e legibilidade em tela pequena.

Aprovação técnica não significa que a locução ou o vídeo estejam subjetivamente perfeitos. Este relatório registra QA automático e não substitui revisão humana.

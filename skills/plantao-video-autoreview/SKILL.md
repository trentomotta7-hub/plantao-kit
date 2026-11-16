---
name: plantao-video-autoreview
description: Revisão pré-entrega de vídeos narrados do Plantão Kit. Use antes de exportar ou entregar qualquer edição para conferir continuidade da fala, palavras cortadas, sincronismo, mixagem, imagem, texto e integridade do arquivo; bloqueia a entrega até passar pelos testes técnicos e pela escuta humana.
---

# Autorrevisão de vídeo narrado — Plantão Kit

## Princípio de liberação

Não prometer “100% perfeito”: usar uma porta de qualidade verificável. Só marcar **APROVADO PARA ENTREGA** depois de passar nos testes técnicos, comparar fala e roteiro, ouvir a narração e o MP4 completo em velocidade normal, e conferir todas as transições visuais. Se alguma checagem subjetiva não puder ser feita, declarar **PENDENTE DE ESCUTA/REVISÃO**, nunca “pronto”.

## Fluxo obrigatório

1. **Congelar a fonte da fala.** Para locução de uma voz, gerar o texto como uma única passagem/turno sempre que couber no limite do TTS. Usar a mesma voz e uma direção curta e constante. Abrir um novo turno só para mudança intencional de locutor ou interpretação. Não gerar dez parágrafos como dez turnos para depois colá-los como se fossem uma tomada contínua.
2. **Ouvir o WAV seco.** Antes da música, ouvir do início ao fim. Conferir nomes, números, sílabas finais, respiração, naturalidade, ritmo e mudanças involuntárias de timbre/entonação. Corrigir roteiro ou regenerar a tomada inteira; não esconder defeitos com trilha.
3. **Não cortar fonemas.** Não aparar silêncio por limiar/RMS, não segmentar automaticamente por `dips`, e não aplicar `atempo` por padrão. Não deslocar a forma de onda para casar com cartões. Se houver uma falha no TTS, regenerar a passagem. Se uma edição de áudio for absolutamente necessária, selecionar pontos de silêncio verificados por palavra, fazer fade/crossfade curto sem sobrepor fala e escutar cada emenda isoladamente e no contexto.
4. **Transcrever a fonte final.** Usar transcrição com timestamps de palavra no WAV aprovado. Comparar todas as palavras com o texto efetivamente narrado; resolver omissões, inserções, trocas, pronúncias e nomes próprios. Só então gerar `beats.json` com `timing.py`. A imagem se move para acompanhar a fala, nunca a fala para acompanhar a imagem.
5. **Mixar sem mascarar.** Conferir voz inteligível em alto-falante de celular, música abaixo da fala, sem boom/riser cobrindo consoantes. Meta inicial: cerca de −14 LUFS integrados e true peak ≤ −1 dBTP; adaptar apenas com justificativa de plataforma/projeto.
6. **Executar a auditoria técnica.** Rodar `scripts/audit_video.py` com MP4, beats, roteiro, transcrição e número de turnos TTS. Corrigir toda falha; investigar todos os avisos.
7. **Fazer revisão humana completa.** Reproduzir o MP4 inteiro, em velocidade normal e com áudio, sem pular trechos. Escutar novamente cada emenda/corte com pelo menos 1,5 s antes e depois. Conferir especificamente: palavra começando ou terminando no meio; frase interrompida; pausa inesperada; mudança de timbre/volume/emoção entre turnos; ênfase incoerente; música/SFX mascarando fala; pop ou mapa fora da palavra; cartela/ticker ilegível; visual cortando antes da conclusão verbal; quadro inicial e final.
8. **Inspecionar imagem em transições.** Conferir o primeiro quadro, todos os cortes (`beats.cuts`), entradas dos elementos principais e último quadro. Ler números, nomes, estados, fontes/legendas e áreas seguras. Fazer amostra temporal densa ao redor de transições, não apenas uma folha de contato espaçada.
9. **Repetir após qualquer alteração.** Se mudar voz, edição, trilha, mix, timing, conteúdo visual ou encode, refazer auditoria técnica e escutar de novo pelo menos os trechos afetados e as duas transições adjacentes. Uma correção nunca herda aprovação anterior.
10. **Entregar com transparência.** Guardar relatório e versão exata do MP4 aprovado. Informar limitações restantes. Não entregar uma versão marcada como final se o checklist humano ainda estiver pendente.

## Rodar a checagem técnica

```bash
python3 <skill>/scripts/audit_video.py \
  --video out/edicao.mp4 \
  --beats beats.json \
  --script roteiro.txt \
  --stt vo_transcription.json \
  --preset explainer \
  --tts-turns 1 \
  --report qa_report.md
```

`--preset` aceita `quick` (20–45 s), `standard` (60–75 s), `explainer` (75–90 s) e `legacy` (45–75 s, padrão compatível). `--min-duration` e `--max-duration` podem substituir os limites de um preset. O script confere streams, formato/fps, duração, loudness/true peak, duração MP4 vs. beats, lead visual antes da voz, primeira palavra, respiros e alinhamento aproximado entre roteiro e transcrição. Opcionalmente, `--audio-cuts 8.2,15.9` sinaliza qualquer corte de áudio dentro de palavra. Uma aprovação técnica **não substitui a escuta**: timbre, entonação, truncamento perceptivo e inteligibilidade em celular exigem revisão humana.

Código de saída `1` = falha; `2` = há aviso ou checklist humano incompleto; `0` = nenhuma falha/aviso e checklist marcado como aprovado via `--human-checklist`. Não ignorar `1` ou `2` para publicar. Registrar a lista preenchida com `templates/review_checklist.md`.

## Critérios de bloqueio

- Qualquer palavra audivelmente cortada, sílaba engolida, frase interrompida ou pronúncia errada: **REPROVADO**.
- Uma mesma voz narradora muda de timbre/entonação sem intenção entre turnos: **REPROVADO**; preferir uma tomada contínua.
- Roteiro e fala divergem em dado, nome, número ou negação: **REPROVADO**.
- Trilha ou impacto encobre uma palavra; voz distorce ou true peak excede o teto: **REPROVADO**.
- Frame/corte visual contradiz a fala, informação não é legível ou arquivo não abre: **REPROVADO**.
- Auditoria técnica passa, mas a revisão humana está incompleta: **PENDENTE**, não aprovado.

## Limites

Automação detecta metadados, níveis, tempos e divergências textuais aproximadas; ela não prova naturalidade, emoção, dicção ou perfeição visual. Não inferir “100% perfeito” de LUFS, transcrição, frames isolados ou qualquer pontuação automática. Se houver incerteza, marcar o trecho e pedir escuta/decisão, em vez de declarar aprovação.

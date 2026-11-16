#!/usr/bin/env python3
"""Normaliza as propostas editoriais V5 e ancora eventos nos timecodes reais da fala.

Os timestamps de beats.json são relativos a starts[i] (início da fala), não a cuts[i].
O evento visual entra 100 ms antes da palavra, limitado ao início do beat.
"""
from __future__ import annotations
import json
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ED003 = HERE.parent
V32 = ED003 / "revisao_v3_cortes_visuais"
JOB_OUTPUT = Path("/home/ubuntu/.manus-jobs/1e411c0ca950/output.txt")
BEATS_FILE = V32 / "beats.json"
OUT_JSON = HERE / "storyboard_v5.json"
OUT_MD = HERE / "storyboard_v5.md"
AUDIT_MD = HERE / "timing_audit_v5.md"
LEAD = 0.10


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def main() -> None:
    job = json.loads(JOB_OUTPUT.read_text(encoding="utf-8"))
    plan = job["storyboard"]
    audio = json.loads(BEATS_FILE.read_text(encoding="utf-8"))

    # Um estímulo de abertura simples, ligado à palavra “mensagem”, antes da
    # cartela “MENSAGEM ATRIBUÍDA”; não antecipa texto nem evidencia inexistente.
    first = plan["beats"][0]
    first["visual_events"].insert(0, {
        "trigger_word": "mensagem",
        "relative_time_s": float(audio["words"][0][1]["t"]) - LEAD,
        "global_time_s": 0.0,
        "visual_kind": "carimbo de abertura",
        "asset_or_source": "Tipografia editorial original; relato atribuído ao UOL conforme briefing e FONTES.md.",
        "on_screen_text": "MENSAGEM",
        "camera_motion": "Carimbo amarelo entra em corte seco, com um pequeno assentamento 2.5D; masthead permanece fixo e grande no topo.",
        "editorial_guardrail": "Sincronizar à palavra ‘mensagem’; não simular conversa, captura de tela ou documento original."
    })

    normalized_beats = []
    audit_rows = []
    for i, source_beat in enumerate(plan["beats"]):
        cut = float(audio["cuts"][i])
        speech = float(audio["starts"][i])
        end = float(audio["cuts"][i + 1]) if i + 1 < len(audio["cuts"]) else float(audio["dur"])
        tokens = audio["words"][i]
        events = []
        for j, source_event in enumerate(source_beat["visual_events"]):
            trigger = source_event["trigger_word"]
            target_local = float(source_event.get("relative_time_s", 0.0)) + LEAD
            needle = norm(trigger)
            candidates = [(k, w) for k, w in enumerate(tokens) if norm(w["w"]) == needle]
            if not candidates:
                raise ValueError(f"Gatilho sem palavra correspondente: beat {i+1}, {trigger!r}")
            word_index, word = min(candidates, key=lambda pair: abs(float(pair[1]["t"]) - target_local))
            word_time = speech + float(word["t"])
            visual_time = max(cut, word_time - LEAD)
            lead = word_time - visual_time
            if abs(lead - LEAD) > 0.001:
                raise ValueError(f"Lead não fecha em 100 ms: beat {i+1}, {trigger!r}, {lead:.3f}s")
            event = dict(source_event)
            event.update({
                "event_number": j + 1,
                "trigger_word_index": word_index,
                "matched_transcript_token": word["w"],
                "word_time_s": round(word_time, 3),
                "time_s": round(visual_time, 3),
                "relative_time_s": round(visual_time - cut, 3),
                "lead_s": round(lead, 3),
            })
            events.append(event)
            audit_rows.append((i + 1, source_beat["beat_title"], trigger, word["w"],
                               word_time, visual_time, lead, source_event["visual_kind"]))

        events.sort(key=lambda item: (item["time_s"], item["event_number"]))
        normalized_beats.append({
            "beat_number": i + 1,
            "title": source_beat["beat_title"],
            "start_s": cut,
            "speech_start_s": speech,
            "end_s": end,
            "map_use": source_beat["map_use"],
            "style_variety_note": source_beat["style_variety_note"],
            "events": events,
        })

    output = {
        "edition": 3,
        "revision": "V5 — visual fotográfica sincronizada",
        "duration_s": float(audio["dur"]),
        "fps": 30,
        "resolution": [1080, 1920],
        "voice_visual_lead_s": LEAD,
        "map_decision": plan["map_decision"],
        "global_rules": plan["global_rules"],
        "cross_beat_variety": plan["cross_beat_variety"],
        "missing_assets_or_rights": plan["missing_assets_or_rights"],
        "timing_risks": plan["timing_risks"],
        "beats": normalized_beats,
    }
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Storyboard V5 — edição 003",
        "",
        "**Direção:** MAPA SUJO maior, centralizado no topo; jornalismo visual com fotos reais, recortes, citações atribuídas, datas, carimbos, linhas do tempo e movimento 2.5D discreto. Sem mapa geográfico nesta edição: o roteiro não nomeia localidade que justifique cartografia.",
        "",
        f"Duração planejada: {audio['dur']:.2f}s · 1080×1920 · 30 fps · {sum(len(b['events']) for b in normalized_beats)} eventos visuais ancorados por palavra.",
        "",
        "**Regra de sincronização:** tempo da palavra = `beats.starts[i] + palavra.t`; início visual = palavra − 0,10s, nunca antes do corte do beat. Legendas palavra a palavra acompanham a fala real.",
        "",
    ]
    for beat in normalized_beats:
        md += [f"## Beat {beat['beat_number']:02d} — {beat['title']}", "",
               f"Janela visual {beat['start_s']:.2f}–{beat['end_s']:.2f}s; início de fala {beat['speech_start_s']:.2f}s. {beat['map_use']}", "",
               "| Entrada visual | Palavra-gatilho | Recurso / texto | Tratamento |",
               "|---:|---|---|---|"]
        for e in beat["events"]:
            txt = e["on_screen_text"].replace("|", "\\|").replace("\n", "<br>")
            kind = e["visual_kind"].replace("|", "\\|")
            asset = e["asset_or_source"].replace("|", "\\|")
            md.append(f"| {e['time_s']:.2f}s | {e['trigger_word']} ({e['word_time_s']:.2f}s) | {txt} — {asset} | {kind} |")
        md += ["", f"**Variação:** {beat['style_variety_note']}", ""]
    md += ["## Pendências antes de publicação", ""]
    md += [f"- {item}" for item in plan["missing_assets_or_rights"]]
    md += ["- Rever a literalidade, acentuação e pontuação da citação do beat 3 contra a fonte primária/reportagem; o render acompanha a locução/transcrição aprovada, sem reescrever o áudio.",
           "- Revisão humana completa de ritmo, leitura em celular, precisão das afirmações e direitos de imagem continua obrigatória.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    audit = [
        "# Auditoria de sincronização — V5",
        "",
        "Os eventos abaixo usam os timestamps palavra-a-palavra de `beats.json`. Para cada gatilho, a imagem/texto entra 100 ms antes do início acústico do token (lead visual → fala), limitado ao início do beat. Se a fala começa 100 ms após o corte, o primeiro token pode ter entrada exatamente no corte.",
        "",
        "| Beat | Evento | Token reconhecido | Visual | Palavra falada | Lead |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for b, title, trigger, token, word_time, visual_time, lead, kind in audit_rows:
        audit.append(f"| {b:02d} · {title} | {trigger} | {token} | {visual_time:.3f}s | {word_time:.3f}s | {lead:.3f}s |")
    audit += ["", f"**Verificação automática:** {len(audit_rows)} entradas; todos os leads = {LEAD:.2f}s; tolerância ±0,001s; gatilhos sem correspondência = 0.",
              "**Definição usada:** os tempos `t` em `beats.json` são locais ao início da fala `starts[i]`, não ao corte `cuts[i]`. Portanto `t_global = starts[i] + t` e `visual = max(cuts[i], t_global − 0,10)`. ", ""]
    AUDIT_MD.write_text("\n".join(audit), encoding="utf-8")
    print(f"Criado {OUT_JSON} com {sum(len(b['events']) for b in normalized_beats)} eventos.")
    print(f"Criado {OUT_MD} e {AUDIT_MD}.")
    print("Leads validados: todos 0,100 s.")


if __name__ == "__main__":
    main()

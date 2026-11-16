#!/usr/bin/env python3
"""Technical preflight for a narrated Plantao Kit video.

This tool cannot certify natural speech or visual quality. A zero exit code is
possible only when measurable checks pass, warnings are resolved, and the human
review checklist is explicitly complete.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def probe(path: Path) -> dict:
    p = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path),
    ])
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "ffprobe failed")
    return json.loads(p.stdout)


def loudness(path: Path) -> tuple[float | None, float | None]:
    p = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
        "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-",
    ])
    matches = re.findall(
        r'"input_i"\s*:\s*"(-?[\d.]+)".*?"input_tp"\s*:\s*"(-?[\d.]+)"',
        p.stderr, re.S,
    )
    if not matches:
        return None, None
    return float(matches[-1][0]), float(matches[-1][1])


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", text)


def wer(reference: list[str], heard: list[str]) -> tuple[float, list[tuple[str, str]]]:
    # Levenshtein with operation labels, retaining a compact set of mismatches.
    n, m = len(reference), len(heard)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    back = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0], back[i][0] = i, "D"
    for j in range(1, m + 1):
        dp[0][j], back[0][j] = j, "I"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if reference[i - 1] == heard[j - 1]:
                dp[i][j], back[i][j] = dp[i - 1][j - 1], "M"
            else:
                choices = (
                    (dp[i - 1][j - 1] + 1, "S"),
                    (dp[i - 1][j] + 1, "D"),
                    (dp[i][j - 1] + 1, "I"),
                )
                dp[i][j], back[i][j] = min(choices)
    edits: list[tuple[str, str]] = []
    i, j = n, m
    while i or j:
        op = back[i][j]
        if op == "M":
            i -= 1
            j -= 1
        elif op == "S":
            edits.append((reference[i - 1], heard[j - 1]))
            i -= 1
            j -= 1
        elif op == "D":
            edits.append((reference[i - 1], "[ausente]"))
            i -= 1
        elif op == "I":
            edits.append(("[extra]", heard[j - 1]))
            j -= 1
        else:
            break
    edits.reverse()
    return (dp[n][m] / max(1, n), edits)


def get_heard_words(stt: dict) -> list[str]:
    ws = stt.get("words") or []
    if ws:
        return tokens(" ".join(str(w.get("text", "")) for w in ws))
    return tokens(str(stt.get("full_text", "")))


def add(rows: list[tuple[str, str, str]], status: str, check: str, detail: str) -> None:
    rows.append((status, check, detail))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True, type=Path)
    ap.add_argument("--beats", required=True, type=Path)
    ap.add_argument("--script", type=Path, help="texto realmente narrado")
    ap.add_argument("--stt", type=Path, help="JSON do manus-speech-to-text")
    ap.add_argument("--tts-turns", type=int, help="número de turnos para a mesma voz narradora")
    ap.add_argument("--audio-cuts", default="", help="cortes de áudio explícitos em segundos, separados por vírgula")
    ap.add_argument("--report", type=Path, default=Path("qa_report.md"))
    ap.add_argument("--human-checklist", type=Path,
                    help="checklist preenchido; APROVADO só vale se todos os itens humanos estiverem marcados")
    ap.add_argument("--preset", choices=("legacy", "quick", "standard", "explainer"), default="legacy",
                    help="faixa editorial: quick 20–45s, standard 60–75s, explainer 75–90s; legacy 45–75s")
    ap.add_argument("--min-duration", type=float, default=None, help="sobrescreve o mínimo do preset")
    ap.add_argument("--max-duration", type=float, default=None, help="sobrescreve o máximo do preset")
    ap.add_argument("--max-gap", type=float, default=1.2)
    ap.add_argument("--max-wer", type=float, default=0.12)
    a = ap.parse_args()
    ranges = {
        "legacy": (45.0, 75.0),
        "quick": (20.0, 45.0),
        "standard": (60.0, 75.0),
        "explainer": (75.0, 90.0),
    }
    preset_min, preset_max = ranges[a.preset]
    min_duration = a.min_duration if a.min_duration is not None else preset_min
    max_duration = a.max_duration if a.max_duration is not None else preset_max
    if min_duration > max_duration:
        ap.error("--min-duration não pode ser maior que --max-duration")
    rows: list[tuple[str, str, str]] = []
    manual = [
        "Ouvir o WAV seco inteiro antes da música.",
        "Ouvir o MP4 inteiro uma vez em velocidade normal, sem pular trechos.",
        "Ouvir cada emenda com pelo menos 1,5 s de contexto dos dois lados.",
        "Conferir consoantes/finais, entonação, pausas, pronúncia e música/SFX mascarando fala.",
        "Inspecionar primeiro/último quadro, cada corte, entradas de dado e legibilidade em tela pequena.",
    ]

    human_ok = False
    if a.human_checklist and a.human_checklist.is_file():
        checklist = a.human_checklist.read_text(encoding="utf-8")
        required = checklist.split("## Estado", 1)[0]
        state = checklist.split("## Estado", 1)[1] if "## Estado" in checklist else ""
        human_ok = "- [ ]" not in required and "- [x] APROVADO PARA ENTREGA" in state

    if not a.video.is_file():
        add(rows, "FAIL", "arquivo", f"vídeo inexistente: {a.video}")
    if not a.beats.is_file():
        add(rows, "FAIL", "beats", f"beats inexistente: {a.beats}")
    if any(s == "FAIL" for s, _, _ in rows):
        return write_report(a.report, rows, manual, human_ok)

    info = probe(a.video)
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    duration = float(info.get("format", {}).get("duration", 0))
    add(rows, "PASS" if video else "FAIL", "vídeo stream", video.get("codec_name", "ok") if video else "ausente")
    add(rows, "PASS" if audio else "FAIL", "áudio stream", audio.get("codec_name", "ok") if audio else "ausente")
    if video:
        shape_ok = (video.get("width"), video.get("height")) == (1080, 1920)
        add(rows, "PASS" if shape_ok else "FAIL", "quadro", f"{video.get('width')}×{video.get('height')} (esperado 1080×1920)")
        try:
            n, d = (video.get("r_frame_rate") or "0/1").split("/")
            fps = float(n) / max(1e-9, float(d))
        except (ValueError, ZeroDivisionError):
            fps = 0.0
        add(rows, "PASS" if abs(fps - 30) < 0.02 else "FAIL", "fps", f"{fps:.3f}")
    add(rows, "PASS" if min_duration <= duration <= max_duration else "FAIL",
        "duração", f"{duration:.2f}s (preset {a.preset}: {min_duration:.0f}–{max_duration:.0f}s)")

    if audio:
        integrated, peak = loudness(a.video)
        if integrated is None or peak is None:
            add(rows, "WARN", "loudness", "ffmpeg não conseguiu medir LUFS/true peak")
        else:
            add(rows, "PASS" if -14.6 <= integrated <= -13.4 else "WARN",
                "loudness", f"{integrated:.1f} LUFS (alvo operacional −14 ±0,6)")
            add(rows, "PASS" if peak <= -1.0 else "FAIL",
                "true peak", f"{peak:.1f} dBTP (limite −1,0)")

    beats = json.loads(a.beats.read_text(encoding="utf-8"))
    starts = beats.get("starts", [])
    cuts = beats.get("cuts", [])
    words_by_block = beats.get("words", [])
    beat_dur = float(beats.get("dur", 0))
    add(rows, "PASS" if words_by_block and len(words_by_block) == len(starts) else "FAIL",
        "beat sheet", f"{len(starts)} blocos; tempos por palavra={'sim' if words_by_block else 'não'}")
    add(rows, "PASS" if abs(duration - beat_dur) <= 0.25 else "FAIL",
        "MP4 × beats", f"{duration:.2f}s vs {beat_dur:.2f}s")

    if starts and cuts and words_by_block:
        # The first block has no preceding visual cut; its opening image is frame 0.
        leads = [s - c for s, c in zip(starts[1:], cuts[1:])]
        bad = [x for x in leads if not 0.06 <= x <= 0.20]
        if leads:
            add(rows, "PASS" if not bad else "FAIL", "lead visual", f"min–max {min(leads):.2f}–{max(leads):.2f}s; alvo 0,06–0,20s")
        first = float(starts[0]) + (float(words_by_block[0][0].get("t", 0)) if words_by_block[0] else 0)
        add(rows, "PASS" if first <= 0.30 else "WARN", "primeira palavra", f"{first:.2f}s")
        long_gaps = []
        for i in range(min(len(starts) - 1, len(words_by_block) - 1)):
            end_word = max((float(w.get("e", 0)) for w in words_by_block[i]), default=0)
            gap = float(starts[i + 1]) - (float(starts[i]) + end_word)
            if gap > a.max_gap:
                long_gaps.append(f"B{i+1:02d} {gap:.2f}s")
        add(rows, "PASS" if not long_gaps else "WARN", "respiros", ", ".join(long_gaps) if long_gaps else "nenhuma pausa acima do limite")

        explicit_cuts = [float(x) for x in a.audio_cuts.split(",") if x.strip()]
        intervals = []
        for start, block_words in zip(starts, words_by_block):
            for w in block_words:
                intervals.append((float(start) + float(w.get("t", 0)),
                                  float(start) + float(w.get("e", w.get("t", 0))), str(w.get("w", "?"))))
        for cut in explicit_cuts:
            overlap = next((word for s, e, word in intervals if s - .03 <= cut <= e + .03), None)
            add(rows, "FAIL" if overlap else "WARN", f"corte áudio {cut:.2f}s",
                f"atravessa a palavra '{overlap}'" if overlap else "fora da palavra; escutar a junção")

    if a.tts_turns is None:
        add(rows, "WARN", "continuidade TTS", "informe --tts-turns; uma única voz deve ser uma tomada contínua salvo mudança intencional")
    elif a.tts_turns == 1:
        add(rows, "PASS", "continuidade TTS", "declarada uma tomada contínua")
    elif a.tts_turns > 1:
        add(rows, "FAIL", "continuidade TTS", f"{a.tts_turns} turnos para uma voz; requer emenda intencional e escuta individual")
    else:
        add(rows, "FAIL", "continuidade TTS", "número de turnos inválido")

    if a.script and a.stt and a.script.is_file() and a.stt.is_file():
        expected = tokens(a.script.read_text(encoding="utf-8"))
        heard_data = json.loads(a.stt.read_text(encoding="utf-8"))
        heard = get_heard_words(heard_data)
        rate, edits = wer(expected, heard)
        examples = "; ".join(f"{x} → {y}" for x, y in edits[:12]) or "nenhuma divergência textual aproximada"
        add(rows, "PASS" if rate <= a.max_wer else "WARN", "roteiro × ASR", f"WER {rate:.1%}; {examples}")
    elif a.script or a.stt:
        add(rows, "WARN", "roteiro × ASR", "forneça ambos --script e --stt")
    else:
        add(rows, "WARN", "roteiro × ASR", "não executado; compare a transcrição word-level com o texto narrado")

    if not human_ok:
        add(rows, "PENDING", "escuta/revisão humana", "complete e marque o checklist humano; automação não certifica entonação, dicção ou clareza visual")
    return write_report(a.report, rows, manual, human_ok)


def write_report(path: Path, rows: list[tuple[str, str, str]], manual: list[str], human_ok: bool = False) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    fails = sum(status == "FAIL" for status, _, _ in rows)
    warnings = sum(status == "WARN" for status, _, _ in rows)
    pending = any(status == "PENDING" for status, _, _ in rows)
    overall = "BLOCKED" if fails else ("NEEDS REVIEW" if warnings else ("PENDING HUMAN REVIEW" if pending or not human_ok else "APPROVED"))
    lines = ["# Relatório pré-entrega", "", f"**Status: {overall}**", "",
             "| Estado | Checagem | Resultado |", "|---|---|---|"]
    for status, name, detail in rows:
        lines.append(f"| {status} | {name} | {detail.replace('|', '/')} |")
    lines += ["", "## Checklist humano obrigatório"]
    lines += [f"- [ ] {item}" for item in manual]
    lines += ["", "Aprovação técnica não significa que a locução ou o vídeo estejam subjetivamente perfeitos."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if fails else (2 if warnings or pending or not human_ok else 0)


if __name__ == "__main__":
    raise SystemExit(main())

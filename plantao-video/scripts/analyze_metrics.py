#!/usr/bin/env python3
"""Calcula métricas normalizadas a partir de uma exportação CSV manual.

Não compara causalmente publicações de pautas ou janelas diferentes. Métricas
indisponíveis permanecem vazias; visualizações zero nunca geram divisão por zero.
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict


def number(row, field):
    value = row.get(field, "").strip()
    if not value:
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except ValueError:
        return None


def analyze(rows):
    normalized = []
    for row in rows:
        duration = number(row, "duration_seconds")
        views = number(row, "views")
        avg_watch = number(row, "avg_watch_seconds")
        group = {
            "platform": row.get("platform", "").strip(),
            "format_id": row.get("format_id", "").strip(),
            "hook_id": row.get("hook_id", "").strip(),
            "measurement_window": row.get("measurement_window", "").strip(),
            "views": views,
            "avg_watch_pct": (100 * avg_watch / duration) if duration and avg_watch is not None else None,
            "completion_pct": (100 * number(row, "completed_views") / views) if views and number(row, "completed_views") is not None else None,
            "shares_per_1k": (1000 * number(row, "shares") / views) if views and number(row, "shares") is not None else None,
            "saves_per_1k": (1000 * number(row, "saves") / views) if views and number(row, "saves") is not None else None,
            "comments_per_1k": (1000 * number(row, "comments") / views) if views and number(row, "comments") is not None else None,
            "followers_per_1k": (1000 * number(row, "followers_gained") / views) if views and number(row, "followers_gained") is not None else None,
        }
        normalized.append(group)

    buckets = defaultdict(list)
    for row in normalized:
        key = (row["platform"], row["measurement_window"], row["format_id"], row["hook_id"])
        buckets[key].append(row)
    summaries = []
    metrics = ("avg_watch_pct", "completion_pct", "shares_per_1k", "saves_per_1k", "comments_per_1k", "followers_per_1k")
    for key, items in sorted(buckets.items()):
        summary = {"platform": key[0], "measurement_window": key[1], "format_id": key[2], "hook_id": key[3], "posts": len(items)}
        for metric in metrics:
            vals = [r[metric] for r in items if r[metric] is not None]
            summary[metric] = round(sum(vals) / len(vals), 2) if vals else None
        summaries.append(summary)
    return normalized, summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV no formato de templates/publication_metrics.csv")
    parser.add_argument("--out", help="arquivo JSON opcional; sem ele, imprime resumo tabular")
    args = parser.parse_args()
    try:
        with open(args.input, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        print(f"Não foi possível abrir CSV: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("CSV sem registros.", file=sys.stderr)
        return 1
    normalized, summaries = analyze(rows)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"posts": normalized, "groups": summaries}, f, ensure_ascii=False, indent=2)
            f.write("\n")
    else:
        print("plataforma | janela | formato | gancho | n | watch% | conclusão% | shares/1k | saves/1k | follows/1k")
        for r in summaries:
            def fmt(k):
                return "—" if r[k] is None else f"{r[k]:.2f}"
            print(f"{r['platform']} | {r['measurement_window']} | {r['format_id']} | {r['hook_id']} | {r['posts']} | {fmt('avg_watch_pct')} | {fmt('completion_pct')} | {fmt('shares_per_1k')} | {fmt('saves_per_1k')} | {fmt('followers_per_1k')}")
    print(f"{len(normalized)} publicação(ões), {len(summaries)} grupo(s). Compare apenas janelas e conteúdos semelhantes; associação não prova causalidade.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

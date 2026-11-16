#!/usr/bin/env python3
"""Checagens mecânicas e consultivas do primeiro bloco; não avalia qualidade criativa."""
import argparse
import json
import sys


def inspect(lines, beats=None, max_chars=180, max_first_word=0.30):
    issues = []
    if not lines:
        return [("FAIL", "roteiro sem linhas/blocos")]
    first = lines[0].strip()
    if not first:
        issues.append(("FAIL", "primeiro bloco está vazio"))
    elif len(first) > max_chars:
        issues.append(("WARN", f"primeiro bloco tem {len(first)} caracteres; avaliar uma abertura mais concisa"))
    if beats is not None:
        try:
            words = beats["words"][0]
            first_word = words[0]
            timestamp = float(beats["starts"][0]) + float(first_word["t"])
            if timestamp > max_first_word:
                issues.append(("FAIL", f"primeira palavra começa em {timestamp:.2f}s (limite {max_first_word:.2f}s)"))
            else:
                issues.append(("PASS", f"primeira palavra começa em {timestamp:.2f}s"))
        except (KeyError, IndexError, TypeError, ValueError):
            issues.append(("WARN", "beats não contém timestamps de palavra utilizáveis para o primeiro bloco"))
    else:
        issues.append(("WARN", "sem beats: timing da primeira palavra não foi verificado"))
    issues.append(("REVIEW", "confirme manualmente que fala, texto e primeiro quadro entregam o mesmo fato e que o gancho é sustentado por fonte"))
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", required=True, help="roteiro.txt, uma linha por bloco")
    parser.add_argument("--beats", help="beats.json opcional, gerado com transcrição word-level")
    parser.add_argument("--max-chars", type=int, default=180)
    parser.add_argument("--max-first-word", type=float, default=0.30)
    args = parser.parse_args()
    try:
        with open(args.script, encoding="utf-8") as f:
            lines = f.read().splitlines()
        beats = None
        if args.beats:
            with open(args.beats, encoding="utf-8") as f:
                beats = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Não foi possível ler arquivo: {exc}", file=sys.stderr)
        return 2
    issues = inspect(lines, beats, args.max_chars, args.max_first_word)
    for level, detail in issues:
        print(f"[{level}] {detail}")
    return 1 if any(level == "FAIL" for level, _ in issues) else 0


if __name__ == "__main__":
    sys.exit(main())

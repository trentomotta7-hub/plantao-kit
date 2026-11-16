#!/usr/bin/env python3
"""Valida estrutura e rastreabilidade básica do briefing editorial.

O script não verifica se uma fonte é verdadeira ou se sustenta de fato uma alegação;
essa leitura continua sendo responsabilidade editorial.
"""
import argparse
import json
import sys
from urllib.parse import urlparse

PRESETS = {
    "quick": (20, 45),
    "standard": (60, 75),
    "explainer": (75, 90),
}
ALLOWED_CLASSIFICATIONS = {"confirmed", "attributed", "uncertain"}


def validate(data):
    errors = []
    warnings = []
    if not data.get("topic", "").strip():
        errors.append("topic precisa estar preenchido")
    preset = data.get("duration_preset")
    if preset not in PRESETS:
        errors.append(f"duration_preset deve ser um de: {', '.join(PRESETS)}")
    else:
        target = data.get("target_duration_seconds")
        lo, hi = PRESETS[preset]
        if not isinstance(target, (int, float)) or not lo <= target <= hi:
            errors.append(f"target_duration_seconds deve ficar entre {lo} e {hi} para {preset}")

    hooks = data.get("hooks") or []
    hook_ids = {h.get("id") for h in hooks}
    if len(hooks) < 3:
        errors.append("registre ao menos três ganchos candidatos")
    for i, hook in enumerate(hooks, 1):
        for field in ("id", "spoken", "on_screen", "first_frame", "claim_id"):
            if not str(hook.get(field, "")).strip():
                errors.append(f"gancho {i}: campo {field} vazio")
        spoken = hook.get("spoken", "").strip()
        if len(spoken) > 150:
            warnings.append(f"gancho {i}: fala tem {len(spoken)} caracteres; revisar concisão")
    selected = data.get("selected_hook_id")
    if selected not in hook_ids:
        errors.append("selected_hook_id não corresponde a um gancho registrado")

    sources = data.get("source_records") or []
    source_ids = {s.get("id") for s in sources}
    if not sources:
        errors.append("registre ao menos uma fonte")
    for i, source in enumerate(sources, 1):
        for field in ("id", "publisher", "title", "published_at", "url"):
            if not str(source.get(field, "")).strip():
                errors.append(f"fonte {i}: campo {field} vazio")
        parsed = urlparse(source.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"fonte {i}: URL precisa ser HTTPS válida")

    claims = data.get("claim_ledger") or []
    claim_ids = {c.get("id") for c in claims}
    if not claims:
        errors.append("registre ao menos uma alegação/fato do roteiro")
    for i, claim in enumerate(claims, 1):
        if not str(claim.get("text", "")).strip():
            errors.append(f"alegação {i}: texto vazio")
        classification = claim.get("classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"alegação {i}: classificação deve ser {', '.join(sorted(ALLOWED_CLASSIFICATIONS))}")
        refs = claim.get("source_ids") or []
        if classification == "confirmed" and not refs:
            errors.append(f"alegação {i}: fato marcado confirmed exige fonte")
        if classification in {"attributed", "uncertain"} and not str(claim.get("attribution", "")).strip():
            errors.append(f"alegação {i}: classificação {classification} exige atribuição explícita")
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"alegação {i}: fonte referenciada inexistente: {ref}")

    for hook in hooks:
        if hook.get("claim_id") and hook["claim_id"] not in claim_ids:
            errors.append(f"gancho {hook.get('id')}: claim_id não existe")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("briefing", help="arquivo JSON de briefing")
    args = parser.parse_args()
    try:
        with open(args.briefing, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERRO: não foi possível ler JSON: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    for warning in warnings:
        print(f"AVISO: {warning}")
    for error in errors:
        print(f"FALHA: {error}")
    if errors:
        print(f"Briefing reprovado: {len(errors)} falha(s), {len(warnings)} aviso(s)")
        return 1
    print(f"Briefing estruturalmente completo: 0 falhas, {len(warnings)} aviso(s). Fontes e alegações ainda exigem leitura humana.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

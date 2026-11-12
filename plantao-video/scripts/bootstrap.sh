#!/usr/bin/env bash
# Confere (e baixa, se faltar) os assets do kit. Rode uma vez por ambiente.
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
A="$S/assets"

need_py() {
  python3 - <<'EOF'
import importlib, sys
falta = [m for m in ("PIL", "numpy") if not importlib.util.find_spec(m)]
print(" ".join(falta))
EOF
}
MISSING=$(need_py)
if [ -n "$MISSING" ]; then
  echo ">> instalando python: $MISSING"
  pip3 install -q pillow numpy
fi

mkdir -p "$A/fonts" "$A/emoji" "$A/geo" "$A/img"

# Fontes (Google Fonts, OFL)
for f in Playfair.ttf Oswald.ttf Anton.ttf BebasNeue.ttf PermanentMarker.ttf \
         Montserrat.ttf Inter.ttf ArchivoBlack.ttf; do
  [ -s "$A/fonts/$f" ] || echo "FALTA fonte: $f"
done

# Twemoji (CC-BY 4.0) — códigos usados nos episódios
EMO="1f4a5 1f6a8 1f440 1f4b0 1f525 1f3af 1f631 1f914 1f921 1f447 1f480 1f37f 1f4a3 1f4b8 1f4c4 1f4c9 1f4ca 1f50d 1f5fa"
for c in $EMO; do
  if [ ! -s "$A/emoji/$c.png" ]; then
    echo ">> baixando emoji $c"
    curl -fsSL "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/$c.png" \
      -o "$A/emoji/$c.png" || echo "falhou $c"
  fi
done

# Malha dos estados (IBGE, domínio público)
if [ ! -s "$A/geo/br_states.geojson" ]; then
  echo "FALTA assets/geo/br_states.geojson (malha IBGE com properties.sigla)"
fi

echo "---"
echo "fontes:  $(ls "$A/fonts" 2>/dev/null | wc -l)"
echo "emojis:  $(ls "$A/emoji" 2>/dev/null | wc -l)"
echo "geo:     $(du -h "$A/geo/br_states.geojson" 2>/dev/null | cut -f1)"
echo "fotos:   $(ls "$A/img" 2>/dev/null | wc -l)"
python3 -c "import PIL, numpy; print('pillow', PIL.__version__, '· numpy', numpy.__version__)"
ffmpeg -version 2>/dev/null | head -1

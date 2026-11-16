#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p work/frames work/frames_out out
rm -f work/frames_out/f_*.jpg

export PLANTAO_WORK="$HERE/work"
export PLANTAO_OUT="$HERE/work/frames_out"
export PLANTAO_BEATS="$HERE/beats.json"
export PLANTAO_EDICAO=3
export PLANTAO_NOME='MAPA SUJO'
export PLANTAO_DATA='DOMINGO, 15 DE NOVEMBRO DE 2026'
export PLANTAO_TICKER='CASO BANCO MASTER  •  MENSAGEM ATRIBUÍDA  •  RELATÓRIO EM REVISÃO  •  PARECER DA PGR NÃO É DECISÃO  •  '

python3 -u serie_ritmo.py conteudo_dinamico.py 2>&1 | tee out/render_v32.log

count="$(find work/frames_out -maxdepth 1 -type f -name 'f_*.jpg' | wc -l)"
expected=2379
if [[ "$count" -ne "$expected" ]]; then
  echo "Esperados $expected quadros; encontrados $count." >&2
  exit 1
fi

ffmpeg -y -hide_banner -loglevel warning \
  -framerate 30 -i work/frames_out/f_%05d.jpg -i mix_ln.wav \
  -map 0:v:0 -map 1:a:0 -vf 'hqdn3d=1.5:1.5:5:5' -c:v libx264 -preset slow -crf 25 \
  -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart \
  out/ed003_v3_cortes_visuais_preview.mp4

ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels \
  -of json out/ed003_v3_cortes_visuais_preview.mp4

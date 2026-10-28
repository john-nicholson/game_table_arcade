#!/usr/bin/env bash
set -euo pipefail
app="$HOME/.local/share/game-table/app"
if [[ -z ${DISPLAY:-} ]]; then
    echo 'The arcade session requires X11. Select it from the login screen.' >&2
    exit 1
fi
python3 "$app/scripts/arcade.py" display
xset s off
xset s noblank
# Some X servers do not expose DPMS.
xset -dpms || true
xsetroot -solid black
exec i3 -c "$app/config/i3.conf"

#!/usr/bin/env bash
set -euo pipefail
ROOT=$(dirname "$(realpath "$0")")
if [[ $EUID -eq 0 ]]; then
    echo 'Run as the arcade user, not root; sudo is used for system changes.' >&2
    exit 1
fi
if [[ ! -r /etc/os-release ]]; then
    echo 'This installer requires Ubuntu Desktop.' >&2
    exit 1
fi
source /etc/os-release
if [[ $ID != ubuntu || $(dpkg --print-architecture) != amd64 ]]; then
    echo 'Initial supported target: Ubuntu Desktop amd64 (24.04 LTS recommended).' >&2
    exit 1
fi
sudo apt-get update
packages=(retroarch retroarch-assets libretro-nestopia i3-wm xterm
    x11-xserver-utils x11-utils xinit xserver-xorg mesa-utils joystick jstest-gtk
    evtest alsa-utils pulseaudio-utils python3 ca-certificates)
# Fail before configuring the account if Universe/package sources are incomplete.
if ! apt-get --simulate install --no-install-recommends "${packages[@]}"; then
    echo 'Package preflight failed. Check Ubuntu sources; RetroArch needs Universe.' >&2
    echo 'To enable it: sudo add-apt-repository universe; then rerun this installer.' >&2
    exit 1
fi
sudo apt-get install -y --no-install-recommends "${packages[@]}"

app="$HOME/.local/share/game-table/app"
mkdir -p "$app/scripts" "$app/config" "$HOME/.local/bin"
# Copy the runtime so a moved checkout does not break the login session.
python3 "$ROOT/scripts/arcade.py" deploy "$ROOT" "$app"
python3 "$app/scripts/arcade.py" configure
if ! cmp -s "$ROOT/scripts/game-table-session" /usr/local/bin/game-table-session; then
    sudo install --backup=numbered -m 755 "$ROOT/scripts/game-table-session" /usr/local/bin/game-table-session
fi
if ! cmp -s "$ROOT/config/game-table.desktop" /usr/share/xsessions/game-table.desktop; then
    sudo install --backup=numbered -m 644 "$ROOT/config/game-table.desktop" /usr/share/xsessions/game-table.desktop
fi
echo 'Installed. Next: ~/.local/bin/game-table download'
echo 'Then run game-table doctor and game-table launch, and select Coffee Table Arcade at login.'

# Coffee-table arcade

Repeatable Ubuntu setup for an Intel i3 coffee-table arcade with two wired arcade
controllers and a screen behind mirrored perspex. Inspired by `../p11z-config`:
small scripts, versioned defaults, and backups when managed configuration changes.

## First deployment

Initial target: **Ubuntu Desktop 24.04 LTS, amd64**, with working graphics and sound.
Other Ubuntu releases are checked for package availability but need on-machine validation.
The table currently runs **24.04.3 LTS**, with a landscape screen and side-by-side
panels offering eight action buttons plus Start per player. The proposed allocation
is six gameplay buttons, Coin/Select, and an admin modifier, plus Start.
Run these commands in this checkout **as the user who will play games**:

```bash
bash install.sh
game-table download
game-table doctor
game-table launch
```

Open a fresh terminal if `~/.local/bin` was not already on your PATH; alternatively
use `~/.local/bin/game-table`. The installer uses sudo for Ubuntu packages and a
login-screen session entry. Downloads and game saves belong to the playing user.
The download step needs internet; installed games work offline.

Log out, select **Coffee Table Arcade** at the login screen, and log in. This starts
a dedicated i3/X11 session with RetroArch fullscreen. **F1** opens the game menu;
**Super+Enter** opens a maintenance terminal; **Super+Shift+E** logs out. Exiting
RetroArch returns to i3; **Super+A** starts it again. Select **Free Homebrew** in
RetroArch's playlists to play the downloaded games.

For boot-to-arcade, first verify that session works, then enable automatic login
for this user in Ubuntu **Settings → System → Users** (24.04). Reboot and verify
the login manager remembers the arcade session. Full-disk encryption still needs
an unlock at boot. See [operations](docs/operations.md) for recovery and updates.

## What this installs

- Ubuntu's RetroArch and Nestopia NES core; no source builds or third-party PPA.
- RetroArch's Ozone controller-friendly menu, fullscreen, aspect-ratio preservation,
  two controller ports, save directories, and a generated homebrew playlist.
- A separate i3 session with screen blanking/DPMS disabled while that session runs.
- **Super Tilt Bro (USA)**, an older, small two-player NES homebrew build, and
  **Nova the Squirrel**, a single-player platform/puzzle game, via `game-table download`.
  Each file is version-pinned and SHA-256 checked. See [game sources](docs/games.md).
- `jstest-gtk`, `evtest`, `mesa-utils`, and audio/display utilities for commissioning.

## Local settings

Edit `~/.config/game-table/settings.json`, then run:

```bash
game-table configure
```

Defaults come from [`config/settings.json`](config/settings.json). Set
`display_output` (for example `HDMI-1`) and `display_rotation` (`normal`, `left`,
`right`, `inverted`) for your screen. Run `xrandr` inside the arcade session to
identify its connector. Rotation is applied at the next arcade login.

Controller mappings live in `~/.config/game-table/retroarch.cfg` and
`~/.config/game-table/autoconfig/`. Map the actual hardware in RetroArch and use
**Main Menu → Configuration File → Save Current Configuration**. Managed settings
are reapplied by `configure`; other RetroArch settings are preserved. Adjust the
managed defaults through settings.json. Differing files are backed up under
`~/.local/state/game-table/backups/`.

## Plan and commissioning

- [Build plan and decisions](docs/plan.md)
- [Two-player controls and table display](docs/hardware.md)
- [Game sources, licences, and adding games](docs/games.md)
- [Updates, diagnostics, backup, and removal](docs/operations.md)

Local checks (no sudo, package installation, or graphical session required):

```bash
python3 -m unittest discover -s tests -v
for script in install.sh scripts/session.sh scripts/game-table scripts/game-table-session; do bash -n "$script"; done
```

To also exercise the real catalogue downloads in a temporary directory:
`GAME_TABLE_NETWORK_TEST=1 python3 -m unittest discover -s tests -v`.

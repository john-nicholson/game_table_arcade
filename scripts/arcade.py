#!/usr/bin/env python3
"""Configuration, curated content and diagnostics; standard-library only."""

import argparse
from datetime import datetime, timezone
import glob
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parent.parent
HOME = Path.home()
CONFIG = HOME / ".config/game-table"
STATE = HOME / ".local/state/game-table"
MAX_ROM_BYTES = 16 * 1024 * 1024


def write_managed(path, content):
    """Back up differing files and replace atomically on the same filesystem."""
    path = Path(path)
    encoded = content.encode()
    if path.exists() and path.read_bytes() == encoded:
        return
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        relative = (path.relative_to(HOME) if path.is_relative_to(HOME)
                    else Path("external") / path.relative_to(path.anchor))
        backup = STATE / "backups" / stamp / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def settings():
    defaults = json.loads((APP / "config/settings.json").read_text())
    path = CONFIG / "settings.json"
    if path.exists():
        defaults.update(json.loads(path.read_text()))
    rotation = defaults["display_rotation"]
    if rotation not in ("normal", "left", "right", "inverted"):
        raise ValueError("display_rotation must be normal, left, right or inverted")
    if not isinstance(defaults["display_output"], str):
        raise ValueError("display_output must be a connector name or an empty string")
    if defaults["menu_driver"] not in ("ozone", "rgui", "xmb"):
        raise ValueError("menu_driver must be ozone, rgui or xmb")
    for key in ("player1_index", "player2_index"):
        if type(defaults[key]) is not int or not 0 <= defaults[key] <= 15:
            raise ValueError(f"{key} must be an integer from 0 to 15")
    if defaults["player1_index"] == defaults["player2_index"]:
        raise ValueError("The two players must use different controller indexes")
    data = Path(defaults["data_dir"]).expanduser()
    if not data.is_absolute() or any(c in str(data) for c in ('"', '\n', '\r')):
        raise ValueError("data_dir must be an absolute path without quotes or newlines")
    defaults["data_dir"] = str(data)
    return defaults


def catalogue():
    games = json.loads((APP / "config/games.json").read_text())
    filenames = set()
    for game in games:
        name = game["filename"]
        if Path(name).name != name or not name.endswith(".nes") or name in filenames:
            raise ValueError(f"Invalid/duplicate ROM filename: {name}")
        filenames.add(name)
        if not re.fullmatch(r"[0-9a-f]{64}", game["sha256"]):
            raise ValueError(f"Invalid SHA-256: {name}")
        if urllib.parse.urlsplit(game["url"]).scheme != "https":
            raise ValueError(f"Download must use HTTPS: {name}")
    return games


def find_core():
    candidates = sorted(glob.glob("/usr/lib/*/libretro/nestopia_libretro.so"))
    candidates += ["/usr/lib/libretro/nestopia_libretro.so"]
    return next((Path(p) for p in candidates if Path(p).is_file()), None)


def merge_config(existing, values):
    """Keep local settings/bindings; replace all occurrences of managed keys."""
    lines = []
    for line in existing.splitlines():
        match = re.match(r"^\s*([a-zA-Z0-9_]+)\s*=", line)
        if not match or match[1] not in values:
            lines.append(line)
    # Stable rendering: do not accumulate blank lines on repeated runs.
    while lines and not lines[-1].strip():
        lines.pop()
    for key, value in values.items():
        lines.append(f'{key} = "{value}"')
    return "\n".join(lines) + "\n"


def configure():
    opts = settings()
    core = find_core()
    if core is None:
        raise ValueError("Nestopia core missing; run bash install.sh on Ubuntu first")
    if not (CONFIG / "settings.json").exists():
        write_managed(CONFIG / "settings.json", (APP / "config/settings.json").read_text())
    data = Path(opts["data_dir"])
    for directory in ("roms/nes", "bios", "saves", "states", "screenshots", "playlists"):
        (data / directory).mkdir(parents=True, exist_ok=True)
    for directory in ("autoconfig", "remaps", "core-configs"):
        (CONFIG / directory).mkdir(parents=True, exist_ok=True)
    values = {
        "menu_driver": opts["menu_driver"],
        "assets_directory": "/usr/share/libretro/assets",
        "libretro_directory": core.parent,
        "libretro_info_path": "/usr/share/libretro/info",
        "audio_driver": "pulse",
        "video_driver": "gl",
        "video_fullscreen": "true",
        "video_windowed_fullscreen": "true",
        "video_vsync": "true",
        "video_smooth": "false",
        "video_force_aspect": "true",
        "video_shader_enable": "false",
        "video_scale_integer": "false",
        "aspect_ratio_index": "22",  # Core-provided aspect ratio in RetroArch.
        "rewind_enable": "false",
        "run_ahead_enabled": "false",
        "input_max_users": "2",
        "input_autodetect_enable": "true",
        "input_player1_joypad_index": opts["player1_index"],
        "input_player2_joypad_index": opts["player2_index"],
        "input_menu_toggle": "f1",
        "menu_pause_libretro": "true",
        "rgui_show_start_screen": "false",
        "menu_show_core_updater": "false",
        "menu_mouse_enable": "false",
        "config_save_on_exit": "false",
        "savestate_auto_save": "false",
        "autosave_interval": "10",
        "system_directory": data / "bios",
        "savefile_directory": data / "saves",
        "savestate_directory": data / "states",
        "screenshot_directory": data / "screenshots",
        "playlist_directory": data / "playlists",
        "rgui_browser_directory": data / "roms",
        "joypad_autoconfig_dir": CONFIG / "autoconfig",
        "input_remapping_directory": CONFIG / "remaps",
        "rgui_config_directory": CONFIG / "core-configs",
        "core_options_path": CONFIG / "retroarch-core-options.cfg",
    }
    config = CONFIG / "retroarch.cfg"
    # Seed a controller-only route back to the menu; preserve later custom hotkeys.
    existing = (config.read_text() if config.exists()
                else 'input_menu_toggle_gamepad_combo = "4"\n')
    write_managed(config, merge_config(existing, values))
    titles = {g["filename"]: g["title"] for g in catalogue()}
    items = [
        {"path": str(rom.resolve()), "label": titles.get(rom.name, rom.stem),
         "core_path": str(core), "core_name": "Nestopia",
         "crc32": "00000000|crc", "db_name": ""}
        for rom in sorted((data / "roms/nes").glob("*.nes")) if rom.is_file()
    ]
    playlist = {"version": "1.5", "default_core_path": str(core),
                "default_core_name": "Nestopia", "items": items}
    write_managed(data / "playlists/Free Homebrew.lpl", json.dumps(playlist, indent=2) + "\n")
    print(f"Configured {config}; playlist contains {len(items)} games.")


def digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def download_game(game, directory):
    target = directory / game["filename"]
    if target.exists():
        if digest(target) != game["sha256"]:
            raise ValueError(f"Existing ROM differs; move it aside before retrying: {target}")
        print(f"Verified existing {game['title']}")
        return
    temporary = None
    try:
        request = urllib.request.Request(game["url"], headers={"User-Agent": "game-table-arcade/1"})
        with urllib.request.urlopen(request, timeout=60) as response:
            if urllib.parse.urlsplit(response.url).scheme != "https":
                raise ValueError("Download redirected away from HTTPS")
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
                temporary = Path(stream.name)
                total = 0
                while block := response.read(65536):
                    total += len(block)
                    if total > MAX_ROM_BYTES:
                        raise ValueError(f"Download exceeds size limit: {game['title']}")
                    stream.write(block)
        if digest(temporary) != game["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {game['title']}; nothing installed")
        with temporary.open("rb") as stream:
            if stream.read(4) != b"NES\x1a":
                raise ValueError(f"Not an iNES ROM: {game['title']}")
        temporary.replace(target)
        print(f"Downloaded {game['title']}")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def download():
    # Validate prerequisites before making network requests.
    configure()
    data = Path(settings()["data_dir"])
    games = catalogue()
    for game in games:
        download_game(game, data / "roms/nes")
    write_managed(data / "SOURCES.json", json.dumps(games, indent=2) + "\n")
    configure()


def display():
    opts = settings()
    if not opts["display_output"]:
        return
    result = subprocess.run(
        ["xrandr", "--output", opts["display_output"], "--rotate", opts["display_rotation"]],
        check=False,
    )
    if result.returncode:
        print("Screen rotation failed; check display_output using xrandr.", file=sys.stderr)


def doctor():
    good = True
    print(Path("/etc/os-release").read_text())
    for command in ("retroarch", "i3", "xrandr", "xterm"):
        found = shutil.which(command)
        print(f"{command}: {found or 'MISSING'}")
        good &= found is not None
    core = find_core()
    print(f"NES core: {core or 'MISSING'}")
    good &= core is not None
    for path in (CONFIG / "retroarch.cfg", Path("/usr/share/xsessions/game-table.desktop")):
        print(f"{path}: {'OK' if path.is_file() else 'MISSING'}")
        good &= path.is_file()
    data = Path(settings()["data_dir"])
    for game in catalogue():
        path = data / "roms/nes" / game["filename"]
        valid = path.is_file() and digest(path) == game["sha256"]
        print(f"{game['title']}: {'OK' if valid else 'MISSING OR CHECKSUM MISMATCH'}")
        good &= valid
    print(f"Session: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}; "
          f"DISPLAY={os.environ.get('DISPLAY', '(none)')}")
    print("Input device links:")
    links = sorted(glob.glob("/dev/input/by-id/*") + glob.glob("/dev/input/by-path/*"))
    print("\n".join(links) if links else "No device links found; inspect controllers on the table.")
    print("Check both pads in jstest-gtk and GPU with glxinfo -B inside the graphical session.")
    return 0 if good else 1


def deploy(source, destination):
    for folder in ("config", "scripts"):
        for path in (Path(source) / folder).iterdir():
            if path.is_file():
                write_managed(Path(destination) / folder / path.name, path.read_text())
    wrapper = HOME / ".local/bin/game-table"
    write_managed(wrapper, (Path(source) / "scripts/game-table").read_text())
    wrapper.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("configure", "download", "doctor", "display", "deploy"))
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    if args.command == "deploy":
        if len(args.paths) != 2:
            parser.error("deploy requires source and destination")
        deploy(*args.paths)
        return 0
    if args.paths:
        parser.error("unexpected arguments")
    return {"configure": configure, "download": download, "doctor": doctor, "display": display}[args.command]()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"game-table: {error}", file=sys.stderr)
        sys.exit(1)

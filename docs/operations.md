# Operations

## Layout

| Path | Contents |
| --- | --- |
| `~/.local/bin/game-table` | CLI wrapper |
| `~/.local/share/game-table/app/` | Installed scripts, templates, catalogue |
| `~/.config/game-table/` | Settings, RetroArch config, controller profiles/remaps |
| `~/Games/game-table/` | ROMs, BIOS directory, saves, states, screenshots, playlists |
| `~/.local/state/game-table/` | Backups and launcher log |
| `/usr/local/bin/game-table-session` | Login session entry point |
| `/usr/share/xsessions/game-table.desktop` | Login-screen session definition |

Paths use the standard HOME layout above. Keep the arcade user's home stable.
The data path is configurable using the absolute `data_dir` setting (`~` expands).

## Update

Pull this checkout using your usual Git workflow, then run `bash install.sh`.
It reapplies managed defaults, backs up differing files, and preserves settings.json,
input bindings, saves, ROMs, and controller profiles. Run `game-table download`
for new curated games. Ubuntu packages update using normal apt maintenance;
schedule updates when the table is not being played. Avoid changing cores during
a play session; save states can depend on core versions.

## Diagnostics and recovery

Run `game-table doctor` for the OS, available commands, installed NES core, ROM
checksums, input devices, and session status. The command returns nonzero for
missing prerequisites or a bad/missing curated ROM. Run it after downloading.
`~/.local/state/game-table/retroarch.log` accumulates launcher output.
Run `glxinfo -B` inside the session to check rendering isn't software-only.

If startup fails, use Super+Enter for a terminal or Super+Shift+E to log out.
Select Ubuntu at the login screen for desktop maintenance. Ctrl+Alt+F3 provides
a text login if the graphical session is unusable. Fix settings and run
`~/.local/bin/game-table configure`, then log back in. If an output name is wrong,
screen rotation is skipped with a message in the session's log output.

No SSH server is enabled by this installer. If remote maintenance is wanted,
install `openssh-server`, configure your existing key-based access, and verify
connectivity before sealing the table. Keep a small maintenance keyboard handy.

## Backup

While RetroArch is closed, back up `~/.config/game-table/` and
`~/Games/game-table/` (or the configured data directory) to another machine or
disk. This includes mappings, native saves, states, ROMs and source records.
Installer configuration backups are not a backup of game progress. Restore these
directories to the arcade user after running the installer on a replacement OS,
then run `game-table configure` to regenerate machine-specific playlist paths.

Differing system session files get numbered backups alongside the original file
when the installer updates them; differing managed user files go into the state
directory's timestamped backups.

## Disable/remove

Disable automatic login in Ubuntu's Users settings and choose the Ubuntu session.
To remove the login entry:

```bash
sudo rm /usr/share/xsessions/game-table.desktop /usr/local/bin/game-table-session
```

User configuration, game data and backups can be archived and removed separately.
Packages can be removed with apt if no other application needs them. Installing
this setup does not replace your normal i3 config or Ubuntu desktop session.

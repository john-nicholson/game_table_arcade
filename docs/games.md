# Free game catalogue

`game-table download` fetches only entries in `config/games.json`. Downloads use
HTTPS, a size limit, a pinned URL and SHA-256, temporary files, and atomic rename.
A matching existing file is reused; a differing existing ROM is left intact and
reported as an error. No archive extraction or executable download is involved.

| Game | Players | Source and permission |
| --- | --- | --- |
| Super Tilt Bro (USA), legacy build | 2 simultaneous | [Author/source](https://github.com/sgadrat/super-tilt-bro), WTFPL; pinned binary from [Libretro content](https://github.com/libretro/libretro-content). The small USA NROM build is deliberately used for baseline Nestopia compatibility; it is not the current network-capable release. |
| Nova the Squirrel v1.0.6a | 1 | [Author release](https://github.com/NovaSquirrel/NovaTheSquirrel/releases/tag/v1.0.6a); code GPL-3.0-or-later, assets CC-BY-NC-SA-4.0. [Author's licence notes](https://github.com/NovaSquirrel/NovaTheSquirrel/tree/v1.0.6a#license). |

The manifest records attribution, licence, source link, and download origin; a
copy is stored alongside installed content as `SOURCES.json`. Keep these records
with backups. Nova's assets are non-commercial: these permissions cover the
intended personal table; review the author's terms before selling/distributing
a table or a game bundle. ROM files themselves are not committed here.

## Add your own NES games

Copy authorised `.nes` files to `~/Games/game-table/roms/nes/`, then run
`game-table configure`. The playlist includes local `.nes` files without relying
on a commercial-ROM database scan. Names come from the manifest where known and
otherwise from the filename. Nestopia needs no external NES BIOS.

To add a free download to the curated catalogue, record an author/release URL,
licence/permission, player count, a pinned direct HTTPS `.nes` URL, and SHA-256 in
`config/games.json`, then rerun `bash install.sh` and `game-table download`.
Review the actual downloaded bytes and test the game with the packaged core.

## Later arcade content

[MAME's authorised ROM downloads](https://www.mamedev.org/roms/) include Gridlee
and other releases with individual terms. [itch.io](https://itch.io/games/free/tag-nes)
also has free homebrew; free-to-download and permission-to-redistribute differ.
Prefer author pages and preserve accompanying terms. MAME/FBNeo installation and
playlists are a later plan phase; `.zip` arcade ROM sets are not playable with
the initial NES core. BIOS-dependent systems need separately sourced authorised
BIOS files and a compatible core. “Abandonware” is not a licence.

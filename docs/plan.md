# Deployment plan

## Confirmed table specification

- Ubuntu **24.04.3 LTS** on the existing Intel i3 machine.
- Two arcade panels, each with **eight action buttons plus a player/Start button**.
  Encoder models and whether they expose gamepad or keyboard events remain to be identified.
- **Landscape screen, side-by-side players** for the current tabletop.
- Catalogue goals: fighters, cooperative beat ’em ups, shooters, and classic arcade
  games. Opposite-side cocktail play is a future tabletop revision.

Initial control allocation: six gameplay buttons, one Coin/Select button, one
admin/menu modifier, and the separate Start button per player. See the
[control layout](hardware.md#proposed-nine-button-panel-allocation).

## 1. Establish a playable baseline — implemented in this repository

Use the existing Ubuntu installation, distro packages, RetroArch + Nestopia, and
a dedicated i3/X11 arcade session. RetroArch is both the emulator host and initial
controller-driven launcher. This keeps the first deployment small and maintainable.
The i3 is a CPU, not necessarily the desktop environment: the arcade session works
alongside Ubuntu's normal desktop and uses its existing login manager.

Install configuration reproducibly, preserve local input bindings, keep game data
separate from the checkout, and download a tiny, known homebrew library. Nothing
needs to be stored in this repository besides scripts, configuration, and docs.

## 2. Commission the hardware — next, on the machine

Record exact CPU/GPU, RAM, monitor resolution/refresh, and USB encoder models and
IDs. Test both controllers together, sound, and graphics acceleration. Commission
the confirmed landscape, side-by-side arrangement first. Capture controller
autoconfiguration after mapping the physical buttons.

Acceptance: cold boot, navigate using player one's controls, start a two-player
game, independently control both players, open the menu, close content, launch
another game, and shut down cleanly. Repeat after unplug/replug and five reboots
to check player assignment. Play for an hour under the actual tabletop and check
temperature, visibility, audio, and missed/diagonal inputs.

## 3. Make it a table appliance

Enable automatic login after the dedicated session works. Tune screen brightness
and the physical black surround behind the perspex. Establish a reachable power
button, saved-game backup, and maintenance access. Verify offline boot and game
launch, shutdown, wake/power behaviour, and recovery to the normal Ubuntu desktop.
Automatic login is configured through Ubuntu's Users settings and tested on the
target login manager; this first version does not replace the display manager.

## 4. Expand the arcade catalogue

Next implementation milestone: add Ubuntu's standalone MAME and a controller-driven
frontend that can launch both MAME and RetroArch. Evaluate ES-DE for that shared
menu before expanding the library; the current RetroArch playlist only launches
NES games. Start with authorised releases such as MAME's free Gridlee/Robby Roto
downloads to validate the arcade launch/return flow. Their ROM
files must match the chosen emulator/core's expected sets; a random archive is
not a compatible catalogue. Add a core, its version/BIOS requirements, controls,
and playlist support together. NES is the first working system, not the full
arcade roadmap. Commercial homebrew purchased from its author is another option.

Build a small, tested favourites collection across these categories:

| Category | Controls and commissioning focus |
| --- | --- |
| Fighters | Six-button per-game layouts; simultaneous inputs and diagonals |
| Co-op beat ’em ups | Two independent players; Start and credit insertion for each |
| Shooters | Joystick-only movement plus fire/bomb; landscape titles first, portrait games pillarboxed |
| Classic arcade | Per-game button legends, credit/start behaviour, and aspect ratios |

The free starter downloads validate deployment; they do not supply a complete
commercial arcade library. Record the source/permission and matching emulator set
requirements for every additional game. Prioritise games playable with sticks and
buttons; trackball, spinner, light-gun, and twin-stick games need additional controls
or a deliberately tested alternative mapping.

## 5. Cabinet presentation

Evaluate ES-DE as a richer frontend once launching, inputs, and exit-to-menu are
reliable. Add a curated favourites list, large artwork, short descriptions and
button legends. Test readability through the actual perspex before spending time
on video-heavy themes. Add a guest/kiosk configuration after maintenance controls
and the final game list are settled.

## Decisions still needed

- i3 generation/GPU, RAM, and screen resolution/refresh rate.
- Encoder/controller models and gamepad vs keyboard mode.
- Individual favourite titles within the confirmed genres.
- Audio output and physical power/shutdown button arrangement.

Do not assume an i3 can run all later 3D systems: measure individual cores and
games. Initial graphics use OpenGL with vsync; shaders, run-ahead, and rewind are
left off until latency and performance have been measured.

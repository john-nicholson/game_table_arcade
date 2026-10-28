# Controls and display commissioning

Current build: Ubuntu **24.04.3 LTS**, landscape screen, and two players seated
side by side. Each panel has eight action buttons and a separate player/Start
button. Keep the display rotation at `normal` for this arrangement unless the
physical screen is mounted upside down.

## Proposed nine-button panel allocation

These are physical roles, not encoder button numbers. Confirm the actual USB
events before creating a controller profile.

| Physical control | Role |
| --- | --- |
| Action buttons 1–6 | Six gameplay buttons; map their arrangement per game/core |
| Action button 7 | Select for console games / Insert Coin for arcade games |
| Action button 8 | Admin/hotkey modifier; use the P1 panel for frontend hotkeys |
| Separate player button | Start for that player |

For a conventional two-row six-button cluster, use a consistent RetroPad mapping
on both panels, then set the fighter's punch/kick arrangement with a game remap.
Physical labels and a photo of the panel will help settle the exact layout.
Some games use more than six action buttons; these need a specific remap rather
than assuming the admin and coin buttons are spare gameplay inputs.

Use **P1 admin + Start** for the RetroArch menu after binding and testing it.
Disable the initial Select+Start menu combo when that dedicated binding works.
For the later MAME setup, map Coin and Start for both players separately and
provide an equally deliberate return-to-frontend binding. RetroArch's hotkeys
do not automatically configure standalone MAME.

## Two arcade panels

Prefer each USB encoder presenting as a separate gamepad. Label USB cables P1/P2,
keep each on the same port, and record devices using `game-table doctor` and
`jstest-gtk`. Use `evtest` to inspect raw events if an encoder behaves strangely.
Graphical sessions normally grant access to gamepads; do not run RetroArch as root
or add the user to the broad `input` group just to make a controller work.

1. Start `game-table launch` with a keyboard attached for commissioning.
2. In **Settings → Input → RetroPad Binds → Port 1 Controls** (wording varies by
   RetroArch version), select the P1 device and map directions, face buttons,
   Start, and Select. Repeat for Port 2, selecting the other device.
3. Save each controller profile with **Save Controller Profile**. The configured
   autoconfig directory is `~/.config/game-table/autoconfig/`.
4. Initially **Select+Start** opens the menu. In **Settings → Input → Hotkeys**,
   you can disable that Menu Toggle Controller Combo and bind a spare P1 admin button as **Hotkey
   Enable**, then bind Menu Toggle to Start. This gives admin+Start for the menu.
   F1 remains the keyboard recovery menu shortcut. Avoid an exit combo that fires
   during ordinary play. Use **Close Content** to return to the launcher.
5. Save the current configuration, quit, relaunch, and test both players in
   **Super Tilt Bro**. Save game-specific remaps using **Quick Menu → Controls →
   Manage Remap Files**; global pad mapping and per-game layouts are separate.

Defaults assign gamepad indexes 0 and 1. `player1_index`/`player2_index` in
settings.json can swap them. Identical inexpensive encoders can enumerate in a
different order at boot; numeric indexes alone cannot guarantee stable player
identity. Test cold boots; if assignments swap, identify encoder serials/physical
USB paths and choose an appropriate device reservation solution for that hardware.
Save the working profiles before installing the panels permanently.

The available eight action buttons plus Start accommodate the allocation above.
Four-button games can use fewer action buttons. An NES game uses Select, not
arcade credits. Keyboard encoders such as an
I-PAC need explicit, distinct P1/P2 keyboard bindings; the bundled defaults assume
gamepads. Share the encoder model before finalising the wiring/profile.

## Screen behind mirrored perspex

The default image is unmirrored: viewing through a semi-transparent mirror is
transmission, rather than looking at a reflected screen. Rotation is independent:
set the X11 output and rotation in settings.json to match the physical mounting.
The session validates the rotation and uses `xrandr`; it does not force a mode or
refresh rate. Start with the panel's native mode and at least 60 Hz.

Use dark artwork/backgrounds, a black mask around the active display, and enough
brightness to overcome the tint in the actual room. Test text size, viewing
angles from both seats, reflections, and ventilation with the top fitted. The
LCD backlight may still be visible on a black frame; power-off is the final
hidden-screen state. DPMS is disabled only in the arcade X11 session, so long
idle periods need deliberate shutdown or an eventual attract/idle policy.

Preserve game aspect ratios: a widescreen panel should not stretch 4:3 games.
Opposite-side players cannot both see a conventional single-orientation game
upright. Alternating classic games may offer a per-game **cocktail cabinet** DIP
switch that flips the view on each turn. Simultaneous play generally suits
same-side controls, or titles designed for opposing seats. Global screen rotation
does not implement cocktail mode.

## Sound and power

Select HDMI/analogue audio and a moderate volume in Ubuntu before entering the
arcade session. `pactl info`, `pactl list short sinks`, and `speaker-test` help
diagnose routing. The setup uses the existing Ubuntu audio server.

Use an accessible PC power button with Ubuntu's shutdown action, or choose
**Super+Shift+P** in the arcade session (confirmation dialog) with a maintenance
keyboard. Session shutdown uses logind via `systemctl poweroff`. Test that it
works as the logged-in user. Close content first so saves are flushed; avoid
cutting mains power while running.

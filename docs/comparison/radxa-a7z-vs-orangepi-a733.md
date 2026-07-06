# Radxa A7Z/Z7A vs Orange Pi 4 Pro / Zero 3W

## Purpose

Compare the current A733 board options that matter for Debian desktop bring-up, with a focus on HDMI display, desktop readiness, and how much vendor support each board exposes today.

## Short answer

- If the question is "which vendor currently exposes the more obvious Debian 12 desktop path for A733?", Orange Pi is ahead on paper.
- If the question is "which hardware is more suitable as a reference for HDMI bring-up on A733?", both are useful, but Radxa A7Z gives a very clean Micro HDMI path and Orange Pi 4 Pro gives the clearest Bookworm-oriented build tree.
- If the question is "can we use either one as a basis for our own A733 work?", yes. The useful part is the shared SoC class and the differences in BSP packaging, not the logo on the board.

## Board summary

| Board | Display outputs | Official desktop image signal | BSP signal | Practical takeaway |
| --- | --- | --- | --- | --- |
| Radxa Cubie A7Z | Micro HDMI, USB-C DP Alt Mode | Radxa's A733 image page currently shows Debian 11 desktop images, and the repo warns that the supported public desktop line is the Debian Desktop image | Vendor BSP exists, but public evidence is more conservative about supported desktop combinations | Good baseline for HDMI bring-up; less evidence of a polished Bookworm desktop path |
| Radxa Cubie A7Z / A7A image family | A733 unified image family | Radxa documents a unified A733 image page and states the images are for A7Z, A7A, etc. | R6 is the stable line; t-series are test builds | Useful reference for how Radxa structures shared A733 support |
| Orange Pi 4 Pro | HDMI 2.0 | `bookworm jammy bullseye` are explicitly listed in the board config | `BOARDFAMILY="sun60iw2"` with `pvrsrvkm` in the module list | Best official clue that Bookworm desktop support on A733 is actively targeted |
| Orange Pi Zero 3W | Mini HDMI 2.0 | The board is in the same A733 family and the build tree uses the same `sun60iw2` base | Board config exists, and it participates in the same family-level support path | Good compact-board reference, but the 4 Pro is the stronger desktop reference |

## Radxa details

Radxa A7Z has two display-relevant traits that matter for bring-up:

- A dedicated Micro HDMI port.
- A USB-C port that supports DisplayPort Alt Mode.

For board bring-up, that gives us two separate paths. In practice, Micro HDMI is the safer first target because it is the simplest one to validate and it avoids the extra complexity of USB-C role handling.

Radxa's own download page for A7Z currently shows Debian 11 desktop images in the public download set, and the A7Z GitHub repo says that for most systems the supported public path is the Debian Desktop image. That does not mean Bookworm is impossible. It means the public evidence is narrower and more conservative than what Orange Pi exposes in its build tree.

## Orange Pi details

Orange Pi 4 Pro is the clearest "Bookworm is intended here" signal in the A733 family. Its board config explicitly lists:

- `BOARDFAMILY="sun60iw2"`
- `BOOT_FDT_FILE="allwinner/sun60i-a733-orangepi-4-pro.dtb"`
- `MODULES="aic8800_fdrv aic8800_btlpm pvrsrvkm"`
- `DISTRIB_TYPE_CURRENT="bookworm jammy bullseye"`
- `DISTRIB_TYPE_LEGACY="bookworm jammy bullseye"`

That is important because it tells us Orange Pi is not just building a CLI image and calling it done. It is trying to wire the desktop stack and the GPU module into the Bookworm path.

Orange Pi Zero 3W sits on the same `sun60iw2` family support path, but it is not as strong a desktop reference as the 4 Pro. For our purposes, it is still worth keeping around as a compact-board comparison, especially if we later care about board size, thermal envelope, or minimal wiring.

## What this means for our project

1. Radxa A7Z is still the cleaner reference for basic HDMI hardware bring-up.
2. Orange Pi 4 Pro is the better reference for Debian 12 desktop packaging on A733.
3. The shared `sun60iw2` family support is the bridge between the two vendors.
4. The main gap we need to watch is not "can the SoC display?", but "how complete is the vendor desktop packaging and GPU user-space on Bookworm?"

## Practical conclusion

For this project, the most useful working assumption is:

- Use Radxa A7Z/Z7A to understand the hardware/display path.
- Use Orange Pi 4 Pro to understand how Bookworm desktop support is being wired.
- Treat Orange Pi Zero 3W as a secondary reference unless we need compact-board specifics.
- Keep the target practical: a usable HDMI desktop on Debian 12, not a perfect vendor-style productized distro.

## Sources

- Radxa A7Z documentation: https://docs.radxa.com/en/cubie/a7z
- Radxa A7Z downloads: https://docs.radxa.com/en/cubie/a7z/download
- Radxa A7Z repo: https://github.com/radxa-build/radxa-cubie-a7z
- Orange Pi 4 Pro product page: https://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-4-Pro.html
- Orange Pi Zero 3W product page: https://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3W.html
- Orange Pi build repo: https://github.com/orangepi-xunlong/orangepi-build
- Orange Pi 4 Pro board config: https://github.com/orangepi-xunlong/orangepi-build/blob/next/external/config/boards/orangepi4pro.conf
- Orange Pi Zero 3W board config: https://github.com/orangepi-xunlong/orangepi-build/blob/next/external/config/boards/orangepizero3w.conf
- Orange Pi Bookworm build issue: https://github.com/orangepi-xunlong/orangepi-build/issues/312


# radxa-a7z-display

Documentation hub for bringing up and maintaining HDMI desktop support on Allwinner A733 boards, with a focus on Radxa A7Z/Z7A and related Orange Pi references.

![Radxa Cubie A7Z board, official product photo](https://docs.radxa.com/en/img/cubie/a7z/a7z-top.webp)

Product photo source: [Radxa Cubie A7Z documentation](https://docs.radxa.com/en/cubie/a7z).

## Project Background

I bought a Radxa A7Z in December 2025 because the Allwinner A733 looked unusually strong for its class: an 8-core CPU with 2x Cortex-A76 and 6x Cortex-A55 cores, an Imagination PowerVR GPU, and a 3 TOPS INT8 NPU in a very small board. At the time, the entry A733 boards were priced like budget hobby boards, while the Raspberry Pi-shaped Radxa A7Z 4GB model was still far cheaper than many boards with weaker practical performance. Compared with common RK3566 boards such as the Orange Pi 3B and CM4-style alternatives, the A733 platform looked like a much better performance-per-money target.

The hardware was attractive, but the software situation was not. After buying the board, I found that official system updates were slow. The only officially useful GUI image was an archived Debian 11 build, while newer Debian desktop images were either missing or not in a usable release state for HDMI desktop use.

This project exists to unlock that hardware. The first goal was simple and concrete: make the Radxa A7Z / A733 boot a modern Debian desktop with HDMI output. We now have a Debian 12 Bookworm KDE image that boots, starts SDDM, reaches Plasma Wayland, and displays a 1920x1080 HDMI desktop on real hardware.

That first successful desktop boot was the point where this stopped being only a research note. The board still has unfinished work, especially GPU acceleration, NPU enablement, audio validation, and BSP cleanup, but the main path is now proven. If you bought this board for the same reason, or if you think the A733 still has more potential than its official software support suggests, this repository is meant to be a practical place to continue that work.

## Capability Status

This table is the short, practical view of what currently works and what still needs work on the Debian 12 KDE image.

| Area | Current status | Notes |
| --- | --- | --- |
| Debian 12 Bookworm boot | Working | Boots on Radxa Cubie A7Z / A733 from the RSDK-based image. |
| HDMI desktop output | Working | KDE Plasma Wayland reaches HDMI-A-1 at 1920x1080 60 Hz on real hardware. |
| Display manager | Working | SDDM starts and reaches the graphical login / desktop path. |
| Default user login | Working | `radxa` / `radxa`. |
| Wi-Fi and SSH | Working in first validation | Board was reachable over SSH at `192.168.123.210` during the first test. |
| Root filesystem expansion | Working in first validation | Rootfs expanded to the SD card and mounted from `mmcblk0p3`. |
| Windows-friendly image release | Working | Public `.img.xz` release is available; Rufus or balenaEtcher can be tried directly. |
| Small-screen native mode selection | BSP patch ready; build and board validation pending | The BSP ignores standard DRM `video=` overrides and currently picks a CEA 1080i mode over a preferred 1024x600 EDID timing. |
| GPU acceleration | Not solved | Current renderer is `llvmpipe`; hardware 3D acceleration is not enabled yet. |
| DRM render node | Not solved | Only `/dev/dri/card0` was observed; no separate render node was seen in first validation. |
| HDMI audio | Not validated | Audio devices are visible, but playback and HDMI audio quality still need testing. |
| Bluetooth | Not validated | Controller visibility and pairing/audio profiles still need validation. |
| NPU | Not started | A733 has NPU potential, but this project has not enabled or validated it yet. |
| BSP/kernel cleanup | Open issue | Vendor kernel logs still contain warnings and missing-module messages. |
| Debian 13 / Trixie | Not started | Debian 12 is the current priority and the first working desktop target. |

## What this repository is for

- Collect and preserve research notes about A733 display support.
- Record the technical constraints around Debian 12 desktop bring-up.
- Track implementation decisions, validation steps, and long-term maintenance rules.
- Keep English source documents and Chinese translations side by side.

## Document map

- [Project Overview](docs/project-overview.md)
- [Current Status](docs/status.md)
- [Display Landscape Research](docs/research/a733-display-landscape.md)
- [Display Stack Architecture](docs/architecture/display-stack.md)
- [Contributing Guide](docs/contributing.md)
- [Naming Conventions](docs/naming-conventions.md)
- [Validation Guide](docs/validation.md)
- [Validation Record Template](docs/validation-template.md)
- [Validation Example](docs/examples/radxa-a7z-first-hdmi-example.md)
- [Radxa RSDK vs Orange Pi A733](docs/comparison/radxa-rsdk-vs-orangepi-a733.md)
- [A7Z Debian 12 Report Format](docs/a7z-debian12-report-format.md)
- [Small HDMI Panel Mode Selection](docs/experiments/a733-small-hdmi-panel-mode-selection.md)
- [A7Z Debian 12 Trial Checklist](docs/experiments/a7z-debian12-checklist.md)
- [Decision Log](docs/decision-log.md)
- [Sources Index](docs/sources.md)

## Tools

- `python3 tools/a733_compare.py compare <left-source-tree> <right-source-tree> --left-label <name> --right-label <name> --output report.md`
- `python3 tools/a733_compare.py check <source-tree> --output report.md`
- The tool scans board configs, family configs, and AArch64 DTS files, then renders a Markdown comparison report or a minimum-tree check report.
- `python3 tools/a7z_debian12_report.py <radxa-rsdk-tree> <orangepi-build-tree> --output report.md`
- This tool turns the Radxa/Orange Pi source trees into an A7Z Debian 12 migration report.
- `patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch` makes the vendor DRM driver select the EDID preferred mode before falling back to the first advertised mode.

## Maintenance rules

- English documents are the source of truth.
- Every core document must have a matching `.zh-CN.md` translation.
- Keep decisions in the decision log, not scattered across notes.
- Add sources for any hardware, BSP, or release claim before treating it as a project fact.
- Keep the docs practical and lightweight. This is a personal project first, with collaborators welcome but not required.

## Current status

- Project name: `radxa-a7z-display`
- Scope: Debian 12 HDMI desktop bring-up and long-term maintenance on A733 boards
- Repository state: local git initialized
- Latest test release: [`v0.1.0-a733-debian12-kde`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.0-a733-debian12-kde)

## Download

The first public test image is available from the GitHub release page:

- Release: [`v0.1.0-a733-debian12-kde`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.0-a733-debian12-kde)
- Image: `radxa-a733-debian12-kde-20260707.img.xz`
- Checksum file: `SHA256SUMS`

On Linux, decompress and flash it with:

```bash
xz -d radxa-a733-debian12-kde-20260707.img.xz
sudo dd if=radxa-a733-debian12-kde-20260707.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
sync
```

On Windows, try writing the `.img.xz` directly with Rufus or balenaEtcher. If the writer does not accept `.xz`, decompress it first and write the resulting `.img`.

## First Successful Debian 12 KDE Boot

Date: 2026-07-07

We built a Debian 12 Bookworm KDE image for Radxa Cubie A7Z / A733 from the Radxa RSDK path, flashed it to an SD card, booted the board, and reached a working HDMI Plasma desktop.

Observed on the board:

- Board hostname: `radxa-cubie-a7z`
- Login: `radxa` / `radxa`
- OS: Debian GNU/Linux 12 Bookworm
- Kernel: `5.15.147-21-a733`
- Desktop: KDE Plasma 5.27.5 on Wayland
- Display path: HDMI-A-1, 1920x1080 at 60 Hz
- Display manager: SDDM
- Network: Wi-Fi connected, SSH reachable at `192.168.123.210` during validation
- Storage: rootfs expanded to the SD card, `/` mounted on `mmcblk0p3`

Evidence:

![Debian 12 KDE desktop on A733](docs/assets/a733-debian12-first-boot/debian12-kde-hdmi-01.png)

![A733 system information](docs/assets/a733-debian12-first-boot/debian12-kde-system-info.png)

![A733 display settings](docs/assets/a733-debian12-first-boot/debian12-kde-display-settings.png)

![A733 KDE desktop with terminal](docs/assets/a733-debian12-first-boot/debian12-kde-terminal-validation.png)

Known gaps after first boot:

- Graphics acceleration is not proven. `glxinfo` and Info Center report `llvmpipe`, so rendering is currently software-backed.
- Only `/dev/dri/card0` is present; no separate render node was observed during this validation.
- `xdg-desktop-portal` and `xdg-desktop-portal-kde` were inactive in the user session during the first check.
- Kernel logs contain vendor/BSP warnings, including debug-kernel notices, GPU power-domain probe timeout messages, audio/HDMI warnings, and some missing module entries.
- Audio devices are visible through PipeWire/ALSA, but playback quality was not tested yet.

Detailed record:

- [2026-07-07 A733 Debian 12 KDE first boot validation](docs/validation-records/2026-07-07-a733-debian12-kde-first-boot.md)

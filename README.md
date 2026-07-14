# radxa-a7z-display

[中文说明](README.zh-CN.md)

Debian 12 KDE desktop image, native HDMI mode support, and reproducible A733
display-kernel work for Radxa A7Z/Z7A boards.

![Radxa Cubie A7Z board, official product photo](https://docs.radxa.com/en/img/cubie/a7z/a7z-top.webp)

Product photo source: [Radxa Cubie A7Z documentation](https://docs.radxa.com/en/cubie/a7z).

## Latest Verified Release

The complete display kernel is available from
[`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display).

Verified on a physical Radxa Cubie A7Z:

| Item | Verified result |
| --- | --- |
| Debian | Debian 12 Bookworm with KDE Plasma Wayland |
| Kernel package | `5.15.147-21.1+display2` |
| Boot entry | Custom kernel on `l0`; vendor recovery kernel retained on `l1` |
| Small HDMI panel | `FLY-HDMI-LCD7` at native `1024x600@60Hz` |
| Network | AIC8800 Wi-Fi and SSH working |
| Display policy | Uses the EDID preferred/native timing instead of forcing Full HD |

Release assets include the installable `.deb`, a guarded deployment script,
the BSP source patch, and SHA256 checksums.

## Project Background

I bought a Radxa A7Z in December 2025 because the Allwinner A733 looked unusually strong for its class: an 8-core CPU with 2x Cortex-A76 and 6x Cortex-A55 cores, an Imagination PowerVR GPU, and a 3 TOPS INT8 NPU in a very small board. At the time, the entry A733 boards were priced like budget hobby boards, while the Raspberry Pi-shaped Radxa A7Z 4GB model was still far cheaper than many boards with weaker practical performance. Compared with common RK3566 boards such as the Orange Pi 3B and CM4-style alternatives, the A733 platform looked like a much better performance-per-money target.

The hardware was attractive, but the software situation was not. After buying the board, I found that official system updates were slow. The only officially useful GUI image was an archived Debian 11 build, while newer Debian desktop images were either missing or not in a usable release state for HDMI desktop use.

This project exists to unlock that hardware. The first goal was simple and concrete: make the Radxa A7Z / A733 boot a modern Debian desktop with HDMI output. We now have a Debian 12 Bookworm KDE image that boots, starts SDDM, reaches Plasma Wayland, and selects the connected display's EDID preferred mode. The initial 1080p desktop path and the corrected `FLY-HDMI-LCD7` native `1024x600` path have both run on real hardware; final-kernel regression coverage on additional monitors remains open.

That first successful desktop boot was the point where this stopped being only a research note. The board still has unfinished work, especially GPU acceleration, NPU enablement, audio validation, and BSP cleanup, but the main path is now proven. If you bought this board for the same reason, or if you think the A733 still has more potential than its official software support suggests, this repository is meant to be a practical place to continue that work.

## Capability Status

This table is the short, practical view of what currently works and what still needs work on the Debian 12 KDE image.

| Area | Current status | Notes |
| --- | --- | --- |
| Debian 12 Bookworm boot | Working | Boots on Radxa Cubie A7Z / A733 from the RSDK-based image. |
| HDMI desktop output | Working | KDE Plasma Wayland reaches HDMI-A-1 and follows the display's EDID preferred/native timing. |
| Display manager | Working | SDDM starts and reaches the graphical login / desktop path. |
| Default user login | Working | `radxa` / `radxa`. |
| Wi-Fi and SSH | Working | AIC8800 Wi-Fi modules load under the full display kernel; SSH was verified at `192.168.123.210`. |
| Serial console | Documented | UART0 is available on the 40-pin header for boot and recovery diagnostics. |
| Root filesystem expansion | Working | Rootfs expands to the SD card and mounts from `mmcblk0p3`. |
| Windows-friendly image release | Working | `v0.1.1` is XZ-compressed from the verified raw image without modifying GPT. |
| Small-screen native mode selection | Working | Verified on `FLY-HDMI-LCD7`: the native `1024x600@60Hz` timing is selected without stretching or cropping. |
| Full display kernel package | Working | `5.15.147-21.1+display2` boots from `l0`; SSH, AIC8800 Wi-Fi, KDE, and native HDMI mode are verified. |
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
- [A733 GPU Acceleration Driver Feasibility](docs/research/a733-gpu-acceleration-feasibility.md)
- [Display Stack Architecture](docs/architecture/display-stack.md)
- [Contributing Guide](docs/contributing.md)
- [Naming Conventions](docs/naming-conventions.md)
- [Validation Guide](docs/validation.md)
- [Validation Record Template](docs/validation-template.md)
- [Validation Example](docs/examples/radxa-a7z-first-hdmi-example.md)
- [Radxa RSDK vs Orange Pi A733](docs/comparison/radxa-rsdk-vs-orangepi-a733.md)
- [A7Z Debian 12 Report Format](docs/a7z-debian12-report-format.md)
- [Small HDMI Panel Mode Selection](docs/experiments/a733-small-hdmi-panel-mode-selection.md)
- [Full Display Kernel Release](docs/releases/v0.2.1-a733-full-kernel-display.md)
- [A7Z Debian 12 Trial Checklist](docs/experiments/a7z-debian12-checklist.md)
- [A7Z Serial Console and Recovery](docs/a7z-serial-console.md)
- [Decision Log](docs/decision-log.md)
- [Sources Index](docs/sources.md)

## Tools

- `python3 tools/a733_compare.py compare <left-source-tree> <right-source-tree> --left-label <name> --right-label <name> --output report.md`
- `python3 tools/a733_compare.py check <source-tree> --output report.md`
- The tool scans board configs, family configs, and AArch64 DTS files, then renders a Markdown comparison report or a minimum-tree check report.
- `python3 tools/a7z_debian12_report.py <radxa-rsdk-tree> <orangepi-build-tree> --output report.md`
- This tool turns the Radxa/Orange Pi source trees into an A7Z Debian 12 migration report.
- `patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch` removes A733's forced-FHD policy and makes the vendor DRM driver select the EDID preferred mode before falling back to the first advertised mode.
- `tools/package_a733_kernel_display.sh INPUT.deb OUTPUT.deb` adds the A7Z initramfs size workaround and produces the installable `+display2` kernel package.
- `sudo tools/deploy_a733_display_kernel.sh PACKAGE.deb --activate` installs one package under a lock and verifies DKMS and initramfs safety gates before selecting `l0`.

## Maintenance rules

- English documents are the source of truth.
- Every core document must have a matching `.zh-CN.md` translation.
- Keep decisions in the decision log, not scattered across notes.
- Add sources for any hardware, BSP, or release claim before treating it as a project fact.
- Keep the docs practical and lightweight. This is a personal project first, with collaborators welcome but not required.

## Current status

- Project name: `radxa-a7z-display`
- Scope: Debian 12 HDMI desktop bring-up and long-term maintenance on A733 boards
- Repository state: published and maintained on GitHub
- Latest test release: [`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.1-a733-debian12-kde-raw)
- Latest full display kernel: [`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display)

## Download

The verified install image is available from
[`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.1-a733-debian12-kde-raw):

- Image: `radxa-a733-debian12-kde-20260713.img.xz`
- Checksum file: `SHA256SUMS`
- The XZ asset decompresses to the exact RSDK `output.img` that booted on the
  physical A7Z. Its GPT layout and partition attributes are unchanged.

`v0.1.0-a733-debian12-kde` remains withdrawn. Its PiShrink-processed image
does not boot on the A7Z; do not flash it.

On Linux, decompress and flash the verified release with:

```bash
xz -d radxa-a733-debian12-kde-20260713.img.xz
sudo dd if=radxa-a733-debian12-kde-20260713.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
sync
```

On Windows, try writing the `.img.xz` directly with Rufus or balenaEtcher. If the writer does not accept `.xz`, decompress it first and write the resulting `.img`.

## Install The Full Display Kernel

Boot the Debian 12 image first, then download these assets from
[`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display):

- `linux-image-5.15.147-21.1-a733_5.15.147-21.1+display2_arm64.deb`
- `deploy_a733_display_kernel.sh`
- `SHA256SUMS`

Verify and install on the A7Z:

```bash
sha256sum -c SHA256SUMS
chmod +x deploy_a733_display_kernel.sh
sudo ./deploy_a733_display_kernel.sh \
  linux-image-5.15.147-21.1-a733_5.15.147-21.1+display2_arm64.deb \
  --activate
sudo reboot
```

The installer deliberately runs one foreground `dpkg`/DKMS sequence under a
lock. Do not start another package or DKMS command while it is running, even if
the terminal temporarily produces no output.

After reboot:

```bash
uname -r
dpkg -s linux-image-5.15.147-21.1-a733 | grep -E '^(Status|Version):'
ip -brief address show wlan0
sudo journalctl -b -k --no-pager \
  | grep -E 'Configuration mode|drm hdmi mode set'
```

Expected on the tested small panel:

```text
5.15.147-21.1-a733
Version: 5.15.147-21.1+display2
HDMI-A-1: Configuration mode 1024x600@60Hz
drm hdmi mode set: 1024*600
```

## Recovery

The vendor kernel remains available as `l1`. If the custom entry does not
boot, mount the SD card on another Linux system and change the default entry:

```bash
sudo mount /dev/<root-partition> /mnt/a7z-root
sudo sed -i 's/^default l0$/default l1/' \
  /mnt/a7z-root/boot/extlinux/extlinux.conf
sync
sudo umount /mnt/a7z-root
```

The full failure analysis, including the initramfs size issue and the DKMS
concurrency incident, is recorded in
[A733 Small HDMI Panel Mode Selection](docs/experiments/a733-small-hdmi-panel-mode-selection.md).

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

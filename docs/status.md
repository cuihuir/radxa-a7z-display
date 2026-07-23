# Current Status

> Generated from `docs/status.json`. Edit the JSON source, then run `python3 tools/render_status.py`.

**2026-07-22**

## Verified Baseline

| Item | Verified result |
| --- | --- |
| Board | Radxa Cubie A7Z / Allwinner A733 |
| Operating system | Debian 12 Bookworm · KDE Plasma Wayland |
| Kernel | `5.15.147-21.1-a733` · package `5.15.147-21.1+display4` |
| GPU package | `a733-pvr-gpu 24.2.6603887+gpu8` |
| GPU | PowerVR B-Series BXM-4-64 · DDK `24.2@6603887` |
| Graphics APIs | Vulkan · OpenCL 3.0 · EGL/GBM · OpenGL ES 3.2 |
| Desktop renderer | PowerVR-accelerated KWin / Plasma Wayland |
| Display | `FLY-HDMI-LCD7` · `1024x600@60Hz` · scale 100% |
| Network | AIC8800 Wi-Fi and SSH working |
| Display policy | EDID preferred/native timing; no forced Full HD |
| Recovery | Normal desktop on `l0` · vendor fallback on `l1` · early-fsck recovery on `a7z-recovery` |

## Capability Status

Status: ✅ working · 📘 documented · 🧪 awaiting validation · 🚧 in progress · ⬜ not started

| Area | Current status | Notes |
| --- | --- | --- |
| Debian 12 Bookworm boot | ✅ Working | RSDK-based image boots from SD on Radxa Cubie A7Z/A733. |
| HDMI desktop output | ✅ Working | Plasma Wayland reaches HDMI-A-1 and follows the EDID preferred/native timing. |
| Display manager | ✅ Working | SDDM reaches the graphical login and desktop path. |
| Default user login | ✅ Working | Username and password are both `radxa`. |
| Power-loss filesystem recovery | ✅ Working | An isolated 14.7 MB recovery initramfs repaired an injected ext4 group-descriptor fault before root mount and continued to a complete boot; unrecoverable errors still require offline fsck. |
| Wi-Fi and SSH | ✅ Working | AIC8800 Wi-Fi and SSH are verified with the full display/GPU stack. |
| Serial console | 📘 Documented | UART0 on the 40-pin header is documented for boot and recovery diagnostics. |
| Root filesystem expansion | ✅ Working | Rootfs expands to the SD card and mounts from `mmcblk0p3`. |
| Windows-friendly image release | ✅ Working | `v0.3.3` integrates Debian 12 KDE, `display4`, `gpu8`, packaged XWayland/KWin acceleration, vendor `l1`, and the tested `a7z-recovery` early-fsck entry in one XZ image. |
| Small-screen native mode | ✅ Working | `FLY-HDMI-LCD7` runs at native `1024x600@60Hz` without stretching or cropping. |
| HDMI hotplug recovery | ✅ Working | `display4` keeps HDMI hardware changes synchronized with DRM atomic state; unplug/replug recovers automatically at SDDM without an xrandr or udev workaround. |
| Full display kernel package | ✅ Working | `5.15.147-21.1+display4` boots from `l0`, includes the A7Z DTB, and preserves the explicit vendor DTB and GPU blacklist on recovery entry `l1`. |
| GPU acceleration | ✅ Working (first port) | `gpu8` integrates the verified `pvrsrvkm`, Vulkan, OpenCL, EGL/GBM, PowerVR-accelerated KWin, and packaged XWayland GLES-glamor paths, with a compatible display-kernel dependency range. |
| GPU desktop environment isolation | ✅ Working | Ordinary Plasma clients, Discover, and KScreenLocker remain clean; only KWin and the compatible packaged XWayland receive scoped PowerVR libraries. |
| XWayland acceleration | ✅ Working | Packaged XWayland 24.1.6 GLES glamor reaches 100% GPU utilization, and native-visual X11 EGL/GLES renders on PowerVR; desktop GLX remains llvmpipe. |
| DRM render node | ✅ Working | PowerVR provides `/dev/dri/card1` and `renderD128`; HDMI KMS remains on `card0`. |
| HDMI audio | 🧪 Not validated | Audio devices are visible; playback and HDMI audio quality still need testing. |
| Bluetooth | 🧪 Not validated | Controller visibility, pairing, and audio profiles still need validation. |
| NPU | ⬜ Not started | A733 NPU enablement and validation have not started. |
| BSP/kernel cleanup | 🚧 In progress | Vendor kernel logs still contain warnings and missing-module messages. |
| Debian 13 / Trixie | ⬜ Not started | Debian 12 remains the current priority and verified desktop target. |

## Current Milestone

- Repository: published and maintained on GitHub.
- Verified image: [`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.1.1-a733-debian12-kde-raw).
- Display kernel: [`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.2.1-a733-full-kernel-display).
- GPU image: [`v0.3.0-a733-pvr-gpu`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.0-a733-pvr-gpu), combining the verified display kernel and first PowerVR port.
- Hotplug update: [`v0.3.1-a733-hdmi-hotplug`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.1-a733-hdmi-hotplug), fixing HDMI reconnect and hardening `l0`/`l1` boot entries.
- Power-loss recovery image: [`v0.3.3-a733-touchscreen-recovery`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.3-a733-touchscreen-recovery), adding a hardware-tested early-fsck path and a ready-to-flash integrated image.

## Next Milestones

- Rebuild the validated KWin integration with release optimization, extend stability coverage, and determine the practical desktop GLX boundary of the GLES-only vendor stack.
- Validate HDMI audio playback and Bluetooth pairing/audio profiles.
- Triage remaining vendor BSP/kernel warnings.
- Regression-test native EDID policy on a normal 1080p monitor and additional panels.
- Start A733 NPU enablement research after the desktop stack is stable.

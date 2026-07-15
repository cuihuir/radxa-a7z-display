# Current Status

> Generated from `docs/status.json`. Edit the JSON source, then run `python3 tools/render_status.py`.

**2026-07-15**

## Verified Baseline

| Item | Verified result |
| --- | --- |
| Board | Radxa Cubie A7Z / Allwinner A733 |
| Operating system | Debian 12 Bookworm · KDE Plasma Wayland |
| Kernel | `5.15.147-21.1-a733` · package `5.15.147-21.1+display2` |
| GPU package | `a733-pvr-gpu 24.2.6603887+gpu4` |
| GPU | PowerVR B-Series BXM-4-64 · DDK `24.2@6603887` |
| Graphics APIs | Vulkan · OpenCL 3.0 · EGL/GBM · OpenGL ES 3.2 |
| Desktop renderer | PowerVR-accelerated KWin / Plasma Wayland |
| Display | `FLY-HDMI-LCD7` · `1024x600@60Hz` · scale 100% |
| Network | AIC8800 Wi-Fi and SSH working |
| Display policy | EDID preferred/native timing; no forced Full HD |
| Recovery | Custom stack on `l0` · vendor kernel retained on `l1` |

## Capability Status

Status: ✅ working · 📘 documented · 🧪 awaiting validation · 🚧 in progress · ⬜ not started

| Area | Current status | Notes |
| --- | --- | --- |
| Debian 12 Bookworm boot | ✅ Working | RSDK-based image boots from SD on Radxa Cubie A7Z/A733. |
| HDMI desktop output | ✅ Working | Plasma Wayland reaches HDMI-A-1 and follows the EDID preferred/native timing. |
| Display manager | ✅ Working | SDDM reaches the graphical login and desktop path. |
| Default user login | ✅ Working | Username and password are both `radxa`. |
| Wi-Fi and SSH | ✅ Working | AIC8800 Wi-Fi and SSH are verified with the full display/GPU stack. |
| Serial console | 📘 Documented | UART0 on the 40-pin header is documented for boot and recovery diagnostics. |
| Root filesystem expansion | ✅ Working | Rootfs expands to the SD card and mounts from `mmcblk0p3`. |
| Windows-friendly image release | ✅ Working | `v0.1.1` is XZ-compressed from the verified raw image without modifying GPT. |
| Small-screen native mode | ✅ Working | `FLY-HDMI-LCD7` runs at native `1024x600@60Hz` without stretching or cropping. |
| Full display kernel package | ✅ Working | `5.15.147-21.1+display2` boots from `l0`; recovery remains on `l1`. |
| GPU acceleration | ✅ Working (first port) | `pvrsrvkm`, Vulkan, OpenCL, EGL/GBM, and PowerVR-accelerated KWin are verified. |
| DRM render node | ✅ Working | PowerVR provides `/dev/dri/card1` and `renderD128`; HDMI KMS remains on `card0`. |
| HDMI audio | 🧪 Not validated | Audio devices are visible; playback and HDMI audio quality still need testing. |
| Bluetooth | 🧪 Not validated | Controller visibility, pairing, and audio profiles still need validation. |
| NPU | ⬜ Not started | A733 NPU enablement and validation have not started. |
| BSP/kernel cleanup | 🚧 In progress | Vendor kernel logs still contain warnings and missing-module messages. |
| Debian 13 / Trixie | ⬜ Not started | Debian 12 remains the current priority and verified desktop target. |

## Current Milestone

- Repository: published and maintained on GitHub.
- Verified image: [`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.1-a733-debian12-kde-raw).
- Display kernel: [`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display).
- GPU milestone: [`v0.3.0-a733-pvr-gpu`](https://github.com/cuihuir/radxa-a7z-display/blob/main/docs/releases/v0.3.0-a733-pvr-gpu.md), verified release candidate staged locally.

## Next Milestones

- Publish the verified `v0.3.0-a733-pvr-gpu` release candidate.
- Validate HDMI audio playback and Bluetooth pairing/audio profiles.
- Triage remaining vendor BSP/kernel warnings.
- Regression-test native EDID policy on a normal 1080p monitor and additional panels.
- Start A733 NPU enablement research after the desktop stack is stable.

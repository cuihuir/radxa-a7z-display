# A733 Small HDMI Panel Mode Selection

Date: 2026-07-13

## Goal

Make the A733 choose the native mode for HDMI panels whose EDID advertises both a low-resolution detailed timing and common CEA television modes.

## Hardware Result

The tested panel identifies itself as `FLY-HDMI-LCD7`. Its vendor HDMI diagnostic reports three `1024x600p` detailed timings, while also listing CEA SVD modes including VIC 5.

The running `5.15.147-21-a733` kernel selected VIC 5 instead:

```text
HDMI-A-1: Configuration mode 1920x1080@60Hz
sunxi hdmi select vic 5 use hdmi14 vsif
[dw video] ... vic | 005 | 1920x540 i | 60
```

The panel consequently showed only part of the 1080 output.

## Rejected Userspace Workaround

We tested the standard DRM command-line override:

```text
video=HDMI-A-1:1024x600@60
```

`u-boot-update` correctly added it to `/boot/extlinux/extlinux.conf`, and it appeared in `/proc/cmdline` after reboot. The vendor `sunxi-hdmi` driver still selected 1080, so this BSP does not honor the standard DRM override for its early HDMI mode selection. The override was removed after the test.

## Root Cause

In `radxa/allwinner-bsp`, `drivers/drm/sunxi_drm_drv.c` calls `list_first_entry_or_null()` to choose a connector mode during initial connection and hot-plug handling. It does not inspect `DRM_MODE_TYPE_PREFERRED`.

For this EDID, the first list entry is a CEA 1080i mode, while the native `1024x600` DTD is marked preferred by the DRM EDID parser. The failure is therefore a BSP mode-priority bug, not a KDE scaling issue and not an absent panel mode.

## Patch

`patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch` adds `sunxi_drm_pick_preferred_mode()` and uses it in all three first-mode fallback paths:

- HDMI hot-plug mode monitor.
- Board boot display-info fallback.
- No-bootloader-display-info fallback.

The helper chooses a `DRM_MODE_TYPE_PREFERRED` mode first and retains the original first-list-entry behavior when no preferred mode exists.

## Build And Test

Build from the matching Radxa packaging repository and submodules:

```bash
git clone --recurse-submodules https://github.com/radxa-pkg/linux-a733.git
cd linux-a733
git -C bsp apply /path/to/radxa-a7z-display/patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch
make deb
```

Install the resulting A733 kernel packages, reboot with the small panel connected, then verify:

```bash
sudo dmesg | grep -E 'Configuration mode|drm hdmi mode set'
cat /sys/class/drm/card0-HDMI-A-1/modes
```

Success criteria:

- The complete desktop is visible on the `FLY-HDMI-LCD7` panel.
- The selected HDMI mode is `1024x600` rather than VIC 5 / `1920x540i`.
- A normal 1080p monitor still selects its EDID preferred mode.

## Status

The patch applies cleanly to the `cubie-aiot-v1.4.6` BSP source used by `linux-a733` release `5.15.147-21`. It has not yet been compiled into a kernel package or validated on hardware.

# A733 PowerVR Desktop Environment Isolation

## Scope

This record validates `a733-pvr-gpu 24.2.6603887+gpu6` on the physical Radxa
Cubie A7Z. The objective is to keep KWin on the PowerVR stack without exposing
ordinary Qt Wayland clients, KScreenLocker, or XWayland to the vendor library
environment.

## Implementation

- Removed the global `/etc/environment.d/90-a733-pvr.conf` and
  `/etc/profile.d/a733-pvr.sh` exports.
- Kept PowerVR `LD_LIBRARY_PATH`, `LIBGL_DRIVERS_PATH`, and `KWIN_DRM_DEVICES`
  in the KWin-only launcher.
- Used a package-owned `dpkg-divert` wrapper to start
  `kscreenlocker_greet` without PowerVR variables.
- Added a clean-environment XWayland wrapper.
- Kept Vulkan and OpenCL selection explicit through `a733-pvr-run`.

## Hardware Results

| Check | Result |
|---|---|
| Kernel | `5.15.147-21.1-a733` |
| GPU package | `24.2.6603887+gpu6` |
| HDMI | `card0-HDMI-A-1` connected |
| KWin renderer | `PowerVR B-Series BXM-4-64`, OpenGL ES 3.2 |
| KWin DRM nodes | `card0` plus `renderD128` open |
| Vulkan | PowerVR B-Series Vulkan Driver `24.2@6603887` |
| OpenCL | PowerVR B-Series BXM-4-64, OpenCL 3.0 |
| Plasma environment | No PowerVR library variables |
| Discover | Clean environment; survived startup without the previous crash |
| KScreenLocker | Clean environment; software Qt Quick backend; remained running |
| Logout | Returned cleanly to SDDM |
| Disable/enable | Diversion and wrappers removed and restored correctly |

The lock-screen test no longer produced the earlier `EGL not available`
message. `kscreenlocker_greet` remained alive through repeated remote
lock/unlock cycles.

## Remaining Finding

XWayland `22.1.9` no longer inherits `LD_LIBRARY_PATH` or
`LIBGL_DRIVERS_PATH`, but still logs `Failed to initialize glamor, falling back
to sw`. It opens both `card0` and `renderD128`; the distribution Mesa path loads
`libdril_dri.so` and reports `egl: failed to create dri2 screen`.

A controlled vendor-environment comparison loads `pvr_dri.so`, exposes the
PowerVR DRI image and fence extensions, and still falls back after EGL config
enumeration. This narrows the remaining issue to XWayland/glamor compatibility
with the proprietary PVR DRI/EGL stack rather than environment variables or a
missing render node. Testing a newer XWayland and tracing its glamor EGL config
selection are the next useful experiments.

The board was returned to `default l0`, the temporary SDDM autologin file was
removed, and the graphical login screen was restored.

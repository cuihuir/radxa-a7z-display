# A733 PowerVR GPU Hardening Roadmap

## Current Baseline

The first A7Z PowerVR port is functional and verified on real hardware:

- `pvrsrvkm` DDK `24.2@6603887`, BVNC `36.56.104.183`;
- firmware startup and `/dev/dri/renderD128`;
- Vulkan, OpenCL 3.0, EGL/GBM, and OpenGL ES 3.2;
- PowerVR-accelerated KWin on Plasma Wayland;
- native `1024x600@60Hz` HDMI output and the `l1` recovery path.

This is a first port, not the end of GPU work. The remaining tasks below are
ordered by release risk.

## P0: Desktop Environment Isolation

The `gpu4` package exports the vendor library paths through
`/etc/profile.d/a733-pvr.sh`. This makes KWin use PowerVR, but also exposes
ordinary Qt Wayland clients to the vendor EGL stack.

Observed consequences include `EGL not available` warnings, a Discover crash,
and a broken KScreenLocker greeter when the Qt Quick scene graph backend was
forced to OpenGL. The stable setting for the first release is:

```ini
[QtQuickRendererSettings]
SceneGraphBackend=software
```

The next package revision should:

1. remove global PowerVR `LD_LIBRARY_PATH` and `LIBGL_DRIVERS_PATH` exports;
2. inject the vendor environment only into the KWin launch path;
3. launch `kscreenlocker_greet` with a clean Mesa environment;
4. keep Vulkan/OpenCL probes behind `a733-pvr-run`;
5. add login, lock/unlock, logout, and user-switch regression tests.

## P1: Acceleration Coverage

- Investigate XWayland's `Failed to initialize glamor, falling back to sw`
  result. Native Wayland composition is accelerated, but X11 applications may
  still use software rendering.
- Determine whether Qt Quick clients can safely use GPU rendering with a
  compatible Wayland EGL path. For `v0.3.0`, Qt Quick software rendering plus
  PowerVR KWin composition is the supported configuration.
- Validate Firefox/Chromium acceleration separately from KWin. Video decode is
  also a separate subsystem and must not be inferred from 3D acceleration.

## P1: Stability Validation

- Repeat cold boot, reboot, SDDM login, logout, lock/unlock, package disable,
  package enable, and package removal tests.
- Run Vulkan and OpenCL workloads long enough to detect GPU faults or resets.
- Check HDMI hotplug, multi-hour KWin operation, memory growth, and thermal
  behavior.
- Refresh and revalidate the capability-free KWin shadow copy after every
  distribution KWin upgrade.

## P2: Clock, Power, and Kernel Maintenance

- The DTS does not provide a default GPU clock rate, so the driver falls back
  to 600 MHz. Measure the actual clock and DVFS behavior before changing it.
- Triage the existing GPU power-domain and BSP warnings without treating every
  vendor debug warning as a GPU failure.
- Keep DDK `24.2@6603887`, firmware BVNC `36.56.104.183`, and userspace as one
  locked set.
- Use the official 6.6/Trixie integration as a reference, not as evidence that
  it is more mature than the verified Debian 12 path.
- Track mainline PowerVR DRM and Mesa as the long-term open-driver direction.

## v0.3.0 Release Boundary

`v0.3.0-a733-pvr-gpu` publishes the verified first port. Its supported desktop
configuration keeps the Qt Quick scene graph on software rendering while KWin
performs final composition with the PowerVR GPU. The environment-isolation and
XWayland work belongs to the next GPU package revision.

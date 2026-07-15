# 2026-07-14 A733 PowerVR GPU First Activation

## Environment

- Radxa Cubie A7Z with A733;
- Debian 12 Bookworm KDE Plasma Wayland;
- kernel `5.15.147-21.1-a733`, package `5.15.147-21.1+display2`;
- `a733-pvr-gpu 24.2.6603887+gpu4`;
- DDK `24.2@6603887`, BVNC `36.56.104.183`.

## Results

After reboot, `pvrsrvkm` loaded automatically, read BVNC `36.56.104.183` from
hardware registers, and registered DRM `pvr 24.2.6603887`. Both
`rgx.fw.36.56.104.183` and `rgx.sh.36.56.104.183` loaded successfully.

The DRM nodes are now `card0`, `card1`, and `renderD128`. Vulkan reports
`PowerVR B-Series BXM-4-64 MC1`; OpenCL 3.0 reports
`PowerVR B-Series BXM-4-64`; EGL initializes the `sunxi-drm` and `pvr` drivers.

Plasma Wayland also passed. KWin reports:

```text
OpenGL vendor string: Imagination Technologies
OpenGL renderer string: PowerVR B-Series BXM-4-64
OpenGL version string: OpenGL ES 3.2 build 24.2@6603887
```

The live KWin process maps the vendor GLES, `sunxi-drm_dri.so`, Services,
shader-compiler, and USC libraries rather than llvmpipe.

## Desktop Adaptation

The extra connector-less PVR DRM device confused Xorg auto-probing, so the
package pins the system modesetting driver to display device `card0`.

Debian gives `/usr/bin/kwin_wayland` `cap_sys_resource=ep`, enabling secure-exec
and causing the dynamic loader to ignore `LD_LIBRARY_PATH`. The package creates
an unprivileged same-version KWin shadow copy and selects it through PATH.
`KWIN_DRM_DEVICES=/dev/dri/card0` keeps HDMI scanout on the display KMS device
while `sunxi-drm` DRI uses PowerVR rendering.

## Regression Checks

- SDDM greeter starts normally;
- HDMI remains `1024x600@60Hz`;
- AIC8800 Wi-Fi remains available at `192.168.123.210`;
- extlinux defaults to `l0` and retains recovery entry `l1`;
- initramfs remains 42,251,173 bytes because GPU loads after root mount;
- temporary validation autologin was removed.

Known limitations are the expected out-of-tree kernel taint, a DTS clock-rate
fallback to 600 MHz, existing BSP power-domain/pinctrl/storage/display warnings,
and the need to refresh the KWin shadow copy after a distribution KWin update.


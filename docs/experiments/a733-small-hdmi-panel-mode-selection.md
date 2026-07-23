# A733 Small HDMI Panel Mode Selection

Date: 2026-07-14

## Result

Validated on a Radxa Cubie A7Z running Debian 12 KDE and the `FLY-HDMI-LCD7`
panel. HDMI now selects `1024x600@60Hz`; the complete desktop is visible
without stretching or cropping.

```text
HDMI-A-1: Configuration mode 1024x600@60Hz
sunxi-hdmi: drm hdmi mode set: 1024*600
```

The board booted the patched package as `5.15.147-21.1-a733`. Wi-Fi remained
available after the DKMS modules were rebuilt.

## Root Cause

The panel EDID has a base-block detailed timing for `1024x600`, but also
advertises common CEA modes up to `1920x1080`. A733 BSP configuration file
`configs/linux-5.15/sun60iw2p1.dtsi` enabled both of these DRM properties:

```text
quirk-prefer-fhd;
quirk-prefer-large-60;
```

The vendor EDID code cleared the native preferred flag and selected the largest
mode no larger than Full HD. The driver then chose `1920x1080@60Hz`, producing
a stretched and cropped desktop. Its mode-monitor path also used the first
advertised mode rather than the DRM preferred mode.

## Fix

`patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch`:

- removes the A733-wide forced-FHD and largest-60Hz EDID policy;
- selects `DRM_MODE_TYPE_PREFERRED` before falling back to the first mode in
  all three vendor DRM connection paths.

This is EDID-driven and does not hard-code a panel name or resolution. A normal
display with a valid preferred EDID timing continues to use that timing.

## Build

`linux-a733` copies `bsp/configs/linux-5.15/*.dtsi` into the kernel tree during
`pre_build`. Apply the patch to the `bsp` submodule, not only to the generated
`src/` copy:

```bash
git clone --recurse-submodules https://github.com/radxa-pkg/linux-a733.git
cd linux-a733
git -C bsp apply /path/to/radxa-a7z-debian12/patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch
make deb
```

For this RSDK build, `.github/local/Makefile.local` must set:

```make
KBUILD_IMAGE=arch/arm64/boot/Image
```

The packaged `/boot/vmlinuz-*` must be an uncompressed `Image`. If it is
`Image.gz`, U-Boot cannot load it and silently falls back to the vendor kernel.

```bash
dpkg-deb --fsys-tarfile linux-image-*.deb \
  | tar xOf - ./boot/vmlinuz-5.15.147-21.1-a733 | file -
```

Expected output includes `Linux kernel ARM64 boot executable Image`.

## Installation And Validation

Keep the vendor kernel as an `l1` extlinux fallback. Reinstalling the
same-version image package removes DKMS modules, so rebuild them before
switching to `l0`:

```bash
sudo dpkg -i linux-image-5.15.147-21.1-a733_*.deb
sudo dkms install --force -m aic8800-usb -v 5.0+git20260123.5f7be68d-6 \
  -k 5.15.147-21.1-a733
sudo dkms install --force -m radxa-overlays -v 0.2.25 \
  -k 5.15.147-21.1-a733
sudo sed -i 's/^default l1$/default l0/' /boot/extlinux/extlinux.conf
sudo reboot
```

Verify after reboot:

```bash
uname -r
sudo journalctl -b -k --no-pager | grep -E 'Configuration mode|drm hdmi mode set'
```

Expected result:

```text
5.15.147-21.1-a733
HDMI-A-1: Configuration mode 1024x600@60Hz
sunxi-hdmi: drm hdmi mode set: 1024*600
```

## Tested Facts

- `video=HDMI-A-1:1024x600@60` was ignored by the vendor early HDMI path.
- `fb0` reports `1024x1200`; its virtual height is double-buffering, while the
  physical HDMI mode is `1024x600`.
- If booting fails, select `default l1` offline in
  `/boot/extlinux/extlinux.conf` and reboot.

## Full Kernel Package Failure And Fix

The first complete package attempt had two independent failures:

1. An interrupted installation was followed by a second DKMS invocation while
   the first one was still running. Concurrent writes corrupted ext4 directory
   metadata. Offline `e2fsck -fy` repaired the filesystem. Kernel deployment
   must use one foreground `dpkg` process protected by a lock; never start a
   second DKMS build because SSH output appears to stop.
2. The regenerated `5.15.147-21.1` initramfs was 42,672,314 bytes and failed
   before persistent journal logging. Reusing the vendor initramfs booted the
   same custom kernel. A temporary initramfs without the fsck hook was
   42,251,056 bytes and also booted. The evidence points to an A733 U-Boot or
   early load-memory limit rather than a corrupt kernel or archive.

`config/initramfs-tools/hooks/zz-a7z-skip-early-fsck` removes fsck binaries and
their ext2fs-only libraries from the generated initramfs. It does not remove
filesystem repair tools from the running Debian system. The packaged
`5.15.147-21.1+display2` result generated a 42,251,173-byte initramfs and booted
from the standard `l0` entry.

Final board evidence:

```text
Linux 5.15.147-21.1-a733
Package version: 5.15.147-21.1+display2
wlan0: 192.168.123.210/24
HDMI-A-1: Configuration mode 1024x600@60Hz
drm hdmi mode set: 1024*600
```

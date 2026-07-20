# A733 HDMI Hotplug Recovery Validation

## Objective

Fix HDMI output that remained blank after unplugging and reconnecting the cable,
even though the kernel detected HPD and reread the EDID.

## Root Cause

The BSP HDMI plug-out handler directly cleared cached DRM state and disabled the
HDMI hardware outside a DRM atomic commit. Xorg therefore retained an enabled
connector with the same mode, and reconnecting did not trigger a new modeset.
Manual `xrandr --output HDMI-1 --off` followed by `--mode 1024x600` confirmed
that a full atomic disable/enable sequence recovered the panel.

## Fix

- `0002-drm-hdmi-keep-atomic-state-across-hpd.patch` removes the out-of-band
  state clearing and hardware disable from the HPD plug-out handler.
- Kernel package `5.15.147-21.1+display3` explicitly installs the compiled A7Z
  DTB, which prevents an unbootable `l0` entry.
- Both deployment tools restore the vendor A7Z DTB and
  `module_blacklist=pvrsrvkm` on `l1` after every `u-boot-update`.

## Hardware Result

On July 20, 2026, the board booted `l0` with kernel
`5.15.147-21.1-a733`, package `5.15.147-21.1+display3`, and GPU package
`24.2.6603887+gpu8`. SDDM selected `1024x600@60Hz`; `pvrsrvkm` loaded and HDMI
was `connected` and `enabled`. A physical HDMI unplug/replug recovered the
display automatically without an xrandr command or udev rule.

Recovery entry `l1` remains independently bootable with the vendor kernel,
explicit vendor A7Z DTB, and PowerVR module blacklist.

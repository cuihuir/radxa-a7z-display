# A733 GPU Acceleration Driver Feasibility

## Scope

- Date: 2026-07-14
- Target: Radxa Cubie A7Z/A733, using Orange Pi 4 Pro and Zero 3W as references
- Current system: Debian 12 Bookworm KDE on Allwinner/Radxa BSP Linux `5.15.147`
- This pass studies source, packages, and upstream status only. It does not install a driver or modify an image.

## Conclusion

A733 acceleration is feasible, through two distinct paths:

| Path | Feasibility now | Capability | Main limitation |
| --- | --- | --- | --- |
| Vendor PowerVR DDK: `pvrsrvkm` plus matched userspace | High; best first experiment | OpenGL ES, Vulkan, OpenCL; existing A733 hardware results | Closed userspace, strict KM/UM lockstep, old Xorg/SSL conflicts |
| Mainline Linux PowerVR DRM plus Mesa PowerVR | Viable longer term, not yet a BSP replacement | Open Vulkan, with Zink as a possible OpenGL layer | Mainline Linux does not yet accept the exact A733 BVNC; A733 DT/power integration is missing |

Panfrost and Panthor are not applicable. A733 contains an Imagination PowerVR
`BXM-4-64`, BVNC `36.56.104.183`; those drivers and Mali `kbase` target ARM Mali.

The recommended first experiment is Radxa's matched set:

- `img-bxm-dkms`, producing `pvrsrvkm.ko`;
- `xserver-xorg-img-bxm-1.21.1-2.deb` userspace;
- common DDK `24.2@6603887`;
- firmware `rgx.fw.36.56.104.183`.

Do not initially mix Orange Pi's kernel module with arbitrary userspace. PowerVR
Services uses a private KM/UM interface and mismatches commonly fail during
device, firmware, or first-client initialization.

## Evidence in This Project

The local GPU node in
`sources/linux-a733/bsp/configs/linux-5.15/sun60iw2p1.dtsi` declares
`compatible = "img,gpu"`, MMIO at `0x01800000`, GPU and DVFS interrupts, and
Allwinner-specific clocks, reset, OPP, and power integration. The config selects
`CONFIG_AW_GPU_TYPE="bxm"`.

Buildable module source is present at
`sources/linux-a733/bsp/modules/gpu/img-bxm/linux/rogue_km`. Its sunxi build fixes
BVNC `36.56.104.183`, DDK `24.2@6603887`, `nulldrmws`, and `pvrsrvkm.ko`.

The current image uses llvmpipe because:

- `linux-image-5.15.147-21-a733` has no `pvrsrvkm.ko`;
- packaged Panfrost/Lima modules cannot drive BXM;
- `rootfs.tar` has no PowerVR userspace, module, or `img_icd.json`;
- its Mesa `25.0.7` package has no PowerVR ICD;
- cached `task-a733` depends on the BXM packages, but did not reach the rootfs.

Working HDMI DRM/KMS output does not itself provide GPU 3D acceleration.

## Vendor DDK Path

Radxa's `a733-bullseye` repository still published these on 2026-07-14:

| Package | Version | Contents |
| --- | --- | --- |
| `img-bxm-dkms` | `0.1.0-3` | PowerVR BXM kernel source and DKMS metadata |
| `xserver-xorg-img-bxm-1.21.1-2.deb` | `1.0.1` | Matching EGL/GLES/Vulkan/OpenCL/DRI userspace, firmware, and vendor Xorg files |

The userspace package contains versioned PVR GLES/OpenCL/DRI libraries,
`pvr_dri.so`, `sunxi-drm_dri.so`, `libpvr_mesa_wsi.so`, firmware
`rgx.fw.36.56.104.183`, and vendor Xorg/modesetting/glamor files. The literal
`.deb` in its package name is historical repository metadata.

Cross-vendor hardware evidence is strong:

- `Incipiens/OrangePiZero3W-GPU-VPU` transplanted Radxa userspace and rebuilt
  DKMS for Orange Pi `6.6.98-sun60iw2`;
- an Armbian sun60iw2 draft records `pvrsrvkm`, DRM `24.2.6603887`, firmware,
  and `renderD128` working on Orange Pi 4 Pro;
- `clinfo` enumerated `PowerVR B-Series BXM-4-64` with driver
  `24.2@6603887`;
- community testing recorded Chromium hardware rasterization through ANGLE/Vulkan.

The A7Z `5.15.147` environment is closer to Radxa's original stack than the
successful 6.6 transplant, but the first experiment must still verify BSP
headers such as `sunxi-sid.h`, `Module.symvers`, vermagic, exact DDK equality,
GPU power/clock/reset/interrupt setup, and controlled selection between Mesa,
GLVND, and vendor libraries.

### Risks

1. **Closed userspace and redistribution**: review licenses before publishing
   images or packages. On-demand download is safer than storing binaries here.
2. **KM/UM lockstep**: module `24.2.6603887`, userspace, and
   `36.56.104.183` firmware must remain one set.
3. **Distribution replacement**: the package carries a full Xorg and vendor
   drivers. Community tests saw file conflicts, old `libssl1.1`/`libcrypto1.1`
   dependencies, and DRI2/DRI3 issues. Avoid replacing Xorg in the first pass.
4. **API-specific validation**: a module and render node do not prove OpenCL,
   Vulkan, EGL/GLES, KWin, and Chromium all work.
5. **Power-domain warnings**: compare clocks, power, thermals, and suspend/resume
   around driver loading.

## Mainline Linux and Mesa Path

Current Mesa PowerVR documentation lists exact BVNC `36.56.104.183` as an
actively developed BXM-4-64 with a Vulkan 1.2 target. Imagination's firmware
repository contains `powervr/rogue_36.56.104.183_v1.fw`, added in 2025 and
updated on 2026-04-15.

However, as of 2026-07-14 Torvalds' PowerVR DRM driver still treats this BVNC as
unknown and rejects it. Its DT binding also differs from the BSP:

| Item | A733 BSP | Upstream binding |
| --- | --- | --- |
| compatible | `img,gpu` | `img,img-rogue` plus SoC/product compatibles |
| interrupts | GPU and DVFS | currently at most one |
| clocks | private sunxi names | `core`, `mem`, `sys` |
| power | private GPU top/core domains | standard power-domain interface |

The upstream path therefore needs an A733 binding and DT, CCU/reset/power
integration, Linux acceptance of `36.56.104.183`, upstream firmware, recent
Mesa, and hardware validation of coherency, DMA/IOMMU, stability, and suspend.

Mesa PowerVR is a Vulkan driver, not native Gallium OpenGL. Zink may later supply
desktop OpenGL, but this BXM is not yet a conformant Vulkan device; Mesa requires
`PVR_I_WANT_A_BROKEN_VULKAN_DRIVER=1`. This is a longer-term upstream prototype,
not the near-term Debian 12 desktop path.

## Recommended Sequence

### Phase 0: Read-Only Baseline

```bash
uname -a
cat /proc/device-tree/compatible | tr '\0' '\n'
ls -l /dev/dri
lsmod | grep -E 'pvr|panfrost|lima'
dmesg | grep -Ei 'gpu|pvr|rgx|power domain|iommu'
glxinfo -B
eglinfo
vulkaninfo --summary
```

Also preserve package state, `ldconfig -p`, Vulkan ICD files, and session type.

### Phase 1: Offline Package Audit and DKMS Build

1. Download and verify the matched Radxa packages.
2. Compare DDK, BVNC, firmware, and shared-library dependencies.
3. Build DKMS against current headers in a temporary rootfs or separate image.
4. Inspect `modinfo`, undefined symbols, and vermagic.
5. Do not overwrite Xorg or the bootable image.

Pass when a current-kernel `pvrsrvkm.ko` is produced with no unresolved symbols.

### Phase 2: Minimal Vendor-Stack Hardware Test

1. Use a cloned or second SD card.
2. Install the matched KM/UM set without initially replacing Xorg.
3. Validate module, firmware, render node, and PVR logs.
4. Validate headless OpenCL, then Vulkan.
5. Validate Wayland EGL/GLES, KWin, and Chromium ANGLE last.
6. Test reboot, suspend/resume, thermals, and sustained load.

### Phase 3: Upstream Prototype

1. Select a new kernel containing PowerVR DRM.
2. Port A733 CCU, power domains, and GPU DT.
3. Add and validate BVNC `36.56.104.183` and upstream firmware.
4. Build Mesa PowerVR Vulkan.
5. Run `vulkaninfo` and a CTS subset before Zink or compositor testing.

## Decision Gate

Proceed with the vendor DDK first only if DKMS needs no or small compatibility
patches, `pvrsrvkm` preserves HDMI DRM/KMS, at least one hardware API works
without replacing Xorg, and the binary distribution model is acceptable.

If it requires replacing the full Xorg stack, unsupported SSL libraries, or
heavy kernel changes, keep it experimental and raise the upstream path priority.

## Sources

- Local A733 BSP: `sources/linux-a733`
- Local RSDK output: `sources/rsdk/out/radxa-a733_bookworm_kde`
- Radxa A733 Bullseye repository: https://radxa-repo.github.io/a733-bullseye/
- Mesa PowerVR documentation: https://docs.mesa3d.org/drivers/powervr.html
- Linux PowerVR DRM: https://github.com/torvalds/linux/tree/master/drivers/gpu/drm/imagination
- PowerVR DT binding: https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml
- Imagination firmware: https://gitlab.freedesktop.org/imagination/linux-firmware
- Orange Pi Zero 3W GPU/VPU transplant: https://github.com/Incipiens/OrangePiZero3W-GPU-VPU
- Armbian A733 GPU draft: https://github.com/shkolnik/armbian-build/pull/10
- Armbian Orange Pi 4 Pro support: https://github.com/armbian/build/pull/9967
- Armbian Cubie A7Z support: https://github.com/armbian/build/pull/10036
- Radxa A733 missing GPU issue: https://github.com/radxa-build/radxa-a733/issues/17


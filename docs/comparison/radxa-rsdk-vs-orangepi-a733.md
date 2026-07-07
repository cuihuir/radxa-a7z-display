# Radxa RSDK vs Orange Pi A733

## What was compared

- Radxa's actual build framework: `sources/rsdk`
- Orange Pi's actual board/build tree: `sources/orangepi-build`

Radxa's `radxa-cubie-a7z` repository is only the release/workflow shell. The real A733 build logic lives in `rsdk`, so that is the correct source to compare against Orange Pi's build tree.

## Short answer

- Orange Pi exposes the more direct Debian 12 desktop path for A733.
- Radxa exposes the more explicit A733-specific limitation notes and release target policy.
- For our porting work, Orange Pi is the better Bookworm desktop reference.
- For understanding A733 desktop constraints, Radxa RSDK is the better source.

## Side-by-side summary

| Topic | Radxa RSDK | Orange Pi build tree | What it means |
| --- | --- | --- | --- |
| Public A733 product | `radxa-a733` | `orangepi4pro`, `orangepizero3w` | Both target A733, but the release model is different |
| Supported desktop target | `kde` and `cli` | Desktop images are built for A733 boards | Orange Pi presents the desktop path more directly |
| Supported suite | `trixie` | `bookworm`, `jammy`, `bullseye` | Orange Pi is more useful for Debian 12 bring-up |
| GPU note | A733 GPU support is OpenGL ES only | `pvrsrvkm` is integrated into the board tree | Orange Pi shows the GPU module wiring more explicitly |
| Default terminal / display path | `kmscon` with DRM backend for A733 on `trixie` | Standard board/image path with desktop stack and BSP modules | Radxa documents framebuffer limitations more openly |
| Board-specific overlay | Product metadata only | `sun60i-a733` overlay prefix for A733 boards | Orange Pi carries more board-specific plumbing in the tree |

## Radxa findings

The Radxa build framework identifies `radxa-a733` as:

- product name: `Generic A733 Image for Radxa products`
- supported suite: `trixie`
- supported editions: `kde` and `cli`
- SoC: `a733`

The same framework says the Allwinner family includes `a733` and has install recommendations for `bullseye` and `trixie`, but the product itself is still only published as `trixie`.

The most important A733-specific note is in the KDE package logic:

- Radxa states that the A733 GPU driver only supports OpenGL ES.
- KDE is wired to use `libqt5gui5-gles` so it can use hardware acceleration.
- Radxa explicitly says the A733 GPU driver does not support GDM for now.
- For `trixie` on A733, Radxa switches the default TTY terminal to `kmscon` with a DRM backend because framebuffer support is limited.

That is the clearest upstream signal we have about the real limit of the A733 graphics stack.

## Orange Pi findings

Orange Pi's A733 board configs are much more concrete for Debian 12:

- `orangepi4pro.conf` and `orangepizero3w.conf` both use `BOARDFAMILY="sun60iw2"`.
- Both boards use `BOOTCONFIG="sun60iw2p1_t736_defconfig"`.
- Both set `BOOT_FDT_FILE` to A733 DTBs.
- Both include `DISTRIB_TYPE_CURRENT="bookworm jammy bullseye"`.
- Both include `DISTRIB_TYPE_LEGACY="bookworm jammy bullseye"`.

Orange Pi 4 Pro goes one step further and wires in:

- `MODULES="aic8800_fdrv aic8800_btlpm pvrsrvkm"`

The `sun60iw2` family logic also does more A733-specific work:

- It switches the overlay prefix to `sun60i-a733` for `orangepi4pro` and `orangepizero3w`.
- It uses A733-specific Linux config names for both `legacy` and `current`.
- It installs `pvrsrvkm.ko` into the image.
- It pulls in `libAWIspApi` and desktop multimedia packages.

That is enough to say Orange Pi is not only advertising Bookworm support, it is actually wiring the desktop and GPU pieces into the board tree.

## What this means for our port

1. Orange Pi is the better reference for getting a Debian 12 desktop image together.
2. Radxa is the better reference for A733-specific graphics limitations and what will likely break first.
3. Both trees confirm that A733 desktop support is still BSP-driven, not a simple mainline-only story.
4. The first practical gap to watch is the graphics path:
   - Radxa documents framebuffer and GDM limitations.
   - Orange Pi wires `pvrsrvkm` and A733 desktop packages more aggressively.

## Direct conclusion

If our goal is "Debian 12 + HDMI desktop on A733", Orange Pi is the clearer build reference.

If our goal is "understand why A733 desktop support is fragile", Radxa RSDK gives the more honest limitation notes.

That makes the two trees complementary rather than redundant.

## Sources

- [Radxa Cubie A7Z repository](../../sources/radxa-cubie-a7z/README.md)
- [Radxa RSDK product metadata](../../sources/rsdk/src/share/rsdk/configs/products.json)
- [Radxa RSDK SoC metadata](../../sources/rsdk/src/share/rsdk/configs/socs.json)
- [Radxa RSDK KDE package logic](../../sources/rsdk/src/share/rsdk/build/mod/packages/kde.libjsonnet)
- [Radxa RSDK core package logic](../../sources/rsdk/src/share/rsdk/build/mod/packages/categories/core.libjsonnet)
- [Orange Pi 4 Pro board config](../../sources/orangepi-build/external/config/boards/orangepi4pro.conf)
- [Orange Pi Zero 3W board config](../../sources/orangepi-build/external/config/boards/orangepizero3w.conf)
- [Orange Pi sun60iw2 family config](../../sources/orangepi-build/external/config/sources/families/sun60iw2.conf)


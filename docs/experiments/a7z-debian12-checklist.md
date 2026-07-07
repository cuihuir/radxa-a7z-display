# A7Z Debian 12 Trial Checklist

This is a living checklist for the Debian 12 trial branch on Radxa Cubie A7Z.

## Current hypothesis

- Radxa `rsdk` can expose `bookworm` for `radxa-a733` without needing a rewrite of the entire A733 stack.
- The desktop path is likely to work first with the existing Radxa board boot/display pieces, then with Debian 12 user-space and desktop packaging.
- Micro HDMI is the first path to validate.

## Current local changes

- [x] Identify the real Radxa A733 build source as `rsdk`.
- [x] Confirm `radxa-cubie-a7z` is only the workflow/release shell.
- [x] Identify A733 desktop constraints in Radxa RSDK.
- [x] Identify Orange Pi A733 Bookworm desktop wiring as a reference.
- [x] Enable `bookworm` in `radxa-a733` supported suites.
- [x] Add `bookworm` to the Allwinner `soc_install_recommends` list.
- [x] Capture the two-line Radxa trial change as a reusable patch artifact.
- [x] Confirm `radxa-a733` now defaults to `bookworm` locally.
- [x] Initialize RSDK submodules after the first dry-run failure.
- [x] Confirm the current host needs a Debian/Ubuntu build environment.
- [x] Use the existing local Debian 12 distrobox for dependency installation and dry-run validation.
- [x] Add a Jsonnet 0.18 compatibility patch for Debian 12.
- [x] Confirm Debian 12 distrobox dry run completes for `radxa-a733 bookworm kde`.
- [x] Confirm host `qemu-aarch64` binfmt is registered.
- [x] Confirm `a733-bookworm` Radxa repository does not exist.
- [x] Confirm generic Radxa `bookworm` repository exists and is usable.
- [x] Add a local `.deb` cache downloader for A733 Bookworm kernel/U-Boot packages.
- [x] Skip the nonexistent A733 Bookworm SoC repository in RSDK.
- [x] Skip `radxa-otgutils` for A733/Bookworm because its postinst fails in the chroot.
- [x] Confirm A733 kernel, headers, and U-Boot install from the local cache.
- [x] Confirm `task-radxa-a733` installs from generic Radxa Bookworm.
- [x] Confirm full rootfs build completes under qemu-user.
- [x] Confirm `libguestfs-tools` is required for image generation.
- [x] Confirm `sgdisk` from `gdisk` must be reachable through PATH for image shrink.
- [x] Confirm RSDK generates `output.img`.
- [x] Capture the image-tool dependency/PATH fix as `patches/rsdk/0005-rsdk-image-tool-dependencies-and-sgdisk-path.patch`.

## Things to watch

- [x] Does `rsdk build radxa-a733` now default to `bookworm`?
- [ ] Does KDE on A733 still avoid GDM on `bookworm`?
- [ ] Does the generated image still keep Micro HDMI as the first workable path?
- [ ] Do any package hooks assume `trixie`-only behavior after the suite change?
- [ ] Does the generated A7Z report still point at the real next blocker after the metadata change?
- [x] Does a Debian/Ubuntu build environment complete the dry run?
- [x] Confirm real image build currently fails in the distrobox because host `qemu-aarch64` binfmt is missing.
- [x] Is `qemu-aarch64` registered on the host through `binfmt_misc`?
- [x] Does the KDE package set finish installing under qemu-user?
- [x] Does RSDK emit a non-empty `rootfs.tar`?
- [x] Does RSDK generate a flashable image after rootfs completion?
- [x] Does the generated image boot on A7Z/Z7A?
- [x] Does HDMI show a usable desktop on A7Z/Z7A?
- [x] Does Debian 12 reach SDDM/KDE on HDMI?
- [x] Capture first successful board screenshots.
- [x] Record first successful board validation note.
- [ ] Does Mesa expose hardware GPU acceleration instead of `llvmpipe`?
- [ ] Does HDMI audio playback work?
- [ ] Does Bluetooth pairing work?

## Findings so far

- `rsdk` already has A733-specific KDE logic for GLES and limited framebuffer support.
- `rsdk` already has `bookworm` handling in desktop package logic.
- The main blocker on the public side was the product metadata only advertising `trixie`.
- After the local metadata change, the remaining blocker should be runtime build/boot validation.
- The first dry run selected `radxa-a733 bookworm kde`, then failed on missing `jsonnet`.
- RSDK native setup only supports Debian/Ubuntu; the current host uses `dnf`.
- Debian 12 ships `jsonnet 0.18.0`, which lacks newer `std.contains` and `std.all` calls used by current RSDK.
- Replacing those calls with `std.member` and `std.filter`/length comparison lets the Debian 12 distrobox complete dry run.
- Installing `qemu-user-static` inside the current unprivileged distrobox warns that it cannot write `/proc/sys/fs/binfmt_misc`.
- Real build fails immediately because arm64 cannot run natively or through binfmt.
- The Fedora/RPM host has `qemu-user-static-aarch64` and `qemu-user-binfmt` available, but `sudo` requires a password in this session.
- Host binfmt is now enabled and `/proc/sys/fs/binfmt_misc/qemu-aarch64` exists.
- `https://radxa-repo.github.io/a733-bookworm/pkgs.json` returns 404, so RSDK must not add that repository for A733/Bookworm.
- `https://radxa-repo.github.io/bookworm/pkgs.json` exists and includes A733-related source metadata, but the APT index does not publish the A733 kernel/U-Boot binary package names.
- The A733 kernel/U-Boot packages can be supplied through `--debs sources/rsdk/debs/a733-bookworm`.
- `radxa-otgutils` version `0.3.3` has a chroot-hostile postinst; skipping it avoids the previous mmdebstrap failure.
- Full KDE installation is slow under qemu-user and should be treated as a long-running validation stage, not as a hang unless process state stops changing.
- Full rootfs generation completed and produced `sources/rsdk/out/radxa-a733_bookworm_kde/rootfs.tar`.
- RSDK image generation requires `guestfish`; install `libguestfs-tools` in the Debian build environment.
- RSDK image shrink calls `sgdisk`; install `gdisk` and ensure `/usr/sbin` or `/sbin` is in PATH.
- Patch `0005` makes RSDK setup install `libguestfs-tools`/`gdisk` and makes generated image scripts call `sgdisk` with an explicit sbin PATH.
- `sources/rsdk/out/radxa-a733_bookworm_kde/output.img` was generated successfully and has a GPT partition table.
- The generated image booted from SD card and reached KDE Plasma Wayland over HDMI.
- Default login observed on the image is `radxa` / `radxa`.
- HDMI was connected as `card0-HDMI-A-1` and the GUI ran at 1920x1080.
- `glxinfo` reports `llvmpipe`; hardware GPU acceleration is not solved yet.
- No failed systemd system units were observed during first SSH inspection.

## Next action

- Triage GPU acceleration first, then validate HDMI audio and Bluetooth.

## Notes

- Keep this checklist short.
- Add only what changes the next decision.

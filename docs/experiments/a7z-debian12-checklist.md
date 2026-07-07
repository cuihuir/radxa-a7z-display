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

## Things to watch

- [x] Does `rsdk build radxa-a733` now default to `bookworm`?
- [ ] Does KDE on A733 still avoid GDM on `bookworm`?
- [ ] Does the generated image still keep Micro HDMI as the first workable path?
- [ ] Do any package hooks assume `trixie`-only behavior after the suite change?
- [ ] Does the generated A7Z report still point at the real next blocker after the metadata change?
- [x] Does a Debian/Ubuntu build environment complete the dry run?
- [x] Confirm real image build currently fails in the distrobox because host `qemu-aarch64` binfmt is missing.
- [ ] Is `qemu-aarch64` registered on the host through `binfmt_misc`?

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

## Next action

- Install/register host-level `qemu-aarch64` binfmt, then retry `src/bin/rsdk build radxa-a733` inside the Debian 12 distrobox.

## Notes

- Keep this checklist short.
- Add only what changes the next decision.

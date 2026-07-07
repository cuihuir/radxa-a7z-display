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

## Things to watch

- [ ] Does `rsdk build radxa-a733` now default to `bookworm`?
- [ ] Does KDE on A733 still avoid GDM on `bookworm`?
- [ ] Does the generated image still keep Micro HDMI as the first workable path?
- [ ] Do any package hooks assume `trixie`-only behavior after the suite change?
- [ ] Does the generated A7Z report still point at the real next blocker after the metadata change?

## Findings so far

- `rsdk` already has A733-specific KDE logic for GLES and limited framebuffer support.
- `rsdk` already has `bookworm` handling in desktop package logic.
- The main blocker on the public side was the product metadata only advertising `trixie`.
- After the local metadata change, the remaining blocker should be runtime build/boot validation.

## Next action

- Build or at least dry-run the `radxa-a733` `bookworm` desktop path and log the first failure or success.

## Notes

- Keep this checklist short.
- Add only what changes the next decision.

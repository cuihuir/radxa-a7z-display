# Validation Example: Radxa A7Z First HDMI Bring-up

This is a worked example, not a real lab result. It is based on the public board and release information already collected in this repository.

## Validation record

- Date: 2026-07-06
- Tester: Example record
- Board: Radxa Cubie A7Z
- Board revision: Unknown from public docs
- SoC: Allwinner A733
- Display path: Micro HDMI
- Image or build: Radxa public Debian desktop image line for A7Z
- Kernel version: BSP kernel from the selected image
- Desktop environment: Desktop session expected from the vendor image
- Storage media: microSD or eMMC, depending on the actual test setup
- Power source: Stable USB-C power supply

## Test goal

Prove that the simplest HDMI path on A7Z can boot far enough to reach a desktop session.

## Steps taken

1. Flash the selected Radxa A7Z image to the chosen storage media.
2. Connect a monitor to the Micro HDMI port.
3. Boot the board and wait for the desktop session to appear.

## Commands run

```bash
# Example only
dd if=radxa-a7z-image.img of=/dev/sdX bs=4M status=progress conv=fsync
```

## Observed result

- Boot result: Not executed in this example.
- HDMI result: Expected to be the first path to verify because it is the simplest hardware route.
- Desktop result: Not executed in this example.
- GPU acceleration result: Unknown until the real test is run.
- Input device result: Unknown until the real test is run.

## Evidence

- Logs: None in this example.
- Screenshots: None in this example.
- Photos: None in this example.
- Serial output: None in this example.

## Pass or fail

- Result: Not tested
- Why: This is a planning example, not an actual board run.

## Notes

- Radxa A7Z exposes a direct Micro HDMI path and USB-C DP Alt Mode, but Micro HDMI should be the first validation target.
- The public reference material in this repository suggests that Debian desktop support exists, but Bookworm-specific desktop readiness still needs real validation.

## Sources

- [Radxa A7Z documentation](https://docs.radxa.com/en/cubie/a7z)
- [Radxa A7Z downloads](https://docs.radxa.com/en/cubie/a7z/download)
- [Radxa A7Z repo](https://github.com/radxa-build/radxa-cubie-a7z)
- [A733 display landscape research](../research/a733-display-landscape.md)
- [Board comparison](../comparison/radxa-a7z-vs-orangepi-a733.md)


# A733 Serial Boot Recovery Validation

## Objective

Establish a reliable boot-failure boundary after repeated power-loss recovery,
initramfs experiments, and misleading SSH timeouts.

## Serial Setup

- Adapter: CH341/CH340, USB ID `1a86:7523`;
- host device: `/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0`;
- settings: `115200 8N1`, no flow control;
- board console: UART0, A7Z pin 8 TX to adapter RX, pin 10 RX to adapter TX,
  and pin 6 GND.

## Recovery

Offline `e2fsck -fy` repaired an ext4 orphan-list and allocation-bitmap
inconsistency caused by repeated unclean power removal. The boot configuration
was restored with `l1` as the default, the explicit vendor A7Z DTB, and
`module_blacklist=pvrsrvkm`.

The unverified 14 MB `MODULES=dep` initramfs was removed from the normal boot
path. The `l0` initramfs was restored byte-for-byte from the known bootable
backup:

```text
size=42251056
sha256=395d50f38d752d978d4070cf371e3ee4ec99e23e9ff45f1a6b1b79f5274d7574
```

## Serial Result

The saved UART log showed:

1. U-Boot loaded `/boot/extlinux/extlinux.conf`;
2. entry 1 selected `5.15.147-21.1-a733`;
3. U-Boot loaded the exact initramfs, kernel, and A7Z DTB;
4. the kernel started at approximately 15 seconds;
5. NetworkManager, WPA supplicant, SSH, and SDDM started;
6. the system reached `radxa-cubie-a7z login:` on `ttyAS0`.

SSH subsequently confirmed kernel `5.15.147-21.1-a733`, `default l0`, a healthy
systemd state, `wlan0` at `192.168.123.210`, loaded `pvrsrvkm`, DRM `card0`,
`card1`, and `renderD128`, and connected/enabled HDMI.

## Isolated Early-fsck Retest

An additional `fscktest` extlinux entry was appended without changing
`default l0`. UART input selected menu item 7 numerically. U-Boot loaded:

```text
/boot/initrd.img-5.15.147-21.1-a733.fsck-final-test
size=14701871
sha256=367883cd00c9b0781e3ba97767cd50a1ee19955033c94b247309383e0e41762c
```

The captured boot then showed the intended pre-mount check:

```text
Begin: Will now check root file system ... fsck from util-linux 2.38.1
[/sbin/fsck.ext4 (1) -- /dev/mmcblk0p3] fsck.ext4 -a -C0 /dev/mmcblk0p3
rootfs: clean, 199656/3786960 files, 2092429/15228411 blocks
```

The same boot continued through NetworkManager, SSH, SDDM, and the `ttyAS0`
login prompt. The raw capture is
`artifacts/serial/2026-07-21-fsck-final-isolated-boot.log` when local ignored
artifacts are retained.

## Reproducible Recovery Build

The repository recovery configuration and builder reproduced the result on the
board without modifying the normal `l0` initramfs:

```text
path=/boot/initrd.img-5.15.147-21.1-a733.a7z-recovery
size=14701537
sha256=5f536ec77e793cd4d79687eeb46279923b0df870d1db761191d76df4366fa1ce
```

The protected installer added `label a7z-recovery` while retaining
`default l0`. UART menu item 7 loaded this newly generated image, ran the same
pre-mount `fsck.ext4 -a` check, reached the login prompt, and restored Wi-Fi at
`192.168.123.210`. The generated-image capture is
`artifacts/serial/2026-07-21-generated-a7z-recovery-boot.log`.

The host-side regular-file test also introduced a block-group descriptor
inconsistency, observed `e2fsck -p` status `1`, and verified status `0` on the
read-only follow-up check. This validates automatic repair behavior without
touching the live SD card, but does not replace a future spare-media boot test.

## Spare-media Repair Boot

A smaller 58.2 GiB spare card was created from the running system by preserving
the boot prefix and FAT partitions, rebuilding a reduced ext4 root partition,
and restoring the root filesystem by file. Its first normal `l0` boot reached
the login prompt with Wi-Fi working.

With the spare card offline, block group 0's free-block count was changed with
`debugfs`. A read-only `e2fsck -fn` returned status `4` and reported both an
invalid group-descriptor checksum and an incorrect free-block count. No repair
was performed on the host.

The normal `l0` path then failed to mount root and entered initramfs. On the
next power cycle, UART selected `a7z-recovery`. The recovery initramfs reported:

```text
rootfs: One or more block group descriptor checksums are invalid.  FIXED.
rootfs: Group descriptor 0 checksum is 0x99ce, should be 0x54c2.  FIXED.
fsck exited with status code 1
```

It continued booting to the `ttyAS0` login prompt. SSH confirmed systemd was
running, Wi-Fi was restored at `192.168.123.210`, `default l0` remained
unchanged, and `tune2fs` reported the root filesystem state as `clean`. The
UART evidence is
`artifacts/serial/2026-07-21-spare-sd-fault-recovery-prearmed.log`.

## Final Release Image

On July 22, 2026 the release source was rebuilt as a compact 12 GiB GPT image.
The normal initramfs was reduced to 19,768,890 bytes by excluding unused
AMD/NVIDIA PCI GPU modules and firmware; two consecutive normal reboots passed.
The image was sanitized, compressed to XZ, written back to the spare SD card,
and reached the serial login prompt using `radxa/radxa`. First boot generated a
new machine ID. A dedicated systemd unit was then hardware-tested to generate
unique SSH host keys before starting SSH, eliminating the sanitized-image SSH
failure without publishing shared keys.

## Conclusion

The exact historical `l0` initramfs remains bootable in this captured test.
Earlier incidents also included confirmed filesystem and boot-entry damage, so
their causes cannot be reduced to SSH timing. Future early-boot conclusions
must use UART evidence. The experimental early-fsck image is now proven to boot
and to check a clean root filesystem before mounting it. It remains a
recovery-only path that has now repaired a reproducible ext4 metadata fault on
spare media and continued to a complete boot. Offline fsck remains the fallback
for errors that automatic `e2fsck -a` cannot repair.

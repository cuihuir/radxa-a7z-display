# Radxa A7Z Serial Console

Use the serial console to diagnose boot, HDMI, or network failures before
changing an image. It is the reliable recovery path when the display is
unusable or Wi-Fi is unavailable.

## What You Need

- A 3.3 V TTL USB-to-UART adapter (CP2102, CH340, or FTDI type).
- Three female-to-female Dupont wires.
- The A7Z powered normally through USB-C.

Do not use an RS-232 adapter: its voltage levels can damage the board. Do not
connect the adapter VCC, 3.3 V, or 5 V pin to the A7Z. Only TX, RX, and GND are
needed.

## Header Location And Wiring

The debug console is UART0 on the A7Z 40-pin GPIO header (GPIO interface #12
in the official board documentation). With the standard 40-pin physical pin
numbering:

| A7Z physical pin | A733 signal | Connect to USB-UART adapter |
| --- | --- | --- |
| 8 | PB9 / UART0-TX | RX |
| 10 | PB10 / UART0-RX | TX |
| 6 | GND | GND |

TX and RX must be crossed. Pin 6 is a convenient ground; pins 9, 14, 20, 25,
30, 34, and 39 are also ground pins.

## Terminal Settings

Use `115200 8N1`, with flow control disabled. Start the terminal before
applying power or rebooting the board, so that U-Boot and early kernel messages
are captured.

On a Linux host, first find the adapter:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

The adapter validated on July 21, 2026 is a CH341/CH340 device with USB ID
`1a86:7523`. It appears as:

```text
/dev/ttyUSB0
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
```

The stable `/dev/serial/by-id/` path is preferable in scripts. On systems
where the device is owned by `root:dialout`, add the user to `dialout` and
start a new login session:

```bash
sudo usermod -aG dialout "$USER"
```

Then open it, for example:

```bash
picocom -b 115200 /dev/ttyUSB0
```

Or:

```bash
screen /dev/ttyUSB0 115200
```

For a read-only capture that does not transmit characters to the board:

```bash
stty -F /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 \
  115200 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 120 cat /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 \
  | tee a7z-serial-boot.log
```

The verified image configures the kernel console as `console=ttyAS0,115200n8`, with
`earlyprintk=sunxi-uart,0x02500000`. A successful boot should therefore print
bootloader output followed by kernel messages and eventually a login prompt.

The July 21 validation captured a clean shutdown, the following `l1` boot,
systemd startup, Wi-Fi initialization, SDDM startup, and the final prompt:

```text
Debian GNU/Linux 12 radxa-cubie-a7z ttyAS0
radxa-cubie-a7z login:
```

## Current Recovery Use

For the current Debian 12 image investigation, serial output separates these
otherwise ambiguous failures:

- The SD image does not boot versus the small HDMI panel not displaying it.
- The board boots from a different device instead of the SD card.
- A custom kernel starts but the AIC8800 Wi-Fi DKMS module fails to load.
- The system reaches a login prompt while HDMI mode selection is incorrect.

Capture the complete log from power-on to the login prompt. Do not paste
credentials or Wi-Fi secrets. The most useful parts are the boot source,
kernel command line, root filesystem mount, DRM/HDMI lines, and Wi-Fi/DKMS
errors.

## Optional Early-fsck Recovery Entry

The normal `l0` initramfs intentionally remains on the verified `display3`
policy. Build a separate recovery image on the A7Z instead of changing the
normal image:

```bash
sudo ./tools/build_a733_recovery_initramfs.sh \
  5.15.147-21.1-a733 \
  /boot/initrd.img-5.15.147-21.1-a733.a7z-recovery.new
sudo ./tools/install_a733_recovery_entry.sh \
  5.15.147-21.1-a733 \
  /boot/initrd.img-5.15.147-21.1-a733.a7z-recovery.new
```

The installer adds `a7z-recovery`, keeps the existing default entry unchanged,
and writes a timestamped extlinux backup. Select the recovery item numerically
from the UART U-Boot menu. It uses verbose kernel output and checks ext4 before
the root filesystem is mounted.

Validate the repair policy without a block device or mounted filesystem:

```bash
./tools/test_a733_recovery_fsck.sh
```

The test creates a disposable regular-file ext4 image, introduces a block-group
descriptor inconsistency, requires `e2fsck -p` status `1`, then requires a clean
read-only follow-up check. It never touches the active SD card.

## Evidence And Sources

- Official GPIO pin table: <https://docs.radxa.com/en/cubie/a7z/hardware-use/pin-gpio>
- Official A7Z board page: <https://docs.radxa.com/en/cubie/a7z>
- A733 device configuration: `radxa/device-a733` `configs/cubie_a7z/sys_config.fex`
  specifies `uart_debug_port = 0`, `PB09` as TX, and `PB10` as RX.
- A733 boot environment: `radxa/device-a733` `configs/cubie_a7z/debian/env.cfg`
  specifies `console=ttyS0,115200`.

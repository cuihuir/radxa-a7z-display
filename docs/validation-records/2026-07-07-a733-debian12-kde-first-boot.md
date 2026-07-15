# 2026-07-07 A733 Debian 12 KDE First Boot Validation

> Historical first-boot record. Its `llvmpipe` GPU result was superseded by
> the 2026-07-14 PowerVR activation. See the generated
> [current status](../status.md).

## Validation Record

- Date: 2026-07-07
- Tester: tope, with Codex remote inspection over SSH
- Board: Radxa Cubie A7Z / A733 class board
- Board revision: not recorded
- SoC: Allwinner A733
- Display path: HDMI-A-1
- Image or build: local RSDK `radxa-a733 bookworm kde`
- Kernel version: `5.15.147-21-a733`
- Desktop environment: KDE Plasma 5.27.5, Wayland session, SDDM
- Storage media: SD card, rootfs on `mmcblk0p3`
- Power source: not recorded

## Test Goal

Prove that the locally built Debian 12 Bookworm KDE image can boot on the A733 board and show a working HDMI desktop.

## Steps Taken

1. Built the image with local RSDK patches and local A733 kernel/U-Boot `.deb` cache.
2. Flashed `sources/rsdk/out/radxa-a733_bookworm_kde/output.img` to an SD card.
3. Booted the board from the SD card.
4. Logged into KDE with `radxa` / `radxa`.
5. Enabled SSH and inspected the board remotely at `192.168.123.210`.
6. Captured screenshots from the live Plasma Wayland session with Spectacle.

## Commands Run

```bash
ssh radxa@192.168.123.210
```

Remote inspection commands included:

```bash
hostname
id
uname -a
cat /etc/os-release
loginctl show-user radxa -p Display -p State -p Sessions
systemctl is-active sddm NetworkManager bluetooth ssh
systemctl --failed --no-pager
ps -eo pid,user,comm,args | grep -E 'sddm|Xorg|kwin|plasmashell|wayland|weston'
ls -l /dev/dri
cat /sys/class/drm/card0-HDMI-A-1/status
cat /sys/class/drm/card0-HDMI-A-1/modes
DISPLAY=:1 XAUTHORITY=/run/user/1000/xauth_IlLwEl xrandr --query
glxinfo -B
vulkaninfo --summary
wpctl status
aplay -l
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev status
df -h /
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS
```

Screenshot command pattern:

```bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export QT_QPA_PLATFORM=wayland
spectacle -b -n -o /home/radxa/a733-validation/debian12-kde-hdmi-01.png
```

## Observed Result

- Boot result: pass. The board booted from SD.
- HDMI result: pass. HDMI-A-1 was connected and the desktop was visible at 1920x1080.
- Desktop result: pass. SDDM and KDE Plasma Wayland started.
- SSH result: pass. SSH login worked with `radxa` / `radxa`.
- Network result: pass for Wi-Fi. `wlan0` was connected to `AI3D-5G` and had `192.168.123.210/24`.
- Input device result: pass. USB keyboard/mouse devices were detected in kernel logs and usable from the GUI.
- Storage result: pass. Root filesystem expanded to the SD card; `/dev/mmcblk0p3` was mounted as `/` with about 58 GiB available.
- Audio result: partial. PipeWire and ALSA showed a built-in audio sink and HDMI ALSA device, but playback was not tested.
- Bluetooth result: partial. `bluetooth` service was active and a controller was visible, but pairing/audio profiles were not tested.
- GPU acceleration result: fail/unknown. `glxinfo` and KDE Info Center reported `llvmpipe`; no accelerated renderer was proven.

## Evidence

- Screenshots:
  - `docs/assets/a733-debian12-first-boot/debian12-kde-hdmi-01.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-system-info.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-display-settings.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-terminal-validation.png`
- Kernel:
  - `Linux radxa-cubie-a7z 5.15.147-21-a733 #21 SMP PREEMPT Thu Apr 30 12:14:04 UTC 2026 aarch64 GNU/Linux`
- OS:
  - `Debian GNU/Linux 12 (bookworm)`
- Display:
  - `/sys/class/drm/card0-HDMI-A-1/status`: `connected`
  - Xwayland visible mode: `1920x1080 59.96`
- Services:
  - `sddm`: active
  - `NetworkManager`: active
  - `bluetooth`: active
  - `ssh`: active
  - failed system units: none

## Known Defects And Risks

- Graphics acceleration was not working or exposed through Mesa in this image;
  the renderer observed during this validation was `llvmpipe`.
- `/dev/dri` only showed `card0`; no `renderD*` node was present during validation.
- `xdg-desktop-portal` and `xdg-desktop-portal-kde` were inactive in the user session, and PipeWire logged portal warnings.
- Vendor kernel logs include a debug-kernel notice: `trace_printk() being used`.
- GPU power-domain probe messages appeared, including `pd_gpu_top_test` and `pd_gpu_core_test` timeout/failure lines.
- HDMI works, but logs include repeated `sunxi-hdmi` mode/audio messages and `tcon clock rate is 0`.
- Audio is enumerated but untested; logs include sound-machine warnings.
- Bluetooth is enumerated but untested; logs include some BlueZ profile registration warnings.
- `rfkill` is not installed.
- `kscreen-doctor -o` aborted during one SSH-launched check, although the KDE Display Settings UI worked.
- Board revision and power supply details were not recorded.

## Pass Or Fail

- Result: pass for the primary goal.
- Why: The built Debian 12 image boots on the A733 board and reaches a usable HDMI KDE desktop.
- Remaining work: GPU acceleration, audio validation, Bluetooth validation, portal service cleanup, and kernel warning triage.

## Notes

- This is the first confirmed end-to-end success for the project: local image build, SD boot, HDMI display, SDDM, KDE Plasma, SSH inspection, and screenshot capture.
- The default login observed on this image is `radxa` / `radxa`.

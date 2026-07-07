# 2026-07-07 A733 Debian 12 KDE 首次启动验证

## 验证记录

- 日期：2026-07-07
- 测试人：tope，Codex 通过 SSH 远程检查
- 板卡：Radxa Cubie A7Z / A733 类板卡
- 板卡版本：未记录
- SoC：Allwinner A733
- 显示路径：HDMI-A-1
- 镜像或构建：本地 RSDK `radxa-a733 bookworm kde`
- 内核版本：`5.15.147-21-a733`
- 桌面环境：KDE Plasma 5.27.5，Wayland 会话，SDDM
- 存储介质：SD 卡，rootfs 位于 `mmcblk0p3`
- 供电方式：未记录

## 测试目标

证明本地构建出来的 Debian 12 Bookworm KDE 镜像可以在 A733 板子上启动，并显示可用的 HDMI 桌面。

## 执行步骤

1. 使用本地 RSDK patch 和 A733 kernel/U-Boot 本地 `.deb` 缓存构建镜像。
2. 将 `sources/rsdk/out/radxa-a733_bookworm_kde/output.img` 写入 SD 卡。
3. 从 SD 卡启动板子。
4. 使用 `radxa` / `radxa` 登录 KDE。
5. 开启 SSH，并通过 `192.168.123.210` 远程检查。
6. 使用 Spectacle 从实际 Plasma Wayland 会话中截图。

## 实际命令

```bash
ssh radxa@192.168.123.210
```

远程检查命令包括：

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

截图命令模式：

```bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export QT_QPA_PLATFORM=wayland
spectacle -b -n -o /home/radxa/a733-validation/debian12-kde-hdmi-01.png
```

## 观察结果

- 启动结果：通过。板子可以从 SD 卡启动。
- HDMI 结果：通过。HDMI-A-1 已连接，桌面以 1920x1080 显示。
- 桌面结果：通过。SDDM 和 KDE Plasma Wayland 已启动。
- SSH 结果：通过。可以用 `radxa` / `radxa` 登录。
- 网络结果：Wi-Fi 通过。`wlan0` 已连接到 `AI3D-5G`，地址为 `192.168.123.210/24`。
- 输入设备结果：通过。内核日志中可以看到 USB 键鼠设备，GUI 中可用。
- 存储结果：通过。rootfs 已扩展到 SD 卡，`/dev/mmcblk0p3` 挂载为 `/`，约 58 GiB。
- 音频结果：部分通过。PipeWire 和 ALSA 能看到内置音频 sink 和 HDMI ALSA 设备，但尚未播放测试。
- 蓝牙结果：部分通过。`bluetooth` 服务 active，能看到控制器，但尚未配对/音频测试。
- GPU 加速结果：失败/未知。`glxinfo` 和 KDE Info Center 显示 `llvmpipe`，尚未证明硬件加速可用。

## 证据

- 截图：
  - `docs/assets/a733-debian12-first-boot/debian12-kde-hdmi-01.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-system-info.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-display-settings.png`
  - `docs/assets/a733-debian12-first-boot/debian12-kde-terminal-validation.png`
- 内核：
  - `Linux radxa-cubie-a7z 5.15.147-21-a733 #21 SMP PREEMPT Thu Apr 30 12:14:04 UTC 2026 aarch64 GNU/Linux`
- 系统：
  - `Debian GNU/Linux 12 (bookworm)`
- 显示：
  - `/sys/class/drm/card0-HDMI-A-1/status`: `connected`
  - Xwayland 可见模式：`1920x1080 59.96`
- 服务：
  - `sddm`: active
  - `NetworkManager`: active
  - `bluetooth`: active
  - `ssh`: active
  - failed system units：无

## 已知缺陷与风险

- 图形加速没有工作，或没有通过 Mesa 暴露出来。当前 renderer 是 `llvmpipe`。
- `/dev/dri` 只看到 `card0`，本次验证中没有看到 `renderD*` 节点。
- 用户会话中 `xdg-desktop-portal` 和 `xdg-desktop-portal-kde` 是 inactive，PipeWire 有 portal warning。
- vendor kernel 日志中有 debug-kernel 提示：`trace_printk() being used`。
- GPU power-domain 有 probe timeout/failure 信息，包括 `pd_gpu_top_test` 和 `pd_gpu_core_test`。
- HDMI 可用，但日志里有重复的 `sunxi-hdmi` mode/audio 信息，以及 `tcon clock rate is 0`。
- 音频已枚举但未实测；日志中有 sound-machine warning。
- 蓝牙已枚举但未实测；日志中有部分 BlueZ profile warning。
- `rfkill` 未安装。
- 一次通过 SSH 启动的 `kscreen-doctor -o` 发生 abort，但 KDE Display Settings 图形界面可用。
- 板卡版本和供电方式尚未记录。

## 通过或失败

- 结果：核心目标通过。
- 原因：构建出来的 Debian 12 镜像可以在 A733 板子上启动，并进入可用的 HDMI KDE 桌面。
- 剩余工作：GPU 加速、音频验证、蓝牙验证、portal 服务清理、kernel warning 梳理。

## 备注

- 这是本项目第一次确认的端到端成功：本地构建、SD 启动、HDMI 显示、SDDM、KDE Plasma、SSH 检查和截图取证。
- 本镜像观察到的默认登录是 `radxa` / `radxa`。

# A7Z Debian 12 构建与启动记录

## 在哪里构建

镜像应该在主机上构建，不是在 A7Z 板子上构建。

A7Z 只用于刷写和启动验证。RSDK 会在主机侧使用 Debian 仓库、`qemu-user-static`、chroot 和镜像组装工具来生成 rootfs 和磁盘镜像。

## 推荐构建环境

使用以下之一：

- Debian 12 主机或虚拟机。
- Ubuntu 22.04/24.04 主机或虚拟机。
- 本地工作站上的特权 Debian 12 容器或 devcontainer。
- 本地已有的 `debian12` distrobox，可用于元数据检查和 dry run。

当前工作站有 `dnf`、`podman` 和 `distrobox`。RSDK 的 native setup 只处理 Debian/Ubuntu 的 `apt` 环境，所以不要直接在当前宿主系统上构建，除非先进入 Debian/Ubuntu 容器或虚拟机。

## 当前本地源码状态

本地 `sources/rsdk` 已经改成：

- `radxa-a733` 默认 suite 是 `bookworm`。
- `radxa-a733` 仍然默认使用 `kde` 桌面。
- Allwinner 的 `soc_install_recommends` 已加入 `bookworm`。
- RSDK Jsonnet 避开了 Debian 12 `jsonnet 0.18.0` 不支持的新标准库调用。

同样的改动已经保存为：

```bash
patches/rsdk/0001-enable-bookworm-on-radxa-a733.patch
patches/rsdk/0002-jsonnet-0.18-compat.patch
```

## 第一次 dry run

在仓库根目录运行：

```bash
sources/rsdk/src/bin/rsdk build --dry-run radxa-a733
```

预期能看到：

```text
Building radxa-a733 bookworm kde...
```

这说明 A733 的 Debian 12 默认路径已经生效。

## 主机依赖准备

在 Debian/Ubuntu 构建环境里，先初始化子模块：

```bash
cd sources/rsdk
git submodule update --recursive --init
```

然后执行 RSDK setup：

```bash
src/bin/rsdk setup
```

如果手动安装依赖，核心依赖大致是：

```bash
sudo apt-get update
sudo dpkg --add-architecture arm64
sudo apt-get install -y \
  bash-completion \
  bdebstrap \
  binfmt-support \
  qemu-user-static \
  debian-archive-keyring \
  debian-ports-archive-keyring \
  jsonnet \
  jq \
  gpg \
  libfakechroot:arm64 \
  libfakeroot:arm64
```

对于本地已有的 distrobox：

```bash
distrobox enter debian12 -- bash -lc '
  cd /home/tope/project/buildroot_a733/sources/rsdk
  sudo apt-get update
  sudo dpkg --add-architecture arm64
  sudo apt-get update
  sudo apt-get install -y \
    bash-completion \
    bdebstrap \
    binfmt-support \
    qemu-user-static \
    debian-archive-keyring \
    debian-ports-archive-keyring \
    jsonnet \
    jq \
    gpg \
    libfakechroot:arm64 \
    libfakeroot:arm64
'
```

已知 distrobox 限制：

- 当前非特权 distrobox 不能写 `/proc/sys/fs/binfmt_misc`，因此无法启用 `qemu-aarch64` binfmt。
- dry run 可以跑通。
- 当前真实镜像构建会失败，直到宿主机提供 `qemu-aarch64` binfmt handler。

当前 distrobox 中真实构建的实测失败：

```text
E: arm64 can neither be executed natively nor via qemu user emulation with binfmt_misc
2026-07-07 02:21:08,663 bdebstrap ERROR: mmdebstrap failed with exit code 25. See above for details.
```

宿主机已经启用 `binfmt_misc`，但没有 `qemu-aarch64` handler。当前 Fedora/RPM 宿主可用的包名包括：

```bash
sudo dnf install -y qemu-user-static-aarch64 qemu-user-binfmt
```

安装后验证：

```bash
cat /proc/sys/fs/binfmt_misc/status
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
```

然后回到 distrobox 里重试构建。

## 构建命令

进入 Debian/Ubuntu 构建环境后：

```bash
cd /path/to/buildroot_a733/sources/rsdk
src/bin/rsdk build radxa-a733
```

因为本地产品元数据已经把 `bookworm` 放在第一位，这条命令等价于：

```bash
src/bin/rsdk build radxa-a733 bookworm kde
```

预期输出目录是：

```text
sources/rsdk/out/radxa-a733_bookworm_kde/
```

## 刷写与启动

构建成功后，在下面目录找生成的镜像：

```bash
ls sources/rsdk/out/radxa-a733_bookworm_kde/
```

把生成的镜像刷到 microSD 或 eMMC。实际镜像名以 RSDK 输出为准，写盘前必须确认目标磁盘：

```bash
sudo dd if=<generated-image>.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
sync
```

上电前：

- 先接 Micro HDMI。
- 接键盘和鼠标。
- 使用稳定的 USB-C 电源。
- 如果有串口，优先接串口。

首次启动检查：

- 是否进入 U-Boot / kernel。
- Micro HDMI 是否有信号。
- Debian 12 是否启动。
- KDE 或显示管理器/桌面会话是否启动。
- 如果桌面失败，优先保存串口日志，必要时从目标 rootfs 里取 `journalctl`。

## 当前已知阻塞点

RPM 宿主环境 dry run 已经到达：

```text
Building radxa-a733 bookworm kde...
```

然后因为宿主系统缺少 `jsonnet` 停止。当前宿主是 `dnf` 环境，这个问题应通过 Debian/Ubuntu 构建环境解决。

本地 Debian 12 distrobox 现在可以完成：

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --dry-run radxa-a733'
```

实测结果：

```text
Building radxa-a733 bookworm kde...
Dry run enabled. You can find generated files under '/tmp/rsdk.radxa-a733_bookworm_kde.Fwajs51g'.
```

下一处阻塞点是宿主机层面的 `qemu-aarch64` binfmt 注册。当前会话里 `sudo` 需要密码，所以不能自动安装。

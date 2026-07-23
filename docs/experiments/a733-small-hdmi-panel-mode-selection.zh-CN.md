# A733 HDMI 小屏模式选择

日期：2026-07-14

## 结果

已在运行 Debian 12 KDE 的 Radxa Cubie A7Z 和 `FLY-HDMI-LCD7` 小屏上完成验证。
HDMI 现在实际选择并输出 `1024x600@60Hz`，完整桌面正常显示，无拉伸和裁切。

```text
HDMI-A-1: Configuration mode 1024x600@60Hz
sunxi-hdmi: drm hdmi mode set: 1024*600
```

开发板从补丁内核 `5.15.147-21.1-a733` 启动；重建 DKMS 模块后，Wi-Fi 保持可用。

## 根因

该屏幕的 EDID 基础块包含 `1024x600` 的详细时序，但同时声明了最高
`1920x1080` 的常见 CEA 模式。A733 BSP 配置
`configs/linux-5.15/sun60iw2p1.dtsi` 为 DRM 同时启用了：

```text
quirk-prefer-fhd;
quirk-prefer-large-60;
```

厂商 EDID 代码清除了原生时序的 preferred 标志，并选择不超过 Full HD 的最大模式，
最终输出 `1920x1080@60Hz`，导致小屏桌面拉伸、裁切。其 mode-monitor 路径也只选择
mode list 的第一项，而不读取 DRM 的 preferred 标志。

## 修复

`patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch`：

- 移除 A733 全局的强制 FHD 和最大 60Hz EDID 策略；
- 在三个厂商 DRM 连接路径中优先选择 `DRM_MODE_TYPE_PREFERRED`，没有 preferred
  模式时才回退到第一项。

修复完全依据 EDID，不硬编码屏幕名称或分辨率。普通显示器会继续使用其有效 EDID
preferred 时序。

## 构建

`linux-a733` 会在 `pre_build` 时将 `bsp/configs/linux-5.15/*.dtsi` 复制进内核树。
必须向 `bsp` submodule 打补丁，不能只修改生成的 `src/` 副本：

```bash
git clone --recurse-submodules https://github.com/radxa-pkg/linux-a733.git
cd linux-a733
git -C bsp apply /path/to/radxa-a7z-debian12/patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch
make deb
```

本 RSDK 构建的 `.github/local/Makefile.local` 必须设置：

```make
KBUILD_IMAGE=arch/arm64/boot/Image
```

打包后的 `/boot/vmlinuz-*` 必须是未压缩的 `Image`。若为 `Image.gz`，U-Boot 无法加载，
会静默回退到厂商内核。

```bash
dpkg-deb --fsys-tarfile linux-image-*.deb \
  | tar xOf - ./boot/vmlinuz-5.15.147-21.1-a733 | file -
```

预期输出包含 `Linux kernel ARM64 boot executable Image`。

## 安装与验证

将厂商内核保留为 extlinux 的 `l1` 回退项。覆盖安装同版本 image 包会删除 DKMS 模块，
因此切换到 `l0` 前必须重建：

```bash
sudo dpkg -i linux-image-5.15.147-21.1-a733_*.deb
sudo dkms install --force -m aic8800-usb -v 5.0+git20260123.5f7be68d-6 \
  -k 5.15.147-21.1-a733
sudo dkms install --force -m radxa-overlays -v 0.2.25 \
  -k 5.15.147-21.1-a733
sudo sed -i 's/^default l1$/default l0/' /boot/extlinux/extlinux.conf
sudo reboot
```

重启后检查：

```bash
uname -r
sudo journalctl -b -k --no-pager | grep -E 'Configuration mode|drm hdmi mode set'
```

预期结果：

```text
5.15.147-21.1-a733
HDMI-A-1: Configuration mode 1024x600@60Hz
sunxi-hdmi: drm hdmi mode set: 1024*600
```

## 已验证事实

- `video=HDMI-A-1:1024x600@60` 被厂商早期 HDMI 路径忽略。
- `fb0` 的 `1024x1200` 是双缓冲虚拟高度，物理 HDMI 模式仍为 `1024x600`。
- 若无法启动，可离线将 `/boot/extlinux/extlinux.conf` 的默认项改回 `default l1` 后重启。

## 完整内核包失败与修复

第一次完整内核包尝试包含两个独立问题：

1. 安装输出中断后，在第一个 DKMS 仍运行时又启动了第二次 DKMS。并发写入损坏了
   ext4 目录元数据，最终通过离线 `e2fsck -fy` 修复。以后部署必须使用带锁的单个前台
   `dpkg` 进程，不能因为 SSH 暂时没有输出就再次启动 DKMS。
2. 重新生成的 `5.15.147-21.1` initramfs 为 42,672,314 字节，在产生持久化 journal
   之前启动失败。相同自定义 kernel 使用厂商 initramfs 可以启动；去掉 fsck hook 的临时
   initramfs 为 42,251,056 字节，也可以启动。证据指向 A733 U-Boot 或早期加载内存限制，
   而不是 kernel 或压缩包损坏。

`config/initramfs-tools/hooks/zz-a7z-skip-early-fsck` 从生成的 initramfs 中移除 fsck
程序及仅供 ext2fs 使用的库，不会删除 Debian 根文件系统中的修复工具。最终
`5.15.147-21.1+display2` 包生成 42,251,173 字节的 initramfs，并已通过标准 `l0`
启动。

最终板端证据：

```text
Linux 5.15.147-21.1-a733
Package version: 5.15.147-21.1+display2
wlan0: 192.168.123.210/24
HDMI-A-1: Configuration mode 1024x600@60Hz
drm hdmi mode set: 1024*600
```

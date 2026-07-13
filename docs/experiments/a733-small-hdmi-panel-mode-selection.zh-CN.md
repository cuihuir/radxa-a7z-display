# A733 HDMI 小屏模式选择

日期：2026-07-13

## 目标

让 A733 在 HDMI 小屏的 EDID 同时声明低分辨率详细时序和常见 CEA 电视模式时，选择屏幕原生模式。

## 板端结果

测试屏幕识别为 `FLY-HDMI-LCD7`。厂商 HDMI 诊断接口列出了三个 `1024x600p` 详细时序，同时也列出了包括 VIC 5 在内的 CEA SVD 模式。

运行中的 `5.15.147-21-a733` 内核却选择了 VIC 5：

```text
HDMI-A-1: Configuration mode 1920x1080@60Hz
sunxi hdmi select vic 5 use hdmi14 vsif
[dw video] ... vic | 005 | 1920x540 i | 60
```

因此小屏只能显示 1080 输出的一部分。

## 已否定的用户态方案

我们测试了标准 DRM command-line 覆盖：

```text
video=HDMI-A-1:1024x600@60
```

`u-boot-update` 已正确把它写入 `/boot/extlinux/extlinux.conf`，重启后 `/proc/cmdline` 也能看到该参数。但厂商 `sunxi-hdmi` 驱动仍然选择 1080，说明该 BSP 的早期 HDMI mode selection 不遵守标准 DRM override。测试结束后已删除这个覆盖参数。

## 根因

`radxa/allwinner-bsp` 的 `drivers/drm/sunxi_drm_drv.c` 在初始连接和热插拔处理时，使用 `list_first_entry_or_null()` 选择 connector mode，没有检查 `DRM_MODE_TYPE_PREFERRED`。

对于这块屏，mode 列表第一项是 CEA 1080i，而 DRM EDID 解析器标记为 preferred 的原生 DTD 是 `1024x600`。所以这是 BSP mode priority bug，不是 KDE 缩放问题，也不是屏幕没有提供原生模式。

## 补丁

`patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch` 添加 `sunxi_drm_pick_preferred_mode()`，并替换三处 first-mode fallback：

- HDMI 热插拔 mode monitor。
- 板级 boot display-info fallback。
- 没有 bootloader display-info 时的 fallback。

该 helper 优先选择 `DRM_MODE_TYPE_PREFERRED`，当没有 preferred mode 时保留原本的首项 fallback 行为。

## 构建与测试

从匹配的 Radxa 打包仓库及 submodule 构建：

```bash
git clone --recurse-submodules https://github.com/radxa-pkg/linux-a733.git
cd linux-a733
git -C bsp apply /path/to/radxa-a7z-display/patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch
make deb
```

A733 RSDK 镜像的启动路径必须把重建的 kernel 放入厂商 `boot.img`。仅安装生成的 Debian 包并不充分：在已测试镜像中，即使 `u-boot-update` 已在 `/boot/extlinux/extlinux.conf` 选择新包，U-Boot 重启后仍会加载原有 boot image 内的 kernel。

应使用带补丁 BSP kernel 重建完整 RSDK 镜像，烧录后接好小屏启动，再检查：

```bash
sudo dmesg | grep -E 'Configuration mode|drm hdmi mode set'
cat /sys/class/drm/card0-HDMI-A-1/modes
```

成功标准：

- `FLY-HDMI-LCD7` 能显示完整桌面。
- HDMI 实际选择 `1024x600`，而不是 VIC 5 / `1920x540i`。
- 普通 1080p 显示器仍然选择其 EDID preferred mode。

## 状态

补丁已确认可应用到 `linux-a733` release `5.15.147-21` 使用的 `cubie-aiot-v1.4.6` BSP 源码，并已编译为独立 ABI 包 `5.15.147-21.1-a733`。该包及匹配的 DKMS Wi-Fi 模块已成功安装到板子，但它没有成为运行内核：重启后板子仍报告 `5.15.147-21-a733`。因此下一份验证产物必须是带补丁的 RSDK 完整镜像，而不是单独的 Debian kernel 包。

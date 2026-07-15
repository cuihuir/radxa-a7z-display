# 2026-07-14 A733 PowerVR GPU 第一版激活验证

## 环境

- 板卡：Radxa Cubie A7z，A733；
- 系统：Debian 12 Bookworm KDE Plasma Wayland；
- 内核：`5.15.147-21.1-a733`，包版本 `5.15.147-21.1+display2`；
- GPU 包：`a733-pvr-gpu 24.2.6603887+gpu4`；
- DDK/BVNC：`24.2@6603887` / `36.56.104.183`。

## 结果

重启后 `pvrsrvkm` 自动加载，内核从硬件寄存器读出 BVNC
`36.56.104.183`，DRM 初始化为 `pvr 24.2.6603887`。固件
`rgx.fw.36.56.104.183` 和 shader `rgx.sh.36.56.104.183` 均成功加载。

设备节点从原来的单一 `card0` 变为：

```text
/dev/dri/card0
/dev/dri/card1
/dev/dri/renderD128
```

API 验证：

| 项目 | 实机结果 |
| --- | --- |
| Vulkan | `PowerVR B-Series BXM-4-64 MC1`，驱动 `24.2@6603887`，通过 |
| OpenCL | OpenCL 3.0，`PowerVR B-Series BXM-4-64`，通过 |
| EGL/GBM | `sunxi-drm` 和 `pvr` 驱动均可初始化，通过 |
| KWin | OpenGL ES 3.2，renderer 为 `PowerVR B-Series BXM-4-64`，通过 |
| Plasma Wayland | `kwin_wayland`、Xwayland、`plasmashell` 持续运行，通过 |

KWin 进程实际映射了厂商 `libGLESv2_PVR_MESA`、`sunxi-drm_dri.so`、
`libsrv_um`、shader compiler 和 USC 库，不再是 llvmpipe。

## 桌面适配

新增 PVR DRM 设备后，系统 Xorg 会把无显示输出的 `card1` 也纳入自动探测，
导致 SDDM greeter 无可用 screen。最终配置把系统 modesetting 驱动固定到
`/dev/dri/card0`。

Debian 的 `/usr/bin/kwin_wayland` 带 `cap_sys_resource=ep`，动态链接器处于
secure-exec 模式并忽略 `LD_LIBRARY_PATH`。GPU 包因此生成无 capability 的
同版本 KWin 副本，并通过 PATH 使用它。`KWIN_DRM_DEVICES=/dev/dri/card0`
保证 KWin 用 HDMI KMS 扫描输出，同时通过 `sunxi-drm` DRI 使用 PowerVR 渲染。

## 回归检查

- SDDM greeter 正常启动；
- HDMI 仍为 `1024x600@60Hz`；
- AIC8800 Wi-Fi 正常，地址仍为 `192.168.123.210`；
- extlinux 默认项为 `l0`，恢复项 `l1` 保留；
- initramfs 保持 `42,251,173` 字节，GPU 模块不进入早期启动镜像；
- 临时自动登录配置已删除，恢复手动登录行为。

## 已知事项

- 外部模块会 taint 内核；
- DTS 未提供默认 GPU clock rate，驱动回退到 `600 MHz`；
- BSP 仍有既有的 GPU power-domain test timeout、pinctrl、存储和显示 warning；
- KWin 影子副本必须在发行版 KWin 升级后由 GPU 包重新执行 `enable` 刷新。


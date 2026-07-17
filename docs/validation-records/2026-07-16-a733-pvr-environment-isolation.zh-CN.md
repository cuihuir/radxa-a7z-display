# A733 PowerVR 桌面环境隔离验证

## 范围

本记录验证 Radxa Cubie A7Z 实机上的
`a733-pvr-gpu 24.2.6603887+gpu6`。目标是在 KWin 继续使用 PowerVR 的同时，
不再让普通 Qt Wayland 客户端、KScreenLocker 和 XWayland 继承厂商库环境。

## 实现

- 删除全局 `/etc/environment.d/90-a733-pvr.conf` 和
  `/etc/profile.d/a733-pvr.sh` 导出；
- 只在 KWin 启动器中设置 PowerVR `LD_LIBRARY_PATH`、
  `LIBGL_DRIVERS_PATH` 和 `KWIN_DRM_DEVICES`；
- 使用属于 GPU 包的 `dpkg-divert` wrapper，以清洁环境启动
  `kscreenlocker_greet`；
- 增加清洁环境的 XWayland wrapper；
- Vulkan 和 OpenCL 继续通过 `a733-pvr-run` 显式选择厂商栈。

## 实机结果

| 检查项 | 结果 |
|---|---|
| 内核 | `5.15.147-21.1-a733` |
| GPU 包 | `24.2.6603887+gpu6` |
| HDMI | `card0-HDMI-A-1` 已连接 |
| KWin renderer | `PowerVR B-Series BXM-4-64`，OpenGL ES 3.2 |
| KWin DRM 节点 | 已打开 `card0` 和 `renderD128` |
| Vulkan | PowerVR B-Series Vulkan Driver `24.2@6603887` |
| OpenCL | PowerVR B-Series BXM-4-64，OpenCL 3.0 |
| Plasma 环境 | 不包含 PowerVR 库变量 |
| Discover | 使用清洁环境启动，未复现此前崩溃 |
| KScreenLocker | 清洁环境、Qt Quick 软件后端，进程持续运行 |
| 注销 | 正常返回 SDDM |
| disable/enable | diversion 和 wrapper 均可正确移除与恢复 |

锁屏测试不再出现此前的 `EGL not available`，`kscreenlocker_greet` 在多次远程
锁定/解锁过程中保持运行。

## 剩余发现

XWayland `22.1.9` 已不再继承 `LD_LIBRARY_PATH` 或
`LIBGL_DRIVERS_PATH`，但仍记录 `Failed to initialize glamor, falling back
to sw`。它同时打开 `card0` 和 `renderD128`；发行版 Mesa 路径加载
`libdril_dri.so`，并报告 `egl: failed to create dri2 screen`。

对照测试中为 XWayland 单独注入厂商环境后，它可以加载 `pvr_dri.so`，也能识别
PowerVR 的 DRI image 和 fence 扩展，但在枚举 EGL config 后仍然回退。这把剩余
问题收敛到 XWayland/glamor 与闭源 PVR DRI/EGL 栈的兼容性，而不是环境变量或
缺少 render node。下一步适合测试更新版 XWayland，并跟踪 glamor 的 EGL config
选择过程。

测试结束后，板卡已恢复为 `default l0`，临时 SDDM 自动登录配置已删除，图形
登录界面已经恢复。

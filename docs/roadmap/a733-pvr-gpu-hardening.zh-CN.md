# A733 PowerVR GPU 加固路线

## 当前基线

A7Z PowerVR 第一版移植已经在实机正常运行并完成验证：

- `pvrsrvkm` DDK `24.2@6603887`，BVNC `36.56.104.183`；
- 固件启动和 `/dev/dri/renderD128`；
- Vulkan、OpenCL 3.0、EGL/GBM 和 OpenGL ES 3.2；
- Plasma Wayland 上使用 PowerVR 加速的 KWin；
- HDMI 原生 `1024x600@60Hz` 和 `l1` 恢复路径。

这只是第一版移植，并不代表 GPU 工作已经全部结束。下面按发布风险排列剩余任务。

## P0：桌面环境隔离——已在 `gpu6` 完成

`gpu4` 包通过 `/etc/profile.d/a733-pvr.sh` 导出厂商库路径。这样可以让
KWin 使用 PowerVR，但普通 Qt Wayland 客户端也会看到厂商 EGL 栈。

已经观察到的结果包括 `EGL not available` warning、Discover 崩溃，以及在
Qt Quick scene graph backend 强制设为 OpenGL 时，KScreenLocker greeter
无法工作。第一版发布的稳定配置是：

```ini
[QtQuickRendererSettings]
SceneGraphBackend=software
```

`24.2.6603887+gpu6` 已完成第一轮隔离：

1. 移除全局 PowerVR `LD_LIBRARY_PATH`、`LIBGL_DRIVERS_PATH`、Vulkan 和
   OpenCL 环境变量；
2. 只由 KWin wrapper 注入厂商 EGL/GLES 环境；
3. 通过清洁环境 wrapper 启动 `kscreenlocker_greet`；
4. 通过清洁环境 wrapper 启动 XWayland；
5. Vulkan/OpenCL 检查继续通过 `a733-pvr-run` 运行。

实机已经通过 PowerVR KWin 合成、Plasma 清洁环境、锁屏、Discover 启动、
注销和 enable/disable 可逆性验证。详见
[环境隔离验证记录](../validation-records/2026-07-16-a733-pvr-environment-isolation.zh-CN.md)。

## P1：加速覆盖范围

- 排查 XWayland 的 `Failed to initialize glamor, falling back to sw`。原生
  XWayland 清除 PowerVR 环境变量后仍然出现该问题，说明全局环境污染并非
  唯一原因。原生 Wayland 合成已加速，但 X11 应用仍可能使用软件渲染。
  下一步测试更新版 XWayland，并跟踪厂商 `pvr_dri.so` 路径被拒绝时所缺少的
  EGL config 条件。
- 研究 Qt Quick 客户端能否通过兼容的 Wayland EGL 路径安全使用 GPU。
  `v0.3.0` 支持的配置是 Qt Quick 软件绘制加 PowerVR KWin 合成。
- 单独验证 Firefox/Chromium 加速。视频解码属于另一套子系统，不能根据 3D
  加速结果直接推断。

## P1：稳定性验证

- 重复执行冷启动、重启、SDDM 登录、注销、锁屏/解锁、禁用 GPU 包、重新
  启用和卸载测试。
- 长时间运行 Vulkan 和 OpenCL workload，检查 GPU fault 或 reset。
- 检查 HDMI 热插拔、KWin 长时间运行、内存增长和温度表现。
- Debian KWin 每次升级后，刷新并重新验证无 capability 的 KWin shadow copy。

## P2：时钟、电源和内核维护

- DTS 没有提供默认 GPU clock rate，驱动回退到 600 MHz。修改前先测量真实
  时钟和 DVFS 行为。
- 梳理 GPU 电源域和 BSP warning，不把所有厂商调试 warning 都视为 GPU 故障。
- DDK `24.2@6603887`、BVNC `36.56.104.183` 固件和用户态必须作为一个
  锁定版本集合维护。
- 官方 6.6/Trixie 接入只作为参考，不把它视为比已验证 Debian 12 路线更成熟
  的证据。
- 长期跟踪主线 PowerVR DRM 和 Mesa 开源驱动路线。

## v0.3.0 发布边界

`v0.3.0-a733-pvr-gpu` 发布已经验证的第一版移植。支持的桌面配置让 Qt Quick
scene graph 使用软件绘制，最终桌面合成由 PowerVR GPU 上的 KWin 完成。环境
隔离和 XWayland 加速属于下一版 GPU 包工作。

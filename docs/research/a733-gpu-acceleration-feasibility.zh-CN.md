# A733 GPU 加速驱动可行性调研

## 调研范围

- 日期：2026-07-14
- 目标平台：Radxa Cubie A7Z/A733，参考 Orange Pi 4 Pro、Orange Pi Zero 3W
- 当前系统：Debian 12 Bookworm KDE，Allwinner/Radxa BSP Linux `5.15.147`
- 本轮只做源码、软件包和上游状态调研，不安装驱动、不修改镜像

## 结论

A733 的 GPU 加速具备明确可行性，但应分成两条路线：

| 路线 | 当前可行性 | 能力边界 | 主要问题 |
| --- | --- | --- | --- |
| 厂商 PowerVR DDK：`pvrsrvkm` + 匹配用户态 | 高，适合作为第一阶段 | OpenGL ES、Vulkan、OpenCL；已有 A733 实机案例 | 用户态闭源、KM/UM 必须严格同版本、旧 Xorg/SSL 包装冲突 |
| 主线 Linux PowerVR DRM + Mesa PowerVR | 中长期可行，当前不适合替代 BSP | 开源 Vulkan；可进一步研究 Zink 提供 OpenGL | Linux 主线尚未接受 A733 的精确 BVNC，A733 DT/电源接入也未完成 |

最短路径不是 Panfrost/Panthor。A733 使用 Imagination PowerVR
`BXM-4-64`，硬件标识 BVNC 为 `36.56.104.183`；Panfrost、Panthor 和 Mali
`kbase` 面向 ARM Mali GPU，与这颗 GPU 不匹配。

第一阶段应优先验证 Radxa 发布的成套驱动：

- 内核侧：`img-bxm-dkms`，构建 `pvrsrvkm.ko`；
- 用户态：`xserver-xorg-img-bxm-1.21.1-2.deb`；
- 二者均为 DDK `24.2@6603887`；
- 固件：`rgx.fw.36.56.104.183`。

不建议把 Orange Pi 内核树中的 `pvrsrvkm` 与任意用户态库混搭。PowerVR
Services 的内核态和用户态共用私有 ABI，版本不匹配通常会在设备初始化、固件
兼容性检查或第一个图形客户端连接时失败。

## 当前工程证据

### 硬件和设备树

本地 A733 BSP 的 GPU 节点位于
`sources/linux-a733/bsp/configs/linux-5.15/sun60iw2p1.dtsi`，声明了：

- `compatible = "img,gpu"`；
- MMIO 基址 `0x01800000`；
- GPU 和 DVFS 两个中断；
- Allwinner 私有时钟、复位、OPP 和电源域接入；
- `CONFIG_AW_GPU_TYPE="bxm"`。

厂商模块的构建配置进一步固定了：BXM、BVNC `36.56.104.183`、DDK
`24.2@6603887`、window system `nulldrmws`，输出为 `pvrsrvkm.ko`。

### BSP 已包含可编译源码

源码位于
`sources/linux-a733/bsp/modules/gpu/img-bxm/linux/rogue_km`。顶层
`bsp/modules/gpu/Makefile` 已有 `GPU_TYPE=bxm` 分支，并会进入
`build/linux/sunxi_linux` 构建模块。因此“能否获得内核模块源码”不是障碍。

### 当前镜像为什么仍是 llvmpipe

现有镜像和包的检查结果与实机记录一致：

- `linux-image-5.15.147-21-a733` 不包含 `pvrsrvkm.ko`；
- 包内 Panfrost/Lima 只是通用配置产物，不能驱动 BXM；
- `rootfs.tar` 中没有 PowerVR 用户态库、模块或 `img_icd.json`；
- manifest 只有通用 Mesa `25.0.7` Vulkan 驱动，不包含 PowerVR ICD；
- 本地 `task-a733` 虽依赖 `img-bxm-dkms` 和 BXM 用户态包，但这些任务包
  没有进入最终 rootfs。

所以当前 `llvmpipe` 不是显示驱动故障，而是 3D 内核模块和匹配用户态均未安装。
HDMI DRM/KMS 能正常显示，并不能自动提供 GPU 3D 加速。

## 厂商 DDK 路线

### 可获得的软件包

Radxa 的 `a733-bullseye` 仓库在 2026-07-14 仍公开：

| 包 | 版本 | 内容 |
| --- | --- | --- |
| `img-bxm-dkms` | `0.1.0-3` | PowerVR BXM 内核模块源码和 DKMS 配置 |
| `xserver-xorg-img-bxm-1.21.1-2.deb` | `1.0.1` | 匹配的 EGL/GLES/Vulkan/OpenCL/DRI 用户态、固件和厂商 Xorg 文件 |

用户态包内可见的关键文件包括：

- `libGLESv2_PVR_MESA.so.24.2.6603887`；
- `libPVROCL.so.24.2.6603887`；
- `libpvr_dri_support.so.24.2.6603887`；
- `pvr_dri.so`、`sunxi-drm_dri.so`、`libpvr_mesa_wsi.so`；
- `rgx.fw.36.56.104.183`；
- 厂商版 `Xorg`、`modesetting_drv.so` 和 `libglamoregl.so`。

包名里的 `.deb` 是 Radxa 仓库元数据本身的历史命名，不代表文件损坏。

### 跨厂商实机证据

Orange Pi 和 Armbian 社区已经证明同一 A733 驱动组合可以移植：

- `Incipiens/OrangePiZero3W-GPU-VPU` 把 Radxa A733 用户态移到 Orange Pi
  Zero 3W，并针对 `6.6.98-sun60iw2` 通过 DKMS 重建内核模块；
- Armbian 的 sun60iw2 GPU 草案在 Orange Pi 4 Pro 上记录：`pvrsrvkm` 加载、
  DRM 初始化为 `24.2.6603887`、固件加载、`renderD128` 出现；
- `clinfo` 识别 `PowerVR B-Series BXM-4-64`，并报告相同的
  `24.2@6603887` 驱动版本；
- 社区还记录 Chromium 通过 ANGLE/Vulkan 获得硬件 rasterization。

这些结果不能替代本项目的 A7Z 实机验证，但已经证明 A733 GPU 和这套 DDK
可工作，DKMS 可以跨 5.15/6.6 BSP 重建，且 Radxa 用户态不必绑定 Radxa 板卡，
只要 SoC、BVNC、固件和 KM ABI 一致。

### 对本项目的适配判断

当前 A7Z 使用 `5.15.147`，比社区的 6.6 移植更接近 Radxa 原始环境，第一轮
成功概率较高，但仍须验证：

- 当前 headers 是否包含 DKMS 需要的 `bsp/include`，尤其 `sunxi-sid.h`；
- `Module.symvers`、编译器和内核配置是否足以重建 DKMS；
- 内核模块、用户态和固件是否完全同版；
- `pvrsrvkm` 是否正确取得 GPU 电源域、时钟、复位和中断；
- SDDM/Plasma Wayland 是否能在不替换系统 Xorg 的情况下使用硬件 API；
- Mesa/GLVND 与 `/usr/local/lib` 厂商库的加载优先级是否可控。

### 主要风险

1. **闭源用户态和再分发**：内核模块有源码，但 EGL/GLES/Vulkan/OpenCL
   用户态是厂商二进制。发布镜像或包前必须核对许可证；按需从 Radxa 仓库下载
   比把二进制直接纳入本仓库更稳妥。
2. **KM/UM 版本锁定**：必须将 `24.2.6603887` 模块、用户态和
   `36.56.104.183` 固件作为一组，不能仅以“都叫 BXM”判断兼容。
3. **覆盖发行版组件**：用户态包包含完整 `Xorg`、modesetting 和 glamor。
   社区遇到过文件覆盖、旧 `libssl1.1`/`libcrypto1.1` 和 DRI2/DRI3 问题。
   第一轮应避免替换 Xorg，先验证 headless OpenCL、Vulkan 和 Wayland/EGL。
4. **模块加载不等于桌面加速**：render node 只证明内核侧初始化，还需分别验证
   OpenCL、Vulkan、EGL/GLES、KWin 和 Chromium。
5. **电源域 warning**：已有实机日志出现 GPU top/core 超时。加载前后必须比较
   电源域、时钟、温度和 suspend/resume 行为。

## 主线 Linux + Mesa 路线

### 有利证据

最新 Mesa PowerVR 文档明确把 `BXM-4-64`、精确 BVNC
`36.56.104.183` 列为活跃开发对象，Vulkan 目标为 1.2。Imagination firmware
仓库也包含 `powervr/rogue_36.56.104.183_v1.fw`；历史显示该固件在 2025 年
加入并于 2026-04-15 更新。这说明 A733 的精确硬件版本已经进入开源生态。

### 当前阻塞

截至 2026-07-14，Torvalds Linux 主线 PowerVR DRM 仍只把
`33.15.11.3` 和 `36.53.104.796` 标为 supported，把 `36.52.104.182` 标为
experimental；`36.56.104.183` 会落入 unknown 并返回不支持。

主线 binding 与厂商 A733 DT 也存在明显差异：

| 项目 | A733 BSP | 主线 PowerVR binding |
| --- | --- | --- |
| compatible | `img,gpu` | `img,img-rogue`，并要求 SoC/产品 compatible |
| 中断 | GPU + DVFS 两个 | 当前最多一个 |
| 时钟名 | 私有 `clk_parent`、`clk`、`clk_bus` 等 | `core`、`mem`、`sys` |
| 电源 | Allwinner 私有 GPU top/core 域 | 标准 power-domain 接口 |

主线路线至少需要：

1. A733 GPU DT binding 和设备树描述；
2. CCU、reset、power-domain 和电源时序接入；
3. Linux PowerVR 接受并验证 `36.56.104.183`；
4. 安装对应的主线格式 firmware；
5. 构建含 PowerVR Vulkan 的新版 Mesa；
6. 实机验证缓存一致性、IOMMU/DMA、稳定性和 suspend/resume。

Mesa PowerVR 当前是 Vulkan 驱动，不是原生 Gallium OpenGL 驱动。Linux 桌面
OpenGL 可在 Vulkan 稳定后研究 Zink，但这颗 BXM 尚不是 Vulkan conformance
列表中的认证设备；Mesa 要求未认证 GPU 显式设置
`PVR_I_WANT_A_BROKEN_VULKAN_DRIVER=1`。所以这条路线适合作为长期上游化实验，
不应作为近期 Debian 12 桌面交付路径。

## 建议研究顺序

### 阶段 0：只读基线采集

```bash
uname -a
cat /proc/device-tree/compatible | tr '\0' '\n'
ls -l /dev/dri
lsmod | grep -E 'pvr|panfrost|lima'
dmesg | grep -Ei 'gpu|pvr|rgx|power domain|iommu'
glxinfo -B
eglinfo
vulkaninfo --summary
```

同时保存包状态、`ldconfig -p`、Vulkan ICD JSON 和会话类型。

### 阶段 1：离线包审计和 DKMS 编译验证

先不装入运行系统：

1. 下载并校验两个匹配的 Radxa 包；
2. 比较 DDK 版本、BVNC、固件名和动态库依赖；
3. 在临时 rootfs/chroot 或独立实验镜像中针对当前 headers 编译 DKMS；
4. 检查 `modinfo`、未解析符号和 vermagic；
5. 不覆盖 Xorg，不改变当前可启动镜像。

通过条件是生成适配当前内核、无缺失符号的 `pvrsrvkm.ko`。

### 阶段 2：厂商路线最小实机验证

1. 使用克隆卡或第二张 SD 卡；
2. 安装匹配 KM/UM，但先不替换系统 Xorg；
3. 验证模块、固件、render node 和 `pvr` 日志；
4. 先验证 headless OpenCL，再验证 Vulkan；
5. 最后验证 Wayland EGL/GLES、KWin 和 Chromium ANGLE；
6. 完成重启、待机恢复、温度和长时间负载测试。

### 阶段 3：主线路线原型

1. 选择包含 PowerVR DRM 的新内核；
2. 移植 A733 CCU、电源域和 GPU DT；
3. 加入并验证 `36.56.104.183` 和主线 firmware；
4. 构建 Mesa PowerVR Vulkan；
5. 先跑 `vulkaninfo`/CTS 子集，再考虑 Zink 和桌面合成器。

## 决策门槛

第一阶段建议继续厂商 DDK 路线，前提是：

- DKMS 能无补丁或只用少量兼容补丁完成构建；
- `pvrsrvkm` 不破坏现有 HDMI DRM/KMS；
- 不替换发行版 Xorg 也能证明至少一种硬件 API 可用；
- 用户态二进制的使用和发布方式可接受。

若必须替换整套 Xorg、引入停止安全维护的 SSL 库，或大规模修改内核，则应把
厂商路线限制为实验镜像，同时提高主线路线优先级。

## 来源

- 本地 Radxa/Allwinner A733 BSP：`sources/linux-a733`
- 本地 RSDK 输出：`sources/rsdk/out/radxa-a733_bookworm_kde`
- Radxa A733 Bullseye repository：https://radxa-repo.github.io/a733-bullseye/
- Mesa PowerVR 文档：https://docs.mesa3d.org/drivers/powervr.html
- Linux PowerVR DRM：https://github.com/torvalds/linux/tree/master/drivers/gpu/drm/imagination
- PowerVR DT binding：https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/gpu/img,powervr-rogue.yaml
- Imagination firmware：https://gitlab.freedesktop.org/imagination/linux-firmware
- Orange Pi Zero 3W GPU/VPU 移植：https://github.com/Incipiens/OrangePiZero3W-GPU-VPU
- Armbian A733 GPU 草案：https://github.com/shkolnik/armbian-build/pull/10
- Armbian Orange Pi 4 Pro 支持：https://github.com/armbian/build/pull/9967
- Armbian Cubie A7Z 支持：https://github.com/armbian/build/pull/10036
- Radxa A733 GPU 缺失问题：https://github.com/radxa-build/radxa-a733/issues/17


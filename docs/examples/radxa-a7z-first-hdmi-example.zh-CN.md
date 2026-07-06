# 验证示例：Radxa A7Z 首次 HDMI 启动

这是一份示例记录，不是真实实测结果。内容基于本仓库里已经收集到的公开资料。

## 验证记录

- 日期：2026-07-06
- 测试人：示例记录
- 板卡：Radxa Cubie A7Z
- 板卡版本：公开资料中未明确
- SoC：Allwinner A733
- 显示路径：Micro HDMI
- 镜像或构建：Radxa A7Z 公开 Debian 桌面镜像线
- 内核版本：所选镜像里的 BSP 内核
- 桌面环境：厂商镜像预期提供的桌面会话
- 存储介质：microSD 或 eMMC，取决于实际测试环境
- 供电方式：稳定的 USB-C 电源

## 测试目标

证明 A7Z 上最简单的 HDMI 路径能否启动到桌面会话。

## 执行步骤

1. 将选定的 Radxa A7Z 镜像刷入存储介质。
2. 把显示器接到 Micro HDMI 口。
3. 启动板卡并等待桌面出现。

## 实际命令

```bash
# 仅示例
dd if=radxa-a7z-image.img of=/dev/sdX bs=4M status=progress conv=fsync
```

## 观察结果

- 启动结果：本示例未执行。
- HDMI 结果：预期应优先验证，因为这是最简单的硬件路径。
- 桌面结果：本示例未执行。
- GPU 加速结果：需要实际测试后才能确认。
- 输入设备结果：需要实际测试后才能确认。

## 证据

- 日志：本示例无。
- 截图：本示例无。
- 照片：本示例无。
- 串口输出：本示例无。

## 通过或失败

- 结果：未测试
- 原因：这是计划示例，不是实际板卡运行结果。

## 备注

- Radxa A7Z 提供了直接的 Micro HDMI 路径和 USB-C DP Alt Mode，但第一次验证应先选 Micro HDMI。
- 仓库里的公开资料说明 Debian 桌面支持是存在的，但 Bookworm 的桌面就绪程度仍需要真实验证。

## 来源

- [Radxa A7Z 文档](https://docs.radxa.com/en/cubie/a7z)
- [Radxa A7Z 下载页](https://docs.radxa.com/en/cubie/a7z/download)
- [Radxa A7Z 仓库](https://github.com/radxa-build/radxa-cubie-a7z)
- [A733 显示生态调研](../research/a733-display-landscape.zh-CN.md)
- [板卡对照](../comparison/radxa-a7z-vs-orangepi-a733.zh-CN.md)


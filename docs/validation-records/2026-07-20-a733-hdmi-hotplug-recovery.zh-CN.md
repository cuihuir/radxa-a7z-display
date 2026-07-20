# A733 HDMI 热插拔恢复验证

## 目标

修复 HDMI 拔出后重新插入仍然黑屏的问题。当时内核能够检测 HPD 并重新读取
EDID，但显示输出不会自动恢复。

## 根因

BSP HDMI 拔出处理函数绕过 DRM atomic commit，直接清除缓存的 DRM 状态并关闭
HDMI 硬件。Xorg 仍保留相同模式下的 enabled connector，因此重新插入时不会触发
新的 modeset。手动依次执行 `xrandr --output HDMI-1 --off` 和
`--mode 1024x600` 后可以恢复，证明完整 atomic disable/enable 流程有效。

## 修复

- `0002-drm-hdmi-keep-atomic-state-across-hpd.patch` 移除 HPD 拔出处理中的
  非 atomic 状态清理和硬件关闭。
- 内核包 `5.15.147-21.1+display3` 显式安装已编译的 A7Z DTB，避免生成无法启动的
  `l0`。
- 两个部署工具都会在每次 `u-boot-update` 后恢复 `l1` 的 vendor A7Z DTB 和
  `module_blacklist=pvrsrvkm`。

## 实机结果

2026 年 7 月 20 日，板卡从 `l0` 启动，内核为 `5.15.147-21.1-a733`，内核包为
`5.15.147-21.1+display3`，GPU 包为 `24.2.6603887+gpu8`。SDDM 使用
`1024x600@60Hz`，`pvrsrvkm` 已加载，HDMI 状态为 `connected` 和 `enabled`。
实际拔出并重新插入 HDMI 后，显示自动恢复，不需要 xrandr 命令或 udev 规则。

恢复项 `l1` 继续使用独立 vendor 内核、显式 vendor A7Z DTB 和 PowerVR 模块黑名单。

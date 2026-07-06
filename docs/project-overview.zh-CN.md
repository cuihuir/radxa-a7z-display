# 项目总览

## 目标

为基于 A733 的开发板建立并维护一条面向 Debian 12 的 HDMI 桌面启动路径，先以 Radxa A7Z/Z7A 为主，再参考 Orange Pi 的 A733 资料作为补充。

## 范围

本项目覆盖：

- A733 硬件上的板级显示启动。
- Debian 12 或更高版本上的 HDMI 图形桌面。
- BSP 依赖、内核/显示栈约束以及可执行的验证步骤。
- Radxa 与 Orange Pi 两条 A733 实现路径的对照分析。
- 资产、笔记和决策的长期维护规则。

本项目不覆盖：

- 与 A733 无关的通用 Linux 发行版支持。
- 超出显示栈验证所需的桌面应用层定制。
- 与 A733 显示启动无直接关系的上游内核或 Mesa 开发。

## 工作方式

这个仓库以文档为中心。来源材料、测试结果和结论都应落到文件里，而不是只留在聊天记录中。

## 成功标准

- 维护者无需阅读聊天记录，就能了解 A733 HDMI 桌面支持的当前状态。
- 仓库中保留了清晰的约束、已知可用的验证步骤和开放风险。
- 文档集合长期保持双语且内部一致。

## 关键参考

- Radxa A7Z 文档：https://docs.radxa.com/en/cubie/a7z
- Radxa build 仓库：https://github.com/radxa-build/radxa-cubie-a7z
- Radxa A733 build 仓库：https://github.com/radxa-build/radxa-a733
- Armbian 论坛讨论：https://forum.armbian.com/topic/56130-radxa-cubie-a7aa7z-allwinner-a733/


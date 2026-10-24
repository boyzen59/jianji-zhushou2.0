---
name: jianji-zhushou
description: 根据中文文案、原声和素材设计分镜、视觉与动效，用 Remotion 制作预览或成片，支持参考视频拆解、素材提示词及局部回修。
---

# jianji-zhushou 3.2 · Remotion

文案决定画面，设计决定质感，Remotion 负责统一时间轴和最终渲染。调用名仍为 `$jianji-zhushou`。

## 启动时自动自检与更新

每次调用本技能，第一步执行 `python -X utf8 "<本技能目录>/scripts/startup.py"`。脚本检查本技能公开仓库与全部保留模块的上游HEAD，补齐完整包并更新到最新版本；不按同日缓存跳过远端检查。包包含源码、配置、依赖清单、字体／图片等仓库内运行资产，按用户要求跳过视频与生成的node_modules。

本地改动保留，新上游版本放入incoming供融合；已被上游删除的旧文件归档。离线保留现有包并说明受影响项。外部账号、未随仓库提供的模型和Git子模块按实际状态记录，不把索引或下载清单称为完整包。

## 核心约定

- 先理解原句的主张、证据、因果、对比与情绪，再选择主体、构图、动作和节奏。原声已定时，视觉跟随原声；生成图不充当事实证据。
- Remotion主导合成和最终渲染；GSAP、Motion、Lottie、Canvas、SVG、Three.js按镜头需要配合，适配统一时间轴。已收录的技能、动效和网页缓存都是可调用制作能力，选中后读取、吸收规则并落实组件，不停留在列链接。
- 全片共用 art-direction 与 tokens。高级感来自清晰主体、精确排版、可信材质、动作重量与阅读停留，按[视觉标准](references/visual-style.md)直接落实到构图和实现。
- 当前用户要求 → 有依据的本项目决定 → 本技能 → 外部资料。保留前15秒真人全屏、随后右下小窗；字幕、AI片段时长、画幅和交付物按项目设置，见[项目设置](references/production-defaults.md)。
- 先按语义找需要的模块；只读选中的模块，由当前模型判断、组合和解决冲突。外部教程的模型、片长、审批、配额和安装流程不转为本技能规则。只要求提示词时，输出 GPT 图片与 Gemini 视频提示词，不调用生成服务。

## 执行

1. 接收文案、原声与素材，确定本次交付范围；续作先读项目交接。
2. 按[导演流程](references/storyboard-direction.md)建立原句 → 视觉目的 → 镜头。需要找表现手段时查[语义地图](references/capability-map.md)。
3. 定一套视觉体系；按文案直接制作；确需用户决定的方向问题集中成一份MD一次性展示，一次收集意见，已有授权直接继续。
4. 启动更新完成后，按[模块说明](references/local-modules.md)调用完整本地包；需要外部方法时查[参考路由](references/motion-reference-index.md)；口播词级动效查[Talkcraft索引](references/talkcraft-motion-routing.md)，生成素材前期查[提示词流程](references/prompt-direction.md)。
5. 按[Remotion制作](references/remotion-production.md)实现和渲染；做必要结构与运行检查，不例行截图回看、不反复验证文稿。

## 按任务读取

| 当前任务 | 资料 |
|---|---|
| 数据结构／全量文字审阅／Word回修 | [数据与审阅](references/qa-and-schema.md)、[内容约定](references/content-and-approval.md) |
| 动作实现／对象接力 | [动效配方](references/motion-recipes.md)、[连续性](references/playback-continuity.md) |
| 史料／AI素材／素材状态 | [素材管理](references/assets-and-history.md) |
| 原声／真人录制／音轨／交付 | [声音与录制](references/audio-render-delivery.md) |
| 恢复或交接 | [交接](references/execution-handoff.md) |
| 历史地图／军事调度／边界变迁 | [地图制作](references/historical-maps.md) |
| 本地技能与上游更新 | [本地模块](references/local-modules.md) |
| 创建工程或依赖缺失 | [安装支持](references/installation-and-support.md)、[本机环境](references/local-installation.md) |

文稿、分镜、意见与说明默认写MD，最后按需粘贴或转换到Word；不对Word/PDF截图回看。只交付本次需要的计划、提示词、视觉稿或成片。结构通过、文档已读、组件已实现、实际渲染与动态已检查分别记录；文件齐全不代表画面好看。未到素材只阻塞对应镜头。

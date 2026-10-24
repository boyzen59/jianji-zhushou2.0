# jianji-zhushou2.0

文案驱动的视频制作技能。Remotion负责统一时间轴和最终合成，GSAP、Motion、Lottie、Canvas、SVG、Three.js按镜头需要配合。

仓库名为`jianji-zhushou2.0`；技能调用名保持`$jianji-zhushou`，当前内部版本为3.2。

## 使用

先安装 Git 和 Git LFS，执行 `git lfs install` 后克隆本仓库；若此前已克隆，执行 `git lfs pull` 补齐大文件。GitHub网页的ZIP可能仅含LFS指针，完整离线包另行提供。

将仓库放到代理的技能目录，文件夹命名为`jianji-zhushou`，从[SKILL.md](SKILL.md)进入。

```text
使用 $jianji-zhushou，根据我的文案和素材设计分镜、统一视觉，并完成本次要求的提示词、预览或成片。
```

所有镜头从文案语义反推；模型自主选择技能、组合动作并裁决冲突。保留前15秒真人全屏、后续右下小窗。方向性问题集中到一份MD一次沟通。文稿默认Markdown，按需转Word，不设置文稿截图回看流程。

## 本地模块与代码归档

- 49个登记模块，按实际需求加载规则、源码和素材。
- Wise Motion：462个目录条目；已归档完整非视频包（源码、配置、依赖清单与仓库资产），保留原许可证与来源。视频不随本次归档下载。
- Talkcraft：完整非视频包，包含108张卡及对应TSX，保留PolyForm Noncommercial许可证；商业使用需满足原作者授权条件。
- Prompt Motion：33个案例已逐页查找源码链接。这些页面提供提示词与视频展示，页面没有公开工程源码链接，状态逐条保存在本地索引中；不把页面脚本或索引冒充动画源码。
- 地图工具：Mapshaper、d3-geo与SVG绘图器，支持历史阶段边界、调度路线和地名标注。

少数来源未明确提供根许可证，公开仓库仅保留其原创适配说明、来源与下载关系；完整包已保存在本地；公开安装在首次启动时自动从原库补齐。

```text
python scripts/query_motion_library.py --talkcraft "对比 图片" --input 图 --limit 6
node modules/upstream/wise-motion/scripts/match.mjs "卡片依次上移显现，不要弹跳"
python scripts/sync_sources.py --source wise-motion
python scripts/archive_web_sources.py --source wise-motion
```

新工程参见[安装支持](references/installation-and-support.md)，本地来源与更新参见[模块说明](references/local-modules.md)。每次调用首先执行 `python -X utf8 scripts/startup.py`，实际检查本技能与49个原库的最新版本并更新；本地改动保留，上游冲突文件放入modules/incoming。离线保留已有包并记录失败。依赖安装与外部模型按选用功能准备。视频不下载。

## 许可

本项目原创编排、规则与脚本采用[MIT](LICENSE)。`modules/upstream`中的第三方材料适用各自原许可，详见[第三方来源](THIRD_PARTY_NOTICES.md)及各模块许可证；根许可证不覆盖第三方材料。

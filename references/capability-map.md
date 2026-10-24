# 文案反推能力

选择从原句开始。需要时检索对应知识卡，再接入[本地制作模块](motion-reference-index.md)；没有匹配项可原创，不要求遍历全库。

| 原句需要解释什么 | 知识卡／制作能力 |
|---|---|
| 人物、史料、局部证据 | evidence-focus；原件定位、同源放大、题注、圈注 |
| 数量、趋势、排名、规模 | quantitative-comparison；同口径图表、表格、数值揭示 |
| 军事调度、迁徙、疆界变化 | geography-route；[历史地图](historical-maps.md)、分阶段边界、路线与节点 |
| 因果、机制、层级、流程 | causal-model；结构图、拆层、物件流转 |
| 观点并置、多证据 | editorial-collage；Vox拼贴、蒙版、照片与图解 |
| 气氛、艺术材料 | art-image-extension；Lemo/Huashu风格、关键帧与生成提示词 |
| 同一对象变化、转折 | shape-story；Wise Motion轮廓／状态接力、匹配剪辑 |
| 产品价值与操作证据 | product-demonstration；真实UI、状态变化、光标；短片才用发布片流程 |
| 局部到整体、空间关系 | spatial-camera；2.5D、3D、素材巡游 |
| 论点、关键词、语义层次 | typography-choreography；动态排版、Talkcraft |
| 抽象概念由主体演示 | character-action；手绘角色与骨架、Canvas/SVG |
| 原声与动作同步 | audio-events；词级锚点、动作音效、声音桥 |
| 跨章节统一质感 | style-system；共享tokens、LottieFiles |
| 构图／运动问题 | quality-review；按具体问题一次回修，默认不例行截图循环 |
| 程序艺术与规律 | procedural-simulation；纯帧函数、预计算运动 |
| 长切短、局部替换、多版本 | editing-reuse；稳定ID、源时码、EDL、检查点 |

`python scripts/query_motion_library.py --knowledge "原句关键词"` 查询知识卡；加 `--materials` 查询本地素材配方。源码组件、需要实施的配方、外部模型服务分别标记实际状态。所有出镜镜头遵循前15秒真人全屏、后续右下小窗。

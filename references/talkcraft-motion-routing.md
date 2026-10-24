# Talkcraft 108动效卡

来源：[video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft)。108张卡的ID、名称、输入、语义、能量和源码路径见[talkcraft-motions.json](talkcraft-motions.json)；卡片正文与TSX在`modules/upstream/video-talkcraft/`。

先从文案反推：这句在比较、解释机制、列举、强调、引用、展示过程，还是切换章节；再按已有图片／截图／人物／数据过滤。卡是候选动作，构图、配色、时长、字幕和组合仍由本片导演决定。

```text
python scripts/query_motion_library.py --talkcraft "对比 图片" --input 图 --limit 6
python scripts/query_motion_library.py --talkcraft "机制" --energy 中
```

选中卡后读取其本地MD与TSX，替换写死内容、按项目tokens改皮、对齐语义cue并保持媒体原点。模块本身的独立组件可能依赖共享文件，使用前沿import补齐；不把下载完称为108项均已集成运行。

分类为字幕花字、强调标注、数据信息图、素材呈现、转场结构、人物互动、运镜。用它们解决信息任务，不按分类轮播。固定“每句必须动”“只能某类转场”“每片限某数量”“Apple默认皮肤”等规则由模型按文案取舍；前15秒真人全屏和后续右下小窗沿用本技能约定。

上游为PolyForm Noncommercial 1.0.0，商业使用需作者授权。未满足时自动选择其他可用模块或原创动作实现；索引可以帮助发现功能类型，不把限制性源码改名后用于商业成片。

# 场景数据与审阅回修

## 数据与机器校验

新片使用 `assets/templates/storyboard-example.json` 的schema 7。schema 4／5／6可读取以恢复已有项目；旧版演示只用于兼容检查，不作为新片默认值。迁移时保留有依据的项目决定，移除没有用户／项目依据的历史模板默认，并记录迁移前后。非Remotion工程先在副本中重建等效镜头与时间轴，验证后再续作。

- 全局右开帧区间[start_frame, end_frame_exclusive)，相邻镜头首尾相接；settled_frame在镜内。当前脚本支持整数1–240 fps，其他时基先适配，不静默取整。
- source_ids与narrative_intent记录原句及解释目的；cue写锚点与精度。start_state、end_state、component可描述静态证据和计划中的组件。
- style_system含共享id及tokens_reference；镜头默认继承，不能悄悄换成不相关皮肤。校验只验证关联，视觉一致性仍需检查。
- motion_beats可以为空或省略；有动作才写主体、参数及start/peak/settled_frame。跨镜shared交接共用object_id、boundary_state和window_frames。
- reference_sources及reference_uses可为空或省略，原创镜头不必虚构引用。实际引用时保留来源、机制与改编；共用决定记一次。
- texts使用稳定id、role、zh/en；重复ID内容一致。旁白属于内容层，实际字幕投射与production_policy.subtitles.mode一致（off／burned／external）。
- media_layers的kind、asset_id、availability、path和可见窗口真实登记；pending不能声称已有路径。ai_video、video、presenter逐个记录playback_id、source_in_seconds、source_out_seconds、playback_rate；窗口按源长÷速度核对。同一playback_id跨镜保持同一源与时钟；重复使用另建播放ID。
- verification为planned／implemented／rendered／reviewed，后两项需实际evidence。文件存在不代表审美或事实已验证。

schema 7的 `production_policy.subtitles.mode` 记录字幕选择。`presenter.opening_fullscreen_seconds=15`、`later_mode=bottom_right_pip` 保留。片长短于15秒时全片真人全屏；excerpt只是片中摘例。缺真人素材记pending，继续其他制作。

`ai_video` 可省略；`duration_confirmation_required` 默认false。若项目要求先确认，设true，pending只可保留计划；若已confirmed，保存 `confirmation_basis` 与 `durations_seconds`（asset_id→播放秒数）并校验对应窗口。没有AI视频不产生时长确认项。源长、可见窗口和用户约定是不同概念。

字幕安全区用归一化x/y/width/height，范围在画面内；scope为full_film或excerpt。`engine` 在母版和场景统一为remotion。校验不强制外部引用、每镜运动、固定5页或某类视觉模板。

~~~text
python scripts/validate_storyboard.py storyboard.json
python scripts/validate_storyboard.py storyboard.json --check-files media-root
~~~

校验器检查结构、ID、连续范围和媒体时间，不验证事实、实际像素、听感或用户批准。不要用“结构通过”代替成片检查。

## 文字唯一登记

登记拟上屏的标题、关键词、人物地点、日期数字单位、图表标签、引文、来源和共用角标；新增文字先登记再出图，避免遗漏装饰性英文或年份。动态数字登记依据与终值。素材内嵌文字若被当作可读信息使用，另标“非直接可编辑”，给转写／中文语义与处理方案；未查看真实素材则标待转写，受用户素材分析范围限制时明确覆盖边界。无需逐字转写未作为信息使用的远景纹理。页码、占位提示、REV等仅是审阅层，不进入成片登记。

Markdown是默认文稿与修改入口；需要Word时导出相同内容，含对应画面缩略图、稳定ID、场景／时间／PDF页码索引、原值与可编辑正文列；图像仅供对照，正文必须是真正可编辑的文字。共用标题和角标设一次编辑入口，并列出全部出现位置；不同语义对象不因同字串而合并。旁白完整台词另放录制包。字幕若在审阅范围内，以独立ID和清楚标识的章节纳入。

用户回传后先按ID与保存的原值比较，列出新增、删除、重复ID冲突及无法匹配项；可确定的改动继续处理，歧义只阻塞相关项。然后更新所有出现位置、关联英文和受影响布局，重新生成页码映射与核验报告。一个文字ID可对应多张画面，Word分页会变化，不能按页号猜映射。英文状态按项目策略，不用旧译文逆向覆盖中文。回填协议不等于已实现自动导入器，实际自动化能力需以已运行的脚本及结果为准。

## 文字画面PDF

PDF展示视频真实构图，不是文字清单或文档截图。每个不同文字组合／布局给落定状态；入场或变形影响理解时补关键中间态。页面按项目画幅，默认16:9；源于实际制作布局，登记坐标、尺寸、字体、颜色及出现方式。

按“不同文字组合／布局的出现记录”检查全量覆盖：分组总览便于读全文，不能替代各镜头中不同的实际组合。需要时提供分组与逐镜两种视图，同一组合可复用画面，但映射必须列全。仅要求选风格时按请求展示代表构图与关键状态。全量任务不能只交几张样例。

- 同一数据生成Word、文字注册表、PDF及ID→页码映射；保留章节书签、scene_id、源／成片时间、text_ids、状态页脚，审阅信息不遮画面。
- 修改入口默认MD，可按需同步Word；可用渲染静帧作PDF画面，但不称PNG为可编辑文本。
- 按策略预留英文与字幕区，两者分开；正式画面去除预留框和占位标签。
- 标明画面的生成依据：排版设计稿、源片参考帧合成或成片截帧，并标出素材到位情况。分组总览可能汇集不同时间出现的字，不能暗示全部同时上屏。字幕演示叠加不改变项目external／burned策略。未到素材可在审阅层作明确示意；不据此声称素材已检查。风格对比预览按[导演流程](storyboard-direction.md)，PDF本身不强制生成额外视频。
- 核对文字ID覆盖、实际文字与登记一致、长文换行、裁切、字号、面部及安全区避让；不截图回看PDF。静帧只能证明采样状态，运动另查。

## 可编辑PPT（仅按要求）

每镜采用稳定构图；文字、卡片、箭头及真实数据图表用原生对象，图片可替换。不要用整页PNG冒充可编辑PPT。玻璃／折射可局部近似，备注说明差异，文字与容器仍可编辑。

对象命名如`REV-0001.heading.zh`、`REV-0001.asset.main`。备注保存时码、素材序列、版本和未决项；早于落定帧的素材仍保留在清单。回写文字、坐标、尺寸、字体、裁切和层级变化，新增／复制对象明确映射。

## 回修与验收

按本次交付检查可打开、页幅、ID映射、文本溢出、来源和实际渲染；文稿用MD与稳定ID进行一次必要数据核对，不对Word/PDF截图回看。构图与动作直接遵循[视觉标准](visual-style.md)。真人录制和按需前期交付见[制作默认值](production-defaults.md)，此处不重复展开。不设置例行反复审阅；回修只更新受影响文字、译文、页面和片段；检查点追踪输入指纹，避免无条件重建已完成成果。明确未完成的用户校对和技术检查，不将工作版称为终审通过。

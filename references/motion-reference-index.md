# 按文案调用制作模块

本模型主导全片。先从原句判断信息任务、素材条件、情绪与节奏，再选技能和动作，吸收其有用规则并完成实际镜头；冲突按本次文案和制作条件裁决。外部规则不新增审批、强制截图或效果配额。

模块均存于 `modules/upstream/<source-id>/`；具体来源、缓存文件和更新分支见[motion-sources.json](motion-sources.json)。选用时先读本地ADAPTER，再读所需规则／源码；[更新方式](local-modules.md)自动关联原始GitHub。这里只是路由，不要求逐行加载。用户移除的来源登记在research-sources.json的excluded中，不再重新引入。

| 文案／制作需求 | 模块ID | 吸收和使用方式 |
|---|---|---|
| 代码动画构思 | [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | 动画代码案例，按文案意图挑案例并转成本片镜头；不按模型品牌选效果 |
| Seedance提示词 | [awesome-seedance](https://github.com/ZeroLu/awesome-seedance) | 仅在目标为Seedance时优化动作和运镜提示；不代替GPT/Gemini双提示词 |
| 参考片拆解 | [hypit](https://github.com/hypit-ai/hypit) | 从参考视频提取语义拍、素材层、锚词和可复用编辑结构，改编到自己的文案 |
| 风格与材料 | [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 按故事语气选择风格、材质和光线；全片统一到本项目tokens |
| 提示词案例 | [awesome-opus-5-5-video-prompts](https://github.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts) | 动画代码提示与视觉构思来源，按具体案例适配 |
| 故事到素材规划 | [vimax](https://github.com/HKUDS/ViMax) | 只吸收多角色规划与角色连续性，交GPT图片提示词和Gemini视频提示词，不运行生成流水线 |
| 营销剪辑 | [short-video-factory](https://github.com/YILS-LIN/short-video-factory) | 按卖点→证据→行动组织镜头；独立桌面程序按需作素材辅助，不接管母版 |
| 产品讲解 | [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | 产品演示、发布说明和Sprint叙事；选用组件前处理真实lib依赖，不能当官方Remotion |
| 自然语言剪辑 | [firered-openstoryline](https://github.com/FireRedTeam/FireRed-OpenStoryline) | 已有素材检索、粗剪与对话回修方法；选段与素材元数据进入本地Remotion工程 |
| 社媒脚本 | [social-media-skills](https://github.com/charlie947/social-media-skills) | LinkedIn语气、Reel脚本和标题方法；不自动发布或发送内容 |
| 主题营销 | [moneyprinterturbo](https://github.com/harry0703/MoneyPrinterTurbo) | 脚本、素材、旁白与字幕编排方法；README不能证明具有自动发布能力 |
| 影视解说服务 | [narrator-ai-cli](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill) | 收费CLI/账号型素材生产；只有实际选择服务时检查账户和额度 |
| 营销制作组织 | [openmontage](https://github.com/9018/openmontage) | 用户指定9018仓库，README指向calesthio；只纳入适合Remotion的制作方法，不接入其整套双引擎应用 |
| 图文解说 | [pixelle-video](https://github.com/zesks/pixelle-video) | 文案分段→配图→旁白→音乐方法，生成资产回到本工程合成 |
| Vox拼贴 | [vox-director](https://github.com/Alisa0808/vox-director) | 论点→证据→抠图层→视觉揭示；移除固定云服务依赖，用本地时间轴组合 |
| 手绘科普 | [doodle-anim](https://github.com/feitangyuan/doodle-anim) | 程序绘制角色、姿态和图解；Canvas按帧绘制，非仅头像生成 |
| 叙事分镜 | [openstory](https://github.com/openstory-so/openstory) | 故事拆镜、角色与关键帧连续性；仅需方案时交提示词，不启动外部平台 |
| 手绘故事 | [handdrawn-story-studio](https://github.com/masonweb3/handdrawn-story-studio) | 实际来源masonweb3，README说明9:16母版与有限场景实现；按需扩展，不宣称全自动成熟产线 |
| 手绘揭示 | [story-to-handdrawn-video](https://github.com/iilovelive/story-to-handdrawn-video) | Remotion文字→画稿→色彩揭示与翻页；3:4和默认彩铅可按文案改 |
| 数字人素材 | [avatar-forge](https://github.com/LycheeAILab/avatar-forge) | 仅avatar-only模式输出原始人物MP4，后续由本工程15秒全屏及小窗组织 |
| 穿搭营销 | [female-outfit-director](https://github.com/liyue-aigc/female-outfit-director) | 同一成年主体与服装一致性、拼贴首帧和节奏换装；输出所需素材规划 |
| 肖像动作素材 | [liveportrait](https://github.com/KlingAIResearch/LivePortrait) | 照片+驱动视频生成面部动作；外部模型/依赖按实际需要配置，检查相关模型许可 |
| 口型素材备选 | [wav2lip](https://github.com/Rudrabha/Wav2Lip) | 旧版Wav2Lip模型为非商业研究用途；商业任务改选可合法使用的方案 |
| 长切短 | [youtube-shorts-generator](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator) | 转写、语义高光与竖屏裁切方法，沿用源时码与完整语义 |
| 长切短 | [autoclip](https://github.com/artbyjazi/autoclip) | 本地高光、说话人跟随与字幕；独立应用按需提供片段/EDL，母版统一合成 |
| 动效工艺 | [claude-motion](https://github.com/whaleyxbt/claude-motion) | 缓动、阅读停留、字体尺度、纹理与有动机转场；数值是参考而非配额 |
| Remotion动效 | [claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | 错峰、遮罩与动作节奏；持续运动、每图推拉等固定规则由文案裁决 |
| 核心运行库 | [remotion](https://github.com/remotion-dev/remotion) | Remotion主工程，包与锁文件统一版本 |
| 官方实现技能 | [remotion-official](https://github.com/remotion-dev/skills) | 读取官方动画、字幕、渲染与时间轴规则；与本机同名第三方扩展区分 |
| 口播动效 | [video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft) | 108卡按输入与语义检索，适配到本片；非商业许可，商业使用需满足作者授权 |
| 艺术动画 | [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) | 让材料、造型和画内对象承担叙事；按内容安排动作 |
| 模块发现 | [motion-skills](https://github.com/iart-ai/motion-skills) | 实际是55技能/18分包索引；按需要选择独立包，不整套加载商业平台流程 |
| 运动语言 | [lottiefiles-motion-design](https://github.com/LottieFiles/motion-design-skill) | 动作目的、曲线、错峰与时长；UI时间值按视频节奏调整 |
| Canvas叙事 | [animate](https://github.com/cth9191/animate) | 代码绘制、形状接力与程序声音；按帧接入Remotion |
| 复杂节奏 | [claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | HTML/Canvas镜头与声音事件方法；可采样后合成或移植为Remotion组件 |
| GSAP辅助 | [gsap](https://github.com/greensock/GSAP) | 暂停timeline按母版时间seek；不以实时ticker推进导出 |
| Lottie素材 | [lottie-web](https://github.com/airbnb/lottie-web) | 矢量动画与图标，按统一时间采样或用同版本@remotion/lottie |
| Wise Motion | [wise-motion](https://github.com/WiseWong6/wise-motion) | 动作需求→主体/关系/起末状态→匹配源码；组合、字幕、配色由本模型按文案决定 |
| Motion辅助 | [motion](https://github.com/motiondivision/motion) | 暂停动画并设置time，或使用纯函数求值；不让浏览器真实时间控制导出 |
| 地图数据处理 | [mapshaper](https://github.com/mbloch/mapshaper) | 本地矢量边界清理、简化、裁切和SVG/GeoJSON导出 |

## 常用检索

```text
python scripts/query_motion_library.py --knowledge "税收 对比 表格"
python scripts/query_motion_library.py --talkcraft "引用 强调" --input 截图 --limit 6
node modules/upstream/wise-motion/scripts/match.mjs "路线汇聚成一个节点" --details
node modules/upstream/wise-motion/scripts/show.mjs <条目ID>
node modules/upstream/wise-motion/scripts/export.mjs <条目ID> --out-dir <工程组件目录>
```

Wise Motion本地目录包含315个单动作、99个插画、48个组合，共462项（当前上游目录统计）。文字动效、转场和插画都可参与镜头；其上游“仅显式调用”设置不限制本技能已获授权的按需调用。导出代码后补齐选中条目的依赖／资产并接入本片。

网页案例缓存与既有语义知识卡也属于制作体系。选中案例后取其实际源码／适用素材或按机制实现；没有匹配项时原创设计。Talkcraft的108卡按[专用路由](talkcraft-motion-routing.md)使用；历史地图按[地图模块](historical-maps.md)处理。

Claude版教程不因名字排除；只调整工具、路径、模型专属命令与不适用的工作流。独立应用可输出素材、选段、时间戳或布局数据供本工程使用，不让另一套主流程重复编剧、配音和重渲整片。收费服务、GPU模型及宿主连接只记录真实状态。

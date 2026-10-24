# 本地安装与运行支持

技能规则、动作源码和插件文件保存在本技能的modules目录，原始GitHub来源与更新见[本地模块](local-modules.md)。安装按已授权范围自主完成，缺项只影响实际需要的模块。文本任务不安装整个视频软件栈。

## Remotion工程

已有工程沿用package.json与锁文件；新工程复制`assets/remotion-kit/`。Python最低3.10，Node最低18，推荐22/24 LTS；Remotion与所有@remotion包版本一致。随附工程准确版本以package.json为准，不在文档重复维护版本号。

```text
python scripts/check_installation.py --project-root <工程>
python scripts/setup_support.py --project-root <工程> --install
python scripts/setup_support.py --project-root <工程> --feature maps --feature charts --install
```

默认只含core；仅在需要时加入documents、images、maps、charts、diagrams、doodle、collage、logo、asr、review。用`--with-references`准备所选功能的本地来源。媒体与音轨处理需要实际可用的FFmpeg/FFprobe；已有Remotion compositor可提供路径。

## 可组合能力

| 能力 | 接入 |
|---|---|
| GSAP | 本地gsap，暂停timeline后按母版时间seek |
| Motion | 本地motion，暂停并设置time或纯函数采样 |
| Lottie | @remotion/lottie与工程同版本，素材图片和字体本地化 |
| Canvas / SVG | 原生帧驱动绘制；不另设播放时钟 |
| 地图 | 本技能assets/map-kit已提供Mapshaper、d3-geo与SVG绘图器；QGIS按需作历史图配准 |
| 图表／图解 | D3做数据与布局；Rough.js固定seed；Mermaid产SVG后适配tokens |
| 词级对齐 | 仅已有录音缺可靠时间戳时启用ASR；不自动删改原声 |
| 文档 | 默认MD；确需Word/PDF时调用可用文档工具，不截图回看 |

源码与技能可本地保存；外部模型、GPU、账户和宿主连接仍需真实可用，不能因文件存在就写成已安装。模块适用时直接吸收并实施，运行报错再修具体问题，不每次重复全栈检查。

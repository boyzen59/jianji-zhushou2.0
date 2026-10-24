# 历史地图、军事调度与边界变化

按文案提取年代、地名、行动者、路线、控制范围和变化节点，再决定地图景别与图层。地图是解释事实的画面；漂亮的纹理不能代替历史依据。

## 本地绘图工具

- **Mapshaper**：本技能`assets/map-kit/`内安装，负责GeoJSON/TopoJSON/Shapefile裁切、投影、简化与导出。维护拓扑的简化适合视频中复杂边界。
- **SVG绘图器**：同目录`draw-map.mjs`把分层GeoJSON、地名与路线生成可编辑SVG及投影参数。已有Remotion工程可按输出的图层ID、路径与地理坐标做揭示、调度箭头和镜头移动。
- **QGIS**：需要扫描古地图配准、编辑历史疆界、地形栅格、复杂投影时选用[QGIS](https://qgis.org/)。这是重型数据准备工具，当前包不伪称已经装好桌面QGIS；可用已安装QGIS／PyQGIS，或在确实需要时安装到本技能tools目录。
- **Inkscape**：需要人工矢量细修时可选[Inkscape](https://inkscape.org/)；普通地图直接用本地SVG工具，不为此强制安装桌面软件。

```text
# 在 assets/map-kit 目录使用；依赖缺失时 npm ci
npx mapshaper input.geojson -simplify 8% keep-shapes -o format=geojson clean.geojson
node draw-map.mjs scene.json map.svg
```

scene.json包含title、period、layers（id/date/source/geojson/fill/stroke，可设disputed）、routes（id/date/source/coordinates，可设approximate）、places（name/coordinates/dx/dy），以及画幅和theme。geojson可内嵌或相对路径；每个阶段边界独立一层。导出map.svg和map.map.json。字体、线宽、强调色适配本片tokens；默认是低饱和纸本地图，可改为深色战术图或其他方向。

## 数据怎样选择

现代地形与海岸可查[Natural Earth](https://www.naturalearthdata.com/)，现代道路／地物可查[OpenStreetMap](https://www.openstreetmap.org/)并保留署名与许可。它们的现代国界不用于证明历史疆界。

中国历史地理按年代查[CHGIS](https://chgis.fas.harvard.edu/)与可引用的学术地图；其他时期使用有出处的历史地图、GIS数据或档案。扫描图先在QGIS配准，保留原图、控制点、投影与误差说明。缺可靠边界时用标明“范围示意”的区域，不生成精确国界。

军事调度按文案事件列出日期、起终点、途经点、方向和依据。史实缺乏精确路线时用虚线与“路线示意”；箭头宽度只有在有兵力数据时编码数量。多支军队通过颜色／线型／标签区分，不靠任意粗细制造规模差。

国界变化以各日期真实边界作为阶段状态，按语义cue切换／遮罩揭示；行政归属变化、军事控制和主张范围分层标注。不同拓扑的多边形不强行点对点形变成虚假中间疆界。争议或不确定范围用虚线／斜纹和简短题注。

全部路线、城市、疆界保持同一投影与相机。SVG路线可用pathLength=1按进度描边，兵力标记沿同一地理路径采样，年份与边界共用cue。地图设计先保证位置、层级与可读性，避免重复缩放和装饰HUD遮挡史实。

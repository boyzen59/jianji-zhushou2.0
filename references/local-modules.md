# 本地完整包与启动更新

每次启动先运行scripts/startup.py。默认检查本技能GitHub仓库和全部保留模块的最新HEAD，不按日期跳过。首次补齐完整仓库包，后续只在远端变化或包文件缺失时更新。

包保存在modules/upstream/<source-id>，包括源码、配置、依赖清单和原库提供的运行资产；跳过视频、node_modules和用户已排除的渲染器目录。Git对象缓存位于modules/.package-cache，本地修改的新上游候选位于modules/incoming，退出当前版本的旧文件进入modules/history。原文件、LICENSE与NOTICE保留；上游项目未提供的私有服务或模型不可能靠索引补出，必须记录实际缺项。

```text
python scripts/startup.py
python scripts/startup.py --source video-shotcraft
```

同一项目已经渲染的片段与锁文件保持其版本；技能启动获取的最新模块在本次需要的镜头中由模型判断与适配。所有模块冲突由模型按文案裁决，外部审批链和固定审美配额不接管主流程。

新增模块登记其原始GitHub仓库，放入同一更新机制。research-sources.json中excluded记录的用户移除项目不重新引入。公开分发保留各上游许可，许可未明确的原文包由使用者从原库下载，本机已下载内容不因公开包的分发范围而丢失。

网页案例必须区分公开源码和展示页面。Prompt Motion当前33个页面未给工程源码链接，逐条记录no_source_code_link_on_case_page；视频按用户要求不下载。Wise Motion与Video Shotcraft等有公开仓库的模块直接获取完整包，不再只存规则与目录。

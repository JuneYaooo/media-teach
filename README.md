# 自媒体实战课堂

用你自己的账号，在 WorkBuddy 里学会用开源 Skills 完成：找对标 → 账号诊断 → 视频拆解（逆向） → 爆款复刻 → 视频复刻 → 违规风险审核。

**[进入课程网站](https://juneyaooo.github.io/media-teach/)**

- 每课先用一张流程图讲技能怎么干活，再给提示词（只写需求），最后看你会拿到什么
- 录屏用演示账号「阿夏的AI片场」完整演示（后台数据虚构，样片自制；找对标是平台实搜）
- 共 15 节：00 总纲、01 入门、六个模块各 2 节、07 结课
- 工具：[JuneYaooo](https://github.com/JuneYaooo) 的开源自媒体项目，包括用 [cheap-claude-video](https://github.com/JuneYaooo/cheap-claude-video) 做爆款复刻，以及 Hypit、HyperFrames 等开源项目
- AI 视频生成两条路线：开源 MiniMax H3（自己在 AutoDL 租 GPU，或直接调 MiniMax / RunningHub 的 API），或 HyperFrames 代码视频
- 演示与录屏：WorkBuddy

## 使用

1. 安装 WorkBuddy。
2. 准备你自己的主页链接、后台数据截图、一两条想学的对标爆款。
3. 新建一个工作文件夹，在 WorkBuddy 里选为工作空间，从 01 入门课开始。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `课程规划/` | 整体规划、演示数据设计、v0.7 改版方案 |
| `自媒体教程/课程/*.md` | 讲义源稿 |
| `录屏方案/演示素材/` | 演示账号的素材，只给录屏用（虚构数据、样片、评论区、发布资料） |
| `录屏方案/` | 给 Codex 的录屏与剪辑规格：通用规范、实践手册、样片制作、每课逐步操作与旁白 |
| `scripts/build_site.py` | 生成静态网站 |
| `scripts/materials/` | 演示素材里截图的生成模板 |

## 编辑课程

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build_site.py
```

没有录屏的课程页会显示“录屏制作中”。

## 内容范围

演示账号的作品、数据、评论都是编的；样片是课程自己做的，人物都是 AI 原创角色。平台规则会变，审核结论以平台最新公告为准。

课程结构参考 [medical-teach](https://github.com/JuneYaooo/medical-teach)。

# AI 视频博主课堂

在 WorkBuddy 里用开源 Skills，帮一个 AI 视频博主完成：找对标 → 账号诊断 → 视频拆解（逆向） → 爆款复刻 → 视频复刻 → 违规风险审核。

**[进入课程网站](https://juneyaooo.github.io/media-teach/)**

- 贯穿案例：虚构账号「阿夏的 AI 片场」（抖音 + 小红书）
- 共 15 节：00 总纲、01 入门、六个模块各 2 节、07 结课
- 工具：[JuneYaooo](https://github.com/JuneYaooo) 的开源自媒体项目，加上 Hypit、HyperFrames 等 GitHub 热门项目
- AI 视频生成只用两条低成本路线：AutoDL 上的开源 MiniMax H3，或 HyperFrames 代码视频
- 演示与录屏：WorkBuddy

## 使用

1. 安装 WorkBuddy。
2. 在网站首页下载 `AI视频教程-练习包.zip` 并解压，得到 `阿夏的AI片场` 文件夹（资料、空的成果文件夹、参考结果）。
3. 在 WorkBuddy 新建任务时把这个文件夹选为工作空间，从 01 入门课开始。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `课程规划/` | 整体规划、练习包与课程数据设计（所有数字和核对点的唯一来源） |
| `AI视频教程/课程/*.md` | 讲义源稿 |
| `AI视频教程/资料/` | 练习包资料（虚构数据、样片、评论区、发布资料） |
| `AI视频教程/成果/` | 作者试跑的参考结果（打包为“参考结果”） |
| `录屏方案/` | 给 Codex 的录屏与剪辑规格：通用规范、实践手册、样片制作、每课逐步操作与旁白 |
| `scripts/build_site.py` | 生成静态网站和练习包 |
| `scripts/materials/` | 练习资料里截图的生成模板 |

## 编辑课程

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build_site.py
```

构建脚本同时重新生成练习包。没有录屏的课程页会显示“录屏制作中”。

## 内容范围

账号、作品、数据、评论均为虚构；样片为课程自制，人物均为 AI 原创角色。平台规则会变，审核结论以平台最新公告为准。

课程结构参考 [medical-teach](https://github.com/JuneYaooo/medical-teach)。

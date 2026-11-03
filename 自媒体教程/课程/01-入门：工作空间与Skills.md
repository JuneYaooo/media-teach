# 01 入门：工作空间与 Skills

这一课做四件事：把练习文件夹设为 WorkBuddy 的工作空间，检查电脑环境，装好本课程要用的技能，再让 WorkBuddy 写出第一份账号摘要，并当场抓出它写错的数字。

课前文件：

- [账号档案.md](../资料/账号档案.md)：阿夏的账号情况，摘要要用
- [自己账号-作品数据.csv](../资料/自己账号-作品数据.csv)：42 条作品的播放、点赞、完播等数据

这些文件都在练习包里。解压后按第 1 步把 `阿夏的AI片场` 文件夹选为工作空间即可。

## 快速实操：照着提示词做一遍

先按“完整方法”第 1 步选好工作空间，再依次提交下面的提示词。实操 2 安装技能时，遇到填 API Key 的地方，自己在终端或文件里填，不要贴进对话。

### 实操 1

```text
请检查这台电脑有没有装好：Python 3.10 以上、Node.js 22 以上、ffmpeg、git。逐个运行查看版本的命令，把结果列成一张表（工具、要求版本、实际版本、是否满足）。缺的告诉我在 macOS 上怎么装，先不要自己安装。
```

### 实操 2

```text
请帮我安装 social-account-doctor 技能，安装说明在：
https://raw.githubusercontent.com/JuneYaooo/social-account-doctor/main/docs/install.md
请先告诉我你打算把技能装到哪个目录、为什么装在那里能被识别，我确认后再装。需要填 API Key 时停下来，告诉我写到哪个文件的哪一行，我自己填，不要在对话里显示任何 Key。装完告诉我是否需要重启。
```

它说明打算装到哪个目录后，看一眼路径合理，再回复：

```text
确认，就装到这个目录。
```

### 实操 3

```text
请读取 资料/账号档案.md 和 资料/自己账号-作品数据.csv，写一份 200 字左右的账号现状摘要：粉丝数、作品数、更新频率、一般一条作品有多少播放、表现最好和最差的内容类型。需要计算的数字请写脚本算，不要估算；每个数字注明来自哪个文件。保存到 成果/01/账号现状摘要.md。
```

### 实操 4

```text
请核对摘要里的两处数字：
1. 账号档案里抖音粉丝是 5,800，这是净值；6,240 是累计新增关注，没有扣掉 440 个取关。摘要里的粉丝数应写 5,800。
2. 42 条作品的播放均值约 1,152，但被几条爆款拉高了；中位数是 655。“一般一条有多少播放”应该用中位数，均值可以作为补充，并说明为什么两者差这么多。
请修改 成果/01/账号现状摘要.md，并在文末列出每个数字的来源文件和算法。
```

## 完整方法：理解每一步，迁移到自己的账号

WorkBuddy 是一个能在你电脑上干活的 AI 助手：你用中文说要做什么，它会读指定文件夹里的资料、调用技能、运行脚本，把结果存成文件。这一课先把“干活的地方”和“干活的方法”准备好，再做一个小任务，练习最重要的习惯：**AI 说完了，你要打开文件核对。**

| 项目 | 内容 |
| --- | --- |
| 难度 | 1 |
| 时长 | 40 分钟（含安装） |
| 前置 | 无 |
| 产出 | 环境检查表、已安装的技能、账号现状摘要 |
| 用到的工具 | WorkBuddy；social-account-doctor、benchmark-outlier-radar 等本课程技能 |

## 1. 选择工作空间

1. 打开 WorkBuddy，点左上角“新建任务”。
2. 在输入框下方点“选择工作空间”，选“打开本地文件夹”。
3. 选中解压出来的 `阿夏的AI片场` 文件夹。
4. 输入框下方出现 `阿夏的AI片场`，就选好了。

以后每课都先确认这里显示的是 `阿夏的AI片场`。没选对，Agent 读不到资料，结果也会存错地方。

**为什么这样做**：资料放在 `资料/`，结果放在 `成果/`。每个提示词都写清输入文件和输出位置，你才能找到结果，并确认它真的生成了文件。

## 2. 检查电脑环境（实操 1）

本课程的技能会在你电脑上运行脚本，需要这几样：

| 工具 | 要求 | 谁要用 |
| --- | --- | --- |
| Python | 3.10 以上（Capsule Cinema 要 3.12） | 大部分技能的脚本 |
| Node.js | 22 以上 | Hypit、HyperFrames |
| ffmpeg | 任意较新版本 | 拆视频、剪视频 |
| git | 任意版本 | 下载技能仓库 |

**检查点**：表里每一行都要有“实际版本”。Agent 说“已安装”但没给版本号，让它把命令输出贴出来。

## 3. 什么是技能（Skill）

技能就是一份写好的操作规则，有的还带脚本。它规定某类任务怎么做：先读什么、怎么算、结果存成什么样、哪些事不能做。装上以后，你在提示词里点名“请使用 XX 技能”，Agent 就会照着规则做。

每个技能文件夹里都有一个 `SKILL.md`：

- 最上面的 `name` 是技能名，`description` 写什么时候该用它。
- 正文是具体步骤和边界。

装之前花两分钟读一遍，重点看三件事：**它会运行什么脚本、要不要 API Key、会不会联网或花钱。**

## 4. 安装本课程的技能

WorkBuddy 有两种装法：

- **界面上传**：左侧栏“专家·技能·连接器”→ 顶部“技能”→ 右上角“添加技能”→“上传技能”，选一个技能的 zip 包。适合没有额外依赖、纯规则或只用 Python 标准库的技能。
- **让 WorkBuddy 自己装**：把技能的安装说明链接发给它（实操 2 的写法），它会下载仓库、装依赖、提示你填 Key。适合要装 Python/Node 依赖的技能。

装完都到“已安装”列表里确认开关是开着的。如果提示同名技能已存在，说明装过了，确认开关打开即可。

### 全课程技能清单

不用一次装完。前四个现在就装；做视频的工具学到对应模块时再装也行，装法都在这里。

| 工具 | 用在 | 装法 | 需要的 Key 或账号 |
| --- | --- | --- | --- |
| [social-account-doctor](https://github.com/JuneYaooo/social-account-doctor) | 1-1、2-1、2-2、3-2、4-1 | 让 WorkBuddy 按 [安装说明](https://raw.githubusercontent.com/JuneYaooo/social-account-doctor/main/docs/install.md) 装（实操 2） | 看图/看视频的多模态模型 Key（必填，2-2、3-2 要用）；TikHub Key 可选，本课程不需要 |
| [benchmark-outlier-radar](https://github.com/JuneYaooo/benchmark-outlier-radar) | 1-2 | GitHub 页面点 Code → Download ZIP，再“上传技能” | 不需要，纯本地脚本 |
| [rea-video](https://github.com/JuneYaooo/rea-video) | 3-1、5-1 | 对 WorkBuddy 说“安装 https://github.com/JuneYaooo/rea-video ”（技能在仓库的 `skills/rea-video/`） | 可选：一个能看视频的模型（Gemini、豆包等），不配也能用 |
| [self-media-compliance-review](https://github.com/JuneYaooo/self-media-compliance-review) | 6-1、6-2 | Download ZIP 后上传，或让 WorkBuddy 按 README 装 | 不需要；默认不联网 |
| [Capsule Cinema](https://github.com/JuneYaooo/cheap-claude-video) | 5-1、5-2 | 让 WorkBuddy 按 [安装说明](https://raw.githubusercontent.com/JuneYaooo/cheap-claude-video/main/docs/install.md) 装（要 Python 3.12） | 演示里只用它做分镜和质检；走“直接调 API”时，它也是生成渠道（MiniMax 或 RunningHub 的 API Key） |
| [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) | 5-1 | 让 WorkBuddy 克隆仓库，把 `skills/` 下的 `minimax-h3`、`h3-prompt-writing`、`autodl-app-instance` 放进 WorkBuddy 的技能目录 | AutoDL 账号和 API Token（只在“自己租 GPU”时需要） |
| [Hypit](https://github.com/hypit-ai/hypit) | 4-2 | 终端运行 `npx skills add hypit-ai/hypit -g`，再确认 WorkBuddy 能识别 | 代码视频路线不需要模型 Key |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | 5-2 | 终端运行 `npx hyperframes skills update`（只装核心技能） | 不需要 |
| [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) | 3-1（只讲不演示） | 本地用 Docker 运行 | 抖音需要自己的 Cookie |

> 以试跑为准：social-account-doctor 和 self-media-compliance-review 的说明里写了支持 WorkBuddy；其余工具的说明只写了 Claude Code、Codex 等。用 `npx skills add` 装的技能默认放在通用技能目录，WorkBuddy 能否直接识别，要装完后到“已安装”列表确认。看不到时，让 WorkBuddy 把技能文件夹复制到它自己的技能目录，或打包成 zip 用“上传技能”导入。

**安全提醒**：

- API Key、Token、Cookie 只写进本地的 `.env` 或配置文件，不要贴进对话，不要截图发给别人。
- 装第三方技能前看一眼它会运行什么脚本、会不会联网。
- 要花钱的步骤（GPU、付费接口），技能都应该先问你。没问就开始扣费的，停下来检查。

### 去哪找更多技能

[awesome-ai-media-skills-cn](https://github.com/JuneYaooo/awesome-ai-media-skills-cn) 整理了 AI 视频和自媒体方向的技能、MCP 服务器和工具，按视频生成、多平台运营、内容自动化分类。想找新工具时先查这里，[awesome-ai-media-cn](https://github.com/JuneYaooo/awesome-ai-media-cn) 则收录了 150 多个开源项目。

## 5. 第一个任务：账号现状摘要（实操 3、4）

技能装好后，做一个不需要技能的小任务，确认 WorkBuddy 能读写工作空间，也练习核对。

提交实操 3。等文件卡片出现后，打开 `成果/01/账号现状摘要.md`，对着资料检查两个数字：

**检查点 1：粉丝数。** 账号档案写的抖音粉丝是 5,800。作品数据里 `new_followers` 一列加起来是 6,240，那是累计新增关注，没扣掉 440 个取关。摘要写 6,240 就错了。

**检查点 2：“一般一条多少播放”。** 42 条作品的播放均值约 1,152，中位数 655。阿夏有几条九千多、六千多的爆款，把均值拉高了。说“一般一条一千多播放”会让人高估账号的常态。描述“一般”，用中位数更准。

发现问题就提交实操 4。改完再打开文件看一遍，并到电脑的 `成果/01/` 文件夹里确认文件真的存在，不能只听 AI 说“已保存”。

**为什么这样做**：后面每一课的结论都建立在数字上。粉丝数错了，“量级差几倍”就会算错；均值当常态，“这条算不算爆”就会判错。

## 6. 写提示词的四个要素

每个任务写清楚四件事，结果会稳定很多：

| 要素 | 例子 |
| --- | --- |
| 用什么技能 | 请使用 social-account-doctor 技能 |
| 输入是什么 | 资料/账号档案.md、资料/自己账号-作品数据.csv |
| 要做什么、有什么限制 | 不联网搜索；数字用脚本算，不要估算；注明来源 |
| 结果存到哪 | 保存到 成果/01/账号现状摘要.md |

## 7. 自查清单

- [ ] 输入框下方显示的工作空间是 `阿夏的AI片场`
- [ ] 环境检查表每一项都有实际版本号
- [ ] social-account-doctor、benchmark-outlier-radar 在“已安装”列表里，开关打开
- [ ] API Key 没有出现在对话、截图或录屏里
- [ ] 摘要里粉丝数是 5,800，“一般一条”用的是中位数 655
- [ ] `成果/01/账号现状摘要.md` 在电脑文件夹里真的存在

## 8. 常见问题

**提交后没看到文件？** 先看输入框下方的工作空间是不是 `阿夏的AI片场`。再打开电脑上的 `成果` 文件夹确认。

**装技能时 Agent 想把 Key 打印出来？** 让它停下，改成告诉你写到哪个文件，你自己填。

**“已安装”里看不到用命令装的技能？** 重启 WorkBuddy 再看。还看不到，让 WorkBuddy 把技能文件夹打包成 zip，用“上传技能”导入。

**为什么不直接用均值？** 均值容易被一两条爆款拉高。自媒体数据大多是“少数很高、多数一般”，看常态用中位数，看有没有爆款看最高值。

## 9. 练习

把你自己账号最近 20 条作品的播放、点赞、评论整理成一张表（列名参照 `自己账号-作品数据.csv` 的前 8 列），让 WorkBuddy 算均值和中位数，看看两者差多少。

## 下一课

1-1 扫同赛道，筛出真对标：用 social-account-doctor 从 4 个候选账号里挑出值得学的 2–3 个，并排除一个“看着像、其实不是同赛道”的账号。

## 本次任务结果与核对

预期核对点：

- 粉丝数应为 **5,800**（净值），不是 6,240（累计新增关注，未扣 440 个取关）。
- “一般一条多少播放”应用中位数 **655**；均值 **1,152** 被爆款拉高，只能作补充说明。
- 环境检查表每项都有实际版本号；技能在“已安装”中处于开启状态。
- Key 没有出现在对话里。

> 作者试跑结果待补：实际产物、发现的问题与修订、交付文件链接。

## 操作画面

截图待录制后补充。

[观看 01 实操录屏](../录屏/01-WorkBuddy实操.mp4) · [字幕](../录屏/01-WorkBuddy实操.vtt)

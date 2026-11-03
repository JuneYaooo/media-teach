"""Build the static course site from the Markdown lessons.

Recordings are optional: a lesson without `录屏/<code>-WorkBuddy实操.json` shows a
"录屏制作中" notice instead of the video player.
"""
from pathlib import Path
import html, json, re, zipfile
from urllib.parse import quote
import mistune

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '自媒体教程'
PACK_NAME = '自媒体教程-练习包.zip'
PACK_DIR = '阿夏的AI片场'
WORKBUDDY_URL = 'https://www.workbuddy.cn'
GITHUB_URL = 'https://github.com/JuneYaooo/media-teach'
SITE_NAME = '自媒体实战课堂'

TRACKS = {
    'start': dict(name='入门', codes=['00', '01'], desc='认识案例、练习包和 WorkBuddy，装好本课程用到的技能。'),
    'm1': dict(name='① 找对标', codes=['1-1', '1-2'], desc='谁才是真对标？对标这周出了什么爆款？'),
    'm2': dict(name='② 账号诊断', codes=['2-1', '2-2'], desc='我的号差在哪？这一条为什么不爆？'),
    'm3': dict(name='③ 视频拆解（逆向）', codes=['3-1', '3-2'], desc='爆款的画面、剪辑、声音、钩子和文案是怎么做的？'),
    'm4': dict(name='④ 爆款复刻', codes=['4-1', '4-2'], desc='保留爆款的套路，换成我的内容。'),
    'm5': dict(name='⑤ 视频复刻', codes=['5-1', '5-2'], desc='按拆解结果，把画面真正做出来。'),
    'm6': dict(name='⑥ 违规审核', codes=['6-1', '6-2'], desc='这条能不能发？账号为什么被限流？'),
    'end': dict(name='结课', codes=['07'], desc='一条视频从找对标走到可发布。'),
}
ORDER = [c for t in TRACKS.values() for c in t['codes']]
FOCUS = {
    '00': '课程路线、贯穿案例、练习包和两条视频生成路线。',
    '01': '设好工作空间，装好技能，学会打开文件核对结果。',
    '1-1': '从候选账号里筛出真对标，排除看着像的干扰项。',
    '1-2': '用中位数倍数找出对标的异常爆款，选出本周要拆的。',
    '2-1': '对比对标，看清自己的强项、短板和下一步动作。',
    '2-2': '读后台数据，找出一条作品没起量的真正原因。',
    '3-1': '逐镜拆出 AI 短剧的画面、花字、剪辑和声音。',
    '3-2': '拆钩子、结构和评论区，整理成爆款拆解卡。',
    '4-1': '沿用爆款结构，写出自己选题的脚本和标题封面。',
    '4-2': '用 Hypit 把爆款克隆成工作流，批量出变体。',
    '5-1': '在 AutoDL 上用开源 H3 还原 AI 镜头。',
    '5-2': '用 HyperFrames 复刻花字和动效，存成可复用配方。',
    '6-1': '发布前做五级风险审核，按证据修改后复审。',
    '6-2': '排查限流原因，区分平台规则和经验，准备申诉。',
    '07': '把六个模块串起来，交付一个可发布的作品包。',
}
EXTRA_META = {'00': {'产出': '选定学习顺序，下载练习包'}}
LEVEL = {'1': '入门', '1-2': '基础', '2': '基础', '2-3': '进阶', '3': '进阶'}
META_KEYS = ['难度', '时长', '前置', '产出', '用到的工具']
CODE_RE = r'(?<![0-9-])(?:[1-6]-[12]|0[017])(?![0-9-])'

md = mistune.create_markdown(plugins=['table', 'strikethrough', 'task_lists', 'url'])


def esc(s): return html.escape(str(s), quote=True)
def url(p): return quote(str(p), safe='/')
def track_of(code): return next(k for k, t in TRACKS.items() if code in t['codes'])


def parse_meta(code, text):
    meta = {}
    for key in META_KEYS:
        m = re.search(r'^\| ' + key + r' \| (.+?) \|\s*$', text, re.M)
        if m: meta[key] = m.group(1).strip()
    meta.update(EXTRA_META.get(code, {}))
    return meta


def short_prereq(s):
    while re.search(r'（[^（）]*）', s): s = re.sub(r'（[^（）]*）', '', s)
    return re.sub(r'\s*[；、，]\s*', ' · ', s).strip()


def link_codes(s, prefix=''):
    out, last = '', 0
    for m in re.finditer(CODE_RE, s):
        l = by_code.get(m.group(0))
        out += esc(s[last:m.start()])
        out += f'<a href="{prefix}{url(l["html"])}">{esc(m.group(0))}</a>' if l else esc(m.group(0))
        last = m.end()
    return out + esc(s[last:])


lessons = []
for code in ORDER:
    found = sorted((SITE / '课程').glob(code + '-*.md'))
    if not found:
        print(f'skip {code}: lesson file not written yet')
        continue
    p = found[0]
    text = p.read_text()
    title = text.splitlines()[0].lstrip('# ')
    display = re.sub(r'^' + re.escape(code) + r'[：:\s]*', '', title)
    video = SITE / '录屏' / f'{code}-WorkBuddy实操.mp4'
    vjson = video.with_suffix('.json')
    chapters = json.loads(vjson.read_text())['chapters'] if vjson.exists() and video.exists() else None
    lessons.append(dict(code=code, path=p, html=p.with_suffix('.html').name, text=text, title=title,
                        display=display, video=video, chapters=chapters,
                        meta=parse_meta(code, text), track=track_of(code)))
by_code = {l['code']: l for l in lessons}
ORDER = [l['code'] for l in lessons]
for t in TRACKS.values(): t['codes'] = [c for c in t['codes'] if c in by_code]


# ---------- practice pack ----------
def build_pack():
    """Zip the practice workspace. Fixed timestamps keep the file stable between builds."""
    target = SITE / PACK_NAME
    readme = f'''{SITE_NAME} · 练习包

1. 把整个“{PACK_DIR}”文件夹放在你方便找到的位置。
2. 打开 WorkBuddy，点击“新建任务”→“选择工作空间”→“打开本地文件夹”，选中“{PACK_DIR}”。
3. 打开课程网站，从“01 入门”开始，把每课的提示词复制到 WorkBuddy。

文件夹说明
- 资料/：每课要读取的练习文件（账号档案、作品数据、对标快照、爆款样片、评论区、发布资料等）。
- 成果/：空文件夹，你每课的结果保存在“成果/课号/”。
- 参考结果/：课程作者实际跑出的结果，用来和你的结果对照。
  跳过某课时，把对应文件夹复制到“成果/”。例如没做 3-1 想直接学 5-1，就把“参考结果/3-1”复制成“成果/3-1”。
  （较大的成片视频没有放进练习包，可在课程网页上直接播放。）

账号、作品、数据、评论均为虚构；样片为课程自制，人物均为 AI 原创角色。

课程网站：https://juneyaooo.github.io/media-teach/
'''
    files = [(f, f'{PACK_DIR}/' + str(f.relative_to(SITE))) for f in sorted((SITE / '资料').rglob('*')) if f.is_file()]
    if (SITE / '成果').exists():
        files += [(f, f'{PACK_DIR}/参考结果/' + str(f.relative_to(SITE / '成果'))) for f in sorted((SITE / '成果').rglob('*'))
                  if f.is_file() and f.stat().st_size < 5_000_000]
    samples_ready = any((SITE / '资料/爆款样片').glob('*.mp4'))
    files = [(f, n) for f, n in files
             if f.name != '.DS_Store' and not (f.name == '样片待制作.txt' and samples_ready)]

    def info(name):
        zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = (0o40755 if name.endswith('/') else 0o100644) << 16
        return zi
    with zipfile.ZipFile(target, 'w') as z:
        z.writestr(info(f'{PACK_DIR}/开始前请读.txt'), readme)
        z.writestr(info(f'{PACK_DIR}/成果/'), '')
        for f, name in files: z.writestr(info(name), f.read_bytes())
    return target.stat().st_size


pack_size = build_pack()
pack_label = f'{pack_size / 1024 / 1024:.1f} MB' if pack_size > 1024 * 1024 else f'{pack_size // 1024} KB'


# ---------- shared pieces ----------
def shell(title, body, prefix='', bodyclass='', code=''):
    data = f' data-code="{code}"' if code else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="自媒体人的 WorkBuddy 实操课程：找对标、账号诊断、视频拆解、爆款复刻、视频复刻、违规审核。"><meta name="theme-color" content="#252f6a"><title>{esc(title)} · {SITE_NAME}</title><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body class="{bodyclass}"{data}><a class="skip-link" href="#main">跳到正文</a>{body}</body></html>'''


def brand(home):
    return f'<a class="brand" href="{home}"><span class="brand-icon" aria-hidden="true">▶</span><span>{SITE_NAME}<small>WorkBuddy 实操教程</small></span></a>'


def facts_line(l):
    m, bits = l['meta'], []
    if '时长' in m: bits.append(re.sub(r'（.*?）$', '', m['时长']))
    if '难度' in m: bits.append(LEVEL.get(m['难度'], '难度 ' + m['难度']))
    if '前置' in m and m['前置'] not in ('无', '—'): bits.append('前置 ' + short_prereq(m['前置']))
    return ' · '.join(bits)


def pack_button(prefix, cls='secondary'):
    return f'<a class="{cls}" href="{prefix}{url(PACK_NAME)}" download>下载练习包 <span>{pack_label}</span></a>'


# ---------- catalog ----------
def course_card(l, prefix):
    search = ' '.join([l['code'], l['display'], FOCUS[l['code']], TRACKS[l['track']]['name']])
    facts = facts_line(l)
    return (f'<li><a class="course-card" data-code="{l["code"]}" data-course="{esc(search)}" href="{prefix}课程/{url(l["html"])}">'
            f'<span class="course-code">{l["code"]}</span><span class="course-text"><strong>{esc(l["display"])}</strong>'
            f'<span>{FOCUS[l["code"]]}</span>' + (f'<small>{esc(facts)}</small>' if facts else '') +
            '</span><span class="course-state" aria-hidden="true"></span></a></li>')


def catalog(prefix=''):
    p = prefix
    first = by_code.get('01') or lessons[0]
    start_cards = ''.join(course_card(by_code[c], p) for c in ['01', '00'] if c in by_code)
    start = f'''<section class="course-group start-group" id="start"><div class="section-heading"><div><span class="eyebrow">第一步</span><h2>先学入门课</h2></div><p>设好工作空间，装好技能，学会打开文件核对结果。</p></div>
<ol class="start-cards">{start_cards}</ol></section>'''
    tracks = ''
    for key, t in TRACKS.items():
        if key == 'start' or not t['codes']: continue
        cards = ''.join(course_card(by_code[c], p) for c in t['codes'])
        tracks += f'''<section class="course-group track" id="{key}"><div class="track-head"><div><h3>{t["name"]}</h3><p>{t["desc"]}</p></div><span class="track-progress" data-track="{key}" data-total="{len(t["codes"])}">{len(t["codes"])} 课</span></div><ol class="course-list">{cards}</ol></section>'''
    body = f'''<header class="site-header">{brand(p + '课程目录.html')}<nav aria-label="主导航"><a href="#prepare">开始前准备</a><a href="#m1">课程</a><a href="#faq">常见问题</a><a href="{GITHUB_URL}">GitHub</a></nav></header>
<main id="main" class="home"><section class="hero"><div><p class="eyebrow">找对标 · 账号诊断 · 视频拆解 · 爆款复刻 · 视频复刻 · 违规审核</p><h1>用 AI 做自媒体，<br>每一步都能核对。</h1><p class="hero-lead">跟着一个虚构的自媒体账号「阿夏的AI片场」，在 WorkBuddy 里用开源技能完成从找对标到安全发布的全过程。每一步都拿到能打开、能核对的文件。</p><p class="hero-what">WorkBuddy 是腾讯推出的桌面 AI 助手：你用中文说清要做什么，它会读取你电脑上指定文件夹里的资料，调用技能分析数据、拆视频、写脚本、出片，并把结果保存成文件。不需要会编程。</p>
<div class="hero-actions"><a class="primary" href="{p}课程/{url(first["html"])}">开始入门课 <span aria-hidden="true">→</span></a>{pack_button(p)}</div>
<p id="resume" class="resume" hidden></p><p class="hero-meta">{len(lessons)} 节课程 · 讲解录屏 · 可复制提示词 · 参考结果对照</p></div>
<aside class="prepare" id="prepare"><h2>开始前准备</h2><ol>
<li><span>1</span><div><strong>安装并登录 WorkBuddy</strong><p>从<a href="{WORKBUDDY_URL}">官网</a>下载 Windows 或 Mac 版并登录。使用会消耗积分，具体规则以应用内说明为准。</p></div></li>
<li><span>2</span><div><strong>下载练习包并解压</strong><p>得到“{PACK_DIR}”文件夹，里面有资料、空的成果文件夹和参考结果。</p></div></li>
<li><span>3</span><div><strong>把文件夹设为工作空间</strong><p>在 WorkBuddy 点“新建任务”→“选择工作空间”→“打开本地文件夹”，选中它。</p></div></li>
<li><span>4</span><div><strong>从 01 入门开始</strong><p>01 会带你装好本课程的全部技能。之后每课：看录屏 → 复制提示词 → 打开结果核对。</p></div></li>
</ol></aside></section>
{start}
<div class="catalog-tools"><div><span class="eyebrow">第二步</span><h2>按模块学下去</h2><p>六个模块按顺序衔接：前一课的结果是后一课的输入。也可以跳着学，缺的结果从“参考结果”复制。</p></div><label class="search-label">查找课程<input id="course-search" type="search" placeholder="课程名、编号或关键词" autocomplete="off"></label></div>
<p id="search-empty" hidden>没有匹配的课程，请试试“对标”“复刻”或课程编号。</p>
<div class="tracks">{tracks}</div>
<section class="faq" id="faq"><h2>卡住了怎么办</h2>
<details><summary>提交任务后，没看到生成的文件</summary><p>先看输入框下方是否显示“{PACK_DIR}”。没有的话，说明没选工作空间，新建任务重新选择。再打开电脑上的“成果”文件夹确认文件是否真的存在，不要只看回复里说“已保存”。</p></details>
<details><summary>我的结果和录屏、参考结果不一样</summary><p>正常。AI 每次生成的内容都会不同。用每课的核对要点检查你的结果，再对照练习包里的“参考结果”。实操 2 起的提示词是针对作者那次结果写的纠正，你的结果没有同类问题就跳过。</p></details>
<details><summary>没有显卡，也不想花钱租 GPU</summary><p>走代码视频路线：4-2、5-2 用 Hypit 和 HyperFrames 做代码类视频，不需要显卡。5-1 的 AI 镜头生成可以只看录屏，用参考结果里的成片继续往下学。</p></details>
<details><summary>想用真实平台数据练习</summary><p>练习包里的数据已经够用。真要采集，可以用 MediaCrawler 这类工具，但要控制频率和数据量，采得太快太多容易被封号；只采公开数据，只做个人研究。</p></details>
<details><summary>能不能拿别人的视频直接复刻发布？</summary><p>不能。拆解只用于学习做法；复刻要换成自己的故事、角色和文案，去掉原作者的水印和标识，并在发布前做 6-1 的审核。不要用真人明星的脸或声音。</p></details>
<details><summary>想跳过某一课，或者前一课没做完</summary><p>把练习包“参考结果”里对应课号的文件夹复制到“成果”下，再学后面的课。</p></details>
</section>
<aside class="scope-note"><strong>关于练习素材</strong><p>账号、作品、数据和评论均为虚构；样片为课程自制，人物均为 AI 原创角色。平台规则会变，审核结论以平台最新公告为准。学习进度只保存在你当前使用的浏览器里。</p></aside></main>
<footer class="site-footer"><span>{SITE_NAME} · 按步骤学习，依据结果核对。</span><a href="{GITHUB_URL}">查看 Markdown 与课程文件</a></footer>'''
    return shell('课程目录', body, prefix, 'home-page')


# ---------- lesson pages ----------
def pager(code):
    i = ORDER.index(code)
    out = '<nav class="lesson-pager" aria-label="前后课">'
    if i:
        l = by_code[ORDER[i - 1]]
        out += f'<a class="prev" href="{url(l["html"])}"><span>← 上一课 · {l["code"]}</span><strong>{esc(l["display"])}</strong></a>'
    else:
        out += '<a class="prev" href="../课程目录.html"><span>← 课程目录</span><strong>查看全部课程</strong></a>'
    if i + 1 < len(ORDER):
        l = by_code[ORDER[i + 1]]
        out += f'<a class="next" href="{url(l["html"])}"><span>下一课 · {l["code"]} →</span><strong>{esc(l["display"])}</strong></a>'
    else:
        out += '<a class="next" href="../课程目录.html"><span>课程目录 →</span><strong>回到全部课程</strong></a>'
    return out + '</nav>'


def sidebar(current):
    out = '<details class="course-nav" open><summary>全部课程</summary><nav aria-label="课程导航">'
    for t in TRACKS.values():
        if not t['codes']: continue
        out += f'<p>{t["name"]}</p>'
        for c in t['codes']:
            item = by_code[c]
            cur = ' aria-current="page"' if item is current else ''
            out += f'<a href="{url(item["html"])}" data-code="{c}"{cur}><span>{c}</span>{esc(item["display"])}</a>'
    return out + '</nav></details>'


def overview(l):
    m = l['meta']
    rows = ''
    for key in META_KEYS:
        if key not in m: continue
        val = link_codes(m[key]) if key == '前置' else esc(LEVEL.get(m[key], m[key]) if key == '难度' else m[key])
        rows += f'<div><dt>{key}</dt><dd>{val}</dd></div>'
    if l['code'] == '00':
        how = '读完路线说明后，回到目录从 01 入门开始。'
    elif l['code'] == '01':
        how = '跟着步骤设好工作空间、装好技能，再生成第一个文件并核对。后面每一课都按这个循环来。'
    else:
        how = ('先看讲解录屏了解全过程；再把“实操 1”的提示词复制到 WorkBuddy，完成后打开结果文件核对；最后读“完整方法”，换成自己的账号再做一次。'
               '<br>注意：AI 每次的结果都不一样。实操 2 起是针对常见错误的纠正提示词，'
               '先检查你的结果有没有同类问题，有就参照改写后再发，没有就跳过，不要原样照抄。')
    return (f'<section class="lesson-overview" aria-label="本课概览">' + (f'<dl>{rows}</dl>' if rows else '') +
            f'<p class="how"><strong>怎么学</strong>{how}</p><div class="overview-actions">{pack_button("../")}'
            f'<a class="secondary" href="#recording">看讲解录屏</a></div></section>')


def recording(l):
    chapters = l['chapters']
    if not chapters:
        return ('<section id="recording" class="recording"><h2>实操录屏</h2>'
                '<p>录屏制作中。先按下面的提示词自己动手做，录屏上线后这里会自动出现。</p></section>')
    out = (f'<section id="recording" class="recording"><h2>实操录屏</h2><p>带旁白和字幕，约 {round(chapters[-1]["end"] / 60) or 1} 分钟。点下面的阶段可以直接跳过去。</p>'
           f'<video id="lesson-video" controls playsinline preload="metadata" aria-label="{l["code"]} WorkBuddy 实操录屏">'
           f'<source src="../录屏/{url(l["video"].name)}" type="video/mp4">'
           f'<track kind="captions" src="../录屏/{url(l["video"].with_suffix(".vtt").name)}" srclang="zh-CN" label="旁白字幕"></video>'
           f'<div class="chapters" aria-label="录屏章节">')
    for ch in chapters:
        s = int(ch['start'])
        out += f'<button type="button" data-seek="{ch["start"]}"><span>{s // 60:02}:{s % 60:02}</span>{esc(ch["title"])}</button>'
    data = json.dumps(chapters, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
    return out + f'</div><script type="application/json" id="video-chapters">{data}</script></section>'


def shots_gallery(rendered):
    """Show the screenshots at the end of a lesson as a grid of thumbnails."""
    head, sep, tail = rendered.partition('>操作画面</h2>')
    if not sep: return rendered
    fig = r'<p><img loading="lazy" decoding="async" src="([^"]+)" alt="([^"]*)" />\s*</p>\s*'
    figs = re.findall(fig, tail)
    if not figs: return rendered
    grid = '<p class="shots-note">点击截图查看大图。</p><div class="shots">' + ''.join(
        f'<figure><a href="{src}" target="_blank" rel="noopener"><img loading="lazy" decoding="async" src="{src}" alt="{alt}"></a><figcaption>{alt}</figcaption></figure>'
        for src, alt in figs) + '</div>'
    return head + sep + grid + re.sub(fig, '', tail)


def drop_missing_video_link(l, text):
    """Hide the trailing recording link until the video exists."""
    if l['chapters']: return text
    return re.sub(r'^\[观看 .*?实操录屏\]\(.*?\)( · \[字幕\]\(.*?\))?\s*$', '', text, flags=re.M)


for l in lessons:
    rendered = md(drop_missing_video_link(l, l['text']))
    rendered = re.sub(r'<img ', '<img loading="lazy" decoding="async" ', rendered)
    rendered = re.sub(r'<h4>(作者原文示例[^<]*)</h4>\s*(<pre>.*?</pre>)', r'<details class="author-example"><summary>\1</summary>\2</details>', rendered, flags=re.S)
    sections = []

    def heading(m):
        label = re.sub('<[^>]+>', '', m.group(1)); anchor = 'section-' + str(len(sections) + 1); sections.append((anchor, label))
        return f'<h2 id="{anchor}">{m.group(1)}</h2>'
    rendered = re.sub(r'<h2>(.*?)</h2>', heading, rendered, flags=re.S)
    rendered = shots_gallery(rendered)
    toc = '<details class="page-toc"><summary>本课目录</summary><nav aria-label="本课目录">' + ''.join(f'<a href="#{a}">{t}</a>' for a, t in sections) + '</nav></details>'
    cut = rendered.find('<h2')
    intro, rest = (rendered[:cut], rendered[cut:]) if cut >= 0 else (rendered, '')
    t = TRACKS[l['track']]
    pos = t['codes'].index(l['code']) + 1
    kicker = f'<div class="lesson-kicker"><span>{t["name"]} · 第 {pos} / {len(t["codes"])} 课</span><span class="done-flag" hidden>✓ 已学完</span></div>'
    done = '<div class="mark-done"><button type="button" id="mark-done" aria-pressed="false">标记本课已学完</button><span>进度只保存在当前浏览器里。</span></div>'
    body = (f'<header class="site-header">{brand("../课程目录.html")}<nav aria-label="主导航"><a href="../课程目录.html">课程目录</a>'
            f'<a href="../{url(PACK_NAME)}" download>下载练习包</a><a href="{url(l["path"].name)}" download>下载本课 Markdown</a></nav></header>'
            f'<div class="lesson-layout"><aside class="sidebar">{sidebar(l)}</aside><main id="main" class="lesson">{kicker}'
            f'<article>{intro}{overview(l)}{recording(l)}{toc}{rest}</article>{done}{pager(l["code"])}'
            f'<footer class="lesson-footer">练习素材均为虚构。复刻只学做法，发布前请做违规审核；平台规则以最新公告为准。</footer></main></div>')
    (SITE / '课程' / l['html']).write_text(shell(l['title'], body, '../', 'lesson-page', l['code']))

(SITE / '课程目录.html').write_text(catalog())
(ROOT / 'index.html').write_text(catalog('自媒体教程/'))
(ROOT / '.nojekyll').write_text('')
(SITE / 'assets/courses.json').write_text(json.dumps(
    [{'code': l['code'], 'title': l['display'], 'url': '课程/' + l['html']} for l in lessons], ensure_ascii=False, indent=2))
# A Markdown course list for people browsing the repository.
rows = '\n'.join(f'| {l["code"]} | [{l["display"]}](课程/{url(l["html"])}) | {FOCUS[l["code"]]} |' for l in lessons)
(SITE / '课程目录.md').write_text(f'# {SITE_NAME} · 课程目录\n\n| 课程 | 标题 | 内容 |\n| --- | --- | --- |\n{rows}\n')
print(f'Built {len(lessons)} lessons, course directory and practice pack ({pack_label})')

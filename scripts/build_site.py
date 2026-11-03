"""Build the static course site from the Markdown lessons.

Recordings are optional: a lesson without `录屏/<code>-WorkBuddy实操.json` shows a
"录屏制作中" notice instead of the video player.
"""
from pathlib import Path
import html, json, re
from urllib.parse import quote, unquote
import mistune

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '自媒体教程'
WORKBUDDY_URL = 'https://www.workbuddy.cn'
GITHUB_URL = 'https://github.com/JuneYaooo/media-teach'
SITE_NAME = '自媒体实战课堂'

TRACKS = {
    'start': dict(name='入门', codes=['00', '01'], desc='认识课程路线，装好 AI 助手，拿到第一个结果。'),
    'm1': dict(name='① 找对标', codes=['1-1', '1-2'], desc='谁才是真对标？对标这周出了什么爆款？'),
    'm2': dict(name='② 账号诊断', codes=['2-1', '2-2'], desc='我的号差在哪？这一条为什么不爆？'),
    'm3': dict(name='③ 视频拆解（逆向）', codes=['3-1', '3-2'], desc='爆款的画面、剪辑、声音、钩子和文案是怎么做的？'),
    'm4': dict(name='④ 爆款复刻', codes=['4-1', '4-2'], desc='保留爆款的套路，换成我的内容。'),
    'm5': dict(name='⑤ 视频复刻（选学）', codes=['5-1', '5-2'], desc='做 AI 画面的号才需要。拍实拍、做口播的，写完脚本自己拍剪，直接接 ⑥。'),
    'm6': dict(name='⑥ 违规审核', codes=['6-1', '6-2'], desc='这条能不能发？账号为什么被限流？'),
    'end': dict(name='结课', codes=['07'], desc='一条视频从找对标走到可发布。'),
}
ORDER = [c for t in TRACKS.values() for c in t['codes']]
FOCUS = {
    '00': '这门课帮你省掉哪些活儿、怎么学、名词小抄、大概花多少钱。',
    '01': '不开终端、不写代码：申请看图 Key，装好第一个技能，写出你的账号定位。',
    '1-1': '不知道该学谁？给出主页，让 AI 按你的特征去平台上搜出对标。',
    '1-2': '不比点赞绝对数，看每条是它平时的几倍，找出对标这周爆了的那条。',
    '2-1': '流量卡在哪、和对标差在哪，拿到按优先级排好的改进清单。',
    '2-2': '截一张后台数据，看这条卡在曝光、点击、完播还是互动。',
    '3-1': '一镜一镜看清爆款的景别、节奏、花字和配乐，拿到照着做的方案。',
    '3-2': '开头靠什么留人、正文什么骨架、评论区在要什么，找出能抄的那一招。',
    '4-1': '套用爆款结构写你的选题：3 个标题、3 个封面字、开头和脚本。',
    '4-2': '字幕卡片、榜单类视频：把爆款做成模板，换内容批量出变体。',
    '5-1': '选学：按分镜用 AI 生成镜头，先出一条校准再批量。',
    '5-2': '选学：做花字和标题卡，把整套做法存成下集能复用的配方。',
    '6-1': '发之前审一遍：哪一秒、哪一句有风险，怎么改，改完复审。',
    '6-2': '被限流了：按证据排查原因，先整改再申诉，备好申诉材料。',
    '07': '用你自己的账号跑通全流程，变成每周循环。',
}
EXTRA_META = {'00': {'产出': '选定学习顺序，准备好自己的账号资料'}}
LEVEL = {'1': '入门', '1-2': '基础', '2': '基础', '2-3': '进阶', '3': '进阶'}
META_KEYS = ['难度', '时长', '前置', '产出', '用到的工具']
CODE_RE = r'(?<![0-9-])(?:[1-6]-[12]|0[017])(?![0-9-])'

md = mistune.create_markdown(plugins=['table', 'strikethrough', 'task_lists', 'url'])


FOLD_RE = re.compile(r'^::: ?(.+?)\n(.*?)\n:::[ \t]*$', re.M | re.S)


def render_md(text):
    """Render Markdown; `::: 标题` … `:::` blocks become collapsed <details>."""
    out, last = '', 0
    for m in FOLD_RE.finditer(text):
        out += md(text[last:m.start()])
        inner = md(m.group(2)).replace('<code class="language-text">', '<code class="language-shell">')
        out += f'<details class="fold"><summary>{esc(m.group(1).strip())}</summary>{inner}</details>'
        last = m.end()
    return out + md(text[last:])


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
    if '前置' in m and m['前置'] not in ('无', '—'):
        codes = ' · '.join(dict.fromkeys(re.findall(CODE_RE, m['前置'])))
        bits.append('先学 ' + (codes or short_prereq(m['前置'])))
    return ' · '.join(bits)


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
    start = f'''<section class="course-group start-group" id="start"><div class="section-heading"><div><span class="eyebrow">第一步</span><h2>先学入门课</h2></div><p>30 分钟装好 AI 助手，拿到你账号的第一个结果。不用开终端，不用写代码。</p></div>
<ol class="start-cards">{start_cards}</ol></section>'''
    tracks = ''
    for key, t in TRACKS.items():
        if key == 'start' or not t['codes']: continue
        cards = ''.join(course_card(by_code[c], p) for c in t['codes'])
        tracks += f'''<section class="course-group track" id="{key}"><div class="track-head"><div><h3>{t["name"]}</h3><p>{t["desc"]}</p></div><span class="track-progress" data-track="{key}" data-total="{len(t["codes"])}">{len(t["codes"])} 课</span></div><ol class="course-list">{cards}</ol></section>'''
    body = f'''<header class="site-header">{brand(p + '课程目录.html')}<nav aria-label="主导航"><a href="#prepare">开始前准备</a><a href="#m1">课程</a><a href="#faq">常见问题</a><a href="{GITHUB_URL}">GitHub</a></nav></header>
<main id="main" class="home"><section class="hero"><div><p class="eyebrow">找对标 · 账号诊断 · 视频拆解 · 爆款复刻 · 视频复刻 · 违规审核</p><h1>找对标、拆爆款、写脚本，<br>交给 AI 去做。</h1><p class="hero-lead">用你自己的账号，在 WorkBuddy 里学会用开源技能找对标、做诊断、拆爆款、写脚本、出片和发布前审核。每课先讲技能怎么干活，再带你做出结果，自己打开核对。</p><p class="hero-what">WorkBuddy 是腾讯的桌面 AI 助手。你用中文说要做什么，它去读你指定文件夹里的资料，调技能分析数据、拆视频、写脚本、出片，结果存成文件。不用会编程。</p>
<div class="hero-actions"><a class="primary" href="{p}课程/{url(first["html"])}">开始入门课 <span aria-hidden="true">→</span></a><a class="secondary" href="#prepare">开始前准备</a></div>
<p id="resume" class="resume" hidden></p><p class="hero-meta">{len(lessons)} 节课 · 每课一张原理图 · 提示词一键复制 · 每一步都能核对</p></div>
<aside class="prepare" id="prepare"><h2>开始前准备</h2><ol>
<li><span>1</span><div><strong>安装并登录 WorkBuddy</strong><p>从<a href="{WORKBUDDY_URL}">官网</a>下载 Windows 或 Mac 版并登录。用起来会扣积分，规则看应用内说明。</p></div></li>
<li><span>2</span><div><strong>准备你自己的账号资料</strong><p>主页链接、后台数据截图，再挑一两条想学的对标爆款视频。还没起号的，想好一句话：做什么内容，给谁看。</p></div></li>
<li><span>3</span><div><strong>建一个工作文件夹</strong><p>在电脑上新建一个文件夹（比如“我的自媒体工作台”），在 WorkBuddy 里选它当工作空间，之后的结果都存在这里。</p></div></li>
<li><span>4</span><div><strong>从 01 入门开始</strong><p>01 带你申请看图 Key、装第一个技能。之后每课的节奏是：看原理图，看录屏，把提示词换成你自己的账号，再核对结果。拍实拍、做口播的，模块⑤可以跳过。</p></div></li>
</ol></aside></section>
{start}
<div class="catalog-tools"><div><span class="eyebrow">第二步</span><h2>按模块学下去</h2><p>六个模块是连着的，前一课的结果就是后一课的材料。只想学某一课也行，把提示词里的材料换成你手上有的。</p></div><label class="search-label">查找课程<input id="course-search" type="search" placeholder="课程名、编号或关键词" autocomplete="off"></label></div>
<p id="search-empty" hidden>没找到，试试“对标”“复刻”或课号。</p>
<div class="tracks">{tracks}</div>
<section class="faq" id="faq"><h2>卡住了怎么办</h2>
<details><summary>提交任务后，没看到生成的文件</summary><p>先看输入框下方有没有显示你的工作文件夹。没有就是没选工作空间，新建任务重选。然后去电脑上打开“成果”文件夹，看文件在不在。回复里说“已保存”不算数。</p></details>
<details><summary>我的结果和录屏不一样</summary><p>正常。录屏用的是演示账号“阿夏的AI片场”，你用的是自己的号，AI 每次生成的内容也不一样。按每课“怎么核对结果”里的几条查就行，不用和录屏逐字比。</p></details>
<details><summary>没有显卡，也不想花钱租 GPU</summary><p>拍实拍、做口播的用不到显卡，模块⑤直接跳过。想做 AI 画面的，可以走代码视频：4-2、5-2 用 Hypit 和 HyperFrames 写代码出片，不用显卡。5-1 的 AI 镜头也能直接调 API，按次付费。</p></details>
<details><summary>学完要花多少钱</summary><p>WorkBuddy 按积分扣，看图模型 Key 按用量付费，打不开平台页面时才需要付费的 TikHub。雷达、拆解、审核这些技能在你电脑上跑，不额外收费。00 总纲里有一张费用表，建议先充一点小钱试跑 1-1、2-1。</p></details>
<details><summary>技能读不到平台数据怎么办</summary><p>技能先用 WorkBuddy 自带的浏览器去看平台页面。读不出来，它会问你是换 TikHub 接口（付费），还是你自己给链接和截图。MediaCrawler 这类批量采集工具容易被封号，课程不演示；非要用的话，控制频率和数据量，只采公开数据，自己研究用。</p></details>
<details><summary>能不能拿别人的视频直接复刻发布？</summary><p>不能。拆解是为了学做法。复刻要换成自己的故事、角色和文案，去掉原作者的水印和标识，发布前过一遍 6-1 的审核。别用真人明星的脸和声音。</p></details>
<details><summary>想跳过某一课，或者前一课没做完</summary><p>可以。把后一课提示词里的“上一课的结果”换成你手上有的材料。比如没做 1-1，就直接告诉它你的 3 个对标账号。</p></details>
</section>
<aside class="scope-note"><strong>关于录屏演示</strong><p>录屏里的“阿夏的AI片场”是演示账号，后台数据是编的；两条爆款样片是课程自己做的，人物都是 AI 原创角色。平台规则会变，审核结论以平台最新公告为准。学习进度只存在你现在用的这个浏览器里。</p></aside></main>
<footer class="site-footer"><span>{SITE_NAME} · 跟着做，对着结果查。</span><a href="{GITHUB_URL}">查看 Markdown 与课程文件</a></footer>'''
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


KINDS = [('它是怎么工作的', 'how', '原理'), ('你要准备什么', 'prep', '准备'), ('动手', 'do', '动手'),
         ('你会拿到什么', 'get', '产出'), ('怎么核对结果', 'check', '核对'), ('常见问题', 'faq', '答疑'),
         ('进阶与边界', 'more', '进阶'), ('下一课', 'next', '下一步'), ('本次任务结果与核对', 'demo', '演示'),
         ('操作画面', 'shots', '截图')]
KIND_LABEL = {k: lab for _, k, lab in KINDS}
PATH_STEPS = [('how', '看懂原理'), ('prep', '准备材料'), ('do', '动手做'), ('check', '核对结果')]


def kind_of(title):
    return next((k for t, k, _ in KINDS if title.startswith(t)), 'plain')


def split_top(s):
    """Split on ；、 that are not inside brackets."""
    out, cur, depth = [], '', 0
    for ch in s:
        depth += (ch in '（(') - (ch in '）)')
        if ch in '；;、' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    return [x for x in out + [cur.strip()] if x]


def overview(l, anchors):
    m = l['meta']
    facts = ''
    if '时长' in m:
        facts += f'<span class="fact" title="{esc(m["时长"])}"><b>时长</b>{esc(re.sub(r"（.*?）", "", m["时长"]))}</span>'
    if '难度' in m:
        facts += f'<span class="fact"><b>难度</b>{esc(LEVEL.get(m["难度"], m["难度"]))}</span>'
    if '前置' in m and m['前置'] not in ('无', '—'):
        codes = ' · '.join(dict.fromkeys(re.findall(CODE_RE, m['前置'])))
        facts += f'<span class="fact" title="{esc(m["前置"])}"><b>先学</b>{link_codes(codes) if codes else esc(short_prereq(m["前置"]))}</span>'
    if not l['chapters']:
        facts += '<span class="fact rec"><b>录屏</b>制作中</span>'
    get = f'<div class="get"><b>学完你会拿到</b><p>{esc(m["产出"])}</p></div>' if '产出' in m else ''
    tools = ''
    if '用到的工具' in m:
        tools = '<div class="tools"><b>用到</b>' + ''.join(f'<span>{esc(t)}</span>' for t in split_top(m['用到的工具'])) + '</div>'
    steps = [(k, lab) for k, lab in PATH_STEPS if k in anchors]
    path = ''.join(f'<li><a href="#{anchors[k]}"><i>{i}</i>{lab}</a></li>' for i, (k, lab) in enumerate(steps, 1))
    path = f'<ol class="path" aria-label="这一课怎么学">{path}</ol>' if path else ''
    return f'<section class="summary" aria-label="本课概览"><div class="facts">{facts}</div>{get}{tools}{path}</section>'


def recording(l):
    chapters = l['chapters']
    if not chapters:
        return ''
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


def prompt_box(m):
    body = re.sub(r'&lt;([^&\n]{1,60}?)&gt;', r'<mark class="ph">&lt;\1&gt;</mark>', m.group(1))
    return ('<div class="prompt"><div class="prompt-head"><span class="prompt-label">发给 WorkBuddy</span></div>'
            f'<pre class="prompt-body"><code>{body}</code></pre></div>')


def callouts(rendered):
    def bq(m):
        text = re.sub('<[^>]+>', '', m.group(1)).strip()
        cls = 'opt' if text.startswith('选学') else 'warn' if '以试跑为准' in text else 'note'
        return f'<aside class="callout {cls}">{m.group(1)}</aside>'
    return re.sub(r'<blockquote>(.*?)</blockquote>', bq, rendered, flags=re.S)


def faq_items(sec):
    """`**问题？** 回答` paragraphs become an accordion."""
    parts = re.split(r'<p><strong>([^<]*?[？?])</strong>\s*', sec)
    if len(parts) < 3: return sec
    out = parts[0]
    for i in range(1, len(parts), 2):
        out += f'<details class="qa"><summary>{parts[i]}</summary><div class="qa-a"><p>{parts[i + 1].strip()}</div></details>'
    return out


TASK_H3 = r'<h3>((?:实操 ?\d+|第 ?\d+ ?步)[^<：]*?)[：:]\s*(.*?)</h3>'


def lesson_sections(rendered):
    """Wrap each <h2> section in <section class="sec sec-KIND">, restyle it per kind, build the outline."""
    chunks = re.split(r'(?=<h2>)', callouts(rendered))
    secs, anchors = [], {}
    for i, ch in enumerate(chunks[1:], 1):
        title = re.sub('<[^>]+>', '', re.match(r'<h2>(.*?)</h2>', ch, re.S).group(1))
        kind, anchor = kind_of(title), f'section-{i}'
        anchors.setdefault(kind, anchor)
        ch = ch.replace('<h2>', f'<h2 id="{anchor}">', 1)
        if kind == 'how':
            ch = re.sub(r'<li><strong>(.*?)</strong>[：:]\s*', r'<li><strong class="step-title">\1</strong>', ch)
        ch = re.sub(TASK_H3, r'<h3 class="task"><span class="task-no">\1</span>\2</h3>', ch)
        if kind == 'check':
            ch = ch.replace('<ul>\n<li class="task-list-item">', '<ul class="checks">\n<li class="task-list-item">')
            ch = re.sub(r'(<input class="task-list-item-checkbox"[^>]*>)(.*?)</li>', r'\1<span>\2</span></li>', ch, flags=re.S)
        if kind == 'faq':
            ch = faq_items(ch)
        label = f'<span class="sec-label">{KIND_LABEL[kind]}</span>' if kind in KIND_LABEL else ''
        secs.append({'kind': kind, 'anchor': anchor, 'title': title, 'html': f'<section class="sec sec-{kind}">{label}{ch}</section>'})
    # Until the recording exists, the demo result and screenshot sections are placeholders: fold them into one note.
    demo = next((x for x in secs if x['kind'] == 'demo'), None)
    shots = next((x for x in secs if x['kind'] == 'shots'), None)
    if demo and shots and '待补' in demo['html'] and '<img' not in shots['html']:
        note = re.search(r'<p>(.*?)</p>', demo['html'], re.S)
        demo.update(kind='pending', html='<section class="sec sec-pending"><div class="pending-box"><b>录屏演示制作中</b>'
                    + (f'<p>{note.group(1)}</p>' if note else '')
                    + '<p class="muted">录好后，这里会放演示账号“阿夏的AI片场”的实际结果和操作截图。</p></div></section>')
        secs.remove(shots)
    toc = [(x['anchor'], x['title'], x['kind']) for x in secs if x['kind'] != 'pending']
    return chunks[0] + ''.join(x['html'] for x in secs), toc, anchors


MERMAID = ('<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs";'
           'mermaid.initialize({startOnLoad:true,theme:"base",flowchart:{nodeSpacing:28,rankSpacing:36,padding:8,diagramPadding:4},themeVariables:{primaryColor:"#eef0f8",primaryBorderColor:"#3a4a9c",lineColor:"#8a8fa8",fontSize:"16px",fontFamily:"-apple-system,PingFang SC,Microsoft YaHei,sans-serif"}});</script>')


def fix_material_links(rendered):
    return rendered


for l in lessons:
    # The meta table is shown in the overview box; drop it from the body.
    body_md = re.sub(r'^\| 项目 \| 内容 \|\n\| --- \| --- \|\n(?:\|.*\|\n)+\n?', '', l['text'], flags=re.M)
    rendered = fix_material_links(render_md(drop_missing_video_link(l, body_md)))
    rendered = re.sub(r'<img ', '<img loading="lazy" decoding="async" ', rendered)
    rendered = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>', r'<figure class="flow"><pre class="mermaid">\1</pre></figure>', rendered, flags=re.S)
    rendered = re.sub(r'<h4>(作者原文示例[^<]*)</h4>\s*(<pre>.*?</pre>)', r'<details class="author-example"><summary>\1</summary>\2</details>', rendered, flags=re.S)
    rendered = shots_gallery(rendered)
    rendered = rendered.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    rendered = re.sub(r'<pre><code class="language-text">(.*?)</code></pre>', prompt_box, rendered, flags=re.S)
    article, toc_items, anchors = lesson_sections(rendered)
    rail = ('<nav class="toc-rail" aria-label="本课目录"><p>本课目录</p>' + ''.join(
        f'<a href="#{a}" data-kind="{k}">{t}</a>' for a, t, k in toc_items) + '</nav>')
    toc = ('<details class="page-toc"><summary>本课目录</summary><nav aria-label="本课目录">' + ''.join(
        f'<a href="#{a}">{t}</a>' for a, t, k in toc_items) + '</nav></details>')
    cut = article.find('<section class="sec')
    intro, rest = (article[:cut], article[cut:]) if cut >= 0 else (article, '')
    intro = re.sub(r'(</h1>\s*)<p>', r'\1<p class="lead">', intro, count=1)
    t = TRACKS[l['track']]
    pos = t['codes'].index(l['code']) + 1
    kicker = f'<div class="lesson-kicker"><span>{t["name"]} · 第 {pos} / {len(t["codes"])} 课</span><span class="done-flag" hidden>✓ 已学完</span></div>'
    done = '<div class="mark-done"><button type="button" id="mark-done" aria-pressed="false">标记本课已学完</button><span>进度只保存在当前浏览器里。</span></div>'
    body = (f'<header class="site-header">{brand("../课程目录.html")}<nav aria-label="主导航"><a href="../课程目录.html">课程目录</a>'
            f'<a href="{url(l["path"].name)}" download>下载本课 Markdown</a></nav></header>'
            f'<div class="lesson-layout"><aside class="sidebar">{sidebar(l)}</aside><main id="main" class="lesson">{kicker}'
            f'<article>{intro}{overview(l, anchors)}{recording(l)}{toc}{rest}</article>{done}{pager(l["code"])}'
            f'<footer class="lesson-footer">演示账号的数据为虚构。复刻只学做法，发布前请做违规审核；平台规则以最新公告为准。</footer></main>'
            f'<aside class="rail">{rail}</aside></div>')
    if 'class="mermaid"' in body: body += MERMAID
    (SITE / '课程' / l['html']).write_text(shell(l['title'], body, '../', 'lesson-page', l['code']))

(SITE / '课程目录.html').write_text(catalog())
(ROOT / 'index.html').write_text(catalog('自媒体教程/'))
(ROOT / '.nojekyll').write_text('')
(SITE / 'assets/courses.json').write_text(json.dumps(
    [{'code': l['code'], 'title': l['display'], 'url': '课程/' + l['html']} for l in lessons], ensure_ascii=False, indent=2))
# A Markdown course list for people browsing the repository.
rows = '\n'.join(f'| {l["code"]} | [{l["display"]}](课程/{url(l["html"])}) | {FOCUS[l["code"]]} |' for l in lessons)
(SITE / '课程目录.md').write_text(f'# {SITE_NAME} · 课程目录\n\n| 课程 | 标题 | 内容 |\n| --- | --- | --- |\n{rows}\n')
print(f'Built {len(lessons)} lessons and course directory')

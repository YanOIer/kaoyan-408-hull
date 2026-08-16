# -*- coding: utf-8 -*-
"""
408 知识凸包静态站点生成器
读取 notes/*.md 与 data/*.md，生成 docs/ 下的静态网站（GitHub Pages 用）
"""
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "docs"

SUBJECTS = {
    "DS": {"name": "数据结构", "score": "45 分", "color": "#c0392b", "en": "Data Structures"},
    "CO": {"name": "计算机组成原理", "score": "45 分", "color": "#1f6f8b", "en": "Computer Organization"},
    "OS": {"name": "操作系统", "score": "35 分", "color": "#6a8e3f", "en": "Operating Systems"},
    "CN": {"name": "计算机网络", "score": "25 分", "color": "#b8860b", "en": "Computer Networks"},
}

CSS = """
:root{--bg:#f7f6f3;--card:#fff;--ink:#26221d;--ink2:#6b655c;--line:#e6e2da;--ds:#c0392b;--co:#1f6f8b;--os:#6a8e3f;--cn:#b8860b}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.75;font-size:16px}
a{color:inherit}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
/* 顶栏 */
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,246,243,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar .wrap{display:flex;align-items:center;gap:14px;height:56px}
.topbar .logo{font-weight:800;font-size:17px;letter-spacing:.5px;text-decoration:none}
.topbar .logo em{font-style:normal;color:#b3452a}
.topbar nav{margin-left:auto;display:flex;gap:18px;font-size:14px}
.topbar nav a{text-decoration:none;color:var(--ink2)}
.topbar nav a:hover{color:var(--ink)}
/* 首页 */
.hero{padding:72px 0 40px;border-bottom:1px solid var(--line)}
.hero .tag{display:inline-block;font-size:13px;color:var(--ink2);border:1px solid var(--line);border-radius:999px;padding:3px 12px;background:var(--card);margin-bottom:18px}
.hero h1{font-size:42px;line-height:1.25;font-weight:800;letter-spacing:1px}
.hero h1 span{color:#b3452a}
.hero p.sub{margin-top:14px;color:var(--ink2);max-width:720px;font-size:16px}
.stats{display:flex;gap:36px;margin-top:28px;flex-wrap:wrap}
.stats b{font-size:26px;display:block;font-weight:800}
.stats span{font-size:13px;color:var(--ink2)}
.section{padding:44px 0}
.section h2{font-size:24px;font-weight:800;margin-bottom:6px}
.section .hint{color:var(--ink2);font-size:14px;margin-bottom:22px}
.hull-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.hull-card img{width:100%;border-radius:8px;display:block}
.hull-card figcaption{font-size:13px;color:var(--ink2);margin-top:10px;text-align:center}
.subj-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
@media(max-width:820px){.subj-grid{grid-template-columns:1fr}.hero h1{font-size:30px}}
.subj{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.subj .head{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;align-items:baseline;gap:10px}
.subj .head .dot{width:10px;height:10px;border-radius:3px}
.subj .head h3{font-size:18px;font-weight:800}
.subj .head .score{margin-left:auto;font-size:13px;color:var(--ink2)}
.subj ul{list-style:none}
.subj li a{display:flex;align-items:center;gap:10px;padding:12px 20px;text-decoration:none;border-bottom:1px solid #f0ede6;font-size:15px;transition:background .15s}
.subj li:last-child a{border-bottom:none}
.subj li a:hover{background:#faf9f6}
.badge{font-size:12px;border-radius:6px;padding:1px 8px;white-space:nowrap}
.badge.freq{background:#f3efe8;color:var(--ink2)}
.stars{font-size:12px;letter-spacing:1px}
.usage{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px 28px}
.usage ol{margin-left:20px;display:grid;gap:10px;font-size:15px}
.footer{border-top:1px solid var(--line);padding:28px 0;color:var(--ink2);font-size:13px}
/* 文章页 */
.layout{display:grid;grid-template-columns:250px 1fr;gap:36px;padding:36px 0 64px}
@media(max-width:820px){.layout{grid-template-columns:1fr}.sidebar{position:static!important}}
.sidebar{position:sticky;top:76px;align-self:start;font-size:14px}
.sidebar .group{margin-bottom:18px}
.sidebar .gname{font-weight:800;font-size:13px;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.sidebar a{display:block;text-decoration:none;color:var(--ink2);padding:4px 10px;border-radius:8px;border-left:2px solid transparent}
.sidebar a:hover{background:#efede7;color:var(--ink)}
.sidebar a.on{background:var(--card);color:var(--ink);font-weight:700;border-left-color:currentColor}
.article{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:40px 48px;min-width:0}
@media(max-width:820px){.article{padding:24px 20px}}
.article h1{font-size:28px;font-weight:800;line-height:1.35;margin-bottom:8px}
.article h2{font-size:20px;font-weight:800;margin:34px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
.article h3{font-size:16.5px;font-weight:700;margin:22px 0 8px}
.article p{margin:10px 0}
.article ul,.article ol{margin:10px 0 10px 22px}
.article li{margin:4px 0}
.article blockquote{border-left:3px solid #b3452a;background:#faf6f2;padding:10px 16px;border-radius:0 8px 8px 0;color:var(--ink2);font-size:14.5px;margin:14px 0}
.article table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14.5px;display:block;overflow-x:auto}
.article th,.article td{border:1px solid var(--line);padding:7px 12px;text-align:left}
.article th{background:#faf9f6;font-weight:700}
.article code{font-family:"Cascadia Code",Consolas,"JetBrains Mono",monospace;font-size:13.5px;background:#f3f0ea;border-radius:5px;padding:1px 6px}
.article pre{background:#23272e;border-radius:10px;padding:16px 18px;overflow-x:auto;margin:16px 0}
.article pre code{background:none;color:#e6e1d5;padding:0;font-size:13.5px;line-height:1.6}
.article hr{border:none;border-top:1px solid var(--line);margin:24px 0}
.pagenav{display:flex;justify-content:space-between;gap:14px;margin-top:28px;font-size:14px}
.pagenav a{text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;color:var(--ink2);max-width:48%}
.pagenav a:hover{color:var(--ink);border-color:#cfcabe}
"""


def slugify(name: str) -> str:
    s = name.rsplit(".", 1)[0]
    s = re.sub(r"[^0-9A-Za-z一-鿿]+", "-", s).strip("-").lower()
    return s


def render_md(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def page(title: str, body: str, active: str = "") -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · 408 知识凸包</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="topbar"><div class="wrap">
<a class="logo" href="index.html">408<em>知识凸包</em></a>
<nav>
<a href="index.html#hull">凸包图</a>
<a href="index.html#notes">顶点笔记</a>
<a href="index.html#usage">使用建议</a>
<a href="https://github.com/YanOIer/kaoyan-408-hull">GitHub</a>
</nav>
</div></header>
{body}
<footer class="footer"><div class="wrap">
考研 408 知识凸包 · 基于 2009—2026 统考真题考频统计构建 ·
<a href="https://github.com/YanOIer/kaoyan-408-hull">源代码与数据</a>
</div></footer>
</body></html>"""


def parse_note(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"([A-Z]{2})-(\d+)-(.+)\.md", path.name)
    sub, num, name = m.group(1), m.group(2), m.group(3)
    freq = re.search(r"考频：\*?\*?(\d+)", text)
    stars = re.search(r"难度：(★+)", text)
    return {
        "sub": sub, "num": num, "name": name,
        "code": f"{sub}-{num}",
        "freq": freq.group(1) if freq else "?",
        "stars": stars.group(1) if stars else "",
        "slug": f"{sub.lower()}-{num}.html",
        "text": text,
    }


def sidebar(notes, data_pages, active_slug):
    html = ['<aside class="sidebar">']
    for sub, meta in SUBJECTS.items():
        html.append(f'<div class="group"><div class="gname" style="color:{meta["color"]}">'
                    f'<span>■</span>{meta["name"]}</div>')
        for n in notes:
            if n["sub"] == sub:
                on = " on" if n["slug"] == active_slug else ""
                html.append(f'<a class="x{on}" style="color:inherit" href="{n["slug"]}">{n["code"]} {n["name"]}</a>')
        html.append("</div>")
    html.append('<div class="group"><div class="gname" style="color:#8a857c"><span>■</span>真题数据</div>')
    for d in data_pages:
        on = " on" if d["slug"] == active_slug else ""
        html.append(f'<a class="x{on}" href="{d["slug"]}">{d["title"]}</a>')
    html.append("</div></aside>")
    return "\n".join(html)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    # 资源
    shutil.copy(ROOT / "hull" / "408知识凸包.png", OUT / "assets" / "hull.png")
    (OUT / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    notes = sorted((parse_note(p) for p in (ROOT / "notes").glob("*.md")), key=lambda n: n["code"])
    data_pages = []
    for i, p in enumerate(sorted((ROOT / "data").glob("*.md"))):
        t = p.read_text(encoding="utf-8")
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        title = h1.group(1).strip() if h1 else p.stem
        title = re.sub(r"[*#]", "", title)[:24]
        data_pages.append({"slug": f"data-{i+1}.html", "title": title, "text": t})

    # 笔记页
    for idx, n in enumerate(notes):
        body_html = render_md(n["text"])
        prev_a = (f'<a href="{notes[idx-1]["slug"]}">← {notes[idx-1]["code"]} {notes[idx-1]["name"]}</a>'
                  if idx > 0 else "<span></span>")
        next_a = (f'<a href="{notes[idx+1]["slug"]}">→ {notes[idx+1]["code"]} {notes[idx+1]["name"]}</a>'
                  if idx < len(notes) - 1 else "<span></span>")
        color = SUBJECTS[n["sub"]]["color"]
        body = f"""
<div class="wrap layout">
{sidebar(notes, data_pages, n["slug"])}
<main>
<article class="article" style="border-top:4px solid {color}">
{body_html}
</article>
<div class="pagenav">{prev_a}{next_a}</div>
</main>
</div>"""
        (OUT / n["slug"]).write_text(page(f'{n["code"]} {n["name"]}', body, n["slug"]), encoding="utf-8")

    # 数据页
    for d in data_pages:
        body = f"""
<div class="wrap layout">
{sidebar(notes, data_pages, d["slug"])}
<main>
<article class="article" style="border-top:4px solid #8a857c">
{render_md(d["text"])}
</article>
<div class="pagenav"><a href="index.html">← 返回首页</a><span></span></div>
</main>
</div>"""
        (OUT / d["slug"]).write_text(page(d["title"], body, d["slug"]), encoding="utf-8")

    # 首页
    cards = []
    for sub, meta in SUBJECTS.items():
        items = []
        for n in notes:
            if n["sub"] == sub:
                items.append(
                    f'<li><a href="{n["slug"]}">'
                    f'<span style="flex:1">{n["code"]} {n["name"]}</span>'
                    f'<span class="badge freq">考频 {n["freq"]}</span>'
                    f'<span class="stars" style="color:{meta["color"]}">{n["stars"]}</span>'
                    f"</a></li>")
        cards.append(f"""
<div class="subj">
<div class="head"><span class="dot" style="background:{meta["color"]}"></span>
<h3>{meta["name"]}</h3><span class="score">{meta["en"]} · {meta["score"]}</span></div>
<ul>{"".join(items)}</ul>
</div>""")

    index_body = f"""
<section class="hero"><div class="wrap">
<span class="tag">考频 × 难度 双维定位 · 2009—2026 真题统计</span>
<h1>考研 408 <span>知识凸包</span></h1>
<p class="sub">把数据结构、组成原理、操作系统、计算机网络四科考点画进同一张坐标图，
对每科求凸包——顶点就是框住全科边界的核心知识点。守住 14 个顶点，就守住了整张 408 地图。</p>
<div class="stats">
<div><b>14</b><span>凸包顶点精讲</span></div>
<div><b>4</b><span>科目全覆盖</span></div>
<div><b>18 年</b><span>真题数据支撑</span></div>
<div><b>7 次</b><span>最高单点考频（数据通路）</span></div>
</div>
</div></section>

<section class="section" id="hull"><div class="wrap">
<h2>四科知识凸包</h2>
<p class="hint">右上 = 高频高难（决定上限）· 右下 = 高频低难（必须满分）· 左上 = 低频高难（胜负手）· 左下 = 低频低难（地板）</p>
<figure class="hull-card"><img src="assets/hull.png" alt="408 知识凸包">
<figcaption>横轴：2009—2026 真题综合题考频 · 纵轴：综合难度（★1—5）· ★ 标记为凸包顶点</figcaption>
</figure>
</div></section>

<section class="section" id="notes"><div class="wrap">
<h2>凸包顶点精讲</h2>
<p class="hint">每个顶点一篇：考点定位 → 核心清单（必背代码/公式）→ 真题锚点 → 易错点 → 复习建议</p>
<div class="subj-grid">{"".join(cards)}</div>
</div></section>

<section class="section" id="usage"><div class="wrap">
<h2>使用建议</h2>
<div class="usage"><ol>
<li><b>先看凸包图</b>：知道四科边界在哪里，再决定时间分配。</li>
<li><b>从右下顶点开始</b>（性价比高）：CN-02 子网划分 → CN-01 时延计算 → OS-02 文件系统 → DS-01 栈与队列。</li>
<li><b>攻右上顶点</b>（决定上限）：CO-04 数据通路 → DS-03 图算法 → OS-03 PV 操作 → CN-03 TCP。</li>
<li><b>补左上顶点</b>（冲 130+）：DS-04 灵活算法设计 → CO-01 指令系统 → CO-02 流水线。</li>
<li>每篇笔记的「真题锚点」对应侧栏「真题数据」中的年份整理，精做对应年份综合题。</li>
<li>凸包内部的点（如排序代码、内存管理）同样必考——顶点划定边界，内部点靠顶点间的连线知识覆盖。</li>
</ol></div>
</div></section>"""
    (OUT / "index.html").write_text(page("首页", index_body), encoding="utf-8")

    total = 1 + len(notes) + len(data_pages)
    print(f"OK: {total} pages -> {OUT}")


if __name__ == "__main__":
    main()

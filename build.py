#!/usr/bin/env python3
"""Static site generator for dreadpirateduppie.com archive."""
import html
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content", "posts")
OUT_POSTS = os.path.join(ROOT, "posts")

SITE_TITLE = "Dread Pirate Duppie"
SITE_DESC = "Essays on privacy, power, culture and the cost of your attention. Written from Peckham, London."

# Ordered newest-first, matching the original site's archive order.
POSTS = [
    dict(slug="legalize-it", title="Legalize It", sub="",
         dek="A neighbour smelled a plant through a wall and decided a caged human being was the reasonable response. On how deep the conditioning goes.",
         tags=["Drug Policy", "Control"]),
    dict(slug="introducing-pushinn", title="Introducing PushInn", sub="",
         dek="The project that's been living rent free in my head since 2021. No co-founder, no budget, just a camera roll full of spots and enough delusion to see it through.",
         tags=["Pushinn", "Building"]),
    dict(slug="the-winter-protocol-a-31-day-system-override-for-the-urban-high-performer",
         title="The Winter Protocol", sub="A 31-Day System Override for the Urban High Performer",
         dek="Why everyone's out here playing chemist with their own neurotransmitters — and what an actual reset looks like when the underlying conditions haven't changed.",
         tags=["Health", "Systems"]),
    dict(slug="drake-is-a-clown", title="Drake Is a Clown", sub="",
         dek="A subscriber-only post \u2014 only the headline survived into the archive.",
         tags=["Culture"]),
    dict(slug="dreadpirateroberts", title="DreadPirateRoberts", sub="",
         dek="At long last, Ross is free.", tags=["Freedom"]),
    dict(slug="free-isn-t-free", title="Free Isn't Free", sub="",
         dek="We'll fight tooth and nail over money and sleepwalk straight through our time. Only one of those two things is unrecoverable.",
         tags=["Attention", "Time"]),
    dict(slug="collateral-damage", title="Collateral Damage", sub="",
         dek="My niece is 14 and genuinely smart, and the algorithm ate her. What's actually running under the hood of a phone built to hunt a child.",
         tags=["Attention", "Youth"]),
    dict(slug="the-wagwan-paradox-consuming-the-culture-fearing-the-people",
         title="The Wagwan Paradox", sub="Consuming the Culture, Fearing the People",
         dek="From the living room to the global charts — how society loves Black culture and stays terrified of Black people.",
         tags=["Race", "Culture"]),
    dict(slug="the-digital-reality-check-limited-offer", title="The Digital Reality Check", sub="",
         dek="The difference between an aesthetic and a reality, and the exact point where appreciation ends and extraction begins.",
         tags=["Culture"]),
    dict(slug="the-toll-booth-economy-education-housing-the-end-of-sovereignty",
         title="The Toll Booth Economy", sub="Education, Housing & the End of Sovereignty",
         dek="In 1978 a 23-year-old on a median salary bought a terrace in Zone 3. The ratio was 3:1. It's now 15:1. That wasn't weather — it was policy.",
         tags=["Economics", "London"]),
    dict(slug="xmr-ftw", title="XMR FTW", sub="",
         dek="I said Monero would survive the delisting wave, that privacy couldn't be killed by regulation. One year later I'm back to tell you I was right.",
         tags=["Privacy", "Monero"]),
    dict(slug="xidiocracy", title="Xidiocracy", sub="",
         dek="It's 2025 and society has become unrecognizable. Oxygen, the internet and dopamine are tracked and taxed.",
         tags=["Fiction", "Satire"]),
]

PAYWALL_RE = re.compile(r"###\s*Want to read more\?", re.I)
IMG_MD_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
HASH_RE = re.compile(r"(a055e6_[a-f0-9]+)")
LINK_RE = re.compile(r"\[([^\]]*)\]\(((?:[^()]|\([^()]*\))*)\)")
# Wix autolinked sentence fragments: "obsession.In", "power.It", "matter.ye"
JUNK_LINK_RE = re.compile(r"^https?://[A-Za-z]+\.[A-Za-z]{2,3}/?$")
URLTEXT_RE = re.compile(r"^https?://([^/\s]+)")
# a mangled Wix commerce widget scraped as one run-on line
JUNK_LINES = {"Limited Time OfferThe Clout Chasing Culture Vultures Starter Pack\u00a325.00\u00a35.00Buy Now"}
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")


def _render_link(m):
    text, href = m.group(1), m.group(2)
    # Wix autolinked a sentence boundary into a fake domain — unwrap it.
    if JUNK_LINK_RE.match(href):
        return text if text.strip() else ""
    if not text.strip():
        return ""
    # a bare URL as its own label reads badly; show the host instead
    u = URLTEXT_RE.match(text.strip())
    if u:
        text = u.group(1).replace("www.", "")
    return '<a href="%s" rel="noopener">%s</a>' % (html.escape(href, quote=True), text)


def inline(text):
    """Escape, then apply inline markdown."""
    t = html.escape(text, quote=False)
    t = LINK_RE.sub(_render_link, t)
    t = BOLD_RE.sub(r"<strong>\1</strong>", t)
    t = ITAL_RE.sub(r"<em>\1</em>", t)
    return t


def parse(md_text):
    """Return (blocks, images, locked, wordcount).

    blocks is a list of html strings; images is the ordered list of local
    image filenames referenced by the post.
    """
    lines = md_text.split("\n")
    # drop the title line, the source line and the leading rule
    body, seen_rule = [], False
    for ln in lines:
        if not seen_rule:
            if ln.strip() == "---":
                seen_rule = True
            continue
        body.append(ln)

    locked = False
    kept = []
    for ln in body:
        if PAYWALL_RE.search(ln):
            locked = True
            break
        kept.append(ln)

    blocks, images, para, list_items = [], [], [], []
    words = 0

    def flush_para():
        nonlocal para, words
        if para:
            txt = " ".join(para).strip()
            if txt:
                words += len(txt.split())
                blocks.append("<p>%s</p>" % inline(txt))
            para = []

    def flush_list():
        nonlocal list_items
        if list_items:
            items = "".join("<li>%s</li>" % inline(i) for i in list_items)
            blocks.append("<ul>%s</ul>" % items)
            list_items = []

    for ln in kept:
        s = ln.strip()
        if s in JUNK_LINES:
            continue
        if s in ("DPD.", "DPD"):
            flush_para()
            flush_list()
            blocks.append('<p class="sig">DPD.</p>')
            continue
        if not s:
            flush_para()
            flush_list()
            continue
        m = IMG_MD_RE.fullmatch(s)
        if m:
            flush_para()
            flush_list()
            h = HASH_RE.search(m.group(2))
            if h:
                fn = h.group(1) + ".webp"
                images.append(fn)
                blocks.append(
                    '<figure class="shot"><img src="../assets/img/%s" alt="" '
                    'loading="lazy" decoding="async"></figure>' % fn
                )
            continue
        if s == "---":
            flush_para()
            flush_list()
            blocks.append('<hr class="rule">')
            continue
        if s.startswith("#"):
            flush_para()
            flush_list()
            lvl = len(s) - len(s.lstrip("#"))
            txt = s.lstrip("#").strip()
            words += len(txt.split())
            blocks.append("<h%d>%s</h%d>" % (min(lvl + 1, 4), inline(txt), min(lvl + 1, 4)))
            continue
        if s.startswith("> "):
            flush_para()
            flush_list()
            blocks.append("<blockquote><p>%s</p></blockquote>" % inline(s[2:]))
            continue
        if s.startswith(("- ", "* ")):
            flush_para()
            words += len(s.split())
            list_items.append(s[2:])
            continue
        flush_list()
        para.append(s)

    flush_para()
    flush_list()
    return blocks, images, locked, words


def shell(title, desc, body, css_depth, extra_class="", og_img=None):
    up = "../" if css_depth else ""
    og = ""
    if og_img:
        og = '<meta property="og:image" content="%sassets/img/%s">' % (up, og_img)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:type" content="website">{og}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/css/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%230b0b0c%22/><text y=%2274%22 x=%2250%22 text-anchor=%22middle%22 font-size=%2270%22 fill=%22%23e7b549%22 font-family=%22serif%22>&#9760;</text></svg>">
</head>
<body class="{extra_class}">
<div class="grain" aria-hidden="true"></div>
{body}
</body>
</html>
"""


def tag_html(tags):
    return "".join('<span class="tag">%s</span>' % html.escape(t) for t in tags)


def main():
    if os.path.isdir(OUT_POSTS):
        shutil.rmtree(OUT_POSTS)
    os.makedirs(OUT_POSTS)

    built = []
    for p in POSTS:
        path = os.path.join(SRC, p["slug"] + ".md")
        with open(path) as f:
            blocks, images, locked, words = parse(f.read())
        rec = dict(p)
        rec.update(blocks=blocks, images=images, locked=locked, words=words,
                   mins=max(1, round(words / 220)), lead=images[0] if images else None)
        built.append(rec)

    for i, p in enumerate(built):
        prev_p = built[i - 1] if i > 0 else None
        next_p = built[i + 1] if i < len(built) - 1 else None
        write_post(p, prev_p, next_p)

    write_index(built)
    total_words = sum(p["words"] for p in built)
    print("built %d posts, %d words, %d images"
          % (len(built), total_words, sum(len(p["images"]) for p in built)))


def write_post(p, prev_p, next_p):
    body_blocks = list(p["blocks"])
    lead_fig = ""
    if p["lead"]:
        # promote the first image to a lead visual
        for idx, b in enumerate(body_blocks):
            if p["lead"] in b:
                lead_fig = ('<figure class="lead-shot"><img src="../assets/img/%s" alt="" '
                            'fetchpriority="high" decoding="async"></figure>' % p["lead"])
                body_blocks.pop(idx)
                break

    # if the article opens with the same line we used as the dek, don't print it twice
    if p["dek"]:
        def norm(x):
            return re.sub(r"[^a-z0-9]", "", re.sub(r"<[^>]+>", "", x).lower())[:60]
        for idx, b in enumerate(body_blocks):
            if b.startswith("<p>"):
                if norm(b) and norm(b) == norm(p["dek"]):
                    body_blocks.pop(idx)
                break

    # drop cap on the opening paragraph, but only if it is a real one —
    # a short standfirst or a "A note before you read" label looks silly with it
    for idx, b in enumerate(body_blocks):
        if b.startswith("<p>"):
            if len(re.sub(r"<[^>]+>", "", b)) > 120:
                body_blocks[idx] = '<p class="lede">' + b[3:]
            break

    prose = "\n".join(body_blocks)
    if p["locked"]:
        prose += """
<div class="locked-panel">
  <div class="locked-mark">&#9679;</div>
  <h3>The rest of this one was behind the paywall</h3>
  <p>This post was published as a subscriber-only piece on the original site, so the archive only holds the opening. The full text lives with the original publisher.</p>
  <a class="btn" href="https://www.dreadpirateduppie.com/post/%s" rel="noopener">Read it at the source &#8594;</a>
</div>""" % p["slug"]

    sub = '<p class="post-sub">%s</p>' % html.escape(p["sub"]) if p["sub"] else ""
    dek = '<p class="post-dek">%s</p>' % html.escape(p["dek"]) if p["dek"] else ""

    nav = []
    if prev_p:
        nav.append('<a class="pn prev" href="%s.html"><span class="pn-k">&#8592; Previous</span>'
                   '<span class="pn-t">%s</span></a>' % (prev_p["slug"], html.escape(prev_p["title"])))
    else:
        nav.append('<span class="pn empty"></span>')
    if next_p:
        nav.append('<a class="pn next" href="%s.html"><span class="pn-k">Next &#8594;</span>'
                   '<span class="pn-t">%s</span></a>' % (next_p["slug"], html.escape(next_p["title"])))
    else:
        nav.append('<span class="pn empty"></span>')

    meta = "%d min read &middot; %s words" % (p["mins"], f"{p['words']:,}")
    if p["locked"]:
        meta = "Excerpt &middot; subscriber post"

    body = f"""
<div class="progress" id="progress"></div>
<header class="topbar">
  <a class="topbar-back" href="../index.html">&#8592; <span>Archive</span></a>
  <a class="topbar-mark" href="../index.html">DPD</a>
</header>
<main class="post">
  <div class="post-head">
    <div class="tags">{tag_html(p['tags'])}</div>
    <h1 class="post-title">{html.escape(p['title'])}</h1>
    {sub}
    {dek}
    <div class="post-meta">{meta}</div>
  </div>
  {lead_fig}
  <article class="prose">
    {prose}
  </article>
  <nav class="postnav">{''.join(nav)}</nav>
  <footer class="foot">
    <a href="../index.html" class="foot-home">&#8592; Back to the archive</a>
  </footer>
</main>
<script>
(function(){{
  var bar=document.getElementById('progress');
  function upd(){{
    var h=document.documentElement,
        m=(h.scrollHeight-h.clientHeight);
    bar.style.transform='scaleX('+(m>0?(h.scrollTop||document.body.scrollTop)/m:0)+')';
  }}
  addEventListener('scroll',upd,{{passive:true}});addEventListener('resize',upd);upd();
}})();
</script>
"""
    out = shell("%s — %s" % (p["title"], SITE_TITLE),
                p["dek"] or SITE_DESC, body, css_depth=1,
                extra_class="post-page", og_img=p["lead"])
    with open(os.path.join(OUT_POSTS, p["slug"] + ".html"), "w") as f:
        f.write(out)


def write_index(built):
    rows = []
    for i, p in enumerate(built):
        thumb = ('<img src="assets/img/%s" alt="" loading="lazy" decoding="async">' % p["lead"]
                 if p["lead"] else '<span class="no-thumb">&#9760;</span>')
        lock = '<span class="lock" title="Subscriber post">&#9679; excerpt</span>' if p["locked"] else ""
        meta = ("Excerpt" if p["locked"] else "%d min" % p["mins"])
        rows.append(f"""
    <a class="row{' is-locked' if p['locked'] else ''}" href="posts/{p['slug']}.html">
      <span class="row-num">{i + 1:02d}</span>
      <span class="row-body">
        <span class="row-title">{html.escape(p['title'])}{lock}</span>
        {'<span class="row-sub">' + html.escape(p['sub']) + '</span>' if p['sub'] else ''}
        <span class="row-dek">{html.escape(p['dek'])}</span>
        <span class="row-tags">{tag_html(p['tags'])}<span class="row-mins">{meta}</span></span>
      </span>
      <span class="row-thumb">{thumb}</span>
    </a>""")

    total_words = sum(p["words"] for p in built)
    body = f"""
<header class="hero">
  <div class="hero-inner">
    <p class="kicker">Archive &#183; Peckham, London</p>
    <h1 class="wordmark">
      <span class="wm-l1">DREAD</span>
      <span class="wm-l2">PIRATE</span>
      <span class="wm-l3">DUPPIE</span>
    </h1>
    <p class="hero-tag">{html.escape(SITE_DESC)}</p>
    <div class="hero-stats">
      <span><b>{len(built)}</b> posts</span>
      <span><b>{total_words:,}</b> words</span>
      <span><b>{sum(len(p['images']) for p in built)}</b> images</span>
    </div>
  </div>
  <div class="scroll-hint" aria-hidden="true">&#8595;</div>
</header>

<main>
  <section class="archive" id="archive">
    <h2 class="sec-title"><span>The Archive</span></h2>
    <div class="rows">{''.join(rows)}
    </div>
  </section>

  <section class="about" id="about">
    <h2 class="sec-title"><span>About</span></h2>
    <div class="about-grid">
      <div class="about-text">
        <p>Long-form writing on privacy, power, culture and the cost of your attention &mdash;
        written from Peckham, London, in plain language, with the receipts.</p>
        <p>The same person builds <b>PushInn</b>, a spot-mapping app for skaters born out of
        a camera roll full of ledges collected while delivering food across the city, and runs
        <b>BTEK.FM</b> on the side.</p>
        <p class="about-note">This is a static archive of writing originally published at
        dreadpirateduppie.com. Posts that were subscriber-only appear here as excerpts,
        linking back to the source.</p>
      </div>
      <div class="about-links">
        <a class="lk" href="https://pushinn.app/" rel="noopener"><b>PushInn</b><span>Find the spot. Push in.</span></a>
        <a class="lk" href="https://dreadpirateduppie.github.io/BTEK.FM/" rel="noopener"><b>BTEK.FM</b><span>Radio &amp; live sets</span></a>
        <a class="lk" href="https://dreadpirateduppie.github.io/rmgl-portfolio/" rel="noopener"><b>RMGL</b><span>Photography</span></a>
        <a class="lk" href="https://www.dreadpirateduppie.com" rel="noopener"><b>Original site</b><span>dreadpirateduppie.com</span></a>
        <a class="lk" href="https://github.com/DreadPirateDuppie" rel="noopener"><b>GitHub</b><span>@DreadPirateDuppie</span></a>
      </div>
    </div>
  </section>
</main>

<footer class="site-foot">
  <span class="sf-mark">&#9760;</span>
  <span>Dread Pirate Duppie &mdash; archive</span>
</footer>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(shell(SITE_TITLE + " — Archive", SITE_DESC, body, css_depth=0,
                      extra_class="home", og_img=built[0]["lead"]))


if __name__ == "__main__":
    main()

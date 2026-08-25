#!/usr/bin/env python3
"""Static rebuild of dreadpirateduppie.com.

Metadata (titles, dates, categories, excerpts, read times, cover images) comes
from the site's own RSS feed; post bodies come from the scraped markdown in
content/posts/.
"""
import html
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content", "posts")
OUT_POSTS = os.path.join(ROOT, "posts")

SITE = "DREADPIRATEDUPPIE.COM"
TAGLINE = "> _STANDING_ON_BUSINESS_SINCE_2025."
EMAIL = "Dreadpirateduppie@proton.me"
ORIGIN = "https://www.dreadpirateduppie.com"

NAV = [
    # mirrors the original site's menu. Only the blog is reproduced in this
    # archive; the other sections still live on dreadpirateduppie.com.
    ("Home", "index.html", ""),
    ("Photography", ORIGIN + "/projects-7", "ext"),
    ("Blog", "index.html#blog", ""),
    ("BTEK.FM", ORIGIN + "/livestream", "ext"),
    ("Shop", ORIGIN + "/category/all-products", "ext"),
    ("Letterboxd", ORIGIN + "/letterboxd", "ext"),
    ("About", ORIGIN + "/about", "ext"),
]

# covers that are logos, not photographs: letterbox them instead of cropping
COVER_CONTAIN = {"a055e6_dc2f43b66a114014bf30e2c500eb37f9"}

CATS = [">_General", ">_Trading", ">_Crypto", ">_The_System",
        ">_Pushinn", ">_Captins_Logs", ">_Harm_Reduction"]

# slug, title, date, categories, read time, cover image hash, feed excerpt
POSTS = [
    ("the-ai-copium-bubble-toll-booth-economy-part-ii",
     "The AI Copium Bubble: Toll Booth Economy, Part II", "2026-07-22", "Jul 22",
     [">_Trading", ">_Crypto"], 8, "a055e6_46ecea8660544f2490ea415d245919c8",
     "We are watching an exact repeat of the dot com crash, and the market is completely "
     "swimming in corporate copium. The stock prices of these massive tech monopolies are "
     "completely disconnected from reality..."),
    ("substance-as-a-service-the-crackhead-cliches",
     "Substance as a Service & the Crackhead Clichés", "2026-07-14", "Jul 14",
     [">_Captins_Logs"], 31, "a055e6_fa4c72d220954ed987221b1b634dc255",
     "I am archiving this record as a Time Capsule. When the empire is fully established and "
     "I'm looking back on these foundational years from a much more comfortable vantage point, "
     "it'll be highly amusing to remember exactly what the terrain looked like when I was still "
     "a captain without a physical vessel, forced to navigate the asphalt archipelago of "
     "Peckham on foot..."),
    ("legalize-it", "Legalize it.", "2026-06-08", "Jun 8",
     [">_The_System"], 8, "a055e6_53844be106a944c485076e79c38db673",
     "Wag1, This one's a good one, so get comfortable and suspend your disbelief if you are a "
     "sceptic, as I have a point to make. A friend of mine recently got into some shit with "
     "their neighbor. Not over noise, not over parking, not over anything that actually "
     "disrupts anyone's life in a meaningful way..."),
    ("collateral-damage", "Collateral Damage", "2026-06-06", "Jun 6",
     [">_The_System"], 4, "a055e6_681be9f531ed4f92a3774049847db2ef",
     "Wag1, today I want to share a story about somebody close to me. My niece is 14. And I'm "
     "not gonna lie, watching what's been happening to her lately has been genuinely "
     "disheartening. She's smart. Like, actually smart. But she's been completely swallowed by "
     "a K-pop rabbit hole..."),
    ("free-isn-t-free", "Free Isn't Free", "2026-05-12", "May 12",
     [">_The_System"], 3, "a055e6_ea7369d0b10f4776a4fd816f2c4109d1",
     "Yo, wag1 people. Had this idea floating around in my head for a bit and felt like it "
     "deserved to see the light of day, so here you go. To kick this one off, we're going to do "
     "a thought experiment. Imagine someone steals your phone. What do you do?"),
    ("xmr-ftw", "XMR FTW", "2026-02-17", "Feb 17",
     [">_Crypto", ">_Trading"], 11, "a055e6_dc2f43b66a114014bf30e2c500eb37f9",
     "In a world where every financial decision you make is being watched, tracked, and "
     "recorded, your financial privacy isn't just something nice to have, it's something you "
     "need to protect. Cash is disappearing, banks are tightening their control, and "
     "corporations are profiting off your personal data. This is where Monero (XMR) steps in."),
    ("the-wagwan-paradox-consuming-the-culture-fearing-the-people",
     "The \"Wagwan\" Paradox: Consuming the Culture, Fearing the People", "2026-02-16", "Feb 16",
     [">_General"], 16, "a055e6_78586a8a1d88481181fdbf60aef61e75",
     "From the living room to the global charts—how society loves Black culture but stays "
     "terrified of Black people."),
    ("introducing-pushinn", "Introducing Pushinn", "2026-01-30", "Jan 30",
     [">_Pushinn"], 7, "a055e6_288610b888e5493db1457f08a2a0ff52",
     "Yoo, This post is about a project thats been living rent free in my head since 2021. "
     "Can't lie It’s not just a business idea at this point; it’s become an obsession."),
    ("the-toll-booth-economy-education-housing-the-end-of-sovereignty",
     "The Toll Booth Economy: Education, Housing & The End of Sovereignty", "2026-01-20", "Jan 20",
     [">_The_System"], 3, "a055e6_3be58bbfa946417a8babe3a2eb5935b5",
     "Back In 1978, the economic architecture of London supported a high degree of individual "
     "sovereignty. A twenty-three-year-old on a median salary could typically afford a "
     "Victorian terrace in Zone 3. At that time, the price-to-income ratio for housing was "
     "approximately 3:1."),
    ("the-digital-reality-check-limited-offer",
     "The Clout Chasing Culture Vultures Starter Pack", "2026-01-15", "Jan 15",
     [">_General"], 1, "a055e6_1740b92f2c224735842932dd7e514e64",
     "If you’ve ever felt like your online presence is starting to lean more toward a "
     "\"costume\" than a genuine appreciation, you need to step back. This guide is designed to "
     "help you navigate that line, identifying where appreciation ends and extraction begins."),
    ("the-winter-protocol-a-31-day-system-override-for-the-urban-high-performer",
     "The Grey Sky Detox: A Technical Breakdown for surviving dry Jan in the London Winter",
     "2026-01-12", "Jan 12",
     [">_Harm_Reduction"], 12, "a055e6_8990b372be8c431c89c11cec2fa28de6",
     "it's mid-January and we're damn near halfway through Dry January. If you're still "
     "standing, congrats MF, you've made it past the hardest part. If you've already folded, "
     "no judgment, but maybe give this a read anyway."),
    ("dreadpirateroberts", "@DreadPirateRoberts", "2025-01-23", "Jan 23, 2025",
     [">_Crypto"], 2, "a055e6_92c25e712a0c49a29f09c39810b29c57",
     "At Long Last, Ross Is Free!!! Ten years ago, a crazy MF called Ross Ulbricht created the "
     "Silk Road, a platform that redefined freedom in the digital age. It was revolutionary, a "
     "space for privacy, autonomy, and resistance against centralized control."),
    ("xidiocracy", "Xidiocracy", "2025-01-23", "Jan 23, 2025",
     [">_The_System"], 4, "a055e6_392ba068eb8c4be0a409da57c44e0e05",
     "It’s 2025, and society has become unrecognizable. People are obsessed with laughing "
     "gas, social media, and bias-affirming echo chambers. Birthrates have plummeted as "
     "governments worldwide succumb to the temptations of corruption."),
    ("drake-is-a-clown", "Drake is a  Clown", "2025-01-19", "Jan 19, 2025",
     [">_General"], 2, "a055e6_35affedf822b460e9bdcd6bc543d6e73",
     "Wag1, this one dedicated to Champagne Papi. The other night, I was deep in the YouTube "
     "rabbit hole and stumbled on a video about the self-proclaimed alpha... and man, it's not "
     "looking good for ya boy."),
]

PAYWALL_RE = re.compile(r"###\s*Want to read more\?", re.I)
IMG_MD_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
HASH_RE = re.compile(r"(a055e6_[a-f0-9]+)")
LINK_RE = re.compile(r"\[([^\]]*)\]\(((?:[^()]|\([^()]*\))*)\)")
JUNK_LINK_RE = re.compile(r"^https?://[A-Za-z]+\.[A-Za-z]{2,3}/?$")
URLTEXT_RE = re.compile(r"^https?://([^/\s]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
JUNK_LINES = {
    "Limited Time OfferThe Clout Chasing Culture Vultures Starter Pack£25.00£5.00Buy Now"
}


def _render_link(m):
    text, href = m.group(1), m.group(2)
    if JUNK_LINK_RE.match(href):          # Wix autolinked a sentence boundary
        return text if text.strip() else ""
    if not text.strip():
        return ""
    u = URLTEXT_RE.match(text.strip())    # a bare URL as its own label reads badly
    if u:
        text = u.group(1).replace("www.", "")
    return '<a href="%s" rel="noopener">%s</a>' % (html.escape(href, quote=True), text)


def inline(text):
    t = html.escape(text, quote=False)
    t = LINK_RE.sub(_render_link, t)
    t = BOLD_RE.sub(r"<strong>\1</strong>", t)
    t = ITAL_RE.sub(r"<em>\1</em>", t)
    return t


def parse(md_text):
    """Return (blocks, images, locked)."""
    lines, body, seen_rule = md_text.split("\n"), [], False
    for ln in lines:
        if not seen_rule:
            if ln.strip() == "---":
                seen_rule = True
            continue
        body.append(ln)

    locked, kept = False, []
    for ln in body:
        if PAYWALL_RE.search(ln):
            locked = True
            break
        kept.append(ln)

    blocks, images, para, items = [], [], [], []

    def flush_para():
        if para:
            txt = " ".join(para).strip()
            if txt:
                blocks.append("<p>%s</p>" % inline(txt))
            para.clear()

    def flush_list():
        if items:
            blocks.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(i) for i in items))
            items.clear()

    for ln in kept:
        s = ln.strip()
        if s in JUNK_LINES:
            continue
        if s in ("DPD.", "DPD"):
            flush_para(); flush_list()
            blocks.append('<p class="sig">DPD.</p>')
            continue
        if not s:
            flush_para(); flush_list()
            continue
        m = IMG_MD_RE.fullmatch(s)
        if m:
            flush_para(); flush_list()
            h = HASH_RE.search(m.group(2))
            if h:
                fn = h.group(1) + ".webp"
                images.append(fn)
                blocks.append('<figure><img src="../assets/img/%s" alt="" loading="lazy" '
                              'decoding="async"></figure>' % fn)
            continue
        if s == "---":
            flush_para(); flush_list()
            blocks.append('<hr>')
            continue
        if s.startswith("#"):
            flush_para(); flush_list()
            lvl = min(len(s) - len(s.lstrip("#")) + 1, 4)
            blocks.append("<h%d>%s</h%d>" % (lvl, inline(s.lstrip("#").strip()), lvl))
            continue
        if s.startswith("> "):
            flush_para(); flush_list()
            blocks.append("<blockquote><p>%s</p></blockquote>" % inline(s[2:]))
            continue
        if s.startswith(("- ", "* ")):
            flush_para()
            items.append(s[2:])
            continue
        flush_list()
        para.append(s)

    flush_para(); flush_list()
    return blocks, images, locked


def marquee(pos):
    run = ("<span>" + (" " + TAGLINE) * 6 + "</span>") * 2
    return ('<div class="ticker %s" aria-hidden="true"><div class="ticker-run">%s</div></div>'
            % (pos, run))


def nav(up):
    out = []
    for label, href, kind in NAV:
        h = href if kind == "ext" else up + href
        rel = ' rel="noopener"' if kind == "ext" else ""
        out.append('<a href="%s"%s>%s</a>' % (h, rel, html.escape(label)))
    return '<nav class="nav">%s</nav>' % "".join(out)


def catbar(up, active="all"):
    import urllib.parse
    out = ['<a class="cat%s" href="%sindex.html#blog" data-cat="all">All Posts</a>'
           % (" on" if active == "all" else "", up)]
    for c in CATS:
        out.append('<a class="cat" href="%sindex.html?cat=%s#blog" data-cat="%s">%s</a>'
                   % (up, urllib.parse.quote(c), html.escape(c, quote=True), html.escape(c)))
    return '<div class="catbar">%s</div>' % "".join(out)


def byline(p, cls=""):
    return ('<div class="byline %s"><img class="avatar" src="%savatar.webp" alt="" width="32" '
            'height="32"><span class="who">DPD</span><span class="dot">&middot;</span>'
            '<time datetime="%s">%s</time><span class="dot">&middot;</span>'
            '<span class="rt">%d min read</span></div>'
            % (cls, p["imgbase"], p["date"], p["disp"], p["mins"]))


def chips(p, up):
    import urllib.parse
    return "".join('<a class="chip" href="%sindex.html?cat=%s#blog" data-cat="%s">%s</a>'
                   % (up, urllib.parse.quote(c), html.escape(c, quote=True), html.escape(c))
                   for c in p["cats"])


def shell(title, desc, body, up, og=None, cls=""):
    ogtag = ('<meta property="og:image" content="%sassets/img/%s.webp">' % (up, og)) if og else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:type" content="website">{ogtag}
<link rel="stylesheet" href="{up}assets/css/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%23000%22/><text y=%2278%22 x=%2250%22 text-anchor=%22middle%22 font-size=%2288%22 fill=%22%2300FF07%22 font-family=%22monospace%22>&gt;</text></svg>">
</head>
<body class="{cls}">
{marquee('t')}
{body}
{marquee('b')}
<script src="{up}assets/js/site.js" defer></script>
</body>
</html>
"""


def footer(up):
    return f"""
<footer class="foot" id="about">
  <canvas class="rain" data-rain aria-hidden="true"></canvas>
  <div class="foot-in">
    <p class="foot-mark">&gt;{SITE}</p>
    <p class="foot-line">&copy; DreadPirateDuppie 2026.</p>
    <p class="foot-line"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p class="foot-line"><a class="red" href="{ORIGIN}" rel="noopener">&gt;_ORIGINAL_SITE</a></p>
  </div>
</footer>
"""


def main():
    if os.path.isdir(OUT_POSTS):
        shutil.rmtree(OUT_POSTS)
    os.makedirs(OUT_POSTS)

    built = []
    for (slug, title, date, disp, cats, mins, cover, excerpt) in POSTS:
        with open(os.path.join(SRC, slug + ".md")) as f:
            blocks, images, locked = parse(f.read())
        built.append(dict(slug=slug, title=title, date=date, disp=disp, cats=cats,
                          mins=mins, cover=cover, excerpt=excerpt, blocks=blocks,
                          images=images, locked=locked, imgbase="../assets/img/"))

    for i, p in enumerate(built):
        write_post(p, built[i - 1] if i else None,
                   built[i + 1] if i < len(built) - 1 else None)
    write_index(built)
    print("built %d posts, %d locked" % (len(built), sum(p["locked"] for p in built)))


def write_post(p, prev_p, next_p):
    blocks = list(p["blocks"])
    # some paywalled posts were cut off before the scraper saw any body text;
    # the site's own feed excerpt is the best opening we legitimately have
    if p["locked"]:
        body_len = len(re.sub(r"<[^>]+>", "", " ".join(blocks)))
        if body_len < len(p["excerpt"]):
            blocks = ["<p>%s</p>" % html.escape(p["excerpt"], quote=False)]
    prose = "\n".join(blocks)
    if p["locked"]:
        prose += f"""
<div class="locked">
  <p class="locked-h">&gt;_ACCESS_RESTRICTED</p>
  <p>This one was published as a subscriber-only post, so the archive holds the opening
  only. The full text lives with the original publisher.</p>
  <a class="btn" href="{ORIGIN}/post/{p['slug']}" rel="noopener">&gt;_READ_AT_SOURCE</a>
</div>"""

    nv = []
    if prev_p:
        nv.append('<a class="pn" href="%s.html"><span>&lt; PREV</span><b>%s</b></a>'
                  % (prev_p["slug"], html.escape(prev_p["title"])))
    else:
        nv.append("<span></span>")
    if next_p:
        nv.append('<a class="pn next" href="%s.html"><span>NEXT &gt;</span><b>%s</b></a>'
                  % (next_p["slug"], html.escape(next_p["title"])))
    else:
        nv.append("<span></span>")

    body = f"""
<header class="head compact">
  <canvas class="rain" data-rain aria-hidden="true"></canvas>
  {nav("../")}
  <a class="wordmark small" href="../index.html">&gt;{SITE}</a>
</header>
{catbar("../")}
<main class="wrap">
  <article class="term">
    {byline(p)}
    <h1 class="ptitle">{html.escape(p['title'])}</h1>
    <div class="chips">{chips(p, "../")}</div>
    <div class="prose">
      {prose}
    </div>
  </article>
  <nav class="postnav">{''.join(nv)}</nav>
</main>
{footer("../")}
"""
    with open(os.path.join(OUT_POSTS, p["slug"] + ".html"), "w") as f:
        f.write(shell("%s | %s" % (p["title"], SITE), p["excerpt"], body, "../",
                      og=p["cover"], cls="post-page"))


def write_index(built):
    feat = built[0]
    feat_html = f"""
  <section class="featured">
    <a class="feat-img{" fit" if feat["cover"] in COVER_CONTAIN else ""}" href="posts/{feat['slug']}.html">
      <img src="assets/img/{feat['cover']}.webp" alt="" fetchpriority="high" decoding="async">
    </a>
    <div class="feat-body">
      <div class="feat-row">
        {byline(dict(feat, imgbase="assets/img/"))}
        <span class="feat-label">FEATURED POST</span>
      </div>
      <div class="chips">{chips(feat, "")}</div>
      <h2 class="feat-title"><a href="posts/{feat['slug']}.html">{html.escape(feat['title'])}</a></h2>
      <p class="feat-ex">{html.escape(feat['excerpt'])}</p>
    </div>
  </section>"""

    cards = []
    for p in built:
        lock = '<span class="lock">&gt;_LOCKED</span>' if p["locked"] else ""
        cards.append(f"""
    <article class="card" data-cats="{html.escape(' '.join(p['cats']), quote=True)}">
      <a class="card-img{" fit" if p["cover"] in COVER_CONTAIN else ""}" href="posts/{p['slug']}.html">
        <img src="assets/img/{p['cover']}.webp" alt="" loading="lazy" decoding="async">
      </a>
      <div class="card-body">
        {byline(dict(p, imgbase="assets/img/"))}
        <div class="chips">{chips(p, "")}{lock}</div>
        <h3 class="card-title"><a href="posts/{p['slug']}.html">{html.escape(p['title'])}</a></h3>
        <p class="card-ex">{html.escape(p['excerpt'])}</p>
      </div>
    </article>""")

    body = f"""
<header class="head">
  <canvas class="rain" data-rain aria-hidden="true"></canvas>
  {nav("")}
  <h1 class="wordmark">&gt;{SITE}</h1>
</header>
<main class="wrap">
  {feat_html}
  <div class="sec-row" id="blog">
    <h2 class="sec">"Blog"</h2>
    <p class="count"><span id="shown">{len(built)}</span> / {len(built)} POSTS</p>
  </div>
  {catbar("")}
  <div class="grid">{''.join(cards)}</div>
  <p class="empty" id="empty" hidden>&gt;_NO_POSTS_IN_THIS_CATEGORY</p>

  <section class="who-box">
    <h2 class="sec">Who is DPD?</h2>
    <p>/Founder/Scientist/Student of life/Triptonaught/Statistic/Boss/Citizen of The World/God/G.</p>
    <p>Writing out of Peckham, London on privacy, power, culture and the cost of your attention.</p>
    <p class="note">This is a static archive of {len(built)} posts from
    dreadpirateduppie.com. Subscriber-only posts appear as excerpts and link back to the source.</p>
  </section>
</main>
{footer("")}
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(shell(SITE, "Essays on privacy, power, culture and the cost of your attention. "
                            "Written from Peckham, London.", body, "", og=feat["cover"],
                      cls="home"))


if __name__ == "__main__":
    main()

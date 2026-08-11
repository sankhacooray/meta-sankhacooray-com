#!/usr/bin/env python3
"""Rebuild index.html from the live Open Graph metadata of every network sub-site.

    python3 build/refresh.py

Fetches each domain below, parses its live og:title / og:description / og:image /
theme-color (quote-aware, entity-decoded — exactly what WhatsApp/Slack would read),
and bakes a pre-rendered card grid into ../index.html. Works without JS; the page's
inline script only adds the search filter. Thumbnails hot-link each site's live og:image.

To add / reorder / re-tag a site, edit ORDER. `tag` is not shown as a chip (removed by
request) but is still folded into each card's data-search string so search-by-category works.
"""
import subprocess, re, json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "..", "index.html")

# domain -> category tag (curated order; apex first). tag is search-only, not a visible chip.
ORDER = [
    ("sankhacooray.com",           "home"),
    ("whoami.sankhacooray.com",    "identity"),
    ("v2.sankhacooray.com",        "portfolio"),
    ("v1.sankhacooray.com",        "portfolio"),
    ("dev.sankhacooray.com",       "lab"),
    ("vitals.sankhacooray.com",    "lab"),
    ("biolens.sankhacooray.com",   "research"),
    ("ensemble.sankhacooray.com",  "music"),
    ("conduct.sankhacooray.com",   "music"),
    ("fold.sankhacooray.com",      "craft"),
    ("palette.sankhacooray.com",   "design"),
    ("date.sankhacooray.com",      "playful"),
    ("coffeelab.sankhacooray.com", "tool"),
    ("mixlab.sankhacooray.com",    "tool"),
    ("pixels.sankhacooray.com",    "tool"),
    ("paynow.sankhacooray.com",    "tool"),
    ("travel.sankhacooray.com",    "map"),
    ("cdn.sankhacooray.com",       "infra"),
    ("auth.sankhacooray.com",      "infra"),
]

def fetch(d):
    # -k so a sub-site with an in-flight custom-domain cert (e.g. a fresh deploy) still parses
    return subprocess.run(["curl", "-skL", "--max-time", "25", f"https://{d}/"],
                          capture_output=True, text=True).stdout

def meta(h, prop, attr="property"):
    r = re.search(r'<meta[^>]*' + attr + r'=(["\'])' + re.escape(prop) + r'\1[^>]*?content=(["\'])(.*?)\2', h, re.I | re.S)
    if r: return html.unescape(r.group(3).strip())
    r = re.search(r'<meta[^>]*content=(["\'])(.*?)\1[^>]*?' + attr + r'=(["\'])' + re.escape(prop) + r'\3', h, re.I | re.S)
    return html.unescape(r.group(2).strip()) if r else None

def scrape(d):
    h = fetch(d)
    t = meta(h, "og:title") or meta(h, "twitter:title", "name")
    if not t:
        m = re.search(r'<title>(.*?)</title>', h, re.I | re.S); t = html.unescape(m.group(1).strip()) if m else d
    return {
        "domain": d,
        "title": t,
        "description": meta(h, "og:description") or meta(h, "description", "name") or meta(h, "twitter:description", "name"),
        "image": meta(h, "og:image") or meta(h, "twitter:image", "name"),
        "theme": meta(h, "theme-color", "name") or "#888",
    }

def esc(s): return html.escape(s or "", quote=True)

def card(dom, tag, r):
    title, desc, img, theme = esc(r["title"]), esc(r["description"]), esc(r["image"]), r["theme"]
    label = "sankhacooray.com" if dom == "sankhacooray.com" else dom.replace(".sankhacooray.com", "")
    mono = "SC" if dom == "sankhacooray.com" else esc(label[:2].upper())
    featured = " card--featured" if dom == "sankhacooray.com" else ""
    search = esc((label + " " + (r["title"] or "") + " " + (r["description"] or "") + " " + tag).lower())
    return f'''      <a class="card{featured}" href="https://{dom}/" target="_blank" rel="noopener"
         data-search="{search}" style="--accent:{theme}">
        <div class="thumb">
          <img src="{img}" alt="Share preview of {title}" loading="lazy" decoding="async"
               onerror="this.closest('.thumb').classList.add('thumb--fallback');this.remove();">
          <span class="thumb-fallback" aria-hidden="true">{mono}</span>
        </div>
        <div class="body">
          <span class="domain"><span class="dot"></span>{esc(dom)}</span>
          <h2 class="title">{title}</h2>
          <p class="desc">{desc}</p>
        </div>
      </a>'''

def main():
    rows = {d: scrape(d) for d, _ in ORDER}
    cards = "\n".join(card(d, tag, rows[d]) for d, tag in ORDER)
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    out = tpl.replace("<!--CARDS-->", cards).replace("{{COUNT}}", str(len(ORDER)))
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"wrote {OUT} — {len(ORDER)} cards")

if __name__ == "__main__":
    main()

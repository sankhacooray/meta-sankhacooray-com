#!/usr/bin/env python3
"""Build public/index.html from template.html + sites.json.

    python3 build.py

sites.json is the single list of sites: the page's card groups come from it, and the
Worker (src/worker.js) uses the same file as its /api/og host allowlist. Cards are baked
as placeholders (link + host); the page fills each one at view time from /api/og, so
share data is always live.
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = ("Every public sankhacooray.com site shown as its link preview, read live: "
        "share image, title and description, so a missing or weak card stands out.")
assert 120 <= len(DESC) <= 160, len(DESC)


def card(host):
    short = "sankhacooray" if host == "sankhacooray.com" else host.split(".")[0]
    h = html.escape(host)
    return f'''      <a class="card loading" href="https://{h}/" target="_blank" rel="noopener" data-host="{h}">
        <div class="thumb loading">
          <div class="ph" aria-hidden="true"><b>{html.escape(short)}</b><span>{h}</span></div>
          <span class="flag" hidden></span>
        </div>
        <div class="body">
          <span class="domain"><span class="dot"></span><span class="h">{h}</span><span class="note" hidden></span></span>
          <h3 class="title">{html.escape(short)}</h3>
          <p class="desc"></p>
        </div>
      </a>'''


def main():
    data = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    tabs = "".join(f'<a href="#{g["id"]}">{html.escape(g["tab"])}</a>' for g in data["groups"])
    sections = "\n".join(
        f'''  <section id="{g["id"]}">
    <div class="head"><h2>{html.escape(g["title"])}</h2><p>{html.escape(g["note"])}</p></div>
    <div class="cards">
{chr(10).join(card(h) for h in g["hosts"])}
    </div>
  </section>''' for g in data["groups"])
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    out = tpl.replace("{{TABS}}", tabs).replace("{{SECTIONS}}", sections).replace("{{DESC}}", html.escape(DESC))
    os.makedirs(os.path.join(HERE, "public"), exist_ok=True)
    open(os.path.join(HERE, "public", "index.html"), "w", encoding="utf-8").write(out)
    man = json.load(open(os.path.join(HERE, "public", "manifest.webmanifest")))
    man["description"] = DESC
    open(os.path.join(HERE, "public", "manifest.webmanifest"), "w").write(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    print("wrote public/index.html")


if __name__ == "__main__":
    main()

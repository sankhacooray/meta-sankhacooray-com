# meta.sankhacooray.com

A link-preview gallery of the whole sankhacooray network — every sub-site shown
as the share card you'd see when pasting its URL into WhatsApp / iMessage / Slack.

Static GitHub Pages site. Cards are pre-rendered from each sub-site's live Open
Graph metadata (title / description / og:image) and baked into `index.html`.
Thumbnails hot-link each sub-site's live `og:image`, so they refresh whenever a
sub-site redeploys.

**Refresh the grid** (re-pull everyone's latest OG data, e.g. after a sub-site
changes its share card):

    python3 build/refresh.py

- `index.html` — the grid (self-contained, works without JS; JS only adds search)
- `build/refresh.py` — fetches live OG metadata for every domain and regenerates the grid
- `build/template.html` — page shell with a `<!--CARDS-->` placeholder
- `assets/` — this site's own icon.svg / og-card.html / rendered og-image + PNG icons
- `manifest.webmanifest` — PWA

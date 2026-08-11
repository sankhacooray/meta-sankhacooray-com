# meta.sankhacooray.com

A link-preview gallery of the whole sankhacooray network — every sub-site shown
as the share card you'd see when pasting its URL into WhatsApp / iMessage / Slack.

Static GitHub Pages site. Cards are pre-rendered from each sub-site's live Open
Graph metadata (title / description / og:image), gathered with the fetch script
and baked into `index.html`. Thumbnails hot-link each sub-site's live `og:image`.

- `index.html` — the grid (self-contained, no build step, works without JS; JS adds search)
- `assets/` — this site's own icon.svg / og-card.html / rendered og-image + PNG icons
- `manifest.webmanifest` — PWA

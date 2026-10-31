# meta.sankhacooray.com

See README.md for build and deploy (`python3 build.py`, then `npx wrangler deploy`). Edit
`template.html`, never `public/index.html` directly.

## Lighthouse
<!-- lighthouse-optimized: 2026-10-31 -->
Baseline (mobile): performance 67, accessibility 96, best-practices 100, SEO 100.
Fixed: non-blocking Google Fonts (dropped unused DM Sans 700 and Instrument Serif italic), `--text-muted` raised to ≥4.5:1 in both themes, brand-link aria-label now contains the visible "Meta Network", share images get width/height, `fetchpriority=high` on the first row and `loading=lazy` below it, `_headers` gives `/assets/*` a 30-day TTL.
Left: the card images are other sites' 1200×630 PNG share images streamed by the Worker; resizing them to WebP needs Cloudflare Image Transformations enabled on the zone (currently off, /cdn-cgi/image 404s). `/api/og/image` keeps its 10-min browser TTL on purpose so fixed share cards show within the hour.

# meta.sankhacooray.com

A link-preview gallery of the whole sankhacooray network: every public sub-site shown
as the share card you'd see when pasting its URL into WhatsApp / iMessage / Slack,
read live at view time, with gaps flagged (no share image, broken image, description
outside 120–160 characters). "Show gaps" in the app bar filters to just those.

Cloudflare Worker (`meta-sankhacooray`) with static assets, on the custom domain
meta.sankhacooray.com.

    python3 build.py
    CLOUDFLARE_ACCOUNT_ID=9a1da48a0f61e7cebcba39517856d87e npx wrangler deploy

Local preview: `npx wrangler dev --port 4850` (ports 4850–4859).

- `sites.json` — the one list of sites and their groups. The page's cards and the
  Worker's host allowlist both come from it. To add a site, add its host here, build, deploy.
- `src/worker.js` — `GET /api/og?url=https://<host>/` returns
  `{url, finalUrl, status, title, description, image, imageOk, siteName, theme}`;
  `GET /api/og/image?url=…` streams that page's current og:image. Allowlisted hosts only
  (others get 403); good answers are cached at the edge for 1 h.
- `template.html` → `build.py` → `public/index.html` (cards baked as placeholders, filled by JS).
- `public/` — served as static assets (page, manifest, icons, `og-image-v2.jpg`).
- `og/og-card.html` + `og/ui.png` — source of the share image (render at 1200×630 with
  headless Chrome, save as JPEG to `public/assets/og-image-v2.jpg`).

Left out on purpose: private or family pages (manel, sos, noel, bills, date, ech),
infrastructure and test hosts (auth, cdn, test, chi-review-api, aiseecoder, _domainconnect),
hosts that don't answer (design, sense), duplicates (www and v3 redirect to the apex) and
retired hubs: kitchen (→ food), fold (→ make, paper craft → craft), lab (→ dev),
palette (→ design) and biolens (→ biomed).

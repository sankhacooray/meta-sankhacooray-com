// meta.sankhacooray.com Worker.
// Static files in ./public are served first; anything without a matching file lands here.
//
// GET /api/og?url=https://<host>/
//   Reads the page's current share metadata and returns JSON:
//   { url, finalUrl, status, title, description, image, imageOk, siteName, theme }
//   `image` is the absolute og:image URL; `imageOk` says whether it loads as a real image.
//
// GET /api/og/image?url=https://<host>/
//   Streams that page's current og:image (404 when it has none, or it isn't an image).
//
// Only the hosts listed in sites.json are allowed (no open proxy). Results are kept for
// an hour at the edge, so a fixed share card shows up within the hour.

import sites from "../sites.json";

const ALLOWED_HOSTS = new Set(sites.groups.flatMap((g) => g.hosts));
const TTL = 3600; // seconds the edge keeps a result
const BROWSER_TTL = 600; // seconds a browser keeps it
const SELF = "meta.sankhacooray.com";
const UA = "Mozilla/5.0 (compatible; meta.sankhacooray.com link-preview; +https://meta.sankhacooray.com/)";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/og") return withCache(env, url, ctx, ogJson);
    if (url.pathname === "/api/og/image") return withCache(env, url, ctx, ogImage);
    return env.ASSETS.fetch(request);
  },
};

async function withCache(env, url, ctx, handler) {
  let target;
  try {
    target = new URL(url.searchParams.get("url") || "");
  } catch {
    return miss(400);
  }
  if (target.protocol !== "https:" || !ALLOWED_HOSTS.has(target.hostname)) return miss(403);
  target = new URL(`https://${target.hostname}/`); // always the site's home page

  const cache = caches.default;
  const key = new Request(`https://meta.sankhacooray.com${url.pathname}?v=2&url=${encodeURIComponent(target.href)}`);
  const hit = await cache.match(key);
  if (hit) return hit;

  let res;
  try {
    res = await handler(target, env);
  } catch {
    return miss(502);
  }
  // Only keep good answers; a page that is down or mid-deploy is asked again next time.
  if (res.status === 200 && !res.headers.has("x-og-retry")) ctx.waitUntil(cache.put(key, res.clone()));
  return res;
}

async function readPage(target, env) {
  // A Worker can't fetch its own custom domain, so this site's own card reads its static page.
  const page = target.hostname === SELF
    ? await env.ASSETS.fetch(new Request(target.href))
    : await fetch(target.href, { headers: { "user-agent": UA, accept: "text/html" }, redirect: "follow" });
  const type = page.headers.get("content-type") || "";
  const html = page.ok && type.includes("html") ? (await page.text()).slice(0, 300_000) : "";
  const base = page.url || target.href;
  const m = metaTags(html);
  const titleTag = (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1];
  let image = m["og:image"] || m["og:image:url"] || m["twitter:image"] || null;
  if (image) {
    try {
      image = new URL(image, base).href;
    } catch {
      image = null;
    }
  }
  return {
    url: target.href,
    finalUrl: base,
    status: page.status,
    title: m["og:title"] || m["twitter:title"] || (titleTag ? decode(titleTag.trim()) : null),
    description: m["og:description"] || m["description"] || m["twitter:description"] || null,
    image,
    siteName: m["og:site_name"] || null,
    theme: m["theme-color"] || null,
  };
}

async function fetchImage(src, env) {
  if (!src || !src.startsWith("https:")) return null;
  const img = new URL(src).hostname === SELF ? await env.ASSETS.fetch(new Request(src)) : await fetch(src, {
    headers: { "user-agent": UA, accept: "image/*" },
    cf: { cacheTtl: TTL, cacheEverything: true },
    redirect: "follow",
  });
  const type = img.headers.get("content-type") || "";
  if (!img.ok || !type.startsWith("image/")) {
    img.body?.cancel();
    return null;
  }
  return img;
}

async function ogJson(target, env) {
  const data = await readPage(target, env);
  const img = await fetchImage(data.image, env).catch(() => null);
  data.imageOk = !!img;
  img?.body?.cancel();
  const ok = data.status === 200;
  const headers = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": ok ? `public, max-age=${BROWSER_TTL}, s-maxage=${TTL}` : "no-store",
  };
  if (!ok) headers["x-og-retry"] = "1";
  return new Response(JSON.stringify(data), { headers });
}

async function ogImage(target, env) {
  const { image } = await readPage(target, env);
  const img = await fetchImage(image, env);
  if (!img) return miss(404);
  return new Response(img.body, {
    headers: {
      "content-type": img.headers.get("content-type"),
      "cache-control": `public, max-age=${BROWSER_TTL}, s-maxage=${TTL}`,
      "x-og-source": image,
    },
  });
}

// Every <meta> with a property/name and content, keyed by lower-cased name. First one wins.
function metaTags(html) {
  const out = {};
  for (const tag of html.match(/<meta\b[^>]*>/gi) || []) {
    const name = attr(tag, "property") || attr(tag, "name");
    const content = attr(tag, "content");
    if (!name || content == null) continue;
    const k = name.toLowerCase();
    if (!(k in out)) out[k] = decode(content.trim());
  }
  return out;
}

function attr(tag, name) {
  const m = tag.match(new RegExp(`\\b${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)')`, "i"));
  return m ? (m[1] ?? m[2]) : null;
}

function decode(s) {
  return s
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&");
}

function miss(status) {
  return new Response(null, { status, headers: { "cache-control": "public, max-age=300" } });
}

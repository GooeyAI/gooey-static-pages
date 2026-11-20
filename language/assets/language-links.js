// Links between the language, ai-agent and model pages are written as relative paths, so they can be checked
// against the files in this repo and work on the raw Cloudflare Pages site. When gooey.ai serves a page through
// its proxy, the <base> is the Pages host, so a relative link would leave gooey.ai; point those at gooey.ai instead.
(() => {
  const base = new URL(document.baseURI);
  if (base.host === location.host) return;
  document.querySelectorAll("a[href]").forEach(a => {
    const raw = a.getAttribute("href");
    if (/^([a-z][a-z0-9+.-]*:|\/\/|#)/i.test(raw)) return;
    const url = new URL(raw, document.baseURI);
    a.href = location.origin + url.pathname + url.search + url.hash;
  });
})();

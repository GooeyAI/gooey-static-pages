"""The one canonical copy of the site header: logo, page title, Login button.

Every top-level page (sovereignty/, research/, ecocost/, and whatever comes
next) embeds its own copy of this markup and CSS — there's no shared include,
because each page is served standalone through the gooey.ai proxy (see
README.md). That means nothing stops the copies from drifting, which is
exactly what happened before this file existed: sovereignty, research and
ecocost each ended up with a different header position, button shape and
button color.

So this file is the source of truth instead. When the header design changes,
edit HEADER_CSS/HEADER_HTML here, then paste the result into every page in
PAGES. `python3 scripts/check_site_header.py` verifies they haven't drifted —
run it (or let CI run it) before opening a PR that touches a page's header.

Adding a new top-level page? Add it to PAGES with its title, and copy
HEADER_CSS/HEADER_HTML into its <head>/<body> like the existing pages do.
"""

from __future__ import annotations

# folder/index.html -> the page's <span class="h-title"> text
PAGES = {
    "sovereignty/index.html": "How Middle Powers Cooperate for AI Sovereignty",
    "research/index.html": "Gooey.AI Research",
    "ecocost/index.html": "EcoCost",
}

HEADER_CSS = """      .site-header {
        position: sticky;
        top: 0;
        z-index: 50;
        display: flex;
        align-items: center;
        gap: 16px;
        height: var(--site-header-h);
        padding: 0 var(--pad-x);
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: saturate(180%) blur(12px);
        border-bottom: 1px solid var(--gy-line-soft);
      }
      .site-header .logo-link {
        display: flex;
        align-items: center;
      }
      .site-header .logo {
        height: 26px;
        width: auto;
        display: block;
      }
      .site-header .h-title {
        font-family: var(--gy-font-serif);
        font-size: 15px;
        opacity: 0;
        transition: opacity 0.25s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .site-header.scrolled .h-title {
        opacity: 1;
      }
      .site-header .login-btn {
        margin-left: auto;
        flex: none;
        padding: 8px 20px;
        border: 1px solid var(--gy-line);
        border-radius: 32px;
        font-size: 14px;
        font-weight: 500;
        background: var(--gy-white);
        text-decoration: none;
      }
      .site-header .login-btn:hover {
        background: var(--gy-surface-100);
        text-decoration: none;
      }"""

# {title} is the only thing that varies per page.
HEADER_HTML = """    <header class="site-header" id="siteHeader">
      <a class="logo-link" href="https://gooey.ai/" aria-label="Gooey.AI home">
        <img class="logo" src="assets/gooey-logo.png" alt="Gooey.AI" />
      </a>
      <span class="h-title">{title}</span>
      <a class="login-btn" href="https://gooey.ai/login/">Login</a>
    </header>"""

# A page also needs a `--pad-x` and `--site-header-h` custom property in its
# :root (both `clamp(20px, 4vw, 60px)` / `60px` in the pages above), and a
# scroll listener toggling `.scrolled` on #siteHeader so the title fades in
# — see the bottom of research/index.html for the simplest version:
#
#   const header = document.getElementById("siteHeader");
#   const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
#   window.addEventListener("scroll", onScroll, { passive: true });
#   onScroll();

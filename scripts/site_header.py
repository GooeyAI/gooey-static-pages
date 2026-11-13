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
    "lokalibrary/index.html": "LokaLibrary",
    "language-evaluation/index.html": "Low-Resource Language Evaluations",
    "language/kinyarwanda/index.html": "Best AI for Kinyarwanda",
    "language/swahili/index.html": "Best AI for Swahili",
    "language/kikuyu/index.html": "Best AI for Kikuyu",
    "language/hausa/index.html": "Best AI for Hausa",
    "language/kinyarwanda/ai-agent/index.html": "Build a Kinyarwanda AI agent",
    "language/swahili/ai-agent/index.html": "Build a Swahili AI agent",
    "language/kikuyu/ai-agent/index.html": "Build a Kikuyu AI agent",
    "language/hausa/ai-agent/index.html": "Build a Hausa AI agent",
    "models/gemini-3-1-pro/hausa/index.html": "Gemini 3.1 Pro in Hausa",
    "models/kimi-k3/hausa/index.html": "Kimi K3 in Hausa",
    "models/gpt-5-6-sol/hausa/index.html": "GPT-5.6 Sol in Hausa",
    "models/gemini-3-7-flash/hausa/index.html": "Gemini 3.7 Flash in Hausa",
    "models/claude-sonnet-5/hausa/index.html": "Claude Sonnet 5 in Hausa",
    "models/deepseek-v4/hausa/index.html": "DeepSeek V4 in Hausa",
    "models/gemini-3-1-pro/kikuyu/index.html": "Gemini 3.1 Pro in Kikuyu",
    "models/gpt-5-6-sol/kikuyu/index.html": "GPT-5.6 Sol in Kikuyu",
    "models/gemini-3-7-flash/kikuyu/index.html": "Gemini 3.7 Flash in Kikuyu",
    "models/claude-sonnet-5/kikuyu/index.html": "Claude Sonnet 5 in Kikuyu",
    "models/deepseek-v4/kikuyu/index.html": "DeepSeek V4 in Kikuyu",
    "models/kimi-k3/kikuyu/index.html": "Kimi K3 in Kikuyu",
    "models/deepseek-v4/kinyarwanda/index.html": "DeepSeek V4 in Kinyarwanda",
    "models/gemini-3-1-pro/kinyarwanda/index.html": "Gemini 3.1 Pro in Kinyarwanda",
    "models/claude-sonnet-5/kinyarwanda/index.html": "Claude Sonnet 5 in Kinyarwanda",
    "models/gpt-5-6-sol/kinyarwanda/index.html": "GPT-5.6 Sol in Kinyarwanda",
    "models/kimi-k3/kinyarwanda/index.html": "Kimi K3 in Kinyarwanda",
    "models/gemini-3-1-pro/swahili/index.html": "Gemini 3.1 Pro in Swahili",
    "models/deepseek-v4/swahili/index.html": "DeepSeek V4 in Swahili",
    "models/claude-sonnet-5/swahili/index.html": "Claude Sonnet 5 in Swahili",
    "models/gpt-5-6-sol/swahili/index.html": "GPT-5.6 Sol in Swahili",
    "models/gemini-3-7-flash/swahili/index.html": "Gemini 3.7 Flash in Swahili",
    "models/kimi-k3/swahili/index.html": "Kimi K3 in Swahili",
}

HEADER_CSS = """      .site-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 55;
        height: var(--site-header-h);
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 0 26px;
        background: rgba(255, 254, 253, 0.82);
        backdrop-filter: saturate(140%) blur(8px);
        border-bottom: 1px solid var(--gy-line-soft);
      }
      .site-header .logo-link {
        display: flex;
        align-items: center;
      }
      .site-header .logo {
        height: 24px;
        width: auto;
        display: block;
      }
      .site-header .h-title {
        font-family: var(--gy-font-serif);
        font-size: 14px;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        opacity: 0;
        transition: opacity 0.2s ease;
      }
      .site-header.scrolled .h-title {
        opacity: 1;
      }
      .site-header .login-btn {
        margin-left: auto;
        flex: none;
        display: inline-flex;
        align-items: center;
        padding: 9px 22px;
        border-radius: 12px;
        background: transparent;
        color: var(--gy-ink);
        border: 1.5px solid var(--gy-line);
        font-family: var(--gy-font-sans);
        font-size: 15px;
        font-weight: 600;
        line-height: 1;
        text-decoration: none;
        white-space: nowrap;
        transition:
          border-color 0.15s ease,
          background 0.15s ease;
      }
      .site-header .login-btn:hover {
        border-color: var(--gy-line-strong);
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

# A page also needs a `--site-header-h: 60px` custom property in its :root, and
# a scroll listener toggling `.scrolled` on #siteHeader so the title fades in
# — see the bottom of research/index.html for the simplest version:
#
#   const header = document.getElementById("siteHeader");
#   const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
#   window.addEventListener("scroll", onScroll, { passive: true });
#   onScroll();
#
# The header is `position: fixed`, so it is out of flow and covers the top
# `--site-header-h` of the page. Whatever comes first (the hero, normally) has
# to carry that height itself in its own top padding, on top of whatever
# spacing it wanted anyway — `80px` in research, `calc(var(--site-header-h) +
# clamp(48px, 7vw, 80px))` in ecocost. Forget it and the first heading sits
# under the header.
#
# `--pad-x: clamp(20px, 4vw, 60px)` is still worth defining: the header uses a
# flat 26px gutter, but every page's content column uses --pad-x.

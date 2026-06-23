# gooey-static-pages

Static pages hosted on **Cloudflare Pages** (project: `gooey-static-pages`) and served through gooey.ai via a proxy (`serve_static_file`).

Each top-level folder maps to a URL path. Today there is one page:

```
gooey-static-pages/        ← repo root = the site root that gets deployed
└── sovereignty/           ← this folder name = the URL /sovereignty
    ├── index.html         ← the html page for /sovereignty
    ├── globe.js
    ├── globe-grid.bin
    ├── art.js
    ├── assets/ ...
    └── images/ ...
```

## 📤 How to update the `/sovereignty` page

This repo is connected to **Cloudflare Pages**, so **pushing to GitHub deploys the site automatically**. No manual upload and no gooey.ai server deploy needed.

### 1. Edit the files

Edit the files under `sovereignty/`. Keep these in mind so the page keeps working when served through gooey.ai (the current page already does this — don't break it):

- **Required:** keep the `<!-- GOOEY-BASE-HREF -->` comment in `<head>`. The proxy swaps it for the right CDN `<base>` tag — remove it and images/fonts/the globe break on gooey.ai.
- **Required:** use **relative** asset paths (`assets/x.png`, `images/y.png`) — never `/static/...` or `/sovereignty/...`. The proxy rewrites relative paths to the right CDN base.
- **Optional:** add a `<...>Login</...>` button — it gets replaced with the user's name when they're logged in.

### 2. Commit and push

```bash
git add -A
git commit -m "Update sovereignty page"
git push
```

That's it — Cloudflare Pages picks up the push and builds a new deployment. Watch it under **Workers & Pages → `gooey-static-pages` → Deployments** in the [Cloudflare dashboard](https://dash.cloudflare.com/). The repo root is published as the site root, so the `sovereignty/` folder is served at `/sovereignty`.

<details>
<summary>Manual deploy (only if you can't push, or to test a one-off)</summary>

```bash
wrangler login                                      # one time
wrangler pages deploy . --project-name gooey-static-pages
```

Or drag the **repo root** folder into **Create deployment** on the project's dashboard page.

</details>

### 3. Verify

- CDN (raw): https://gooey-static-pages.pages.dev/sovereignty/
- Live (through gooey.ai): https://gooey.ai/sovereignty

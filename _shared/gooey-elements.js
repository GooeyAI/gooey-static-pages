// Shared custom elements for gooey-static-pages.
//
// Pages load this one module by absolute URL (see page-skeleton.html) and
// write content only; layout and styling live here and in styles.css.
// Every element and slot is shown in components.html.
//
// Developer-owned. Content editors never edit this file.

const SHARED = new URL(".", import.meta.url);
const LOGO = new URL("gooey-logo.png", SHARED).href;
const YEAR = new Date().getFullYear();

// One fetch, used twice: as a <style> in every shadow root (no flash of
// unstyled shadow content, unlike a <link>) and once in the page <head> for
// slotted content. Needs CORS when served cross-origin; see /_headers.
const CSS = await fetch(new URL("styles.css", SHARED)).then((res) => {
  if (!res.ok) throw new Error(`gooey-elements: styles.css ${res.status}`);
  return res.text();
});
const SHADOW_CSS = CSS.replace(/@import[^;]+;/g, "");

const pageStyle = document.createElement("style");
pageStyle.dataset.gooey = "";
pageStyle.textContent = CSS;
document.head.prepend(pageStyle);

function template(html) {
  const t = document.createElement("template");
  t.innerHTML = `<style>${SHADOW_CSS}</style>${html}`;
  return t;
}

class GooeyElement extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" }).append(
      this.constructor.template.content.cloneNode(true),
    );
  }

  // Toggle `className` on `target` whenever the named slot gains or loses
  // content, for chrome (separators, borders) that only makes sense when
  // the editor filled that slot.
  watchSlot(name, target, className) {
    const slot = this.shadowRoot.querySelector(
      name ? `slot[name="${name}"]` : "slot:not([name])",
    );
    const update = () =>
      target.classList.toggle(
        className,
        slot.assignedNodes().some(
          (n) => n.nodeType === Node.ELEMENT_NODE || n.textContent.trim(),
        ),
      );
    slot.addEventListener("slotchange", update);
    update();
  }
}

/* ---------- gooey-header ---------- */
class GooeyHeader extends GooeyElement {
  static template = template(`
    <header class="g-header" part="header">
      <a class="g-logo-link" href="https://gooey.ai/" aria-label="Gooey.AI home">
        <img class="g-logo" src="${LOGO}" alt="Gooey.AI">
      </a>
      <span class="g-header-title" part="title"><slot name="title"></slot></span>
      <nav class="g-nav" part="nav" aria-label="Page"><slot></slot></nav>
      <slot name="login"></slot>
    </header>`);

  connectedCallback() {
    const bar = this.shadowRoot.querySelector(".g-header");
    this.onScroll = () => bar.classList.toggle("scrolled", scrollY > 220);
    addEventListener("scroll", this.onScroll, { passive: true });
    this.onScroll();
  }

  disconnectedCallback() {
    removeEventListener("scroll", this.onScroll);
  }
}

/* ---------- gooey-footer ---------- */
class GooeyFooter extends GooeyElement {
  static template = template(`
    <footer class="g-footer" part="footer">
      <div class="g-wrap">
        <slot></slot>
        <div class="g-footer-brand" part="brand">
          <img class="g-logo" src="${LOGO}" alt="Gooey.AI">
          <span>© ${YEAR} Gooey.AI<span class="g-sep"> — </span><slot name="title"></slot></span>
        </div>
      </div>
    </footer>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot(null, root.querySelector(".g-footer"), "has-content");
    this.watchSlot("title", root.querySelector(".g-sep"), "g-shown");
  }
}

/* ---------- gooey-page ---------- */
class GooeyPage extends GooeyElement {
  static template = template(`<slot></slot>`);
}

customElements.define("gooey-header", GooeyHeader);
customElements.define("gooey-footer", GooeyFooter);
// Defined last: the loading spinner in each page waits for gooey-page, so by
// the time it disappears every other element is already upgraded.
customElements.define("gooey-page", GooeyPage);

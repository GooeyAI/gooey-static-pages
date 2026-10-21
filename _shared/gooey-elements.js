// Shared custom elements for gooey-static-pages.
//
// Pages load this one module by absolute URL (see page-skeleton.html) and
// write content only; layout and styling live here and in styles.css.
// Every element and slot is shown in components.html.
//
// Developer-owned. Content editors never edit this file.

const SHARED = new URL(".", import.meta.url);
const LOGO = new URL("gooey-logo.png", SHARED).href;
const WORDMARK = new URL("gooey-wordmark.png", SHARED).href;

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

  // Toggle `className` on `target` whenever the named slot (null for the
  // default slot) gains or loses content, for chrome that only makes sense
  // when the editor filled that slot. `.g-optional` wrappers are hidden
  // until they get `g-filled`.
  watchSlot(name, target, className = "g-filled") {
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
    </header>
    <div class="g-progress g-hidden" part="progress" aria-hidden="true"><i></i></div>`);

  connectedCallback() {
    const root = this.shadowRoot;
    const bar = root.querySelector(".g-header");
    // Attribute `progress`: show a reading-progress bar along the top.
    const progress = root.querySelector(".g-progress");
    progress.classList.toggle("g-hidden", !this.hasAttribute("progress"));
    this.onScroll = () => {
      bar.classList.toggle("scrolled", scrollY > 220);
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      progress.firstChild.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    };
    addEventListener("scroll", this.onScroll, { passive: true });
    this.onScroll();

    // gooey.ai may expose the signed-in user to the page as well as
    // rewriting the Login text in the HTML; honour either.
    const login = this.querySelector('[slot="login"]');
    const name = window.gooeyUser?.name;
    if (login && name) login.textContent = name;
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
          <a class="g-logo-link" href="https://gooey.ai/" aria-label="Gooey.AI home">
            <img class="g-footer-logo" src="${WORDMARK}" alt="Gooey.AI">
          </a>
          <span class="g-footer-note" part="note"><slot name="note"></slot></span>
        </div>
      </div>
    </footer>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot(null, root.querySelector(".g-footer"), "has-content");
  }
}

/* ---------- gooey-hero ---------- */
class GooeyHero extends GooeyElement {
  static template = template(`
    <header class="g-hero" part="hero">
      <div class="g-hero-inner">
        <div class="g-hero-text">
          <slot name="eyebrow"></slot>
          <h1 class="g-hero-title" part="title"><slot name="title"></slot></h1>
          <p class="g-hero-sub g-optional" part="subtitle"><slot name="subtitle"></slot></p>
          <div class="g-hero-body" part="body"><slot></slot></div>
          <div class="g-hero-cta g-optional"><slot name="cta"></slot></div>
          <slot name="byline"></slot>
        </div>
        <slot name="image"></slot>
      </div>
    </header>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot("subtitle", root.querySelector(".g-hero-sub"));
    this.watchSlot("cta", root.querySelector(".g-hero-cta"));
    this.watchSlot("image", root.querySelector(".g-hero"), "has-image");
  }
}

/* ---------- gooey-section ---------- */
// One observer for every section's scroll-in fade.
const revealer =
  "IntersectionObserver" in window &&
  new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.shadowRoot.querySelector(".g-section").classList.add("is-visible");
        revealer.unobserve(entry.target);
      }
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" },
  );

class GooeySection extends GooeyElement {
  static template = template(`
    <section class="g-section" part="section">
      <div class="g-wrap">
        <h2 class="g-section-heading g-optional" part="heading"><slot name="heading"></slot></h2>
        <p class="g-section-intro g-optional" part="intro"><slot name="intro"></slot></p>
        <slot></slot>
      </div>
    </section>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot("heading", root.querySelector(".g-section-heading"));
    this.watchSlot("intro", root.querySelector(".g-section-intro"));
    if (revealer) root.querySelector(".g-section").classList.add("g-reveal");
  }

  connectedCallback() {
    if (revealer) revealer.observe(this);
  }

  disconnectedCallback() {
    if (revealer) revealer.unobserve(this);
  }
}

/* ---------- gooey-columns ---------- */
class GooeyColumns extends GooeyElement {
  static template = template(`<slot></slot>`);
}

/* ---------- gooey-card ---------- */
class GooeyCard extends GooeyElement {
  static template = template(`
    <article class="g-card" part="card">
      <slot name="image"></slot>
      <h3 class="g-card-title g-optional" part="title"><slot name="title"></slot></h3>
      <div class="g-card-body" part="body"><slot></slot></div>
    </article>`);

  constructor() {
    super();
    this.watchSlot("title", this.shadowRoot.querySelector(".g-card-title"));
  }
}

/* ---------- gooey-feature ---------- */
class GooeyFeature extends GooeyElement {
  static template = template(`
    <div class="g-feature" part="feature">
      <slot name="icon"></slot>
      <slot name="logo"></slot>
      <slot name="value"></slot>
      <h3 class="g-feature-title g-optional" part="title"><slot name="title"></slot></h3>
      <div class="g-feature-body g-optional" part="body"><slot></slot></div>
      <slot name="cta"></slot>
    </div>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot("title", root.querySelector(".g-feature-title"));
    this.watchSlot(null, root.querySelector(".g-feature-body"));
  }
}

/* ---------- gooey-stat ---------- */
class GooeyStat extends GooeyElement {
  static template = template(`
    <div class="g-stat" part="stat">
      <span class="g-stat-label g-optional" part="label"><slot name="label"></slot></span>
      <span class="g-stat-value" part="value"><slot name="value"></slot></span>
      <span class="g-stat-note g-optional" part="note"><slot name="note"></slot></span>
    </div>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot("label", root.querySelector(".g-stat-label"));
    this.watchSlot("note", root.querySelector(".g-stat-note"));
  }
}

/* ---------- gooey-button ---------- */
class GooeyButton extends GooeyElement {
  static template = template(
    `<span class="g-button" part="button"><slot></slot></span>`,
  );
}

/* ---------- gooey-image ---------- */
class GooeyImage extends GooeyElement {
  static template = template(`
    <figure class="g-figure" part="figure">
      <slot></slot>
      <figcaption class="g-optional" part="caption"><slot name="caption"></slot></figcaption>
    </figure>`);

  constructor() {
    super();
    this.watchSlot("caption", this.shadowRoot.querySelector("figcaption"));
  }
}

/* ---------- gooey-quote ---------- */
class GooeyQuote extends GooeyElement {
  static template = template(`
    <blockquote class="g-quote" part="quote">
      <div class="g-quote-text" part="text"><slot></slot></div>
      <div class="g-quote-by g-optional" part="attribution"><slot name="attribution"></slot></div>
    </blockquote>`);

  constructor() {
    super();
    this.watchSlot("attribution", this.shadowRoot.querySelector(".g-quote-by"));
  }
}

/* ---------- gooey-person ---------- */
class GooeyPerson extends GooeyElement {
  static template = template(`
    <div class="g-person" part="person">
      <slot name="photo"></slot>
      <div class="g-person-text">
        <span class="g-person-name" part="name"><slot name="name"></slot></span>
        <span class="g-person-role g-optional" part="role"><slot name="role"></slot></span>
        <span class="g-optional" part="link"><slot name="link"></slot></span>
      </div>
    </div>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot("role", root.querySelector(".g-person-role"));
    this.watchSlot("link", root.querySelector('[part="link"]'));
  }
}

/* ---------- gooey-faq / gooey-faq-item ---------- */
class GooeyFaq extends GooeyElement {
  static template = template(`<div class="g-faq" part="faq"><slot></slot></div>`);
}

// Native <details>/<summary>: keyboard-operable and announced as a
// disclosure without any script.
class GooeyFaqItem extends GooeyElement {
  static template = template(`
    <details class="g-faq-item" part="item">
      <summary part="question">
        <span><slot name="question"></slot></span>
        <span class="g-faq-icon" aria-hidden="true"></span>
      </summary>
      <div class="g-faq-answer" part="answer"><slot></slot></div>
    </details>`);
}

/* ---------- gooey-callout ---------- */
class GooeyCallout extends GooeyElement {
  static template = template(
    `<div class="g-callout" part="callout" role="note"><slot></slot></div>`,
  );
}

/* ---------- gooey-tags ---------- */
class GooeyTags extends GooeyElement {
  static template = template(`<div class="g-tags" part="tags"><slot></slot></div>`);
}

/* ---------- gooey-steps / gooey-step ---------- */
// A numbered list of steps. Numbers come from each step's position, so
// adding, removing or reordering steps never needs renumbering by hand.
class GooeySteps extends GooeyElement {
  static template = template(`<div class="g-steps" part="steps" role="list"><slot></slot></div>`);
}

class GooeyStep extends GooeyElement {
  static template = template(`
    <div class="g-step" part="step">
      <span class="g-step-n" part="number" aria-hidden="true"></span>
      <div>
        <h3 class="g-step-title g-optional" part="title"><slot name="title"></slot></h3>
        <div class="g-step-body" part="body"><slot></slot></div>
      </div>
    </div>`);

  constructor() {
    super();
    this.watchSlot("title", this.shadowRoot.querySelector(".g-step-title"));
  }

  connectedCallback() {
    if (!this.hasAttribute("role")) this.setAttribute("role", "listitem");
    const steps = [...(this.parentElement?.children ?? [])].filter(
      (el) => el.localName === "gooey-step",
    );
    const n = steps.indexOf(this) + 1;
    this.shadowRoot.querySelector(".g-step-n").textContent = String(n).padStart(2, "0");
  }
}

/* ---------- gooey-gallery ---------- */
// A row of images that scrolls sideways (also with the arrow keys once
// focused).
class GooeyGallery extends GooeyElement {
  static template = template(
    `<div class="g-gallery" part="gallery" tabindex="0"><slot></slot></div>`,
  );
}

/* ---------- gooey-page ---------- */
class GooeyPage extends GooeyElement {
  static template = template(
    `<a class="g-skip" href="#main" part="skip">Skip to main content</a><slot></slot>`,
  );

  constructor() {
    super();
    // Focus the page's <main> directly: following "#main" would resolve
    // against the proxy's <base> and leave the page.
    this.shadowRoot.querySelector(".g-skip").addEventListener("click", (e) => {
      const main = this.querySelector("main");
      if (!main) return;
      e.preventDefault();
      if (!main.hasAttribute("tabindex")) main.setAttribute("tabindex", "-1");
      main.focus();
    });
  }
}

customElements.define("gooey-header", GooeyHeader);
customElements.define("gooey-footer", GooeyFooter);
customElements.define("gooey-hero", GooeyHero);
customElements.define("gooey-section", GooeySection);
customElements.define("gooey-columns", GooeyColumns);
customElements.define("gooey-card", GooeyCard);
customElements.define("gooey-feature", GooeyFeature);
customElements.define("gooey-stat", GooeyStat);
customElements.define("gooey-button", GooeyButton);
customElements.define("gooey-image", GooeyImage);
customElements.define("gooey-quote", GooeyQuote);
customElements.define("gooey-person", GooeyPerson);
customElements.define("gooey-faq", GooeyFaq);
customElements.define("gooey-faq-item", GooeyFaqItem);
customElements.define("gooey-callout", GooeyCallout);
customElements.define("gooey-tags", GooeyTags);
customElements.define("gooey-steps", GooeySteps);
customElements.define("gooey-step", GooeyStep);
customElements.define("gooey-gallery", GooeyGallery);
// Defined last: the loading spinner in each page waits for gooey-page, so by
// the time it disappears every other element is already upgraded.
customElements.define("gooey-page", GooeyPage);

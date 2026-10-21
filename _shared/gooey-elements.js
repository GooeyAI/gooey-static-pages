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
          <span>© ${YEAR} Gooey.AI<span class="g-sep g-optional"> — </span><slot name="title"></slot></span>
        </div>
      </div>
    </footer>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot(null, root.querySelector(".g-footer"), "has-content");
    this.watchSlot("title", root.querySelector(".g-sep"));
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
          <p class="g-hero-sub g-optional" part="subtitle"><slot></slot></p>
          <div class="g-hero-cta g-optional"><slot name="cta"></slot></div>
          <slot name="byline"></slot>
        </div>
        <slot name="image"></slot>
      </div>
    </header>`);

  constructor() {
    super();
    const root = this.shadowRoot;
    this.watchSlot(null, root.querySelector(".g-hero-sub"));
    this.watchSlot("cta", root.querySelector(".g-hero-cta"));
    this.watchSlot("image", root.querySelector(".g-hero"), "has-image");
  }
}

/* ---------- gooey-section ---------- */
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
      <h3 class="g-feature-title g-optional" part="title"><slot name="title"></slot></h3>
      <div class="g-feature-body" part="body"><slot></slot></div>
    </div>`);

  constructor() {
    super();
    this.watchSlot("title", this.shadowRoot.querySelector(".g-feature-title"));
  }
}

/* ---------- gooey-stat ---------- */
class GooeyStat extends GooeyElement {
  static template = template(`
    <div class="g-stat" part="stat">
      <span class="g-stat-value" part="value"><slot name="value"></slot></span>
      <span class="g-stat-label" part="label"><slot name="label"></slot></span>
    </div>`);
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

/* ---------- gooey-page ---------- */
class GooeyPage extends GooeyElement {
  static template = template(`<slot></slot>`);
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
// Defined last: the loading spinner in each page waits for gooey-page, so by
// the time it disappears every other element is already upgraded.
customElements.define("gooey-page", GooeyPage);

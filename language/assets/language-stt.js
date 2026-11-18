// Interactions for the /language/<name>/speech-to-text pages. The HTML is written by
// scripts/build_language_pages.py; each model tab carries the Gooey.AI workflow it opens (data-url).

// Try box: the selected tab decides where the mic, Upload audio and Try a sample open.
const tabs = [...document.querySelectorAll(".st-tab")];
const targets = [document.getElementById("stMic"), ...document.querySelectorAll(".st-go")];
const caption = document.getElementById("stCaption");
function pick(tab, focus) {
  tabs.forEach(t => {
    const on = t === tab;
    t.setAttribute("aria-selected", String(on));
    t.tabIndex = on ? 0 : -1;
  });
  targets.forEach(a => { a.href = tab.dataset.url; });
  caption.textContent = tab.dataset.caption;
  if (focus) tab.focus();
}
tabs.forEach((tab, i) => {
  tab.tabIndex = tab.getAttribute("aria-selected") === "true" ? 0 : -1;
  tab.addEventListener("click", () => pick(tab));
  tab.addEventListener("keydown", event => {
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    pick(tabs[(i + step + tabs.length) % tabs.length], true);
  });
});

// Spoken language: go to that language's speech-to-text page (on gooey.ai when served through the proxy,
// the same way language-links.js treats relative links).
const language = document.getElementById("stLang");
if (language) {
  language.addEventListener("change", () => {
    const url = new URL(language.value, document.baseURI);
    location.href = url.host === location.host ? url.href : location.origin + url.pathname;
  });
}

// API: copy a ready-to-paste brief for a coding agent.
const copy = document.getElementById("stCopy");
if (copy) {
  const label = copy.querySelector("span");
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(copy.dataset.copy);
      label.textContent = "Copied";
    } catch {
      label.textContent = "Copy failed";
    }
    setTimeout(() => { label.textContent = "Copy for coding agent"; }, 2000);
  });
}

// Interactions for the /models/<model>/ overview pages. The HTML is written by scripts/build_model_overview.py with
// every language's numbers in it; this only shows the chosen language (the "Show results for" menu, or #<slug>),
// points the "Build an agent" buttons at it, highlights it in the hero Index chart, and switches the Cost / CO2e card.
const O = window.MODEL_OVERVIEW;
const select = document.getElementById("moLang");

function show(slug, push) {
  if (!O.languages[slug]) slug = O.default;
  select.value = slug;
  document.querySelectorAll(".mo-panel[data-lang]").forEach(el => { el.hidden = el.dataset.lang !== slug; });
  const L = O.languages[slug];
  ["moAgent", "moAgent2"].forEach(id => { const a = document.getElementById(id); if (a) a.setAttribute("href", L.agent); });
  document.querySelectorAll(".mo-hero-chart [data-lang]").forEach(el => el.classList.toggle("on", el.dataset.lang === slug));
  const sel = document.getElementById("moSelLang");
  if (sel) sel.textContent = L.lang;
  // An absolute URL: the page's <base href="/models/"> would turn a relative "#slug" into /models/#slug.
  if (push) history.replaceState(null, "", location.origin + location.pathname + location.search + (slug === O.default ? "" : "#" + slug));
}

select.addEventListener("change", () => show(select.value, true));
window.addEventListener("hashchange", () => show(location.hash.slice(1), false));
show(location.hash.slice(1) || O.default, false);

document.querySelectorAll("[data-toggle]").forEach(card => {
  card.querySelectorAll(".mo-seg button").forEach(btn => btn.addEventListener("click", () => {
    card.querySelectorAll(".mo-seg button").forEach(b => b.setAttribute("aria-selected", String(b === btn)));
    card.querySelectorAll(".mo-small").forEach(p => { p.hidden = p.dataset.k !== btn.dataset.k; });
  }));
});

const header = document.getElementById("siteHeader");
const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

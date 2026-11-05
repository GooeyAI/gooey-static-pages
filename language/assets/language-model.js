// Interactions for the /models/<model>/<language> pages. The HTML is written by scripts/build_language_pages.py;
// this renders the sample cards (language-samples.js) and drives the "At your volume" slider.
const M = window.MODEL_PAGE;

renderSampleCards(document.getElementById("sampleCards"), M.samples, M.who,
  { assetBase: "../language/assets/", dataBase: "../language/" });

// "At your volume": a log slider from 1,000 to 200,000 questions a month.
const MIN = 1000, MAX = 200000;
const range = document.getElementById("mdRange");
const two = n => Number(n.toPrecision(2));
const money = v => (v >= 1000 ? "$" + Math.round(v).toLocaleString("en-US") : "$" + v.toFixed(2));
const mass = g => (g >= 1000 ? Number((g / 1000).toPrecision(2)) + " kg" : Math.round(g) + " g");
function amount(v, unit) {
  const digits = v >= 100 ? 0 : v >= 10 ? 1 : 2;
  return Number(v.toFixed(digits)).toLocaleString("en-US") + " " + unit;
}
const FORMAT = { cost: money, co2e: mass, waterL: v => amount(v, "L"), energyKwh: v => amount(v, "kWh") };
function update() {
  const questions = two(MIN * Math.pow(MAX / MIN, Number(range.value) / 100));
  const k = questions / 1000, { subject, ref } = M.volume;
  range.style.setProperty("--fill", range.value + "%");
  document.getElementById("mdVol").textContent = Math.round(questions).toLocaleString("en-US");
  document.querySelectorAll(".md-vol-tile").forEach(tile => {
    const key = tile.dataset.k;
    tile.querySelector("b").textContent = FORMAT[key](subject[key] * k);
    const has = ref && ref[key] != null;
    tile.classList.toggle("has-ref", Boolean(has));
    if (!has) { tile.querySelector("small").textContent = ""; return; }
    const share = Math.min(1, ref[key] / subject[key]);
    tile.querySelector(".md-track i").style.width = (share * 100).toFixed(0) + "%";
    const less = Math.round((1 - share) * 100);
    tile.querySelector("small").textContent = FORMAT[key](ref[key] * k) + (less > 0 ? ` · ${less}% less` : " · same");
  });
}
if (range) {
  range.value = String(Math.round(Math.log(M.volume.perMonth / MIN) / Math.log(MAX / MIN) * 1000) / 10);
  range.addEventListener("input", update);
  update();
}

const header = document.getElementById("siteHeader");
const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

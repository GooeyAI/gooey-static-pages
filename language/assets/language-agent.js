// Interactions for the /language/<name>/ai-agent pages. The HTML is written by
// scripts/build_language_pages.py; this only wires up the mock-ups.
// window.AGENT_PAGE = { perThousand: { cost, co2e, waterL, energyKwh }, channels: { whatsapp, phone, web } }
const A = window.AGENT_PAGE;

// Step 1: choose a chain on the left, or a model in the picker; they stay in sync.
const chainButtons = [...document.querySelectorAll(".ag-chain")];
const modelButtons = [...document.querySelectorAll(".ag-model")];
function select(list, target) {
  list.forEach(b => {
    const on = b === target;
    b.classList.toggle("selected", on);
    b.setAttribute("aria-pressed", String(on));
  });
}
chainButtons.forEach(button => button.addEventListener("click", () => {
  select(chainButtons, button);
  const match = modelButtons.find(m => m.dataset.model === button.dataset.model);
  if (match) select(modelButtons, match);
}));
modelButtons.forEach(button => button.addEventListener("click", () => {
  select(modelButtons, button);
  const match = chainButtons.find(c => c.dataset.model === button.dataset.model);
  select(chainButtons, match || null);
}));
const search = document.getElementById("agSearch");
if (search) {
  search.addEventListener("input", () => {
    const q = search.value.trim().toLowerCase();
    modelButtons.forEach(b => { b.hidden = q !== "" && !b.dataset.model.toLowerCase().includes(q); });
  });
}

// Step 3: channel switch
const channelText = document.getElementById("agChannelText");
document.querySelectorAll(".ag-channels button").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".ag-channels button").forEach(b => b.setAttribute("aria-pressed", String(b === button)));
  channelText.textContent = A.channels[button.dataset.channel];
}));

// Cost calculator: a log slider from 200 to 100,000 conversations, one run per conversation.
const MIN = 200, MAX = 100000, DEFAULT = 1000;
const range = document.getElementById("agRange");
const fmtInt = n => Math.round(n).toLocaleString("en-US");
const two = n => Number(n.toPrecision(2));
function money(v) {
  if (v >= 1000) return "$" + fmtInt(v);
  return "$" + v.toFixed(2);
}
function mass(g) {
  return g >= 1000 ? Number((g / 1000).toPrecision(2)) + " kg" : Math.round(g) + " g";
}
function amount(v, unit) {
  if (v === 0) return "0 " + unit;
  const digits = v >= 100 ? 0 : v >= 10 ? 1 : 2;
  return Number(v.toFixed(digits)).toLocaleString("en-US") + " " + unit;
}
function update() {
  const t = Number(range.value) / 100;
  const conv = two(MIN * Math.pow(MAX / MIN, t));
  const k = conv / 1000;
  const p = A.perThousand;
  range.style.setProperty("--fill", range.value + "%");
  document.getElementById("agConv").textContent = fmtInt(conv);
  document.getElementById("agCost").textContent = money(p.cost * k);
  document.getElementById("agCo2").textContent = p.co2e == null ? "Not covered" : mass(p.co2e * k);
  document.getElementById("agWater").textContent = p.waterL == null ? "Not covered" : amount(p.waterL * k, "L");
  document.getElementById("agEnergy").textContent = p.energyKwh == null ? "Not covered" : amount(p.energyKwh * k, "kWh");
}
if (range) {
  range.value = String(Math.round(Math.log(DEFAULT / MIN) / Math.log(MAX / MIN) * 1000) / 10);
  range.addEventListener("input", update);
  update();
}

// Header title appears once the page heading has scrolled away.
const header = document.getElementById("siteHeader");
const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

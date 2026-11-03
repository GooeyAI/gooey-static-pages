// Shared engine for the /language/<name> evaluation pages.
// Each page sets window.LANG_PAGE (chains, chart geometry, axis ranges) before loading this file;
// scripts/build_language_pages.py writes that object. Nothing language-specific lives here.
const P = window.LANG_PAGE;
const CSV_DATA = P.csv, PRICING_DATA = P.pricing, ECOCOST_DATA = P.eco;
const G = P.geometry;
const WIDE = P.layout === "wide";
const Q = P.questions;
const chains = CSV_DATA.map(([model, speech, acc, time, sovereign], index) => {
  const eco = ECOCOST_DATA[index];
  return { model: model.replace("GPT 5.6 Sol", "GPT-5.6 Sol"), speech, acc, exact: acc * 100, score: Math.round(acc * 100 + 1e-9), time, cost: PRICING_DATA[index], carbon: eco.value ?? null, carbonMin: eco.min, carbonMax: eco.max, carbonConfidence: eco.value === undefined ? null : "Low", carbonReason: eco.reason, sovereign };
});
const ranked = [...chains].sort((a, b) => b.acc - a.acc || a.time - b.time);
ranked.forEach((c, i) => { c.rank = i + 1; });
const byTime = [...chains].sort((a, b) => a.time - b.time);
byTime.forEach((c, i) => { c.timeRank = i + 1; });
const N = chains.length;
const group = c => (c.sovereign ? "sov" : "priv");
const fullName = c => c.model + (c.speech === "Built-in audio" ? "" : " + " + c.speech);
const bestOf = (list, key, desc) => [...list].sort((a, b) => (desc ? b[key] - a[key] : a[key] - b[key]))[0];
const bestSovereign = bestOf(chains.filter(c => c.sovereign), "acc", true);
const LOGO_FILES = { "DeepSeek V4": "logo-deepseek", "Gemini 3.1 Pro": "logo-gemini", "Gemini 3.7 Flash": "logo-gemini", "GPT-5.6 Sol": "logo-openai", "Claude Sonnet 5": "logo-claude", "Kimi K3": "logo-kimi" };
const SPEECH_FILES = { Omnilingual: "logo-meta", Intron: "logo-intron", "GPT Transcribe": "logo-openai", "Kikuyu Whisper v2": "icon-mic-legend", "Built-in audio": "icon-mic" };
const MAKERS = { "DeepSeek V4": "DeepSeek", "Gemini 3.1 Pro": "Google", "Gemini 3.7 Flash": "Google", "GPT-5.6 Sol": "OpenAI", "Claude Sonnet 5": "Anthropic", "Kimi K3": "Moonshot AI" };
const SHORT = { "DeepSeek V4": "DeepSeek", "Gemini 3.1 Pro": "Gemini", "Gemini 3.7 Flash": "Gemini Flash", "GPT-5.6 Sol": "GPT", "Claude Sonnet 5": "Claude", "Kimi K3": "Kimi" };
// Rotated-label box [size, offset past the column centre] for a 12px label at -45 degrees.
const LABEL_BOX = { "DeepSeek V4": [65.054, 4.49], "Gemini 3.1 Pro": [67.175, 4.59], "Gemini 3.7 Flash": [75.2, 4.7], "Claude Sonnet 5": [77.075, 4.68], "GPT-5.6 Sol": [58.69, 4.95], "Kimi K3": [41.012, 5.31] };
const model = (name, size) => `<img src="assets/kinyarwanda/${LOGO_FILES[name]}.svg" alt="" width="${size}" height="${size}" />`;
const speechIcon = (name, size = 16) => `<img src="assets/kinyarwanda/${SPEECH_FILES[name] === "icon-mic" ? "icon-mic-legend" : SPEECH_FILES[name]}.svg" alt="" width="${size}" height="${size}" />`;

const ICONS = {
  score: '<img src="assets/kinyarwanda/icon-bullseye.svg" alt="" width="16" height="16" />',
  time: '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="#0a1021" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="9" r="5.25"/><path d="M8 6.2V9l1.8 1.2M6.5 1.5h3M8 1.5v2.3"/></svg>',
  cost: '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="#0a1021" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="1.75" y="1.75" width="12.5" height="12.5" rx="2.5"/><path d="M8 4v8M10.2 5.9C9.8 5.3 9 5 8 5c-1.2 0-2.2.5-2.2 1.5S6.7 8 8 8s2.2.5 2.2 1.5S9.2 11 8 11c-1 0-1.8-.3-2.2-.9"/></svg>',
  carbon: '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="#0a1021" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 13.5C2.5 7 6 3 13.5 2.5c0 7-4 11-11 11zM2.5 13.5c1.8-3.2 4-5.3 6.5-6.8"/></svg>'
};
const CHARTS = [
  { icon: "score", title: "Answer score", sub: `Out of 100, averaged over ${Q} questions. Higher is better.`, order: (a, b) => b.acc - a.acc || a.time - b.time, height: c => c.exact * G.score, value: c => String(c.score), lines: G.lines.score,
    best: [bestOf(chains.filter(c => c.sovereign), "acc", true), bestOf(chains.filter(c => !c.sovereign), "acc", true)], show: c => String(c.score) },
  { icon: "time", title: "Response time", sub: "Median seconds, voice note to answer. Lower is better. Calls need under 10 s.", order: (a, b) => a.time - b.time, height: c => c.time * G.time, value: c => c.time.toFixed(1) + " s", lines: G.lines.time, limit: true,
    best: [bestOf(chains.filter(c => c.sovereign), "time", false), bestOf(chains.filter(c => !c.sovereign), "time", false)], show: c => c.time.toFixed(1) + " s" },
  { icon: "cost", title: "Cost per 1,000 questions", sub: `Observed whole-workflow Gooey.AI charge in US dollars; ${Q} runs per chain.`, order: (a, b) => a.cost - b.cost || b.acc - a.acc, height: c => G.costBase + (c.cost - 40) * G.costPerDollar, value: c => "$" + c.cost.toFixed(G.costDecimals ?? 2), lines: G.lines.cost,
    best: [bestOf(chains.filter(c => c.sovereign), "cost", false), bestOf(chains.filter(c => !c.sovereign), "cost", false)], show: c => "$" + c.cost.toFixed(2) },
  { icon: "carbon", title: "Text-model CO₂e per 1,000 questions", sub: "EcoCost estimate in grams; excludes speech and direct audio. Lower is better.", order: (a, b) => (a.carbon ?? Infinity) - (b.carbon ?? Infinity), height: c => Number.isFinite(c.carbon) ? c.carbon * G.carbon : 0, value: c => Number.isFinite(c.carbon) ? c.carbon.toFixed(G.carbonDecimals ?? 1) + " g" : "N/A", lines: G.lines.carbon,
    best: [bestOf(chains.filter(c => c.sovereign && Number.isFinite(c.carbon)), "carbon", false), bestOf(chains.filter(c => !c.sovereign && Number.isFinite(c.carbon)), "carbon", false)], show: c => c.carbon.toFixed(1) + " g" }
];
// Chart coordinates are drawn in a 470 px plot (fluid, as percentages) or, for wide layouts, in pixels.
const COL_PITCH = G.pitch;
const LIMIT_Y = Math.round(212 - 10 * G.time);
const at = WIDE ? (x => x + "px") : (x => (x / 470 * 100).toFixed(3) + "%");
// Figma leaves gaps in the dashed line under the value labels; wide layouts just skip colliding dashes.
const LIMIT_DASHES = WIDE ? [...Array(138).keys()].map(i => i * 7) : [...Array(41).keys()].map(i => i * 7).concat([364], [406, 413, 420, 427, 434, 441]);

function renderMetrics() {
  const grid = document.getElementById("metricGrid");
  CHARTS.forEach(chart => {
    const cols = [...chains].sort(chart.order);
    const plot = [];
    const labelBoxes = [];
    // Smaller value labels when neighbours would touch; the 10 s label goes to the top when bars already cross it.
    const tight = Math.max(...cols.map(c => chart.value(c).length)) * 6.6 > COL_PITCH + 2;
    const limitOnTop = chart.limit && 212 - chart.height(cols[0]) < LIMIT_Y + 24;
    cols.forEach((c, i) => {
      const h = Math.round(chart.height(c));
      const center = 60 + i * COL_PITCH;
      const text = chart.value(c);
      labelBoxes.push([center - text.length * 3.4, center + text.length * 3.4, 212 - h - 18, 212 - h - 4]);
    });
    if (chart.limit) {
      plot.push('<div class="zone"></div><span class="zone-label">Async only</span>');
      LIMIT_DASHES.forEach(x => {
        const l = 26 + x;
        if (labelBoxes.some(([x1, x2, y1, y2]) => l + 4 > x1 && l < x2 && y1 <= LIMIT_Y + 1 && y2 >= LIMIT_Y)) return;
        plot.push(`<i class="dash" style="left:${l}px"></i>`);
      });
      plot.push(`<span class="limit${limitOnTop ? " top" : ""}"><img src="assets/kinyarwanda/icon-phone.svg" alt="" width="12" height="12" />10 s limit for calls</span>`);
    }
    chart.lines.forEach(top => plot.push(`<i class="gl" style="top:${top}px"></i>`));
    plot.push('<i class="gl base" style="top:212px"></i>');
    const labels = [];
    cols.forEach((c, i) => {
      const h = Math.round(chart.height(c));
      const left = 48 + i * COL_PITCH;
      const center = left + 12;
      plot.push(`<i class="col${c.sovereign ? " sov" : ""}" data-g="${group(c)}" style="left:${at(left)};width:${at(24)};top:${212 - h}px;height:${h}px" title="${fullName(c)}"></i><span class="val" data-g="${group(c)}" style="left:calc(${at(center)} - 24px);top:${212 - h - 18}px">${chart.value(c)}</span>`);
      const [size, offset] = LABEL_BOX[c.model];
      labels.push(`<img src="assets/kinyarwanda/${LOGO_FILES[c.model]}.svg" alt="" width="20" height="20" style="left:calc(${at(left)} + 2px);top:2px" /><img src="assets/kinyarwanda/${SPEECH_FILES[c.speech]}.svg" alt="" width="16" height="16" style="left:calc(${at(left)} + 4px);top:28px" /><div class="name" style="left:calc(${at(center)} + ${(offset - size).toFixed(2)}px);width:${size}px;height:${size}px"><span>${c.model}</span></div>`);
    });
    const article = document.createElement("article");
    article.className = "chart-card";
    article.innerHTML = `<div class="chart-head"><h3 class="chart-title">${ICONS[chart.icon]}${chart.title}</h3><p class="chart-sub">${chart.sub}</p></div><div class="chart-body"><div class="plot${tight ? " tight" : ""}" style="--ly:${LIMIT_Y}px">${plot.join("")}</div><div class="labels">${labels.join("")}</div></div><div class="chart-foot"><hr /><div class="best"><div><i class="sov"></i><b>${chart.show(chart.best[0])}</b>best sovereign-deployable</div><div><i></i><b>${chart.show(chart.best[1])}</b>best private API</div></div></div>`;
    grid.appendChild(article);
  });
}

function renderTable(sort = "accuracy") {
  const rows = sort === "speed" ? byTime : ranked;
  document.getElementById("chainRows").innerHTML = rows.map((c, i) => `<div class="ct-row${i === 0 ? " selected" : ""}" data-g="${group(c)}" role="row"><span class="c-rank">${i + 1}</span><span class="c-model">${model(c.model, 24)}<span class="c-name"><a href="../models/${P.modelSlugs[c.model]}/${P.slug}/">${c.model}</a><small class="c-maker">${MAKERS[c.model]}</small></span></span><span class="c-plus">${c.speech === "Built-in audio" ? "" : "+"}</span><span class="c-speech">${speechIcon(c.speech)}${c.speech}</span><span></span><span class="c-score"><span class="bar"><i class="${c.sovereign ? "sovereign" : "private"}" style="width:${c.exact.toFixed(2)}%"></i></span><b class="c-num">${c.score}</b></span><span></span><span class="c-time">${c.time.toFixed(1)} s</span><span class="c-host"><i class="sw${c.sovereign ? " sov" : ""}"></i>${c.sovereign ? "Sovereign" : "Private"}</span><a class="c-cta" href="${P.slug}/ai-agent/">Build with this</a></div>`).join("");
}


function renderLabRank() {
  const list = document.getElementById("labRank");
  if (!list || !P.labSpeech) return;
  list.innerHTML = ranked.filter(c => c.speech === P.labSpeech).map(c => `<li><i class="sw${c.sovereign ? " sov" : ""}"></i>${model(c.model, 16)}<span>${c.model} + ${P.labSpeech}</span><b>${c.score}</b><small>#${c.rank}</small></li>`).join("");
}

const [SC_X0, SC_T0, SC_PER_S] = P.scatter.x;
const MD = P.scatter.metrics;
const SCATTER = {
  x: t => SC_X0 + (t - SC_T0) * SC_PER_S,
  xTicks: P.scatter.xTicks,
  extraLabelled: () => (P.scatter.labelBestSovereign ? [bestSovereign] : []),
  rows: [["score", "Answer score"], ["time", "Response"], ["cost", "Cost per 1,000 questions"], ["carbon", "Text-model CO₂e per 1,000 questions"]],
  metrics: {
    score: { label: "Answer score", title: "Answer score vs. response time", get: c => c.exact, high: true, ...MD.score, tick: v => String(v), beat: "more accurate", hint: "Higher and faster is better" },
    cost: { label: "Cost per 1,000 questions", title: "Cost vs. response time", get: c => c.cost, high: false, ...MD.cost, tick: v => "$" + v.toFixed(2), beat: "cheaper", hint: "Lower and faster is better" },
    carbon: { label: "Text-model CO₂e per 1,000 questions", title: "Text-model CO₂e vs. response time", get: c => c.carbon, high: false, ...MD.carbon, tick: v => v + " g", beat: "lower-carbon", hint: "Lower and faster is better" }
  }
};
const ecoPanel = c => Number.isFinite(c.carbon)
  ? `<div class="p-eco"><div class="p-lab"><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 13.5C2.5 7 6 3 13.5 2.5c0 7-4 11-11 11zM2.5 13.5c1.8-3.2 4-5.3 6.5-6.8"/></svg>Text-model EcoCost</div><span class="big">${c.carbon.toFixed(1)} g <small>CO₂e / 1,000</small></span><span class="likely">${c.carbonMin.toFixed(1)}–${c.carbonMax.toFixed(1)} g · ${c.carbonConfidence.toLowerCase()} confidence</span><span class="likely">Excludes speech recognition</span></div>`
  : `<div class="p-eco"><div class="p-lab"><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 13.5C2.5 7 6 3 13.5 2.5c0 7-4 11-11 11zM2.5 13.5c1.8-3.2 4-5.3 6.5-6.8"/></svg>Text-model EcoCost</div><span class="big"><small>Not covered</small></span><span class="likely">${c.carbonReason}</span></div>`;
const PANEL_DETAILS = c => `<dl class="p-facts"><div><dt>Hosting</dt><dd>${c.sovereign ? "Sovereign-deployable" : "Private API"}</dd></div><div><dt>Speech recognition</dt><dd>${c.speech}</dd></div><div><dt>Accuracy (mean)</dt><dd>${c.exact.toFixed(1)} out of 100</dd></div></dl><div class="p-cost"><span>Observed cost per 1,000 questions</span><b>$${c.cost.toFixed(2)}</b></div>${ecoPanel(c)}`;

// Scatter + hover tooltip + Y-axis menu. Per-page numbers live in SCATTER (see above).
const scoreOf = c => (c.exact !== undefined ? c.exact : c.score);
const scoreRanked = [...chains].sort((a, b) => scoreOf(b) - scoreOf(a) || a.time - b.time);
const timeRanked = [...chains].sort((a, b) => Number(a.time.toFixed(1)) - Number(b.time.toFixed(1)) || scoreOf(b) - scoreOf(a));
const scoreRankOf = c => scoreRanked.indexOf(c) + 1;
const timeRankOf = c => timeRanked.indexOf(c) + 1;
const RING = { "DeepSeek V4": "#4d6bfe", "Gemini 3.1 Pro": "#4285f4", "Gemini 3.7 Flash": "#4285f4", "GPT-5.6 Sol": "#10131c", "Claude Sonnet 5": "#d97757", "Kimi K3": "#1783ff" };
const FORMAT = { score: c => String(c.score), time: c => c.time.toFixed(1) + " s", cost: c => "$" + c.cost.toFixed(2), carbon: c => Number.isFinite(c.carbon) ? c.carbon.toFixed(1) + " g" : "Not covered" };
const SC_W = 690, SC_H = 509;
const pctX = x => (x / SC_W * 100).toFixed(3) + "%";
const pctY = y => (y / SC_H * 100).toFixed(3) + "%";
const scatterY = (m, v) => 79 + (m.max - v) / (m.max - m.min) * 325;
const beats = (m, a, b) => a.time <= b.time && (m.high ? m.get(a) >= m.get(b) : m.get(a) <= m.get(b)) && (a.time < b.time || m.get(a) !== m.get(b));
const metricChains = m => chains.filter(c => Number.isFinite(m.get(c)));
const frontierOf = m => metricChains(m).filter(c => !metricChains(m).some(o => beats(m, o, c)));
const beatenBy = (m, c) => metricChains(m).filter(o => beats(m, o, c)).sort((a, b) => (m.high ? m.get(b) - m.get(a) : m.get(a) - m.get(b)) || a.time - b.time)[0];
const CHECK = '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3.500 8.500 3 3 6-7"/></svg>';
const INFO = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.300" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8" r="6.200"/><path d="M8 7.200v3.600M8 5.200v.1"/></svg>';
let yMetric = Object.keys(SCATTER.metrics)[0];
let selectedChain = scoreRanked[0];
const scatterCard = document.querySelector(".scatter-card");
const tip = document.createElement("div");
tip.className = "sc-tip";
tip.setAttribute("role", "tooltip");
tip.hidden = true;
scatterCard.appendChild(tip);

function renderPanel() {
  const c = selectedChain;
  const dominated = chains.some(o => o !== c && scoreOf(o) >= scoreOf(c) && o.time <= c.time && (scoreOf(o) > scoreOf(c) || o.time < c.time));
  const fast = c.time < 10 ? "Fast enough for phone calls (under 10 s)." : "Too slow for phone calls (over 10 s), fine for WhatsApp messages.";
  document.getElementById("chainPanel").innerHTML = `<span class="eyebrow">${scoreRankOf(c) === 1 ? "Most accurate" : "Selected chain"}</span>
    <div class="p-name">${model(c.model, 20)}<span>${c.model}${c.speech === "Built-in audio" ? " (direct audio)" : " +"}</span>${c.speech === "Built-in audio" ? "" : speechIcon(c.speech, 20) + "<span>" + c.speech + "</span>"}</div>
    <p class="p-sub">${c.speech === "Built-in audio" ? "Listens to the audio directly" : "With " + c.speech + " speech recognition"}, by ${MAKERS[c.model]}</p>
    <div class="p-stats"><div class="p-stat"><span>Answer score</span><b>${c.score}</b><small>#${scoreRankOf(c)} of ${chains.length}</small></div><div class="p-stat"><span>Response</span><b>${c.time.toFixed(1)} s</b><small>#${timeRankOf(c)} of ${chains.length}</small></div></div>
    <p class="p-desc">${fast}${dominated ? "" : " No other chain is both faster and more accurate."}</p>
    ${PANEL_DETAILS(c)}
    <a class="p-btn" href="${P.slug}/ai-agent/">Build an agent with this</a>`;
}

// The panel's content varies with the selected chain (EcoCost text can wrap), but the scatter card and
// panel must not change size when you select one: size both to the tallest panel.
function fitPanelHeight() {
  const evaluation = document.querySelector(".evaluation");
  const panel = document.getElementById("chainPanel");
  if (!evaluation || !panel) return;
  const keep = selectedChain;
  panel.style.height = "auto";
  panel.style.alignSelf = "flex-start";
  let need = 509;
  chains.forEach(c => { selectedChain = c; renderPanel(); need = Math.max(need, panel.offsetHeight); });
  panel.style.height = "";
  panel.style.alignSelf = "";
  selectedChain = keep;
  renderPanel();
  evaluation.style.setProperty("--sc-h", Math.ceil(need) + "px");
}

function tooltipHtml(c, m) {
  const best = !metricChains(m).some(o => beats(m, o, c));
  const by = beatenBy(m, c);
  const rows = SCATTER.rows.map(([key, label]) => `<div class="${key === "time" || key === yMetric ? "strong" : ""}"><span>${label}</span><b>${FORMAT[key](c)}</b><em>${key === "carbon" ? (Number.isFinite(c.carbon) ? "EcoCost · low confidence" : "outside current coverage") : key === "cost" ? `${Q} observed runs` : "#" + (key === "time" ? timeRankOf(c) : scoreRankOf(c)) + " of " + chains.length}</em></div>`).join("");
  return `<div class="sc-tip-head">${model(c.model, 16)}<b>${c.model}${c.speech === "Built-in audio" ? "" : " +"}</b>${c.speech === "Built-in audio" ? "" : speechIcon(c.speech, 14) + "<b>" + c.speech + "</b>"}</div>
    <p class="sc-tip-sub">${MAKERS[c.model]} · ${c.speech === "Built-in audio" ? "Direct audio" : c.speech + " speech recognition"}</p>
    <div class="sc-tip-rows">${rows}</div>
    <p class="sc-tip-note">${best ? CHECK + "<span>Best trade-off: nothing is both faster and " + m.beat + "</span>" : INFO + "<span>Beaten by " + fullName(by) + ": faster and " + m.beat + "</span>"}</p>`;
}

function showTip(button) {
  const c = chains[Number(button.dataset.i)];
  tip.innerHTML = tooltipHtml(c, SCATTER.metrics[yMetric]);
  tip.hidden = false;
  const card = scatterCard.getBoundingClientRect();
  const r = button.getBoundingClientRect();
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let left = r.right - card.left + 8;
  if (left + w > card.width - 8) left = r.left - card.left - w - 8;
  left = Math.max(8, left);
  const top = Math.min(Math.max(8, r.top - card.top + r.height / 2 - 24), card.height - h - 8);
  tip.style.left = left + "px";
  tip.style.top = top + "px";
}
const hideTip = () => { tip.hidden = true; };

function renderScatter() {
  const m = SCATTER.metrics[yMetric];
  const root = document.getElementById("scatter");
  const out = [];
  const zx = Math.max(SCATTER.x(10), SC_X0);
  out.push(`<div class="sc-zone" style="left:${pctX(zx)};width:${pctX(657 - zx)};top:${pctY(71)};height:${pctY(333)}"></div><span class="sc-zone-label" style="left:${pctX(zx + 10)};top:${pctY(79)}">Async only</span>`);
  m.ticks.forEach(v => { const y = pctY(scatterY(m, v)); out.push(`<i class="sc-grid" style="top:${y}"></i><span class="sc-ytick" style="top:${y}">${m.tick(v)}</span>`); });
  SCATTER.xTicks.forEach(t => out.push(`<span class="sc-xtick" style="left:${pctX(SCATTER.x(t))}">${t} s</span>`));
  out.push(`<span class="sc-axis-title">${m.label}</span><span class="sc-xtitle">Median response time</span>`);
  const front = [...new Set([...frontierOf(m), ...SCATTER.extraLabelled(m)])].sort((a, b) => a.time - b.time);
  const pos = c => `${SCATTER.x(c.time).toFixed(1)},${scatterY(m, m.get(c)).toFixed(1)}`;
  out.push(`<svg class="sc-links" viewBox="0 0 ${SC_W} ${SC_H}" preserveAspectRatio="none" aria-hidden="true"><polyline points="${front.map(pos).join(" ")}" fill="none" stroke="#717580" stroke-width="1" stroke-dasharray="3 3" vector-effect="non-scaling-stroke"/></svg>`);
  const coveredChains = metricChains(m);
  const order = [...coveredChains].sort((a, b) => (a === selectedChain) - (b === selectedChain) || front.includes(a) - front.includes(b));
  order.forEach(c => {
    const style = `left:${pctX(SCATTER.x(c.time))};top:${pctY(scatterY(m, m.get(c)))};--ring:${RING[c.model]}`;
    const aria = `${fullName(c)}, score ${c.score}, response ${c.time.toFixed(1)} seconds`;
    const i = chains.indexOf(c);
    if (c === selectedChain) {
      out.push(`<button type="button" class="sc-point chip selected" style="${style}" data-i="${i}" data-g="${group(c)}" aria-label="${aria}">${model(c.model, 20)}<span class="label"><b>${SHORT[c.model]}</b><span>${c.speech === "Built-in audio" ? "direct audio" : "+ " + speechIcon(c.speech, 14) + c.speech}</span></span></button>`);
    } else if (front.includes(c)) {
      out.push(`<button type="button" class="sc-point chip" style="${style}" data-i="${i}" data-g="${group(c)}" aria-label="${aria}">${model(c.model, 16)}<span>${SHORT[c.model]}</span>${c.speech === "Built-in audio" ? "" : '<span class="plus">+</span>' + speechIcon(c.speech) + "<span>" + c.speech + "</span>"}</button>`);
    } else {
      out.push(`<button type="button" class="sc-point" style="${style}" data-i="${i}" data-g="${group(c)}" aria-label="${aria}">${model(c.model, 16)}</button>`);
    }
  });
  root.innerHTML = out.join("");
  root.querySelectorAll(".sc-point").forEach(button => {
    button.addEventListener("click", () => { selectedChain = chains[Number(button.dataset.i)]; hideTip(); renderScatter(); renderPanel(); });
    button.addEventListener("pointerenter", () => showTip(button));
    button.addEventListener("focus", () => showTip(button));
    button.addEventListener("pointerleave", hideTip);
    button.addEventListener("blur", hideTip);
  });
  document.getElementById("scatterTitle").textContent = m.title;
  document.getElementById("tradeText").textContent = m.front;
  document.getElementById("scatterHint").textContent = m.hint;
  document.getElementById("scatterSource").textContent = m.note;
  root.setAttribute("aria-label", `${m.label} against response time for ${coveredChains.length} covered AI chains.`);
}

// Y-axis menu (a custom listbox, so it can be styled like the Figma menu).
const yBtn = document.getElementById("yselectBtn");
const yMenu = document.getElementById("yselectMenu");
let yActive = 0;
function renderYMenu() {
  const keys = Object.keys(SCATTER.metrics);
  yBtn.firstElementChild.textContent = SCATTER.metrics[yMetric].label;
  yMenu.innerHTML = keys.map((k, i) => `<li role="option" id="yopt-${k}" data-k="${k}" aria-selected="${k === yMetric}" class="${i === yActive ? "active" : ""}"><span>${SCATTER.metrics[k].label}</span>${k === yMetric ? CHECK : ""}</li>`).join("");
  yBtn.setAttribute("aria-activedescendant", "yopt-" + keys[yActive]);
}
function setYMenu(open) {
  yMenu.hidden = !open;
  yBtn.setAttribute("aria-expanded", String(open));
  yBtn.closest(".select").classList.toggle("open", open);
  if (open) { yActive = Object.keys(SCATTER.metrics).indexOf(yMetric); renderYMenu(); }
}
function chooseMetric(key) {
  yMetric = key;
  setYMenu(false);
  renderYMenu();
  renderScatter();
}
yBtn.addEventListener("click", () => setYMenu(yMenu.hidden));
yMenu.addEventListener("click", event => { const li = event.target.closest("li"); if (li) chooseMetric(li.dataset.k); });
yMenu.addEventListener("pointermove", event => { const li = event.target.closest("li"); if (li) { yActive = Object.keys(SCATTER.metrics).indexOf(li.dataset.k); yMenu.querySelectorAll("li").forEach((el, i) => el.classList.toggle("active", i === yActive)); } });
yBtn.addEventListener("keydown", event => {
  const keys = Object.keys(SCATTER.metrics);
  if (event.key === "Escape") { setYMenu(false); return; }
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    event.preventDefault();
    if (yMenu.hidden) { setYMenu(true); return; }
    yActive = (yActive + (event.key === "ArrowDown" ? 1 : keys.length - 1)) % keys.length;
    renderYMenu();
  } else if ((event.key === "Enter" || event.key === " ") && !yMenu.hidden) {
    event.preventDefault();
    chooseMetric(keys[yActive]);
  }
});
document.addEventListener("click", event => { if (!event.target.closest(".select")) setYMenu(false); });
renderYMenu();
async function loadSamples() {
  const cards = document.getElementById("sampleCards");
  try {
    const response = await fetch(`${P.dataDir}/samples.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderSampleCards(cards, await response.json(), P.sample);
  } catch (error) {
    cards.innerHTML = '<p role="alert">Sample answers could not be loaded. Please refresh the page to try again.</p>';
    console.error(`Could not load ${P.lang} sample answers:`, error);
  }
}

renderMetrics();
renderTable();
renderLabRank();
renderScatter();
renderPanel();
fitPanelHeight();
if (document.fonts) document.fonts.ready.then(fitPanelHeight);
loadSamples();

document.querySelectorAll("[data-sort]").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll("[data-sort]").forEach(item => item.classList.toggle("active", item === button));
  renderTable(button.dataset.sort);
}));

const header = document.getElementById("siteHeader");
const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 220);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Hovering (or focusing) a legend item spotlights that group in the charts, scatter plot and table.
document.querySelectorAll(".legend > [data-g]").forEach(item => {
  const spotlight = on => { if (on) document.body.dataset.hl = item.dataset.g; else delete document.body.dataset.hl; };
  item.addEventListener("pointerenter", () => spotlight(true));
  item.addEventListener("pointerleave", () => spotlight(false));
  item.addEventListener("focus", () => spotlight(true));
  item.addEventListener("blur", () => spotlight(false));
});

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

const INDEX = P.lang + " Index";
const icon = (name, size = 16) => `<img src="assets/kinyarwanda/${name}.svg" alt="" width="${size}" height="${size}" />`;
const ICONS = { score: icon("icon-bullseye"), time: icon("icon-stopwatch"), cost: icon("icon-dollar"), carbon: icon("icon-leaf") };
const CHARTS = [
  { icon: "score", title: INDEX, sub: `Out of 100, averaged over ${Q} questions. Higher is better.`, order: (a, b) => b.acc - a.acc || a.time - b.time, height: c => c.exact * G.score, value: c => String(c.score), lines: G.lines.score,
    best: [bestOf(chains.filter(c => c.sovereign), "acc", true), bestOf(chains.filter(c => !c.sovereign), "acc", true)], show: c => String(c.score) },
  { icon: "time", title: "Response time", sub: "Median seconds, voice note to answer. Lower is better. Calls need under 10 s.", order: (a, b) => a.time - b.time, height: c => c.time * G.time, value: c => c.time.toFixed(1) + " s", lines: G.lines.time, limit: true,
    best: [bestOf(chains.filter(c => c.sovereign), "time", false), bestOf(chains.filter(c => !c.sovereign), "time", false)], show: c => c.time.toFixed(1) + " s" },
  { icon: "cost", title: "Cost per 1,000 questions", sub: `Observed Gooey.AI charge in USD; ${Q} runs per chain.`, order: (a, b) => a.cost - b.cost || b.acc - a.acc, height: c => G.costBase + (c.cost - 40) * G.costPerDollar, value: c => "$" + (chains.every(o => Number.isInteger(o.cost)) ? String(c.cost) : c.cost.toFixed(G.costDecimals ?? 2)), lines: G.lines.cost,
    best: [bestOf(chains.filter(c => c.sovereign), "cost", false), bestOf(chains.filter(c => !c.sovereign), "cost", false)], show: c => "$" + c.cost.toFixed(2) },
  { icon: "carbon", title: "CO₂e per 1,000 questions", sub: "Grams, LLM step only (EcoCost estimate). Lower is better.", order: (a, b) => (a.carbon ?? Infinity) - (b.carbon ?? Infinity), height: c => Number.isFinite(c.carbon) ? c.carbon * G.carbon : 0, value: c => Number.isFinite(c.carbon) ? c.carbon.toFixed(G.carbonDecimals ?? 1) + " g" : "N/A", lines: G.lines.carbon,
    best: [bestOf(chains.filter(c => c.sovereign && Number.isFinite(c.carbon)), "carbon", false), bestOf(chains.filter(c => !c.sovereign && Number.isFinite(c.carbon)), "carbon", false)], show: c => c.carbon.toFixed(1) + " g" }
];
// Chart coordinates are drawn in a 470 px plot (fluid, as percentages) or, for wide layouts, in pixels.
const COL_PITCH = G.pitch;
const LIMIT_Y = Math.round(212 - 10 * G.time);
const at = WIDE ? (x => x + "px") : (x => (x / 470 * 100).toFixed(3) + "%");
// Figma leaves gaps in the dashed line under the value labels; wide layouts just skip colliding dashes.
const LIMIT_DASHES = WIDE ? [...Array(138).keys()].map(i => i * 7) : [...Array(41).keys()].map(i => i * 7).concat([364], [406, 413, 420, 427, 434, 441]);

let barTipTimer;
// Hover cards are for mouse users on wide screens; on a phone a tap would leave one stuck over the chart.
const CAN_HOVER = matchMedia("(hover: hover) and (min-width: 761px)");
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
      plot.push(`<i class="col${c.sovereign ? " sov" : ""}" data-g="${group(c)}" data-i="${chains.indexOf(c)}" style="left:${at(left)};width:${at(24)};top:${212 - h}px;height:${h}px" aria-label="${fullName(c)}"></i><span class="val" data-g="${group(c)}" style="left:calc(${at(center)} - 24px);top:${212 - h - 18}px">${chart.value(c).replace(/\s+([a-z]+)$/i, '<span class="u"> $1</span>')}</span>`);
      const [size, offset] = LABEL_BOX[c.model];
      labels.push(`<img src="assets/kinyarwanda/${LOGO_FILES[c.model]}.svg" alt="" width="20" height="20" style="left:calc(${at(left)} + 2px);top:2px" /><img src="assets/kinyarwanda/${SPEECH_FILES[c.speech]}.svg" alt="" width="16" height="16" style="left:calc(${at(left)} + 4px);top:28px" /><div class="name" style="left:calc(${at(center)} + ${(offset - size).toFixed(2)}px);width:${size}px;height:${size}px"><span>${c.model}</span></div>`);
    });
    labels.push('<span class="axis-tag" style="top:5.5px">LLM</span><span class="axis-tag" style="top:29.5px">ASR</span>');
    const best = (c, label, cls) => (c ? `<div><i${cls}></i><span>${label} · <em>${c.model}</em></span><b>${chart.show(c)}</b></div>` : "");
    const article = document.createElement("article");
    article.className = "chart-card";
    article.innerHTML = `<div class="chart-head"><h3 class="chart-title">${ICONS[chart.icon]}${chart.title}</h3><p class="chart-sub">${chart.sub}</p></div><div class="chart-body"><div class="plot${tight ? " tight" : ""}" style="--ly:${LIMIT_Y}px">${plot.join("")}</div><div class="labels">${labels.join("")}</div></div><div class="chart-foot"><hr /><div class="best">${best(chart.best[0], "Best sovereign", ' class="sov"')}${best(chart.best[1], "Private", "")}</div></div>`;
    grid.appendChild(article);
    // Hovering a column shows the same card as the scatter, judged on this chart's metric (speed charts use the Index).
    const key = { cost: "cost", carbon: "carbon" }[chart.icon] || "score";
    article.querySelectorAll(".col[data-i]").forEach(col => {
      col.addEventListener("pointerenter", () => { clearTimeout(barTipTimer); if (!CAN_HOVER.matches) return; barTipTimer = setTimeout(() => showTip(col, key), 300); });
      col.addEventListener("pointerleave", () => { clearTimeout(barTipTimer); hideTip(); });
    });
  });
}

function renderTable(sort = "accuracy") {
  const rows = sort === "speed" ? byTime : ranked;
  document.getElementById("chainRows").innerHTML = rows.map((c, i) => `<div class="ct-row" data-g="${group(c)}" role="row"><span class="c-rank" role="cell">${i + 1}</span><span class="c-chain" role="cell"><span class="c-model">${model(c.model, 24)}<span class="c-name"><a href="../models/${P.modelSlugs[c.model]}/${P.slug}/">${c.model}</a></span></span><span class="c-plus">+</span><span class="c-speech">${speechIcon(c.speech)}${c.speech}</span></span><span class="c-score" role="cell"><span class="bar"><i class="${c.sovereign ? "sovereign" : "private"}" style="width:${c.exact.toFixed(2)}%"></i></span><b class="c-num">${c.score}</b></span><span class="c-time" role="cell">${c.time.toFixed(1)} s</span><span class="c-run" role="cell"><a href="${P.evalUrl}" target="_blank" rel="noopener noreferrer" aria-label="View the evaluation run for ${fullName(c)}">View run ↗</a></span></div>`).join("");
}

function renderLabRank() {
  const list = document.getElementById("labRank");
  if (!list || !P.labSpeech) return;
  list.innerHTML = ranked.filter(c => c.speech === P.labSpeech).map(c => `<li><i class="sw${c.sovereign ? " sov" : ""}"></i>${model(c.model, 16)}<span>${c.model} + ${P.labSpeech}</span><b>${c.score}</b><small>#${c.rank}</small><span class="lr-bar"><i${c.sovereign ? ' class="sov"' : ""} style="width:${c.score}%"></i></span></li>`).join("");
}

const [SC_X0, SC_T0, SC_PER_S] = P.scatter.x;
const MD = P.scatter.metrics;
const SCATTER = {
  x: t => SC_X0 + (t - SC_T0) * SC_PER_S,
  xTicks: P.scatter.xTicks,
  extraLabelled: () => (P.scatter.labelBestSovereign ? [bestSovereign] : []),
  rows: [["score", INDEX], ["time", "Response"], ["cost", "Cost"], ["carbon", "CO₂e"]],
  metrics: {
    score: { label: INDEX, title: INDEX + " vs response time", get: c => c.exact, high: true, ...MD.score, tick: v => String(v), beat: "higher on the Index", hint: "Higher and faster is better" },
    cost: { label: "Cost per 1,000 questions", title: "Cost vs response time", get: c => c.cost, high: false, ...MD.cost, tick: v => "$" + Math.round(v), beat: "cheaper", hint: "Lower and faster is better" },
    carbon: { label: "CO₂e per 1,000 questions", title: "CO₂e vs response time", get: c => c.carbon, high: false, ...MD.carbon, tick: v => v + " g", beat: "lower-carbon", hint: "Lower and faster is better" }
  }
};
// Scale for the panel's Eco cost range: 0 to the widest "likely" estimate of any chain.
const ECO_SCALE = Math.max(...chains.map(c => (Number.isFinite(c.carbonMax) ? c.carbonMax : 0)), 1);
const ecoPct = v => Math.min(100, Math.max(0, v / ECO_SCALE * 100)).toFixed(1) + "%";
const ecoPanel = c => `<div class="p-eco"><div class="p-lab">${icon("icon-leaf")}Eco cost</div>` + (Number.isFinite(c.carbon)
  ? `<div class="p-eco-val"><b>${c.carbon.toFixed(1)} g</b><span>CO₂e</span></div><div class="p-range" role="img" aria-label="Likely ${c.carbonMin.toFixed(1)} to ${c.carbonMax.toFixed(1)} grams"><i class="likely" style="left:${ecoPct(c.carbonMin)};width:calc(${ecoPct(c.carbonMax)} - ${ecoPct(c.carbonMin)})"></i><i class="dot" style="left:${ecoPct(c.carbon)}"></i></div><span class="p-cap">Likely ${c.carbonMin.toFixed(1)} to ${c.carbonMax.toFixed(1)} g</span>`
  : `<div class="p-eco-val na"><b>N/A</b></div>`) + "</div>";
const PANEL_DETAILS = c => `<div class="p-cost"><span>Per 1,000 questions</span><b>$${c.cost.toFixed(2)}</b></div>
    <div class="p-where"><div class="p-host"><div><div class="p-lab">${icon(c.sovereign ? "icon-landmark" : "icon-cloud")}Hosting</div><div class="p-val">${c.sovereign ? "Sovereign-deployable" : "Private API"}</div></div><hr /><div><div class="p-lab">${icon("icon-microphone")}Speech recognition</div><div class="p-val">${speechIcon(c.speech)}${c.speech}</div></div></div>${ecoPanel(c)}</div>`;

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
document.body.appendChild(tip);

function renderPanel() {
  const c = selectedChain;
  const dominated = chains.some(o => o !== c && scoreOf(o) >= scoreOf(c) && o.time <= c.time && (scoreOf(o) > scoreOf(c) || o.time < c.time));
  const fast = c.time < 10 ? "Fast enough for phone calls (under 10 s)." : "Too slow for phone calls (over 10 s), fine for WhatsApp messages.";
  document.getElementById("chainPanel").innerHTML = `<div class="p-head">
      <div class="p-name">${model(c.model, 20)}<span>${c.model}${c.speech === "Built-in audio" ? " (direct audio)" : " +"}</span>${c.speech === "Built-in audio" ? "" : speechIcon(c.speech, 20) + "<span>" + c.speech + "</span>"}</div>
      <p class="p-sub">${c.speech === "Built-in audio" ? "Listens to the audio directly" : "With " + c.speech + " speech recognition"}, by ${MAKERS[c.model]}</p>
    </div>
    <div class="p-stats"><div class="p-stat"><span>${INDEX}</span><b>${c.score}</b><small>#${scoreRankOf(c)} of ${chains.length}</small></div><div class="p-stat"><span>Response</span><b>${c.time.toFixed(1)} s</b><small>#${timeRankOf(c)} of ${chains.length}</small></div></div>
    <p class="p-desc">${fast}${dominated ? "" : " No other chain is both faster and higher on the Index."}</p>
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

function tooltipHtml(c, mKey = yMetric) {
  const m = SCATTER.metrics[mKey];
  const best = !metricChains(m).some(o => beats(m, o, c));
  const by = beatenBy(m, c);
  const rows = SCATTER.rows.map(([key, label]) => `<div class="${key === "time" || key === mKey ? "strong" : ""}"><span>${label}</span><b>${FORMAT[key](c)}</b><em>${key === "carbon" || key === "cost" ? "/ 1,000 Q's" : "#" + (key === "time" ? timeRankOf(c) : scoreRankOf(c)) + " of " + chains.length}</em></div>`).join("");
  return `<div class="sc-tip-head">${model(c.model, 16)}<b>${c.model}${c.speech === "Built-in audio" ? "" : " +"}</b>${c.speech === "Built-in audio" ? "" : speechIcon(c.speech, 14) + "<b>" + c.speech + "</b>"}</div>
    <p class="sc-tip-sub">${MAKERS[c.model]} · ${c.speech === "Built-in audio" ? "Direct audio" : c.speech + " speech recognition"}</p>
    <div class="sc-tip-rows">${rows}</div>
    <p class="sc-tip-note">${best ? CHECK + "<span>Best trade-off: nothing is faster and better</span>" : INFO + "<span>Beaten by " + fullName(by) + "</span>"}</p>`;
}

function showTip(anchor, mKey = yMetric) {
  if (!CAN_HOVER.matches) return; // no hover card on phones or touch screens, whatever the trigger (hover or focus)
  const c = chains[Number(anchor.dataset.i)];
  if (!Number.isFinite(SCATTER.metrics[mKey].get(c))) mKey = "score";
  tip.innerHTML = tooltipHtml(c, mKey);
  tip.hidden = false;
  tip.classList.remove("in");
  void tip.offsetWidth;
  tip.classList.add("in");
  // Beside the anchor, flipped to its left near the right edge, kept inside the viewport.
  const r = anchor.getBoundingClientRect();
  const w = tip.offsetWidth, h = tip.offsetHeight, vw = document.documentElement.clientWidth;
  let left = r.right + 8;
  if (left + w > vw - 8) left = r.left - w - 8;
  left = Math.max(8, left);
  const top = Math.min(Math.max(8, r.top + Math.min(r.height, 48) / 2 - 24), window.innerHeight - h - 8);
  tip.style.left = left + window.scrollX + "px";
  tip.style.top = top + window.scrollY + "px";
}
const hideTip = () => { tip.hidden = true; };

// Chains with the same value sit on one horizontal line and can cover each other (every Kinyarwanda chain cost
// $40). Where they would overlap, stack them above and below the line, selected and labelled chains first, and
// draw a short leader back to the true value so the stacking does not read as a different number.
function dodgeTies(root, m) {
  const buttons = [...root.querySelectorAll(".sc-point")].reverse();
  const box = root.getBoundingClientRect();
  const placed = [];
  const PAD = 3;
  const hits = (a, b) => a.left < b.right + PAD && b.left < a.right + PAD && a.top < b.bottom + PAD && b.top < a.bottom + PAD;
  buttons.forEach(button => {
    const c = chains[Number(button.dataset.i)];
    const v = m.get(c);
    const r = button.getBoundingClientRect();
    const step = Math.max(r.height, 24) + 4;
    const peers = placed.filter(p => p.v === v);
    let off = 0;
    for (let k = 1; k < 12 && peers.some(p => hits({ left: r.left, right: r.right, top: r.top + off, bottom: r.bottom + off }, p.r)); k++) {
      off = (k % 2 ? -1 : 1) * Math.ceil(k / 2) * step;
    }
    if (off) {
      button.style.top = `calc(${button.style.top} + ${off}px)`;
      const x = r.left + Math.min(r.width / 2, 12) - box.left;
      const lead = document.createElement("i");
      lead.className = "sc-lead";
      lead.style.cssText = `left:${x}px;top:calc(${pctY(scatterY(m, v))} + ${Math.min(0, off)}px);height:${Math.abs(off)}px`;
      root.insertBefore(lead, root.querySelector(".sc-point"));
    }
    placed.push({ v, off, r: { left: r.left, right: r.right, top: r.top + off, bottom: r.bottom + off } });
  });
  // A soft band behind each stack groups its points with the value they share.
  const grid = root.querySelector(".sc-grid");
  new Set(placed.filter(p => p.off).map(p => p.v)).forEach(v => {
    const offs = placed.filter(p => p.v === v).map(p => p.off);
    const lo = Math.min(...offs) - 18, hi = Math.max(...offs) + 18;
    const band = document.createElement("i");
    band.className = "sc-band";
    band.style.cssText = `left:${grid.offsetLeft}px;width:${grid.offsetWidth}px;top:calc(${pctY(scatterY(m, v))} + ${lo}px);height:${hi - lo}px`;
    root.insertBefore(band, root.querySelector(".sc-lead, .sc-point"));
  });
}

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
    const aria = `${fullName(c)}, Index ${c.score}, response ${c.time.toFixed(1)} seconds`;
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
    button.addEventListener("pointerenter", () => { if (CAN_HOVER.matches) showTip(button); });
    button.addEventListener("focus", () => showTip(button));
    button.addEventListener("pointerleave", hideTip);
    button.addEventListener("blur", hideTip);
  });
  dodgeTies(root, m);
  document.getElementById("tradeText").textContent = m.front;
  document.getElementById("scatterHint").textContent = m.hint;
  const [, sourceText = ""] = m.note.split(/\s*(?=Source:)/);
  const source = document.getElementById("scatterSource");
  source.replaceChildren(Object.assign(document.createElement("span"), { className: "src", textContent: sourceText.replace(/,\s*[A-Z][a-z]{2} \d{1,2}, \d{4}(?=\.?$)/, "") }));
  root.setAttribute("aria-label", `${m.label} against response time for ${coveredChains.length} covered AI chains.`);
}

// Y-axis menu (a custom listbox, so it can be styled like the Figma menu).
const yBtn = document.getElementById("yselectBtn");
const yMenu = document.getElementById("yselectMenu");
let yActive = 0;
function renderYMenu() {
  const keys = Object.keys(SCATTER.metrics);
  // The language name in "<Language> Index vs response time" is dropped on phones, where the two menus share a row.
  const title = k => SCATTER.metrics[k].title.replace(P.lang + " ", `<i class="wide-only">${P.lang} </i>`);
  yBtn.firstElementChild.innerHTML = title(yMetric);
  yMenu.innerHTML = keys.map((k, i) => `<li role="option" id="yopt-${k}" data-k="${k}" aria-selected="${k === yMetric}" class="${i === yActive ? "active" : ""}"><span>${title(k)}</span>${k === yMetric ? CHECK : ""}</li>`).join("");
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
// Eval-date menu: one entry per published evaluation (only the latest one so far).
const evalBtn = document.getElementById("evalBtn");
const evalMenu = document.getElementById("evalMenu");
function setEvalMenu(open) {
  evalMenu.hidden = !open;
  evalBtn.setAttribute("aria-expanded", String(open));
  evalBtn.closest(".select").classList.toggle("open", open);
}
evalBtn.addEventListener("click", () => { setYMenu(false); setEvalMenu(evalMenu.hidden); });
evalBtn.addEventListener("keydown", event => { if (event.key === "Escape") setEvalMenu(false); });
evalMenu.addEventListener("click", () => setEvalMenu(false));
yBtn.addEventListener("click", () => setEvalMenu(false));
document.addEventListener("click", event => {
  if (!event.target.closest(".select-chart")) setYMenu(false);
  if (!event.target.closest(".select-eval")) setEvalMenu(false);
});
renderYMenu();

// Featured labs: one slide per lab. The controls and dots only appear when there is more than one.
function initLabCarousel() {
  const root = document.getElementById("labCarousel");
  if (!root) return;
  const slides = [...root.querySelectorAll(".lab-slide")];
  const controls = document.getElementById("labControls");
  const dots = root.querySelector(".carousel-dots");
  if (slides.length < 2 || !controls || !dots) return;
  const [prev, next] = controls.querySelectorAll("button");
  const count = controls.querySelector(".carousel-count");
  dots.innerHTML = slides.map((_, i) => `<button type="button" aria-label="Show lab ${i + 1} of ${slides.length}"></button>`).join("");
  let current = 0;
  const show = i => {
    current = Math.min(slides.length - 1, Math.max(0, i));
    slides.forEach((slide, k) => { slide.hidden = k !== current; });
    [...dots.children].forEach((dot, k) => dot.classList.toggle("current", k === current));
    count.textContent = `${current + 1} of ${slides.length}`;
    prev.disabled = current === 0;
    next.disabled = current === slides.length - 1;
  };
  prev.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
  dots.addEventListener("click", event => { const i = [...dots.children].indexOf(event.target); if (i >= 0) show(i); });
  controls.hidden = false;
  dots.hidden = false;
  show(0);
}
// Phone rails: the sample cards and the "More" cards scroll sideways; dots under each rail track the position.
function initRail(rail) {
  if (!rail || rail.children.length < 2 || rail.nextElementSibling?.classList.contains("rail-dots")) return;
  const items = [...rail.children];
  const dots = document.createElement("div");
  dots.className = "rail-dots";
  dots.setAttribute("aria-hidden", "true");
  dots.innerHTML = items.map(() => "<i></i>").join("");
  rail.after(dots);
  const sync = () => {
    const start = rail.getBoundingClientRect().left + parseFloat(getComputedStyle(rail).paddingLeft);
    let index = items.length - 1;
    if (rail.scrollLeft + rail.clientWidth < rail.scrollWidth - 2) {
      index = items.reduce((best, item, i) => (Math.abs(item.getBoundingClientRect().left - start) < Math.abs(items[best].getBoundingClientRect().left - start) ? i : best), 0);
    }
    [...dots.children].forEach((dot, i) => dot.classList.toggle("on", i === index));
  };
  rail.addEventListener("scroll", sync, { passive: true });
  window.addEventListener("resize", sync);
  sync();
}
initRail(document.querySelector(".more-grid"));
async function loadSamples() {
  const cards = document.getElementById("sampleCards");
  try {
    const response = await fetch(`${P.dataDir}/samples.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderSampleCards(cards, await response.json(), P.sample, { tag: true, runLink: false });
    // Questions are clamped to three lines; a clamped one shows its full text on hover/focus.
    cards.querySelectorAll(".q strong").forEach(q => {
      if (q.scrollHeight > q.clientHeight + 1) { q.classList.add("clamped"); q.tabIndex = 0; q.title = q.textContent; q.parentElement.dataset.full = q.textContent; }
    });
    initRail(cards);
  } catch (error) {
    cards.innerHTML = '<p role="alert">Sample answers could not be loaded. Please refresh the page to try again.</p>';
    console.error(`Could not load ${P.lang} sample answers:`, error);
  }
}

renderMetrics();
renderTable();
renderLabRank();
initLabCarousel();
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

// Hero voice note: plays a real recorded question. Bars fill as it plays and the clock counts up, like the
// sample cards; only one recording plays at a time on the page.
(function initHeroVoice() {
  const note = document.getElementById("heroVoice");
  if (!note) return;
  const audio = note.querySelector("audio");
  const btn = note.querySelector(".play");
  const clock = note.querySelector("time");
  // Same generated waveform as the sample cards (silent start, bursts of speech), scaled to fit the card.
  const wave = note.querySelector(".wave");
  if (typeof waveHeights === "function") {
    const seed = [...audio.getAttribute("src")].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) >>> 0, 7);
    wave.innerHTML = waveHeights(seed).map(h => `<i class="dim" style="height:${Math.max(2, Math.round(h * 0.6))}px"></i>`).join("");
  }
  const bars = [...wave.querySelectorAll("i")];
  const resting = bars.map(b => b.classList.contains("dim"));
  const fmt = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;
  const sync = () => {
    const playing = !audio.paused && !audio.ended;
    note.classList.toggle("is-playing", playing);
    btn.setAttribute("aria-label", `${playing ? "Pause" : "Play"} the ${P.lang} question`);
    if (audio.currentTime > 0 && !audio.ended) {
      const played = Math.round((audio.currentTime / (audio.duration || 1)) * bars.length);
      bars.forEach((b, i) => b.classList.toggle("dim", i >= played));
      clock.textContent = fmt(audio.currentTime);
    } else {
      bars.forEach((b, i) => b.classList.toggle("dim", resting[i]));
      if (Number.isFinite(audio.duration)) clock.textContent = fmt(Math.round(audio.duration));
    }
  };
  btn.addEventListener("click", () => {
    if (audio.paused) {
      document.querySelectorAll("audio").forEach(a => { if (a !== audio) a.pause(); });
      audio.play().catch(() => {});
    } else audio.pause();
  });
  ["play", "pause", "timeupdate", "loadedmetadata"].forEach(e => audio.addEventListener(e, sync));
  audio.addEventListener("ended", () => { audio.currentTime = 0; sync(); });
  document.addEventListener("play", e => { if (e.target !== audio) audio.pause(); }, true);
})();

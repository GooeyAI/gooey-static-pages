// Sample-answer cards (question audio player, transcript, the chain's answer, score). Shared by the language
// pages and the model pages. dataBase prefixes relative audio paths; assetBase is where the logos live.
function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

// Each sample gets its own waveform, seeded by its question number so it is the same on every load. Voice notes
// usually open with a beat of silence, so the first 2 to 5 bars sit at the minimum height; after that, bursts of
// speech separated by short pauses, tapering off at the end.
const WAVE_BARS = 40;
function waveHeights(seed) {
  let t = (seed * 2654435761) >>> 0;
  const rand = () => { t = (t + 0x6d2b79f5) >>> 0; let r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
  const lead = 2 + Math.floor(rand() * 4);
  const heights = Array(lead).fill(2);
  let level = 0.5;
  while (heights.length < WAVE_BARS) {
    const left = WAVE_BARS - heights.length;
    if (heights.length > lead + 3 && rand() < 0.12) { const gap = 1 + Math.floor(rand() * 2); for (let k = 0; k < gap && heights.length < WAVE_BARS; k++) heights.push(2 + Math.round(rand() * 4)); continue; }
    level = Math.min(1, Math.max(0.15, level + (rand() - 0.5) * 0.6));
    const taper = left < 6 ? left / 6 : 1;
    heights.push(Math.max(3, Math.round((6 + level * 34 * (0.6 + rand() * 0.4)) * taper)));
  }
  return heights;
}

function formatClock(seconds) {
  const total = Math.max(0, Math.round(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

function voiceHtml(sample) {
  const bars = waveHeights(Number(sample.questionNumber) || 1).map(height => `<i style="height:${height}px"></i>`).join("");
  return `<div class="voice" data-question="${sample.questionNumber}" data-duration="${sample.audioDurationSeconds}">
      <button class="play-btn" type="button" aria-label="Play question ${sample.questionNumber} audio">
        <svg class="vp-play" width="13" height="14" viewBox="0 0 13 14" aria-hidden="true"><path d="M1.5 1.5v11l10-5.5z" stroke="currentColor" stroke-width="3" stroke-linejoin="round" /></svg>
        <svg class="vp-pause" width="13" height="14" viewBox="0 0 13 14" aria-hidden="true"><rect x="1.5" y="1" width="3.5" height="12" rx="1.5" /><rect x="8" y="1" width="3.5" height="12" rx="1.5" /></svg>
      </button>
      <span class="wave" aria-hidden="true">${bars}</span>
      <span class="voice-time">${formatClock(sample.audioDurationSeconds)}</span>
      <audio preload="none" src="${escapeHtml(sample.audioUrl)}"></audio>
    </div>`;
}

function initSamplePlayers(cards) {
  const sync = audio => {
    const voice = audio.closest(".voice");
    const duration = Number(voice.dataset.duration);
    const playing = !audio.paused && !audio.ended;
    const bars = voice.querySelectorAll(".wave i");
    const total = Number.isFinite(audio.duration) ? audio.duration : duration;
    const played = Math.round((audio.currentTime / total) * bars.length);
    voice.classList.toggle("is-playing", playing);
    voice.querySelector(".play-btn").setAttribute("aria-label", `${playing ? "Pause" : "Play"} question ${voice.dataset.question} audio`);
    bars.forEach((bar, index) => bar.classList.toggle("played", index < played));
    voice.querySelector(".voice-time").textContent = formatClock(audio.currentTime > 0 ? audio.currentTime : duration);
  };
  cards.addEventListener("click", event => {
    const button = event.target.closest(".play-btn");
    if (!button) return;
    const audio = button.closest(".voice").querySelector("audio");
    if (!audio.paused) { audio.pause(); return; }
    cards.querySelectorAll("audio").forEach(other => { if (other !== audio) other.pause(); });
    audio.play().catch(error => console.error("Could not play sample audio:", error));
  });
  ["play", "pause", "timeupdate", "ended"].forEach(type => cards.addEventListener(type, event => {
    if (!event.target.matches("audio")) return;
    if (type === "ended") event.target.currentTime = 0;
    sync(event.target);
  }, true));
}

// who: the chain that answered, { model, logo, speech, speechLogo }; speech is null for direct audio.
// tag: show the question's category as a chip in the card head. runLink: link to the model's public run.
function renderSampleCards(cards, data, who, { assetBase = "assets/", dataBase = "", tag = false, runLink = true } = {}) {
  const audio = url => (/^https?:/.test(url) ? url : dataBase + url);
  const logo = file => `<img src="${assetBase}kinyarwanda/${file}.svg" alt="" width="16" height="16" />`;
  const named = (file, text) => `<span class="a-who">${logo(file)}<span class="a-label">${text}</span></span>`;
  const answeredBy = who.speech
    ? `${named(who.logo, escapeHtml(who.model))}<span class="a-label">+</span>${named(who.speechLogo, `${escapeHtml(who.speech)}’s answer`)}`
    : named(who.logo, `${escapeHtml(who.model)} (direct audio)’s answer`);
  cards.innerHTML = data.samples.map(sample => `<article class="sample">
    <div class="sample-head">${tag && sample.category ? `<span class="tag">${escapeHtml(sample.category)}</span>` : ""}<span>Question ${sample.questionNumber} of ${data.totalQuestions}</span></div>
    ${voiceHtml({ ...sample, audioUrl: audio(sample.audioUrl) })}
    <p class="q"><span class="q-label">Question, as transcribed</span><strong>${escapeHtml(sample.transcript)}</strong><em>“${escapeHtml(sample.questionEnglish)}”</em></p>
    <hr />
    <div class="a-head">${answeredBy}</div>
    <p class="a-text">${escapeHtml(sample.answer)}</p>
    ${runLink ? `<a class="hear" href="${escapeHtml(sample.runUrl)}" target="_blank" rel="noopener noreferrer">View model run · ${sample.runtimeSeconds.toFixed(2)} s</a>` : ""}
    <p class="expert"><b>Expert answer:</b> ${escapeHtml(sample.expertAnswer)}</p>
    <div class="score"><span class="a-label">Matches the expert’s answer</span><div class="score-row"><span class="score-bar"><i style="width:${sample.score}%"></i></span><b>${sample.score}</b></div></div>
  </article>`).join("");
  initSamplePlayers(cards);
}

// Hero voice note (language/_src/voice-note.frag): plays a real recorded question. Shared by the language and
// speech-to-text pages. Bars fill as it plays and the clock counts up, like the
// sample cards; only one recording plays at a time on the page.
function initVoiceNote(note, lang) {
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
    btn.setAttribute("aria-label", `${playing ? "Pause" : "Play"} the ${lang} question`);
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
}

// Speech-to-text cards: the question audio, the expert's transcript, and what each recognizer heard, with the words
// that differ from the expert's underlined. scripts/build_language_pages.py does the word comparison.
function renderTranscriptCards(cards, data, { assetBase = "assets/", dataBase = "" } = {}) {
  const audio = url => (/^https?:/.test(url) ? url : dataBase + url);
  const lang = data.langCode ? ` lang="${escapeHtml(data.langCode)}"` : "";
  cards.innerHTML = data.samples.map(sample => `<article class="sample transcript">
    <div class="sample-head">${sample.category ? `<span class="tag">${escapeHtml(sample.category)}</span>` : ""}<span>Question ${sample.questionNumber} of ${data.totalQuestions}</span></div>
    ${voiceHtml({ ...sample, audioUrl: audio(sample.audioUrl) })}
    <p class="q"><span class="q-label">Expert transcript</span><strong${lang}>${escapeHtml(sample.expert)}</strong></p>
    <hr />
    ${sample.heard.map(h => `<div class="heard">
      <div class="heard-head"><img src="${assetBase}kinyarwanda/${h.logo}.svg" alt="" width="24" height="24" /><span class="a-label">${escapeHtml(h.label)} heard</span><span class="heard-count">${h.matched} of ${h.total} words</span></div>
      <p class="heard-text"${lang}>${h.words.map(([word, same]) => (same ? escapeHtml(word) : `<u>${escapeHtml(word)}</u>`)).join(" ")}</p>
    </div>`).join("")}
  </article>`).join("");
  initSamplePlayers(cards);
}

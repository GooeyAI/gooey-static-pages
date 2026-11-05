// Sample-answer cards (question audio player, transcript, the chain's answer, score). Shared by the language
// pages and the model pages. dataBase prefixes relative audio paths; assetBase is where the logos live.
function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

const WAVE_HEIGHTS = [15, 23, 28, 40, 38, 36, 28, 33, 36, 5, 15, 32, 26, 20, 18, 2, 2, 17, 6, 30, 8, 23, 16, 14, 8, 2];

function formatClock(seconds) {
  const total = Math.max(0, Math.round(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

function voiceHtml(sample) {
  const bars = WAVE_HEIGHTS.map(height => `<i style="height:${height}px"></i>`).join("");
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

function renderSampleCards(cards, data, who, { assetBase = "assets/", dataBase = "" } = {}) {
  const audio = url => (/^https?:/.test(url) ? url : dataBase + url);
  cards.innerHTML = data.samples.map(sample => `<article class="sample">
    <div class="sample-head"><span>Question ${sample.questionNumber} of ${data.totalQuestions}</span></div>
    ${voiceHtml({ ...sample, audioUrl: audio(sample.audioUrl) })}
    <p class="q"><span class="q-label">Question, as transcribed</span><strong>${escapeHtml(sample.transcript)}</strong><em>“${escapeHtml(sample.questionEnglish)}”</em></p>
    <hr />
    <div class="a-head"><img src="${assetBase}kinyarwanda/${who.logo}.svg" alt="" width="16" height="16" /><span class="a-label">${who.model}’s answer</span></div>
    <p class="a-text">${escapeHtml(sample.answer)}</p>
    <a class="hear" href="${escapeHtml(sample.runUrl)}" target="_blank" rel="noopener noreferrer">View model run · ${sample.runtimeSeconds.toFixed(2)} s</a>
    <p class="expert"><b>Expert answer:</b> ${escapeHtml(sample.expertAnswer)}</p>
    <div class="score"><span class="a-label">Matches the expert’s answer</span><div class="score-row"><span class="score-bar"><i style="width:${sample.score}%"></i></span><b>${sample.score}</b></div></div>
  </article>`).join("");
  initSamplePlayers(cards);
}

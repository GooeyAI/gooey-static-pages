// Interactions for the /language/<name>/speech-to-text pages. The HTML and window.STT_PAGE are written by
// scripts/build_language_pages.py; the voice note and sample cards use the language page's shared players
// in language-samples.js.
const S = window.STT_PAGE;

// Hero: the same voice note as the language page.
initVoiceNote(document.getElementById("heroVoice"), S.lang);

// Sample transcriptions: the language page's sample questions, with what each recognizer heard.
renderTranscriptCards(document.getElementById("sttCards"), S, { dataBase: S.dataBase });

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

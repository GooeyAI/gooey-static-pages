<section class="section" id="faq" aria-labelledby="faq-title">
        <div class="container faq">
          <h2 id="faq-title">Frequently asked questions</h2>
          <div class="faq-list">
            <details open><summary>Can I run a Swahili AI on my own servers?</summary><p>Four chains can: DeepSeek V4 and Kimi K3, each with Omnilingual or Intron speech recognition. Both models have open weights, Omnilingual is open, and Intron says Sahara v2 can run offline on local hardware. DeepSeek V4 + Omnilingual also scored highest of the four in our Aug 30, 2026 test (93 out of 100, 7.5 s). Every other chain needs a private API, which sends audio to its maker’s cloud.</p></details>
            <details open><summary>What is the best AI for Swahili?</summary><p>In our Aug 30, 2026 test, Gemini 3.1 Pro, which listens to the audio directly, scored highest (95 out of 100, 5.8 s). DeepSeek V4 with Omnilingual or Intron speech recognition, and Gemini 3.1 Pro with Omnilingual, came next (93).</p></details>
            <details open><summary>Which is best for phone calls, and which for WhatsApp?</summary><p>For phone calls, Gemini 3.1 Pro with direct audio is the fastest chain overall (5.8 s) and also the most accurate (95). The fastest sovereign-deployable chain scoring 88 or more is DeepSeek V4 + Omnilingual (7.5 s, score 93). 17 of the 19 chains answer in under 10 s. For WhatsApp voice notes and text a second or two matters less: Gemini 3.1 Pro with direct audio is still the most accurate (score 95), and DeepSeek V4 + Omnilingual the best sovereign-deployable chain (93).</p></details>
            <details open><summary>Does ChatGPT understand Swahili?</summary><p>OpenAI’s GPT-5.6 Sol scored 90 with Omnilingual, 88 with Intron and 87 with GPT Transcribe, 8th of 19 at best.</p></details>
            <details open><summary>How did you test?</summary><p>We recorded 24 general-knowledge questions about Kenya in Swahili. Each chain transcribed, translated and answered them, and every answer was scored against a reference answer by comparing meaning. Accuracy is the mean score over the 24 questions and response time is the median.</p></details>
          </div>
        </div>
      </section>

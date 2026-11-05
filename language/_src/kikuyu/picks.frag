<section class="section" id="recommendations" aria-labelledby="pick-title">
        <div class="container pick">
          <div class="pick-head">
            <h2 id="pick-title">Which chain should you pick?</h2>
            <p>Use answer quality for messages; for live calls, balance quality with the 10-second response-time target.</p>
          </div>
          <div class="matrix">
            <div class="matrix-rows">
              <div class="corner">I’m building for</div>
              <div class="row-head"><div class="row-title"><img src="assets/kinyarwanda/icon-phone.svg" alt="" width="16" height="16" />Voice calls</div><p class="pick-rule">Pick: the fastest chain scoring 80 or more</p></div>
              <div class="row-head"><div class="row-title"><img src="assets/kinyarwanda/icon-message.svg" alt="" width="16" height="16" />Async messaging</div><p>WhatsApp voice notes and text. A few seconds’ wait is fine.</p><p class="pick-rule">Pick: the most accurate chain</p></div>
            </div>
            <div class="matrix-col">
              <div class="col-head"><div class="rule"></div><div class="col-title"><img src="assets/kinyarwanda/icon-cloud.svg" alt="" width="16" height="16" /><strong>Fast, high-scoring pick</strong><small>Under 10 seconds</small></div><p>Best measured balance for a live interaction. Deployment must be verified separately.</p></div>
              <article class="pick-card"><div class="chain"><img src="assets/kinyarwanda/logo-gemini-24.svg" alt="" width="24" height="24" /><span>Gemini 3.7 Flash</span><span class="plus">+</span><img src="assets/kinyarwanda/icon-mic-legend.svg" alt="" width="16" height="16" /><span>Kikuyu Whisper v2</span></div><div class="stats"><div class="stat big"><b>82</b><span>answer score</span></div><div class="stat"><b>7.1 s</b><span>response</span></div></div><p>The fastest chain scoring at least 80. It is 4 points behind the most accurate chain but answers 2.4 seconds sooner.</p><hr /><a class="cta" href="kikuyu/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a></article>
              <article class="pick-card"><div class="chain"><img src="assets/kinyarwanda/logo-gemini-24.svg" alt="" width="24" height="24" /><span>Gemini 3.7 Flash</span><span class="plus">+</span><img src="assets/kinyarwanda/icon-mic-legend.svg" alt="" width="16" height="16" /><span>Kikuyu Whisper v2</span></div><div class="stats"><div class="stat big"><b>82</b><span>answer score</span></div><div class="stat"><b>7.1 s</b><span>response</span></div></div><p>A strong alternative when faster replies matter more than the last 4 points of answer quality.</p><hr /><a class="cta" href="kikuyu/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a></article>
            </div>
            <div class="matrix-col recommended">
              <div class="col-head"><div class="rule"></div><div class="col-title"><img src="assets/kinyarwanda/icon-bullseye.svg" alt="" width="16" height="16" /><strong>Most accurate</strong><small>Score 86</small></div><p>Highest mean semantic-match score across the 24 spoken questions.</p></div>
              <article class="pick-card"><div class="chain"><img src="assets/kinyarwanda/logo-gemini-24.svg" alt="" width="24" height="24" /><span>Gemini 3.1 Pro</span><span class="plus">+</span><img src="assets/kinyarwanda/icon-mic-legend.svg" alt="" width="16" height="16" /><span>Kikuyu Whisper v2</span></div><div class="stats"><div class="stat big"><b>86</b><span>answer score</span></div><div class="stat"><b>9.5 s</b><span>response</span></div></div><p>The highest-scoring chain and still under the 10-second call target on median.</p><hr /><a class="cta" href="kikuyu/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a></article>
              <article class="pick-card"><div class="chain"><img src="assets/kinyarwanda/logo-gemini-24.svg" alt="" width="24" height="24" /><span>Gemini 3.1 Pro</span><span class="plus">+</span><img src="assets/kinyarwanda/icon-mic-legend.svg" alt="" width="16" height="16" /><span>Kikuyu Whisper v2</span></div><div class="stats"><div class="stat big"><b>86</b><span>answer score</span></div><div class="stat"><b>9.5 s</b><span>response</span></div></div><p>The best choice when answer quality is the priority and an extra 2.4 seconds versus Gemini Flash is acceptable.</p><hr /><a class="cta" href="kikuyu/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a></article>
            </div>
          </div>
          <p class="board-note">These picks prioritize measured answer score and runtime. Price is the observed whole-workflow Gooey.AI charge across 24 benchmark runs per chain. EcoCost covers text-model inference only and excludes speech recognition and direct audio.</p>
        </div>
      </section>

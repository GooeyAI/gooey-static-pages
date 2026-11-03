<section class="section" id="recommendations" aria-labelledby="pick-title">
        <div class="container pick">
          <div class="pick-head">
            <h2 id="pick-title">Which chain should you pick?</h2>
            <p>Two choices change the answer: where the models run, and whether people reach them by phone call or by message.</p>
          </div>
          <div class="matrix">
            <div class="matrix-rows">
              <div class="corner">I’m building for</div>
              <div class="row-head">
                <div class="row-title"><img src="assets/kinyarwanda/icon-phone.svg" alt="" width="16" height="16" />Voice calls</div>
                <p class="pick-rule">Pick: the fastest chain scoring 51 or more</p>
              </div>
              <div class="row-head">
                <div class="row-title"><img src="assets/kinyarwanda/icon-message.svg" alt="" width="16" height="16" />Async messaging</div>
                <p>WhatsApp voice notes and text. A few seconds’ wait is fine.</p>
                <p class="pick-rule">Pick: the most accurate chain</p>
              </div>
            </div>
            <div class="matrix-col">
              <div class="col-head">
                <div class="rule"></div>
                <div class="col-title"><img src="assets/kinyarwanda/icon-cloud.svg" alt="" width="16" height="16" /><strong>Private API</strong><small>9 chains</small></div>
                <p>At least one step runs on its maker’s cloud. Nothing to run yourself, but your data leaves the country unless a zero-data-retention region fits.</p>
              </div>
            <article class="pick-card">
              <div class="chain"><img src="assets/kinyarwanda/logo-openai-24.svg" alt="" width="24" height="24" /><span>GPT-5.6 Sol</span><span class="plus">+</span><img src="assets/kinyarwanda/logo-meta.svg" alt="" width="16" height="16" /><span>Omnilingual</span></div>
              <div class="stats">
                <div class="stat big"><b>59</b><span>answer score</span></div>
                <div class="stat"><b>14.4 s</b><span>response</span></div>
              </div>
              <p>The fastest private-API chain scoring at least the median (51), and still 4.4 s over the 10 s call limit. Gemini 3.1 Pro (direct audio) is 12 points better but 2.0 s slower.</p>
              <hr />
              <a class="cta" href="hausa/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a>
            </article>
            <article class="pick-card">
              <div class="chain"><img src="assets/kinyarwanda/logo-gemini-24.svg" alt="" width="24" height="24" /><span>Gemini 3.1 Pro</span><span class="dir">(direct audio)</span></div>
              <div class="stats">
                <div class="stat big"><b>71</b><span>answer score</span></div>
                <div class="stat"><b>16.3 s</b><span>response</span></div>
              </div>
              <p>The most accurate of all 13 chains, so it is also the pick for messages. It listens to the audio directly, so there is one model and one bill, and no separate speech step to run. Next best is Kimi K3 with Omnilingual at 63.</p>
              <hr />
              <a class="cta" href="hausa/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a>
            </article>
            </div>
            <div class="matrix-col sovereign">
              <div class="col-head">
                <div class="rule"></div>
                <div class="col-title"><img src="assets/kinyarwanda/icon-landmark.svg" alt="" width="16" height="16" /><strong>Sovereign-deployable</strong><small>4 chains</small></div>
                <p>Every step can run in your own country or on your own servers: open-weight models, or Intron speech on local hardware.</p>
              </div>
            <article class="pick-card">
              <div class="chain"><img src="assets/kinyarwanda/logo-kimi.svg" alt="" width="24" height="24" /><span>Kimi K3</span><span class="plus">+</span><img src="assets/kinyarwanda/logo-meta.svg" alt="" width="16" height="16" /><span>Omnilingual</span></div>
              <div class="stats">
                <div class="stat big"><b>63</b><span>answer score</span></div>
                <div class="stat"><b>20.8 s</b><span>response</span></div>
              </div>
              <p>The fastest sovereign-deployable chain scoring at least the median (51), but at 20.8 s it is too slow for live calls. 8 points behind Gemini 3.1 Pro, the private pick, and 4.5 s slower.</p>
              <hr />
              <a class="cta" href="hausa/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a>
            </article>
            <article class="pick-card">
              <div class="chain"><img src="assets/kinyarwanda/logo-kimi.svg" alt="" width="24" height="24" /><span>Kimi K3</span><span class="plus">+</span><img src="assets/kinyarwanda/logo-meta.svg" alt="" width="16" height="16" /><span>Omnilingual</span></div>
              <div class="stats">
                <div class="stat big"><b>63</b><span>answer score</span></div>
                <div class="stat"><b>20.8 s</b><span>response</span></div>
              </div>
              <p>The most accurate sovereign-deployable chain, so it is also the pick for messages. Kimi K3 with Intron is next at 56.</p>
              <hr />
              <a class="cta" href="hausa/ai-agent/">Build an agent with this<img src="assets/kinyarwanda/icon-arrow.svg" alt="" width="14" height="14" /></a>
            </article>
            </div>
          </div>
          <p class="board-note">Voice calls pick the fastest chain scoring at least the median (51). Async messaging picks the most accurate chain. No Hausa chain answers within the 10 s phone-call limit yet (the fastest takes 13.6 s), so voice assistants need a spoken holding message. Hosting types are sample values until confirmed; Intron counts as sovereign-deployable on the strength of its offline option, which still needs confirming for Hausa.</p>
        </div>
      </section>

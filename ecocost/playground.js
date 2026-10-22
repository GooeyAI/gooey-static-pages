// API playground. Loads Pyodide and the published ecocost wheel on first
// approach, then calls estimate() on every form change. Bump
// ECOCOST_VERSION together with the example figures quoted on this page.
(function () {
  var PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";
  var ECOCOST_VERSION = "0.2.0";

  var root = document.getElementById("playground");
  var form = document.getElementById("pgForm");
  if (!root || !form) return;
  var box = root.querySelector(".pg");
  var statusEl = document.getElementById("pgStatus");
  var resultEl = document.getElementById("pgResult");
  var snippetEl = document.getElementById("pgSnippet");

  var MIX_COLORS = {
    hydro: "#3b82c4",
    wind: "#2bb39a",
    solar: "#f2b632",
    nuclear: "#8b6fd1",
    geothermal: "#c9733b",
    biomass: "#7fb24a",
    gas: "#e8913a",
    oil: "#8a7f72",
    coal: "#4a4a4a",
    other: "#bdbdbd",
  };

  var PY = [
    "import json",
    "import ecocost",
    "from ecocost import estimate",
    "from ecocost.loader import get_kb",
    "from ecocost.display import format_grams, format_wh, format_ml",
    "kb = get_kb()",
    "def pg_catalog():",
    "    return json.dumps({",
    "        'version': ecocost.__version__,",
    "        'models': [{'id': m.id, 'label': m.label, 'creator': m.creator} for m in kb.models.values()],",
    "        'providers': [{'id': p.id, 'label': p.label} for p in kb.providers.values()],",
    "        'regions': [{'id': r.id, 'label': r.label} for r in kb.regions.values()],",
    "    })",
    "def pg_run(args):",
    "    a = json.loads(args)",
    "    try:",
    "        r = estimate(a['model'], provider=a['provider'] or None, region=a['region'] or None,",
    "                     input_tokens=a['input_tokens'], output_tokens=a['output_tokens'],",
    "                     cached_input_tokens=a['cached_input_tokens'])",
    "    except (LookupError, ValueError, TypeError) as e:",
    "        return json.dumps({'error': str(e)})",
    "    c, e, w = r['carbon'], r['energy'], r['water']",
    "    fmt = {",
    "        'carbon': format_grams(c['value']),",
    "        'carbon_range': format_grams(c['min']) + ' – ' + format_grams(c['max']),",
    "        'energy': format_wh(e['value']),",
    "        'energy_range': format_wh(e['min']) + ' – ' + format_wh(e['max']),",
    "        'water': format_ml(w['value']),",
    "        'water_dc': format_ml(w['data_center']['value']),",
    "        'water_pp': format_ml(w['power_plant']['value']),",
    "        'region_label': kb.regions[r['grid']['region']].label if r['grid']['region'] in kb.regions else r['grid']['region'],",
    "    }",
    "    return json.dumps({'result': r, 'fmt': fmt}, default=str)",
  ].join("\n");

  var py = null;
  var booting = false;

  function setStatus(text, isError) {
    statusEl.hidden = false;
    statusEl.classList.toggle("error", !!isError);
    statusEl.textContent = "";
    if (!isError) {
      var spin = document.createElement("i");
      spin.className = "fa-regular fa-spinner-third fa-spin";
      spin.setAttribute("aria-hidden", "true");
      statusEl.appendChild(spin);
    }
    var span = document.createElement("span");
    span.textContent = text;
    statusEl.appendChild(span);
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = function () {
        reject(new Error("Couldn't load " + src));
      };
      document.head.appendChild(s);
    });
  }

  function fillSelect(sel, items, current, groupBy) {
    sel.textContent = "";
    var keep = sel.name === "region" || sel.name === "provider";
    if (keep) {
      var none = document.createElement("option");
      none.value = "";
      none.textContent =
        sel.name === "region" ? "Provider's sites" : "Don't know (infer it)";
      sel.appendChild(none);
    }
    var parent = sel;
    var lastGroup = null;
    items.forEach(function (it) {
      if (groupBy && it[groupBy] !== lastGroup) {
        lastGroup = it[groupBy];
        parent = document.createElement("optgroup");
        parent.label = lastGroup;
        sel.appendChild(parent);
      }
      var o = document.createElement("option");
      o.value = it.id;
      o.textContent = it.label + (groupBy ? "" : " (" + it.id + ")");
      parent.appendChild(o);
    });
    sel.value = current;
  }

  async function boot() {
    if (booting) return;
    booting = true;
    try {
      setStatus("Loading Python in your browser (about 10 MB, once)…");
      await loadScript(PYODIDE_URL + "pyodide.js");
      py = await loadPyodide({ indexURL: PYODIDE_URL });
      setStatus("Installing ecocost " + ECOCOST_VERSION + "…");
      await py.loadPackage(["micropip", "pyyaml"]);
      await py
        .pyimport("micropip")
        .install("ecocost==" + ECOCOST_VERSION);
      py.runPython(PY);
      var cat = JSON.parse(py.globals.get("pg_catalog")());
      var models = cat.models.slice().sort(function (a, b) {
        return (
          a.creator.localeCompare(b.creator) ||
          a.label.localeCompare(b.label)
        );
      });
      fillSelect(form.model, models, form.model.value, "creator");
      fillSelect(form.provider, cat.providers, form.provider.value);
      fillSelect(form.region, cat.regions, form.region.value);
      Array.prototype.forEach.call(form.elements, function (el) {
        el.disabled = false;
      });
      box.setAttribute("aria-busy", "false");
      run();
    } catch (err) {
      console.error(err);
      setStatus(
        "The playground couldn't load in this browser. You can run the same estimate locally with: pip install ecocost",
        true,
      );
    }
  }

  function args() {
    var n = function (el) {
      var v = parseInt(el.value, 10);
      return isNaN(v) ? 0 : v;
    };
    return {
      model: form.model.value,
      provider: form.provider.value,
      region: form.region.value,
      input_tokens: n(form.input_tokens),
      output_tokens: n(form.output_tokens),
      cached_input_tokens: n(form.cached_input_tokens),
    };
  }

  function renderSnippet(a) {
    var lines = ["from ecocost import estimate", "", "estimate("];
    lines.push('    "' + a.model + '",');
    if (a.provider) lines.push('    provider="' + a.provider + '",');
    if (a.region) lines.push('    region="' + a.region + '",');
    lines.push("    input_tokens=" + a.input_tokens + ",");
    lines.push("    output_tokens=" + a.output_tokens + ",");
    if (a.cached_input_tokens)
      lines.push("    cached_input_tokens=" + a.cached_input_tokens + ",");
    lines.push(")");
    snippetEl.textContent = lines.join("\n");
  }

  function sig(x) {
    return Number(Number(x).toPrecision(2)).toLocaleString("en-US", {
      maximumFractionDigits: 10,
    });
  }
  function seconds(s) {
    return s >= 60 ? sig(s / 60) + " min" : sig(s) + " s";
  }

  function setField(name, text) {
    resultEl.querySelector('[data-f="' + name + '"]').textContent = text;
  }

  function render(r, fmt) {
    setField("carbon", fmt.carbon + " CO₂e");
    setField("carbon_range", "likely " + fmt.carbon_range);
    setField("energy", fmt.energy);
    setField("energy_range", "likely " + fmt.energy_range + " at the meter");
    setField("water", fmt.water);
    setField(
      "water_split",
      fmt.water_dc + " cooling · " + fmt.water_pp + " power plants",
    );
    setField("compute", seconds(r.compute.value));
    setField(
      "compute_range",
      "likely " + seconds(r.compute.min) + " – " + seconds(r.compute.max),
    );


    var g = r.grid;
    setField("grid_label", fmt.region_label);
    setField(
      "grid_intensity",
      Math.round(g.carbon_intensity.value) +
        " gCO₂e/kWh (" +
        Math.round(g.carbon_intensity.min) +
        "–" +
        Math.round(g.carbon_intensity.max) +
        ") · " +
        g.data_year,
    );
    var mix = Object.keys(g.mix)
      .map(function (k) {
        return [k, g.mix[k]];
      })
      .sort(function (a, b) {
        return b[1] - a[1];
      });
    var bar = document.getElementById("pgMix");
    var legend = document.getElementById("pgLegend");
    bar.textContent = "";
    legend.textContent = "";
    mix.forEach(function (m) {
      var color = MIX_COLORS[m[0]] || MIX_COLORS.other;
      var seg = document.createElement("span");
      seg.style.width = m[1] * 100 + "%";
      seg.style.background = color;
      bar.appendChild(seg);
      if (m[1] < 0.01) return;
      var li = document.createElement("li");
      var dot = document.createElement("i");
      dot.style.background = color;
      li.appendChild(dot);
      li.appendChild(
        document.createTextNode(
          m[0].charAt(0).toUpperCase() +
            m[0].slice(1) +
            " " +
            Math.round(m[1] * 100) +
            "%",
        ),
      );
      legend.appendChild(li);
    });

    document.getElementById("pgJson").textContent = JSON.stringify(
      r,
      null,
      2,
    );
  }

  function run() {
    var a = args();
    renderSnippet(a);
    if (!py) return;
    var out = JSON.parse(py.globals.get("pg_run")(JSON.stringify(a)));
    if (out.error) {
      setStatus(out.error, true);
      resultEl.hidden = true;
      return;
    }
    statusEl.hidden = true;
    render(out.result, out.fmt);
    resultEl.hidden = false;
  }

  var timer = null;
  form.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(run, 120);
  });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
  });
  document.getElementById("pgCopy").addEventListener("click", function () {
    var btn = this;
    navigator.clipboard.writeText(snippetEl.textContent).then(function () {
      btn.textContent = "Copied";
      setTimeout(function () {
        btn.textContent = "Copy";
      }, 1500);
    });
  });

  renderSnippet(args());
  // Start loading shortly before the section scrolls into view.
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) {
          io.disconnect();
          boot();
        }
      },
      { rootMargin: "600px 0px" },
    );
    io.observe(root);
  } else {
    boot();
  }
})();

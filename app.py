import streamlit as st
import json
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Artemis — LLM Optimization Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal shell CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
[data-testid="stAppViewContainer"] {
    background: #f4f2ff;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
footer, #MainMenu { display: none !important; }
.block-container {
    padding: 1.5rem 2.5rem 2rem !important;
    max-width: 1060px !important;
    margin: 0 auto !important;
    font-family: 'Inter', -apple-system, sans-serif;
}
/* hide streamlit iframe border */
[data-testid="stCustomComponentV1"] iframe {
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"


def list_configs():
    configs = []
    if not DATA_DIR.exists():
        return configs
    for fpath in sorted(DATA_DIR.glob("*.json")):
        try:
            d = json.loads(fpath.read_text())
            m = d.get("meta", {})
            configs.append({
                "config_id": fpath.stem,
                "model":     m.get("model", fpath.stem),
                "hardware":  m.get("hardware", ""),
                "framework": m.get("framework", ""),
            })
        except Exception:
            pass
    return configs


def load_config(config_id: str):
    p = DATA_DIR / f"{config_id}.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


# ── Race iframe HTML ──────────────────────────────────────────────────────────
_RACE_HTML = r"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
  background: transparent;
  padding: 2px 2px 6px;
  -webkit-font-smoothing: antialiased;
}

/* ── Spec bar ── */
.spec-bar {
  background: white;
  border: 1px solid #e6e2ff;
  border-radius: 10px;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 0.81rem;
  box-shadow: 0 1px 8px rgba(124,115,255,0.06);
  flex-wrap: wrap;
}
.spec-lbl { color: #bbb; margin-right: 2px; }
.spec-sep { color: #dcd8f5; margin: 0 10px; font-size: 1rem; }
.sb-sel {
  border: none;
  background: transparent;
  color: #040442;
  font-weight: 700;
  font-size: 0.81rem;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  padding: 0 18px 0 0;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237C73FF' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 2px center;
  background-size: 10px 6px;
}
.sb-sel:hover { color: #7C73FF; }

/* ── Selector row ── */
.sel-row {
  display: flex;
  gap: 10px;
  align-items: stretch;
  margin-bottom: 10px;
}
.sel-wrap { flex: 1; position: relative; }
.sel-wrap select {
  width: 100%;
  padding: 9px 36px 9px 14px;
  border: 1.5px solid #e6e2ff;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #040442;
  background: white;
  cursor: pointer;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}
.sel-wrap select:focus { border-color: #7C73FF; }
.sel-wrap::after {
  content: '';
  position: absolute;
  right: 13px;
  top: 50%;
  transform: translateY(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #7C73FF;
  pointer-events: none;
}

/* ── Prompt preview ── */
.prompt-box {
  background: white;
  border: 1px solid #e6e2ff;
  border-left: 3px solid #7C73FF;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 0.81rem;
  color: #444;
  line-height: 1.55;
  margin-bottom: 14px;
}
.run-btn {
  background: #7C73FF;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 9px 22px;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background .15s;
  letter-spacing: .3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.run-btn:hover:not(:disabled) { background: #6a60f5; }
.run-btn:disabled { background: #b0abf0; cursor: default; }

/* ── Response cards ── */
.cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
.card {
  background: white;
  border: 1px solid #e6e2ff;
  border-radius: 12px;
  padding: 16px 18px;
  min-height: 195px;
  display: flex;
  flex-direction: column;
}
.card-opt { background: #f5fffb; border-color: #b8edcf; }
.card-hdr {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-shrink: 0;
}
.card-title { font-size: .875rem; font-weight: 700; color: #040442; }
.badge {
  font-size: .62rem; font-weight: 800; padding: 2px 10px;
  border-radius: 20px; background: #eeeeff; color: #7C73FF;
  letter-spacing: .3px;
}
.badge-opt { background: #c8f0de; color: #0a8f60; }
.card-time { margin-left: auto; font-size: 1.05rem; font-weight: 800; color: #040442; letter-spacing: -.5px; }
.card-time-opt { color: #1AD598; }
.card-body {
  font-size: .8rem; color: #333; line-height: 1.65;
  flex: 1; white-space: pre-wrap; word-break: break-word;
  min-height: 72px;
}
.placeholder { color: #ccc; font-style: italic; }
.card-footer {
  display: flex; justify-content: space-between;
  font-size: .73rem; color: #aaa;
  margin-top: 10px; padding-top: 8px;
  border-top: 1px solid #f0eeff; flex-shrink: 0;
}
.card-footer-opt { border-color: #d8f2e8; }
.card-footer strong { color: #040442; }
.cur { display: inline-block; width: 2px; height: 12px; background: #7C73FF; margin-left: 1px; vertical-align: middle; animation: bl .7s infinite; }
.cur-opt { background: #1AD598; }
@keyframes bl { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Metrics ── */
.metrics-row {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;
  margin-bottom: 12px;
  opacity: 0;
  transition: opacity .4s;
}
.metrics-row.show { opacity: 1; }
.mc { background: white; border: 1px solid #e6e2ff; border-radius: 12px; padding: 16px 20px; }
.mc-lbl {
  font-size: .59rem; font-weight: 800; letter-spacing: 1.4px;
  text-transform: uppercase; color: #bbb; margin-bottom: 10px;
}
.mc-pct {
  display: block; font-size: 2.2rem; font-weight: 900;
  color: #1AD598; line-height: 1; margin-bottom: 8px; letter-spacing: -1px;
}
.mc-arrow-row {
  font-size: .78rem; color: #aaa; display: flex; align-items: center; gap: 5px;
}
.mc-arrow-row .mc-old-v { text-decoration: line-through; }
.mc-arrow-row .mc-arr   { color: #ccc; }
.mc-arrow-row .mc-new-v { color: #040442; font-weight: 700; }

/* ── Callout ── */
.callout {
  background: white; border: 1.5px solid #1AD598; border-radius: 12px;
  padding: 16px 28px; text-align: center;
  opacity: 0;
  transition: opacity .4s .15s;
}
.callout.show { opacity: 1; }
.co-pills {
  display: flex; gap: 10px; justify-content: center; margin-bottom: 12px; flex-wrap: wrap;
}
.co-pill {
  background: #e8faf3; color: #0a8f60; border-radius: 20px;
  padding: 4px 14px; font-size: .75rem; font-weight: 600;
}
.co-headline {
  font-size: 1.1rem; font-weight: 800; color: #040442; line-height: 1.3;
  margin-bottom: 8px;
}
.co-note {
  font-size: .7rem; color: #bbb; line-height: 1.5;
}
</style>
</head>
<body>

<!-- Spec bar with inline cascade selects -->
<div class="spec-bar">
  <span class="spec-lbl">Model:</span>
  <select class="sb-sel" id="sb-model" onchange="onModelSel(this.value)"></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Framework:</span>
  <select class="sb-sel" id="sb-fw" onchange="onFwSel(this.value)"></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Hardware:</span>
  <select class="sb-sel" id="sb-hw" onchange="onHwSel(this.value)"></select>
</div>

<!-- Selector row: prompt only -->
<div class="sel-row">
  <div class="sel-wrap">
    <select id="prompt-sel" onchange="onPromptChange(this.value)"></select>
  </div>
  <button class="run-btn" id="run-btn" onclick="startRace()">&#9654; Compare</button>
</div>

<!-- Prompt preview -->
<div class="prompt-box" id="prompt-box"></div>

<!-- Response cards -->
<div class="cards-row">
  <div class="card">
    <div class="card-hdr">
      <span class="card-title">Baseline</span>
      <span class="badge" id="done-b" style="display:none">Done</span>
      <span class="card-time" id="time-b"></span>
    </div>
    <div class="card-body" id="text-b"><span class="placeholder">Select a prompt and click Run race</span></div>
    <div class="card-footer" id="foot-b" style="display:none">
      <span>TTFT <strong id="ttft-b">—</strong></span>
      <span>tok/s <strong id="tps-b">—</strong> tok/s</span>
    </div>
  </div>
  <div class="card card-opt">
    <div class="card-hdr">
      <span class="card-title">&#9889; Artemis-optimised</span>
      <span class="badge badge-opt" id="done-a" style="display:none">Done</span>
      <span class="card-time card-time-opt" id="time-a"></span>
    </div>
    <div class="card-body" id="text-a"><span class="placeholder">Select a prompt and click Run race</span></div>
    <div class="card-footer card-footer-opt" id="foot-a" style="display:none">
      <span>TTFT <strong id="ttft-a">—</strong></span>
      <span>tok/s <strong id="tps-a">—</strong> tok/s</span>
    </div>
  </div>
</div>

<!-- Metrics -->
<div class="metrics-row" id="metrics">
  <div class="mc">
    <div class="mc-lbl">Throughput</div>
    <span class="mc-pct" id="m-tps-pct"></span>
    <div class="mc-arrow-row">
      <span class="mc-old-v" id="m-tps-old"></span>
      <span class="mc-arr">→</span>
      <span class="mc-new-v" id="m-tps-new"></span>
    </div>
  </div>
  <div class="mc">
    <div class="mc-lbl">Time to First Token</div>
    <span class="mc-pct" id="m-ttft-pct"></span>
    <div class="mc-arrow-row">
      <span class="mc-old-v" id="m-ttft-old"></span>
      <span class="mc-arr">→</span>
      <span class="mc-new-v" id="m-ttft-new"></span>
    </div>
  </div>
  <div class="mc">
    <div class="mc-lbl">Cost / 1M Tokens</div>
    <span class="mc-pct" id="m-cost-pct"></span>
    <div class="mc-arrow-row">
      <span class="mc-old-v" id="m-cost-old"></span>
      <span class="mc-arr">→</span>
      <span class="mc-new-v" id="m-cost-new"></span>
    </div>
  </div>
</div>

<!-- Callout -->
<div class="callout" id="callout">
  <div class="co-pills">
    <span class="co-pill">✓ Same model</span>
    <span class="co-pill">✓ Same hardware</span>
    <span class="co-pill">✓ Quality intact</span>
  </div>
  <div class="co-headline">No tradeoffs. Just faster, cheaper inference.</div>
  <div class="co-note">Quality validated via semantic similarity ≥ 0.92 (all-MiniLM-L6-v2) across 50 runs at temp=0, seed=42 &nbsp;·&nbsp; Live panel runs at temp=1.0</div>
</div>

<script>
var ALL = __CONFIGS_JSON__;
var curCfg = 0, curPrompt = 0;
var raf = null, t0 = null, bDone = false, aDone = false;

(function init() {
  buildModelSel();
  selectModelByIdx(0);
})();

// ── Spec bar cascade ──────────────────────────────────────────────────────────
function buildModelSel() {
  var ms = document.getElementById('sb-model');
  ms.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg, i) {
    var m = cfg.meta.model;
    if (!seen[m]) { seen[m] = true; addOpt(ms, m, m); }
  });
}

function onModelSel(model) {
  var fs = document.getElementById('sb-fw');
  fs.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg) {
    if (cfg.meta.model === model && !seen[cfg.meta.framework]) {
      seen[cfg.meta.framework] = true;
      addOpt(fs, cfg.meta.framework, cfg.meta.framework);
    }
  });
  onFwSel(fs.value);
}

function onFwSel(fw) {
  var model = document.getElementById('sb-model').value;
  var hs = document.getElementById('sb-hw');
  hs.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg) {
    if (cfg.meta.model === model && cfg.meta.framework === fw && !seen[cfg.meta.hardware]) {
      seen[cfg.meta.hardware] = true;
      addOpt(hs, cfg.meta.hardware, cfg.meta.hardware);
    }
  });
  onHwSel(hs.value);
}

function onHwSel(hw) {
  var model = document.getElementById('sb-model').value;
  var fw    = document.getElementById('sb-fw').value;
  var idx = 0;
  ALL.forEach(function(cfg, i) {
    if (cfg.meta.model === model && cfg.meta.framework === fw && cfg.meta.hardware === hw) idx = i;
  });
  loadCfg(idx);
}

function selectModelByIdx(cfgIdx) {
  var model = ALL[cfgIdx].meta.model;
  document.getElementById('sb-model').value = model;
  onModelSel(model);
  document.getElementById('sb-fw').value = ALL[cfgIdx].meta.framework;
  onFwSel(ALL[cfgIdx].meta.framework);
  document.getElementById('sb-hw').value = ALL[cfgIdx].meta.hardware;
  loadCfg(cfgIdx);
}

function addOpt(sel, val, txt) {
  var o = document.createElement('option'); o.value = val; o.textContent = txt; sel.appendChild(o);
}

// ── Config / prompt loading ───────────────────────────────────────────────────
function loadCfg(idx) {
  curCfg = idx;
  var ps = document.getElementById('prompt-sel');
  ps.innerHTML = '';
  ALL[idx].demo_prompts.forEach(function(p, i) {
    addOpt(ps, i, p.label);
  });
  curPrompt = 0;
  updatePromptBox();
  resetCards();
}

function onPromptChange(v) {
  curPrompt = parseInt(v);
  updatePromptBox();
  resetCards();
}

function updatePromptBox() {
  var p = ALL[curCfg].demo_prompts[curPrompt];
  var txt = p.user || '';
  if (txt.length > 200) txt = txt.slice(0, 200) + '…';
  document.getElementById('prompt-box').textContent = txt;
}

function resetCards() {
  if (raf) { cancelAnimationFrame(raf); raf = null; }
  bDone = false; aDone = false;
  var ph = '<span class="placeholder">Select a prompt and click Compare</span>';
  setHtml('text-b', ph); setHtml('text-a', ph);
  setText('time-b', ''); setText('time-a', '');
  hide('done-b'); hide('done-a'); hide('foot-b'); hide('foot-a');
  document.getElementById('metrics').classList.remove('show');
  document.getElementById('callout').classList.remove('show');
  var btn = document.getElementById('run-btn');
  btn.disabled = false; btn.innerHTML = '&#9654; Compare';
}

function startRace() {
  resetCards();
  var btn = document.getElementById('run-btn');
  btn.disabled = true; btn.textContent = '⏳ Running…';

  var p    = ALL[curCfg].demo_prompts[curPrompt];
  var b    = p.recorded.baseline;
  var a    = p.recorded.optimized;
  var cost = ALL[curCfg].correctness.accuracy.cost_per_1m;

  var bTxt  = strip(b.text || '');
  var aTxt  = strip(a.text || '');
  var bTtft = b.ttft_ms, aTtft = a.ttft_ms;
  var bTps  = b.tps,     aTps  = a.tps;

  // Use recorded P50 total latency when available; compute chars/sec from it
  var bEnd = b.total_ms ? b.total_ms / 1000 : bTtft/1000 + bTxt.length / (bTps * 4.5);
  var aEnd = a.total_ms ? a.total_ms / 1000 : aTtft/1000 + aTxt.length / (aTps * 4.5);
  var bCps = bTxt.length / Math.max(bEnd - bTtft/1000, 0.001);
  var aCps = aTxt.length / Math.max(aEnd - aTtft/1000, 0.001);

  t0 = null;
  function tick(ts) {
    if (!t0) t0 = ts;
    var el = (ts - t0) / 1000;

    if (!bDone) {
      setText('time-b', el.toFixed(1) + 's');
      if (el >= bTtft/1000) {
        var c = Math.min(Math.floor((el - bTtft/1000) * bCps), bTxt.length);
        setHtml('text-b', renderText(bTxt.slice(0, c)) + (el < bEnd ? '<span class="cur"></span>' : ''));
      }
      if (el >= bEnd) {
        bDone = true;
        setHtml('text-b', renderText(bTxt));
        setText('time-b', bEnd.toFixed(1) + 's');
        show('done-b'); setText('ttft-b', bTtft + 'ms'); setText('tps-b', bTps.toFixed(1)); show('foot-b');
      }
    }

    if (!aDone) {
      setText('time-a', el.toFixed(1) + 's');
      if (el >= aTtft/1000) {
        var c = Math.min(Math.floor((el - aTtft/1000) * aCps), aTxt.length);
        setHtml('text-a', renderText(aTxt.slice(0, c)) + (el < aEnd ? '<span class="cur cur-opt"></span>' : ''));
      }
      if (el >= aEnd) {
        aDone = true;
        setHtml('text-a', renderText(aTxt));
        setText('time-a', aEnd.toFixed(1) + 's');
        show('done-a'); setText('ttft-a', aTtft + 'ms'); setText('tps-a', aTps.toFixed(1)); show('foot-a');
      }
    }

    if (!bDone || !aDone) { raf = requestAnimationFrame(tick); }
    else { finish(bTtft, aTtft, bTps, aTps, bEnd, aEnd, cost); }
  }
  raf = requestAnimationFrame(tick);
}

function finish(bTtft,aTtft,bTps,aTps,bEnd,aEnd,cost) {
  var btn = document.getElementById('run-btn');
  btn.disabled = false; btn.textContent = '↺ Compare again';

  var tpsGain  = Math.round((aTps - bTps)  / bTps  * 100);
  var ttftSave = Math.round((bTtft - aTtft) / bTtft * 100);
  var costSave = Math.round((cost.baseline - cost.optimized) / cost.baseline * 100);

  setText('m-tps-pct',  '+' + tpsGain  + '%');
  setText('m-tps-old',  bTps.toFixed(1) + ' tok/s');
  setText('m-tps-new',  aTps.toFixed(1) + ' tok/s');

  setText('m-ttft-pct', '−' + ttftSave + '%');
  setText('m-ttft-old', bTtft + ' ms');
  setText('m-ttft-new', aTtft + ' ms');

  setText('m-cost-pct', '−' + costSave + '%');
  setText('m-cost-old', '$' + cost.baseline.toFixed(2));
  setText('m-cost-new', '$' + cost.optimized.toFixed(2));

  document.getElementById('metrics').classList.add('show');
  setTimeout(function(){ document.getElementById('callout').classList.add('show'); }, 180);
}

function setText(id,v){ document.getElementById(id).textContent = v; }
function setHtml(id,v){ document.getElementById(id).innerHTML  = v; }
function show(id){ document.getElementById(id).style.display = ''; }
function hide(id){ document.getElementById(id).style.display = 'none'; }

function strip(s) {
  return s.replace(/<think>[\s\S]*?<\/think>\n*/g, '').trim();
}
function renderText(s) {
  return s
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>')
    .replace(/\n/g,'<br>');
}
</script>
</body>
</html>"""


def render_race(all_data: list):
    html = _RACE_HTML.replace("__CONFIGS_JSON__", json.dumps(all_data))
    st.components.v1.html(html, height=640, scrolling=False)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    configs = list_configs()
    if not configs:
        st.error("No JSON configs found in `data/`.")
        st.stop()

    all_data = [d for d in (load_config(c["config_id"]) for c in configs) if d]
    render_race(all_data)


main()

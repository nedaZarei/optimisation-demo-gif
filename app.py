import streamlit as st
import json
import base64
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
[data-testid="stAppViewContainer"] {
    background: #020617;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
footer, #MainMenu { display: none !important; }
.block-container {
    padding: 1.5rem 2.5rem 2rem !important;
    max-width: 1060px !important;
    margin: 0 auto !important;
}
[data-testid="stCustomComponentV1"] iframe {
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
_DESIGN_FONTS = Path("/Users/nedazarei/Documents/turintech/artemis design system/fonts")


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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,75..125,100..900;1,75..125,100..900&display=swap" rel="stylesheet">
<style>
/* Hack — embedded for offline use */
@font-face {
  font-family: 'Hack';
  src: url('__HACK_REGULAR__') format('truetype');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Hack';
  src: url('__HACK_BOLD__') format('truetype');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* ── Artemis design tokens (inline subset) ── */
:root {
  --font-sans: 'Archivo', system-ui, -apple-system, Segoe UI, sans-serif;
  --font-mono: 'Hack', ui-monospace, SFMono-Regular, Menlo, monospace;

  /* Brand 1 — violet-indigo */
  --color-brand-400: #7b66ff;
  --color-brand-500: #6350dc;

  /* Slate neutrals */
  --color-slate-50:  #f8fafc;
  --color-slate-100: #f1f5f9;
  --color-slate-200: #e2e8f0;
  --color-slate-300: #cbd5e1;
  --color-slate-400: #94a3b8;
  --color-slate-500: #64748b;
  --color-slate-600: #475569;
  --color-slate-700: #334155;
  --color-slate-800: #1e293b;
  --color-slate-900: #0f172a;
  --color-slate-950: #020617;

  /* Semantic dark */
  --color-background: var(--color-slate-950);
  --color-card:       var(--color-slate-900);
  --color-border:     rgba(255,255,255,0.1);
  --color-primary:    var(--color-brand-400);

  /* Status */
  --color-success:    #4ade80;
  --color-success-fg: #f0fdf4;

  /* Radii */
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-xl: 12px;
  --radius-full: 9999px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-sans);
  background: var(--color-background);
  padding: 2px 2px 16px;
  -webkit-font-smoothing: antialiased;
  color: var(--color-slate-100);
}

/* ── Logo bar ── */
.logo-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.logo-bar img { display: block; }

/* ── Spec bar ── */
.spec-bar {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 0.81rem;
  flex-wrap: wrap;
}
.spec-lbl { color: var(--color-slate-500); margin-right: 2px; }
.spec-sep { color: var(--color-slate-700); margin: 0 10px; font-size: 1rem; }
.sb-sel {
  border: none;
  background: transparent;
  color: var(--color-slate-200);
  font-weight: 700;
  font-size: 0.81rem;
  font-family: var(--font-sans);
  cursor: pointer;
  outline: none;
  padding: 0 18px 0 0;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237b66ff' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 2px center;
  background-size: 10px 6px;
}
.sb-sel:hover { color: var(--color-primary); }
.sb-sel option { background: var(--color-card); color: var(--color-slate-200); }

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
  border: 1px solid rgba(123, 102, 255, 0.3);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  font-family: var(--font-sans);
  color: var(--color-slate-200);
  background: var(--color-card);
  cursor: pointer;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}
.sel-wrap select:focus { border-color: var(--color-primary); }
.sel-wrap select option { background: var(--color-card); }
.sel-wrap::after {
  content: '';
  position: absolute;
  right: 13px;
  top: 50%;
  transform: translateY(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid var(--color-primary);
  pointer-events: none;
}

/* ── Prompt preview ── */
.prompt-box {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-left: 3px solid var(--color-primary);
  border-radius: var(--radius-md);
  padding: 9px 14px;
  font-size: 0.81rem;
  color: var(--color-slate-400);
  line-height: 1.55;
  margin-bottom: 14px;
}

/* ── Run button ── */
.run-btn {
  background: var(--color-primary);
  color: var(--color-slate-50);
  border: none;
  border-radius: var(--radius-md);
  padding: 9px 22px;
  font-size: 0.875rem;
  font-weight: 700;
  font-family: var(--font-sans);
  cursor: pointer;
  white-space: nowrap;
  transition: background .15s;
  letter-spacing: .3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.run-btn:hover:not(:disabled) { background: var(--color-brand-500); }
.run-btn:disabled { background: var(--color-slate-800); color: var(--color-slate-600); cursor: default; }

/* ── Response cards ── */
.cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
.card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 16px 18px;
  min-height: 195px;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.card-opt {
  background: #0b1a11;
  border-color: rgba(74, 222, 128, 0.25);
}
.card-hdr {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-shrink: 0;
}
.card-title {
  font-size: .875rem;
  font-weight: 700;
  color: var(--color-slate-200);
}
.badge {
  font-size: .62rem; font-weight: 800; padding: 2px 10px;
  border-radius: var(--radius-full);
  background: rgba(123, 102, 255, 0.18);
  color: var(--color-primary);
  letter-spacing: .3px;
}
.badge-opt {
  background: rgba(74, 222, 128, 0.15);
  color: var(--color-success);
}
.card-time {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-slate-200);
  letter-spacing: -.5px;
}
.card-time-opt { color: var(--color-success); }
.card-body {
  font-size: .8rem;
  color: var(--color-slate-400);
  line-height: 1.65;
  flex: 1;
  white-space: pre-wrap;
  word-break: break-word;
  min-height: 72px;
}
.card-body strong { color: var(--color-slate-200); }
.placeholder { color: var(--color-slate-700); font-style: italic; }
.code-block {
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-md);
  padding: 10px 13px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  line-height: 1.65;
  overflow-x: auto;
  margin: 6px 0 2px;
  color: #c9d1d9;
  white-space: pre;
  word-break: normal;
}

/* ── Concurrent lanes view ── */
.lanes-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
.lane-col {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 16px 18px;
  min-width: 0;
}
.lane-col-opt {
  background: #0b1a11;
  border-color: rgba(74, 222, 128, 0.25);
}
.lane-col-hdr {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}
.lane {
  display: grid;
  grid-template-columns: 48px 1fr 54px;
  align-items: center;
  gap: 10px;
  margin-bottom: 9px;
}
.lane-lbl {
  font-size: .72rem;
  color: var(--color-slate-500);
  font-family: var(--font-mono);
}
.lane-bar-wrap {
  background: var(--color-slate-800);
  border-radius: var(--radius-full);
  height: 7px;
  overflow: hidden;
}
.lane-fill {
  height: 100%;
  width: 0%;
  border-radius: var(--radius-full);
  background: var(--color-slate-600);
}
.lane-fill-opt { background: var(--color-success); }
.lane-time {
  font-family: var(--font-mono);
  font-size: .72rem;
  color: var(--color-slate-700);
  text-align: right;
  white-space: nowrap;
}
.lane-done     { color: var(--color-slate-300); }
.lane-done-opt { color: var(--color-success); }
.lane-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-top: 1px solid var(--color-border);
  padding-top: 10px;
  margin-top: 4px;
}
.lane-total-opt { border-color: rgba(74,222,128,0.15); }
.lane-total-lbl { font-size: .72rem; color: var(--color-slate-600); }
.lane-total-val {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-slate-500);
  letter-spacing: -.5px;
}
.lane-total-done     { color: var(--color-slate-200); }
.lane-total-done-opt { color: var(--color-success); }
.card-footer {
  display: flex;
  justify-content: space-between;
  font-size: .73rem;
  font-family: var(--font-mono);
  color: var(--color-slate-600);
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.card-footer-opt { border-color: rgba(74, 222, 128, 0.15); }
.card-footer strong { color: var(--color-slate-300); }
.cur {
  display: inline-block; width: 2px; height: 12px;
  background: var(--color-primary);
  margin-left: 1px; vertical-align: middle;
  animation: bl .7s infinite;
}
.cur-opt { background: var(--color-success); }
@keyframes bl { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Metrics ── */
.metrics-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
  opacity: 0;
  transition: opacity .4s;
}
.metrics-row.show { opacity: 1; }
.mc {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 16px 20px;
}
.mc-lbl {
  font-size: .59rem;
  font-weight: 800;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--color-slate-600);
  margin-bottom: 10px;
}
.mc-pct {
  display: block;
  font-family: var(--font-mono);
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--color-success);
  line-height: 1;
  margin-bottom: 8px;
  letter-spacing: -1px;
}
.mc-arrow-row {
  font-size: .78rem;
  font-family: var(--font-mono);
  color: var(--color-slate-600);
  display: flex;
  align-items: center;
  gap: 5px;
}
.mc-arrow-row .mc-old-v { text-decoration: line-through; }
.mc-arrow-row .mc-arr   { color: var(--color-slate-700); }
.mc-arrow-row .mc-new-v { color: var(--color-slate-200); font-weight: 700; }
.mc-note {
  font-size: .72rem;
  color: var(--color-slate-600);
  line-height: 1.4;
  margin-top: 2px;
}
.mc-secondary {
  font-size: .68rem;
  font-family: var(--font-mono);
  color: var(--color-slate-600);
  line-height: 1.5;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--color-border);
}

/* ── Callout ── */
.callout {
  background: #0b1a11;
  border: 1.5px solid rgba(74, 222, 128, 0.35);
  border-radius: var(--radius-xl);
  padding: 16px 28px;
  text-align: center;
  opacity: 0;
  transition: opacity .4s .15s;
}
.callout.show { opacity: 1; }
.co-pills {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.co-pill {
  background: rgba(74, 222, 128, 0.12);
  color: var(--color-success);
  border-radius: var(--radius-full);
  padding: 4px 14px;
  font-size: .75rem;
  font-weight: 600;
}
.co-headline {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--color-slate-100);
  line-height: 1.3;
  margin-bottom: 8px;
}
.co-note {
  font-size: .7rem;
  color: var(--color-slate-600);
  line-height: 1.6;
  white-space: pre-line;
}
</style>
</head>
<body>

<!-- Logo bar -->
<div class="logo-bar">
  <img src="__ARTEMIS_LOGO__" height="28" alt="Artemis">
</div>

<!-- Spec bar with inline cascade selects -->
<div class="spec-bar">
  <span class="spec-lbl">Framework:</span>
  <select class="sb-sel" id="sb-fw" onchange="onFwSel(this.value)"></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Model:</span>
  <select class="sb-sel" id="sb-model" onchange="onModelSel(this.value)"></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Hardware:</span>
  <select class="sb-sel" id="sb-hw" onchange="onHwSel(this.value)"></select>
</div>

<!-- Selector row: prompt only -->
<div class="sel-row">
  <div class="sel-wrap" id="prompt-sel-wrap">
    <select id="prompt-sel" onchange="onPromptChange(this.value)"></select>
  </div>
  <button class="run-btn" id="run-btn" onclick="startRace()">&#9654; Compare</button>
</div>

<!-- Prompt preview / scenario info -->
<div class="prompt-box" id="prompt-box"></div>
<div class="prompt-box" id="scenario-info" style="display:none"></div>

<!-- Response cards (sequential race) -->
<div class="cards-row" id="race-view">
  <div class="card">
    <div class="card-hdr">
      <span class="card-title">Baseline</span>
      <span class="badge" id="done-b" style="display:none">Done</span>
      <span class="card-time" id="time-b"></span>
    </div>
    <div class="card-body" id="text-b"><span class="placeholder">Select a prompt and click Compare</span></div>
    <div class="card-footer" id="foot-b" style="display:none">
      <span>TTFT <strong id="ttft-b">—</strong></span>
      <span id="tps-span-b">tok/s <strong id="tps-b">—</strong></span>
    </div>
  </div>
  <div class="card card-opt">
    <div class="card-hdr">
      <span class="card-title">&#9889; Artemis-optimized</span>
      <span class="badge badge-opt" id="done-a" style="display:none">Done</span>
      <span class="card-time card-time-opt" id="time-a"></span>
    </div>
    <div class="card-body" id="text-a"><span class="placeholder">Select a prompt and click Compare</span></div>
    <div class="card-footer card-footer-opt" id="foot-a" style="display:none">
      <span>TTFT <strong id="ttft-a">—</strong></span>
      <span id="tps-span-a">tok/s <strong id="tps-a">—</strong></span>
    </div>
  </div>
</div>

<!-- Concurrent lanes view -->
<div id="concurrent-view" style="display:none"></div>

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
    <div class="mc-secondary" id="m-ttft-conc" style="display:none"></div>
  </div>
  <div class="mc">
    <div class="mc-lbl">Cost per Token</div>
    <span class="mc-pct" id="m-cost-pct"></span>
    <div class="mc-note" id="m-cost-note"></div>
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
  <div class="co-note" id="co-note"></div>
</div>

<script>
var ALL = __CONFIGS_JSON__;
var curCfg = 0, curPrompt = 0;
var raf = null, t0 = null, bDone = false, aDone = false;

(function init() {
  buildFwSel();
  selectModelByIdx(0);
})();

// ── Spec bar cascade ──────────────────────────────────────────────────────────
function buildFwSel() {
  var fs = document.getElementById('sb-fw');
  fs.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg) {
    var f = cfg.meta.framework;
    if (!seen[f]) { seen[f] = true; addOpt(fs, f, f); }
  });
}

function onFwSel(fw) {
  var ms = document.getElementById('sb-model');
  ms.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg) {
    if (cfg.meta.framework === fw && !seen[cfg.meta.model]) {
      seen[cfg.meta.model] = true;
      addOpt(ms, cfg.meta.model, cfg.meta.model);
    }
  });
  onModelSel(ms.value);
}

function onModelSel(model) {
  var fw = document.getElementById('sb-fw').value;
  var hs = document.getElementById('sb-hw');
  hs.innerHTML = '';
  var seen = {};
  ALL.forEach(function(cfg) {
    if (cfg.meta.framework === fw && cfg.meta.model === model && !seen[cfg.meta.hardware]) {
      seen[cfg.meta.hardware] = true;
      addOpt(hs, cfg.meta.hardware, cfg.meta.hardware);
    }
  });
  onHwSel(hs.value);
}

function onHwSel(hw) {
  var fw    = document.getElementById('sb-fw').value;
  var model = document.getElementById('sb-model').value;
  var idx = 0;
  ALL.forEach(function(cfg, i) {
    if (cfg.meta.framework === fw && cfg.meta.model === model && cfg.meta.hardware === hw) idx = i;
  });
  loadCfg(idx);
}

function selectModelByIdx(cfgIdx) {
  var fw = ALL[cfgIdx].meta.framework;
  document.getElementById('sb-fw').value = fw;
  onFwSel(fw);
  document.getElementById('sb-model').value = ALL[cfgIdx].meta.model;
  onModelSel(ALL[cfgIdx].meta.model);
  document.getElementById('sb-hw').value = ALL[cfgIdx].meta.hardware;
  loadCfg(cfgIdx);
}

function addOpt(sel, val, txt) {
  var o = document.createElement('option'); o.value = val; o.textContent = txt; sel.appendChild(o);
}

// ── Config / prompt loading ───────────────────────────────────────────────────
function loadCfg(idx) {
  curCfg = idx;
  var isConcurrent = !!(ALL[idx].concurrent_demo);

  document.getElementById('race-view').style.display         = isConcurrent ? 'none' : '';
  document.getElementById('concurrent-view').style.display   = isConcurrent ? ''     : 'none';
  document.getElementById('prompt-sel-wrap').style.display   = isConcurrent ? 'none' : '';
  document.getElementById('prompt-box').style.display        = isConcurrent ? 'none' : '';
  document.getElementById('scenario-info').style.display     = isConcurrent ? ''     : 'none';
  document.getElementById('run-btn').innerHTML = isConcurrent ? '&#9654; Run simulation' : '&#9654; Compare';

  if (isConcurrent) {
    var cd = ALL[idx].concurrent_demo;
    document.getElementById('scenario-info').textContent = cd.scenario_label + '  ·  ' + cd.scenario_description;
    renderConcurrentView(cd);
  } else {
    var ps = document.getElementById('prompt-sel');
    ps.innerHTML = '';
    ALL[idx].demo_prompts.forEach(function(p, i) { addOpt(ps, i, p.label); });
    curPrompt = 0;
    updatePromptBox();
  }
  resetCards();
  document.querySelectorAll('#metrics .mc-lbl')[1].textContent = 'Time to First Token';
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
  document.getElementById('metrics').classList.remove('show');
  document.getElementById('callout').classList.remove('show');

  if (ALL[curCfg] && ALL[curCfg].concurrent_demo) {
    resetConcurrentLanes();
    var btn = document.getElementById('run-btn');
    btn.disabled = false; btn.innerHTML = '&#9654; Run simulation';
    return;
  }

  var ph = '<span class="placeholder">Select a prompt and click Compare</span>';
  setHtml('text-b', ph); setHtml('text-a', ph);
  setText('time-b', ''); setText('time-a', '');
  hide('done-b'); hide('done-a'); hide('foot-b'); hide('foot-a');
  show('tps-span-b'); show('tps-span-a');
  var btn = document.getElementById('run-btn');
  btn.disabled = false; btn.innerHTML = '&#9654; Compare';
}

function startRace() {
  if (ALL[curCfg].concurrent_demo) { startConcurrentRace(); return; }
  startSequentialRace();
}

function startSequentialRace() {
  resetCards();
  var btn = document.getElementById('run-btn');
  btn.disabled = true; btn.textContent = '⏳ Running…';

  var p    = ALL[curCfg].demo_prompts[curPrompt];
  var b    = p.recorded.baseline;
  var a    = p.recorded.optimized;

  var bTxt  = strip(b.text || '');
  var aTxt  = strip(a.text || '');
  var bTtft = b.ttft_ms, aTtft = a.ttft_ms;
  var bTps  = b.tps,     aTps  = a.tps;

  var hideFooterTps = !!(ALL[curCfg].bench_serve && ALL[curCfg].bench_serve.tps);

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
        if (hideFooterTps) hide('tps-span-b');
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
        if (hideFooterTps) hide('tps-span-a');
      }
    }

    if (!bDone || !aDone) { raf = requestAnimationFrame(tick); }
    else { finish(bTtft, aTtft, bTps, aTps, bEnd, aEnd); }
  }
  raf = requestAnimationFrame(tick);
}

function finish(bTtft,aTtft,bTps,aTps,bEnd,aEnd) {
  var btn = document.getElementById('run-btn');
  btn.disabled = false;
  btn.textContent = ALL[curCfg].concurrent_demo ? '↺ Run again' : '↺ Compare again';

  var bs = ALL[curCfg].bench_serve;

  // Throughput: use bench_serve.tps (system concurrent) if available, else per-prompt sequential
  var mBTps = (bs && bs.tps && bs.tps.baseline) ? bs.tps.baseline : bTps;
  var mATps = (bs && bs.tps && bs.tps.optimized) ? bs.tps.optimized : aTps;
  var tpsGain  = Math.round((mATps - mBTps) / mBTps * 100);
  var costSave = Math.round((1 - mBTps / mATps) * 100);

  setText('m-tps-pct', '+' + tpsGain + '%');
  setText('m-tps-old', mBTps.toFixed(1) + ' tok/s');
  setText('m-tps-new', mATps.toFixed(1) + ' tok/s');

  setText('m-cost-pct', '−' + costSave + '%');
  setText('m-cost-note', 'throughput-derived · rate-independent');

  // TTFT / latency: use bench_serve if available, else per-prompt sequential
  if (bs && bs.ttft_ms && bs.ttft_ms.baseline && bs.ttft_ms.optimized) {
    var bsTtftSave = Math.round((bs.ttft_ms.baseline - bs.ttft_ms.optimized) / bs.ttft_ms.baseline * 100);
    setText('m-ttft-pct', '−' + bsTtftSave + '%');
    setText('m-ttft-old', bs.ttft_ms.baseline.toLocaleString() + ' ms');
    setText('m-ttft-new', bs.ttft_ms.optimized.toLocaleString() + ' ms');
    document.getElementById('m-ttft-conc').style.display = 'none';
    if (bs.latency_label) document.querySelectorAll('#metrics .mc-lbl')[1].textContent = bs.latency_label;
    var cfg = ALL[curCfg];
    if (cfg.callout_note) {
      setText('co-note', cfg.callout_note);
    } else {
      setText('co-note', cfg.meta.model + ' · ' + cfg.meta.framework + ' · ' + cfg.meta.hardware + '.\nThroughput and TTFT measured under concurrent load (32 req, ABBA design) on vLLM bench serve benchmark.\nQuality validated via semantic similarity ≥ 0.92 · all-MiniLM-L6-v2 · 50 runs per scenario');
    }
  } else {
    var ttftSave = Math.round((bTtft - aTtft) / bTtft * 100);
    setText('m-ttft-pct', '−' + ttftSave + '%');
    setText('m-ttft-old', bTtft + ' ms');
    setText('m-ttft-new', aTtft + ' ms');
    var cfg = ALL[curCfg];
    setText('co-note', cfg.callout_note || 'Quality validated via semantic similarity ≥ 0.92 · all-MiniLM-L6-v2 · 50 runs per scenario');
  }

  document.getElementById('metrics').classList.add('show');
  setTimeout(function(){ document.getElementById('callout').classList.add('show'); }, 180);
}

// ── Concurrent lanes ─────────────────────────────────────────────────────────
function renderConcurrentView(cd) {
  function colHtml(lats, side, isOpt) {
    var cls   = isOpt ? 'lane-col lane-col-opt' : 'lane-col';
    var fill  = isOpt ? 'lane-fill lane-fill-opt' : 'lane-fill';
    var title = isOpt ? '&#9889; Artemis-optimized' : 'Baseline';
    var badge = isOpt ? 'badge badge-opt' : 'badge';
    var h = '<div class="' + cls + '">';
    h += '<div class="lane-col-hdr"><span class="card-title">' + title + '</span>';
    h += '<span class="' + badge + '" id="done-' + side + '" style="display:none">Done</span></div>';
    lats.forEach(function(_, i) {
      h += '<div class="lane">';
      h += '<div class="lane-lbl">Req ' + (i + 1) + '</div>';
      h += '<div class="lane-bar-wrap"><div class="' + fill + '" id="fill-' + side + '-' + i + '"></div></div>';
      h += '<div class="lane-time" id="ltime-' + side + '-' + i + '">—</div>';
      h += '</div>';
    });
    var totCls = isOpt ? 'lane-total lane-total-opt' : 'lane-total';
    h += '<div class="' + totCls + '">';
    h += '<span class="lane-total-lbl">All ' + lats.length + ' done</span>';
    h += '<span class="lane-total-val" id="ltotal-' + side + '">—</span>';
    h += '</div></div>';
    return h;
  }
  document.getElementById('concurrent-view').innerHTML =
    '<div class="lanes-row">' +
    colHtml(cd.baseline_latencies_ms, 'b', false) +
    colHtml(cd.optimized_latencies_ms, 'a', true) +
    '</div>';
}

function resetConcurrentLanes() {
  var cd = ALL[curCfg] && ALL[curCfg].concurrent_demo;
  if (!cd) return;
  cd.baseline_latencies_ms.forEach(function(_, i) {
    var f = document.getElementById('fill-b-' + i);
    var t = document.getElementById('ltime-b-' + i);
    if (f) f.style.width = '0%';
    if (t) { t.textContent = '—'; t.className = 'lane-time'; }
  });
  cd.optimized_latencies_ms.forEach(function(_, j) {
    var f = document.getElementById('fill-a-' + j);
    var t = document.getElementById('ltime-a-' + j);
    if (f) f.style.width = '0%';
    if (t) { t.textContent = '—'; t.className = 'lane-time'; }
  });
  ['b','a'].forEach(function(s) {
    var el = document.getElementById('ltotal-' + s);
    if (el) { el.textContent = '—'; el.className = 'lane-total-val'; }
    hide('done-' + s);
  });
}

function startConcurrentRace() {
  resetCards();
  var btn = document.getElementById('run-btn');
  btn.disabled = true; btn.textContent = '⏳ Running…';

  var cd   = ALL[curCfg].concurrent_demo;
  var bLats = cd.baseline_latencies_ms;
  var aLats = cd.optimized_latencies_ms;
  var spd   = cd.animation_speed || 1;

  var bDoneArr = bLats.map(function() { return false; });
  var aDoneArr = aLats.map(function() { return false; });
  var bMaxSec  = Math.max.apply(null, bLats) / 1000 / spd;
  var aMaxSec  = Math.max.apply(null, aLats) / 1000 / spd;

  t0 = null;
  function tick(ts) {
    if (!t0) t0 = ts;
    var el = (ts - t0) / 1000;

    bLats.forEach(function(lat, i) {
      var dur = lat / 1000 / spd;
      document.getElementById('fill-b-' + i).style.width = Math.min(el / dur, 1) * 100 + '%';
      var tEl = document.getElementById('ltime-b-' + i);
      if (el >= dur && !bDoneArr[i]) {
        bDoneArr[i] = true;
        tEl.textContent = (lat / 1000).toFixed(1) + 's';
        tEl.className = 'lane-time lane-done';
      } else if (!bDoneArr[i]) {
        tEl.textContent = (el * spd).toFixed(1) + 's';
      }
    });

    aLats.forEach(function(lat, j) {
      var dur = lat / 1000 / spd;
      document.getElementById('fill-a-' + j).style.width = Math.min(el / dur, 1) * 100 + '%';
      var tEl = document.getElementById('ltime-a-' + j);
      if (el >= dur && !aDoneArr[j]) {
        aDoneArr[j] = true;
        tEl.textContent = (lat / 1000).toFixed(1) + 's';
        tEl.className = 'lane-time lane-done-opt';
      } else if (!aDoneArr[j]) {
        tEl.textContent = (el * spd).toFixed(1) + 's';
      }
    });

    var bTotEl = document.getElementById('ltotal-b');
    var aTotEl = document.getElementById('ltotal-a');
    var bRealMax = Math.max.apply(null, bLats) / 1000;
    var aRealMax = Math.max.apply(null, aLats) / 1000;

    if (el < bMaxSec) { bTotEl.textContent = (el * spd).toFixed(1) + 's'; }
    else { bTotEl.textContent = bRealMax.toFixed(1) + 's'; bTotEl.className = 'lane-total-val lane-total-done'; }
    if (el < aMaxSec) { aTotEl.textContent = (el * spd).toFixed(1) + 's'; }
    else { aTotEl.textContent = aRealMax.toFixed(1) + 's'; aTotEl.className = 'lane-total-val lane-total-done-opt'; }

    var allB = bDoneArr.every(Boolean);
    var allA = aDoneArr.every(Boolean);
    if (!allB || !allA) {
      raf = requestAnimationFrame(tick);
    } else {
      show('done-b'); show('done-a');
      finish(0, 0, 0, 0, bMaxSec, aMaxSec);
    }
  }
  raf = requestAnimationFrame(tick);
}

function setText(id,v){ document.getElementById(id).textContent = v; }
function setHtml(id,v){ document.getElementById(id).innerHTML  = v; }
function show(id){ document.getElementById(id).style.display = ''; }
function hide(id){ document.getElementById(id).style.display = 'none'; }

function strip(s) {
  return s.replace(/<think>[\s\S]*?<\/think>\n*/g, '').trim();
}
function renderMarkdown(s) {
  return s
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>')
    .replace(/\n/g,'<br>');
}

function renderText(s) {
  var out = '', rest = s;
  while (rest.length > 0) {
    var fenceStart = rest.indexOf('```');
    if (fenceStart === -1) { out += renderMarkdown(rest); break; }
    out += renderMarkdown(rest.slice(0, fenceStart));
    rest = rest.slice(fenceStart + 3);
    var nlIdx = rest.indexOf('\n');
    if (nlIdx === -1) { out += '```' + rest; break; }
    rest = rest.slice(nlIdx + 1);
    var fenceEnd = rest.indexOf('```');
    var code = (fenceEnd === -1 ? rest : rest.slice(0, fenceEnd))
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    out += '<pre class="code-block"><code>' + code + '</code></pre>';
    if (fenceEnd === -1) break;
    rest = rest.slice(fenceEnd + 3);
  }
  return out;
}
</script>
</body>
</html>"""


def render_race(all_data: list):
    logos_dir = Path(__file__).parent / "logos"

    tt_svg = (logos_dir / "TurinTech-light-no Background.svg").read_bytes()
    tt_src = "data:image/svg+xml;base64," + base64.b64encode(tt_svg).decode()

    artemis_png = (logos_dir / "artemis-logo-wordmark.png").read_bytes()
    artemis_src = "data:image/png;base64," + base64.b64encode(artemis_png).decode()

    hack_regular_src = ""
    hack_bold_src = ""
    if _DESIGN_FONTS.exists():
        hack_r = _DESIGN_FONTS / "Hack-Regular.ttf"
        hack_b = _DESIGN_FONTS / "Hack-Bold.ttf"
        if hack_r.exists():
            hack_regular_src = "data:font/ttf;base64," + base64.b64encode(hack_r.read_bytes()).decode()
        if hack_b.exists():
            hack_bold_src = "data:font/ttf;base64," + base64.b64encode(hack_b.read_bytes()).decode()

    html = (
        _RACE_HTML
        .replace("__CONFIGS_JSON__", json.dumps(all_data))
        .replace("__TURINTECH_LOGO__", tt_src)
        .replace("__ARTEMIS_LOGO__", artemis_src)
        .replace("__HACK_REGULAR__", hack_regular_src)
        .replace("__HACK_BOLD__", hack_bold_src)
    )
    st.components.v1.html(html, height=920, scrolling=False)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    configs = list_configs()
    if not configs:
        st.error("No JSON configs found in `data/`.")
        st.stop()

    all_data = [d for d in (load_config(c["config_id"]) for c in configs) if d]
    render_race(all_data)


main()

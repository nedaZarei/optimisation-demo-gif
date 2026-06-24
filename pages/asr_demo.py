import json
import base64
import streamlit as st
from pathlib import Path

_ROOT         = Path(__file__).parent.parent
_DATA_DIR     = _ROOT / "data" / "asr"
_LOGOS_DIR    = _ROOT / "logos"
_DESIGN_FONTS = Path("/Users/nedazarei/Documents/turintech/artemis design system/fonts")
_ASR_CFG_ID   = "whisper-large-v3__rtx3090__faster-whisper"


def _load_cfg():
    p = _DATA_DIR / f"{_ASR_CFG_ID}.json"
    return json.loads(p.read_text()) if p.exists() else None


_ASR_HTML = r"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,75..125,100..900;1,75..125,100..900&display=swap" rel="stylesheet">
<style>
@font-face { font-family:'Hack'; src:url('__HACK_REGULAR__') format('truetype'); font-weight:400; font-display:swap; }
@font-face { font-family:'Hack'; src:url('__HACK_BOLD__')    format('truetype'); font-weight:700; font-display:swap; }
:root {
  --font-sans:'Archivo',system-ui,-apple-system,Segoe UI,sans-serif;
  --font-mono:'Hack',ui-monospace,SFMono-Regular,Menlo,monospace;
  --color-brand-400:#7b66ff; --color-brand-500:#6350dc;
  --color-slate-100:#f1f5f9; --color-slate-200:#e2e8f0; --color-slate-300:#cbd5e1;
  --color-slate-400:#94a3b8; --color-slate-500:#64748b; --color-slate-600:#475569;
  --color-slate-700:#334155; --color-slate-800:#1e293b; --color-slate-900:#0f172a;
  --color-slate-950:#020617;
  --color-bg:var(--color-slate-950); --color-card:var(--color-slate-900);
  --color-border:rgba(255,255,255,0.1); --color-primary:var(--color-brand-400);
  --color-success:#4ade80;
  --r-md:8px; --r-lg:10px; --r-xl:12px; --r-full:9999px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:var(--font-sans);background:var(--color-bg);padding:2px 2px 16px;-webkit-font-smoothing:antialiased;color:var(--color-slate-100);}

.logo-bar{display:flex;align-items:center;margin-bottom:16px;}
.logo-bar img{display:block;}

/* ── Spec bar ── */
.spec-bar{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--r-lg);padding:10px 20px;display:flex;align-items:center;gap:6px;margin-bottom:10px;font-size:0.81rem;flex-wrap:wrap;}
.spec-lbl{color:var(--color-slate-500);margin-right:2px;}
.spec-sep{color:var(--color-slate-700);margin:0 10px;}
.sb-sel{border:none;background:transparent;color:var(--color-slate-200);font-weight:700;font-size:0.81rem;font-family:var(--font-sans);cursor:pointer;outline:none;padding:0 18px 0 0;-webkit-appearance:none;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237b66ff' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 2px center;background-size:10px 6px;}
.sb-sel:hover{color:var(--color-primary);}
.sb-sel option{background:var(--color-card);}

/* ── Scenario strip ── */
.scenario-strip{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-size:0.75rem;color:var(--color-slate-500);flex-wrap:wrap;}
.chip{background:rgba(123,102,255,0.12);color:var(--color-brand-400);border:1px solid rgba(123,102,255,0.2);border-radius:var(--r-full);padding:2px 10px;font-size:0.70rem;font-weight:600;letter-spacing:0.04em;}

/* ── Start button ── */
.start-btn{display:block;width:100%;padding:12px;background:var(--color-brand-400);color:#fff;font-family:var(--font-sans);font-size:0.875rem;font-weight:700;border:none;border-radius:var(--r-lg);cursor:pointer;letter-spacing:0.03em;transition:background 0.2s;margin-bottom:14px;}
.start-btn:hover:not(:disabled){background:var(--color-brand-500);}
.start-btn:disabled{opacity:0.45;cursor:not-allowed;}

/* ── Race columns ── */
.race-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}

.stream-col{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--r-xl);padding:16px 18px;}
.stream-col-opt{background:#0b1a11;border-color:rgba(74,222,128,0.25);}

/* column header */
.col-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.07);}
.stream-col-opt .col-hdr{border-color:rgba(74,222,128,0.1);}
.col-title{font-size:0.70rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--color-slate-400);}
.col-tally{font-family:var(--font-mono);font-size:0.72rem;color:var(--color-slate-500);}
.col-tally strong{color:var(--color-slate-200);}
.col-elapsed{font-family:var(--font-mono);font-size:1.05rem;font-weight:700;color:var(--color-slate-500);letter-spacing:-0.5px;}
.col-elapsed-opt{color:var(--color-success);}

/* stream lanes */
.stream-lane{margin-bottom:10px;}
.stream-lane:last-child{margin-bottom:0;}
.lane-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.lane-label{font-size:0.68rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--color-slate-600);}
.lane-files{font-family:var(--font-mono);font-size:0.68rem;color:var(--color-slate-600);}
.lane-files strong{color:var(--color-slate-300);}
.lane-filename{font-family:var(--font-mono);font-size:0.70rem;color:var(--color-slate-600);margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;height:14px;}
.lane-filename.active{color:var(--color-slate-300);}
.lane-bar-wrap{background:var(--color-slate-800);border-radius:var(--r-full);height:5px;overflow:hidden;}
.lane-bar-fill{height:100%;border-radius:var(--r-full);width:0%;background:var(--color-slate-600);transition:width 0.08s linear;}
.lane-bar-fill-opt{background:var(--color-success);}
.lane-done-row{display:flex;align-items:center;gap:6px;margin-top:2px;font-size:0.68rem;font-family:var(--font-mono);}
.lane-done-tick{color:var(--color-success);font-weight:700;}
.lane-done-time{color:var(--color-slate-600);}

/* column footer */
.col-footer{display:flex;justify-content:space-between;align-items:center;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.07);font-size:0.72rem;}
.stream-col-opt .col-footer{border-color:rgba(74,222,128,0.1);}
.footer-throughput{font-family:var(--font-mono);font-size:0.70rem;color:var(--color-slate-500);}
.footer-throughput strong{color:var(--color-slate-300);}
.footer-badge{font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:var(--r-full);letter-spacing:0.04em;}
.badge-idle      {background:rgba(100,116,139,0.15);color:var(--color-slate-500);}
.badge-running   {background:rgba(123,102,255,0.18);color:var(--color-brand-400);}
.badge-done      {background:rgba(74,222,128,0.15); color:var(--color-success);}

/* ── Results panels ── */
#results-panel{display:none;}

.scale-section{margin-bottom:12px;}
.section-label{font-size:0.65rem;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;color:var(--color-slate-500);margin-bottom:8px;text-align:center;}
.scale-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}
.scale-card{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--r-lg);padding:14px 16px;text-align:center;}
.scale-lbl{font-size:0.62rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:var(--color-slate-500);margin-bottom:6px;line-height:1.4;}
.scale-val{font-family:var(--font-mono);font-size:1.5rem;font-weight:700;color:var(--color-success);line-height:1;margin-bottom:4px;}
.scale-arrow{display:flex;align-items:center;justify-content:center;gap:5px;font-family:var(--font-mono);font-size:0.68rem;color:var(--color-slate-600);}
.scale-arrow .old{text-decoration:line-through;}
.scale-arrow .new{color:var(--color-slate-200);font-weight:700;}
.scale-sub{font-size:0.66rem;color:var(--color-slate-500);margin-top:3px;}

/* transcript */
#transcript-panel{background:var(--color-card);border:1px solid rgba(74,222,128,0.2);border-radius:var(--r-xl);padding:18px 20px;margin-bottom:12px;}
.transcript-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(74,222,128,0.10);color:var(--color-success);border:1px solid rgba(74,222,128,0.25);border-radius:var(--r-full);padding:4px 14px;font-size:0.68rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:12px;}
.transcript-subhead{font-size:0.72rem;color:var(--color-slate-500);margin-bottom:10px;font-style:italic;}
.transcript-text{font-size:0.81rem;line-height:1.75;color:var(--color-slate-300);max-height:170px;overflow-y:auto;padding-right:6px;white-space:pre-wrap;}
.transcript-text::-webkit-scrollbar{width:4px;}
.transcript-text::-webkit-scrollbar-thumb{background:var(--color-slate-700);border-radius:4px;}

/* callout */
#callout{background:rgba(123,102,255,0.06);border:1px solid rgba(123,102,255,0.18);border-radius:var(--r-lg);padding:14px 20px;font-size:0.75rem;color:var(--color-slate-400);line-height:1.65;text-align:center;}
/* cross-hardware */
#cross-hw{margin-top:12px;}
.xhw-head{font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--color-slate-600);margin-bottom:8px;text-align:center;}
.xhw-cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.xhw-card{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--r-lg);padding:14px 16px;}
.xhw-hw-name{font-size:0.82rem;font-weight:700;color:var(--color-slate-200);margin-bottom:2px;}
.xhw-hw-sub{font-size:0.68rem;color:var(--color-slate-500);font-family:var(--font-mono);margin-bottom:10px;}
.xhw-clip{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-top:1px solid rgba(255,255,255,0.05);}
.xhw-clip-lbl{font-size:0.72rem;color:var(--color-slate-400);}
.xhw-clip-val{font-size:1.05rem;font-weight:800;font-family:var(--font-mono);color:var(--color-success);}

/* view toggle */
.view-toggle{display:flex;gap:8px;margin-bottom:12px;}
.vt-btn{flex:1;padding:9px 12px;background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--r-lg);color:var(--color-slate-400);font-family:var(--font-sans);font-size:0.76rem;font-weight:700;cursor:pointer;transition:all 0.15s;}
.vt-btn:hover{color:var(--color-slate-200);}
.vt-btn.vt-active{background:rgba(123,102,255,0.12);border-color:rgba(123,102,255,0.3);color:var(--color-brand-400);}
.clip-select-wrap{display:flex;align-items:center;gap:6px;margin-bottom:12px;font-size:0.81rem;}

/* transcript race */
.ttext{font-size:0.78rem;line-height:1.7;color:var(--color-slate-300);height:230px;overflow-y:auto;padding-right:6px;white-space:pre-wrap;}
.ttext::-webkit-scrollbar{width:4px;}
.ttext::-webkit-scrollbar-thumb{background:var(--color-slate-700);border-radius:4px;}
.ttext-placeholder{color:var(--color-slate-600);font-style:italic;}
.tcol-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.07);}
.stream-col-opt .tcol-hdr{border-color:rgba(74,222,128,0.1);}
</style>
</head>
<body>

<div class="logo-bar">
  <img src="__ARTEMIS_LOGO__" height="28" alt="Artemis">
</div>

<div class="spec-bar">
  <span class="spec-lbl">Framework</span>
  <select class="sb-sel"><option>faster-whisper</option></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Model</span>
  <select class="sb-sel"><option>whisper-large-v3</option></select>
  <span class="spec-sep">·</span>
  <span class="spec-lbl">Hardware</span>
  <select class="sb-sel"><option>NVIDIA RTX 3090</option></select>
</div>

<div class="scenario-strip">
  <span class="chip" id="chip-scenario"></span>
  <span class="chip">int8_float16 · beam=5 · batch=32</span>
  <span class="chip">faster-whisper 1.2.1</span>
</div>

<div class="view-toggle">
  <button class="vt-btn vt-active" id="vt-concurrent" onclick="setMode('concurrent')">4-stream concurrent</button>
  <button class="vt-btn" id="vt-transcript" onclick="setMode('transcript')">Live transcription</button>
</div>

<div class="clip-select-wrap" id="clip-select-wrap" style="display:none">
  <span class="spec-lbl">Clip</span>
  <select class="sb-sel" id="clip-sel" onchange="onClipChange(this.value)"></select>
</div>

<button class="start-btn" id="start-btn" onclick="startRace()">&#9654; Run benchmark</button>

<div id="concurrent-view">
<div class="race-row">
  <!-- Stock -->
  <div class="stream-col" id="col-b">
    <div class="col-hdr">
      <span class="col-title">Stock</span>
      <div style="display:flex;gap:14px;align-items:baseline;">
        <span class="col-tally" id="tally-b"><strong>0</strong>/12 files</span>
        <span class="col-elapsed" id="elapsed-b">0.00s</span>
      </div>
    </div>
    <div id="lanes-b"></div>
    <div class="col-footer">
      <span class="footer-throughput" id="thr-b">—</span>
      <span class="footer-badge badge-idle" id="badge-b">Idle</span>
    </div>
  </div>
  <!-- Optimized -->
  <div class="stream-col stream-col-opt" id="col-o">
    <div class="col-hdr">
      <span class="col-title">&#9889; Optimized</span>
      <div style="display:flex;gap:14px;align-items:baseline;">
        <span class="col-tally" id="tally-o"><strong>0</strong>/12 files</span>
        <span class="col-elapsed col-elapsed-opt" id="elapsed-o">0.00s</span>
      </div>
    </div>
    <div id="lanes-o"></div>
    <div class="col-footer">
      <span class="footer-throughput" id="thr-o">—</span>
      <span class="footer-badge badge-idle" id="badge-o">Idle</span>
    </div>
  </div>
</div>
</div>

<div id="transcript-view" style="display:none">
<div class="race-row">
  <!-- Stock -->
  <div class="stream-col" id="tcol-b">
    <div class="tcol-hdr">
      <span class="col-title">Stock</span>
      <span class="footer-badge badge-idle" id="tbadge-b">Idle</span>
    </div>
    <div class="ttext" id="ttext-b"><span class="ttext-placeholder">Awaiting transcription…</span></div>
    <div class="col-footer">
      <span class="footer-throughput" id="tfoot-b">—</span>
    </div>
  </div>
  <!-- Optimized -->
  <div class="stream-col stream-col-opt" id="tcol-o">
    <div class="tcol-hdr">
      <span class="col-title">&#9889; Optimized</span>
      <span class="footer-badge badge-idle" id="tbadge-o">Idle</span>
    </div>
    <div class="ttext" id="ttext-o"><span class="ttext-placeholder">Awaiting transcription…</span></div>
    <div class="col-footer">
      <span class="footer-throughput" id="tfoot-o">—</span>
    </div>
  </div>
</div>
</div>

<!-- Results (hidden until done) -->
<div id="results-panel">
  <div id="concurrent-results">
  <div class="scale-section">
    <div class="section-label">What this means at scale</div>
    <div class="scale-cards">
      <div class="scale-card">
        <div class="scale-lbl">Throughput improvement<br>(4-stream concurrent)</div>
        <div class="scale-val" id="s-pct">—</div>
        <div class="scale-arrow">
          <span class="old" id="s-old">—</span><span>→</span><span class="new" id="s-new">—</span>
        </div>
        <div class="scale-sub">files / hour</div>
      </div>
      <div class="scale-card">
        <div class="scale-lbl">GPU hours to process<br><span id="s-ref">1,000</span>h of audio</div>
        <div class="scale-val" id="s-saved">—</div>
        <div class="scale-sub" id="s-saved-sub">hours saved</div>
      </div>
      <div class="scale-card">
        <div class="scale-lbl">Accuracy</div>
        <div class="scale-val">6/6</div>
        <div class="scale-sub">noise conditions pass</div>
      </div>
    </div>
  </div>

  <div id="transcript-panel">
    <div class="transcript-badge">&#10003; Both produce identical output &nbsp;&middot;&nbsp; WER delta &asymp; 0%</div>
    <div class="transcript-subhead">Sample transcript · Clean long-form · 5 min studio recording</div>
    <div class="transcript-text" id="transcript-text"></div>
  </div>
  </div>

  <div id="transcript-results" style="display:none">
    <div class="transcript-badge">&#10003; Same transcript text &nbsp;&middot;&nbsp; WER delta &asymp; 0%</div>
    <div class="scale-cards" style="grid-template-columns:repeat(2,1fr);margin-top:10px;">
      <div class="scale-card">
        <div class="scale-lbl">Latency<br>(single request)</div>
        <div class="scale-val" id="tr-pct">—</div>
        <div class="scale-arrow">
          <span class="old" id="tr-old">—</span><span>→</span><span class="new" id="tr-new">—</span>
        </div>
        <div class="scale-sub">ms</div>
      </div>
      <div class="scale-card">
        <div class="scale-lbl">Real-Time Factor</div>
        <div class="scale-val" id="tr-rtf-pct">—</div>
        <div class="scale-arrow">
          <span class="old" id="tr-rtf-old">—</span><span>→</span><span class="new" id="tr-rtf-new">—</span>
        </div>
        <div class="scale-sub">lower is faster</div>
      </div>
    </div>
  </div>

  <div id="callout"></div>
  <div id="cross-hw" style="display:none">
    <div class="xhw-head">Cross-hardware · same optimization codebase</div>
    <div class="xhw-cards" id="xhw-cards"></div>
  </div>
</div>

<script>
var CFG = __CONFIG_JSON__;
var cd  = CFG.concurrent_demo;
var ANIM_MS = 9000;
var running = false, animId = null;
var curMode = 'concurrent';
var curClip = 0;

// ── Compute animation params ──────────────────────────────────────────────────
var rtfB = cd.baseline.rtf_per_stream;   // 0.0096
var rtfO = cd.optimized.rtf_per_stream;  // 0.0073
var nStreams = cd.num_streams;            // 4
var nFiles   = cd.files_per_stream;      // 3
var fileDur  = cd.file_duration_s;       // 300s

var perFileRealB  = fileDur * rtfB * 1000;           // ms per file baseline
var perFileRealO  = fileDur * rtfO * 1000;           // ms per file optimized
var totalRealB    = nFiles * perFileRealB;            // total baseline ms
var totalRealO    = nFiles * perFileRealO;            // total optimized ms
var scale         = ANIM_MS / totalRealB;
var perFileAnimB  = perFileRealB * scale;
var perFileAnimO  = perFileRealO * scale;
var totalAnimB    = ANIM_MS;
var totalAnimO    = totalRealO * scale;

// ── Scenario chip ─────────────────────────────────────────────────────────────
function updateScenarioChip() {
  if (curMode === 'concurrent') {
    document.getElementById('chip-scenario').textContent =
      nStreams + ' parallel streams · ' + nFiles + ' files each · ' +
      Math.floor(fileDur/60) + '-min audio';
  } else {
    var clip = CFG.demo_clips[curClip];
    document.getElementById('chip-scenario').textContent = clip.label + ' · ' + clip.description;
  }
}
updateScenarioChip();

// ── View / clip selection ──────────────────────────────────────────────────────
function setMode(mode) {
  if (running) return;
  curMode = mode;
  document.getElementById('vt-concurrent').classList.toggle('vt-active', mode === 'concurrent');
  document.getElementById('vt-transcript').classList.toggle('vt-active', mode === 'transcript');
  document.getElementById('concurrent-view').style.display = mode === 'concurrent' ? '' : 'none';
  document.getElementById('transcript-view').style.display = mode === 'transcript' ? '' : 'none';
  document.getElementById('clip-select-wrap').style.display = mode === 'transcript' ? '' : 'none';
  updateScenarioChip();
  resetUI();
}
function onClipChange(v) {
  curClip = parseInt(v);
  updateScenarioChip();
  resetUI();
}
function initClipSel() {
  var sel = document.getElementById('clip-sel');
  sel.innerHTML = '';
  CFG.demo_clips.forEach(function(c, i) {
    var o = document.createElement('option');
    o.value = i; o.textContent = c.label + ' · ' + c.description;
    sel.appendChild(o);
  });
}

// ── Build lane rows ───────────────────────────────────────────────────────────
function buildLanes(containerId, isOpt) {
  var el = document.getElementById(containerId);
  el.innerHTML = '';
  var fillCls = isOpt ? 'lane-bar-fill lane-bar-fill-opt' : 'lane-bar-fill';
  for (var s = 0; s < nStreams; s++) {
    var div = document.createElement('div');
    div.className = 'stream-lane';
    div.innerHTML =
      '<div class="lane-hdr">' +
        '<span class="lane-label">Stream ' + (s+1) + '</span>' +
        '<span class="lane-files" id="' + containerId + '-fc-' + s + '"><strong>0</strong>/' + nFiles + ' files</span>' +
      '</div>' +
      '<div class="lane-filename" id="' + containerId + '-fn-' + s + '">—</div>' +
      '<div class="lane-bar-wrap">' +
        '<div class="' + fillCls + '" id="' + containerId + '-bar-' + s + '"></div>' +
      '</div>';
    el.appendChild(div);
  }
}

// ── Update one side during animation ─────────────────────────────────────────
function updateSide(cid, elapsed, perFileAnim, isOpt) {
  var totalDone = 0;
  var realPerFile = (isOpt ? perFileRealO : perFileRealB) / 1000; // seconds

  for (var s = 0; s < nStreams; s++) {
    var files  = cd.stream_files[s];
    var barEl  = document.getElementById(cid + '-bar-' + s);
    var fnEl   = document.getElementById(cid + '-fn-' + s);
    var fcEl   = document.getElementById(cid + '-fc-' + s);

    // Which file in this stream are we on?
    var fileIdx = Math.min(Math.floor(elapsed / perFileAnim), nFiles - 1);
    var posInFile = elapsed - fileIdx * perFileAnim;
    var pct = Math.min(posInFile / perFileAnim * 100, 100);

    // Completed files for this stream
    var done = Math.floor(elapsed / perFileAnim);
    if (elapsed >= nFiles * perFileAnim) done = nFiles;
    totalDone += done;

    fcEl.innerHTML = '<strong>' + done + '</strong>/' + nFiles + ' files';

    if (done >= nFiles) {
      barEl.style.width = '100%';
      fnEl.textContent  = '✓ All done';
      fnEl.className    = 'lane-filename active';
    } else {
      barEl.style.width = pct + '%';
      fnEl.textContent  = files[fileIdx] || '—';
      fnEl.className    = done > 0 || pct > 0 ? 'lane-filename active' : 'lane-filename';
    }
  }

  // Tally
  var tallyEl = document.getElementById('tally-' + (isOpt ? 'o' : 'b'));
  var totalFiles = nStreams * nFiles;
  tallyEl.innerHTML = '<strong>' + totalDone + '</strong>/' + totalFiles + ' files';

  // Elapsed
  var realElapsed = Math.min(elapsed / scale, isOpt ? totalRealO : totalRealB) / 1000;
  document.getElementById('elapsed-' + (isOpt ? 'o' : 'b')).textContent =
    realElapsed.toFixed(2) + 's';

  // Throughput footer (files/hour real-time estimate)
  var thrEl = document.getElementById('thr-' + (isOpt ? 'o' : 'b'));
  if (totalDone > 0 && realElapsed > 0) {
    var filesPerHr = Math.round(totalDone / realElapsed * 3600);
    thrEl.innerHTML = '<strong>' + filesPerHr.toLocaleString() + '</strong> files/hr (live)';
  }
}

// ── Race ──────────────────────────────────────────────────────────────────────
function startRace() {
  if (running) return;
  if (curMode === 'transcript') { startTranscriptRace(); return; }
  startConcurrentRace();
}
function startConcurrentRace() {
  if (running) return;
  running = true;

  document.getElementById('start-btn').disabled = true;
  document.getElementById('results-panel').style.display = 'none';

  // Reset displays
  ['b','o'].forEach(function(s) {
    document.getElementById('badge-' + s).className = 'footer-badge badge-running';
    document.getElementById('badge-' + s).textContent = 'Running…';
    document.getElementById('thr-' + s).innerHTML = '—';
  });

  var t0 = performance.now();
  var bDone = false, oDone = false;

  function tick() {
    var elapsed = performance.now() - t0;

    if (!bDone) updateSide('lanes-b', elapsed, perFileAnimB, false);
    if (!oDone) updateSide('lanes-o', elapsed, perFileAnimO, true);

    if (!oDone && elapsed >= totalAnimO) {
      oDone = true;
      updateSide('lanes-o', totalAnimO, perFileAnimO, true);
      document.getElementById('elapsed-o').textContent = (totalRealO/1000).toFixed(2) + 's';
      document.getElementById('badge-o').className = 'footer-badge badge-done';
      document.getElementById('badge-o').textContent = '✓ Done';
      document.getElementById('thr-o').innerHTML =
        '<strong>' + cd.optimized.files_per_hour.toLocaleString() + '</strong> files/hr';
    }
    if (!bDone && elapsed >= totalAnimB) {
      bDone = true;
      updateSide('lanes-b', totalAnimB, perFileAnimB, false);
      document.getElementById('elapsed-b').textContent = (totalRealB/1000).toFixed(2) + 's';
      document.getElementById('badge-b').className = 'footer-badge badge-done';
      document.getElementById('badge-b').textContent = '✓ Done';
      document.getElementById('thr-b').innerHTML =
        '<strong>' + cd.baseline.files_per_hour.toLocaleString() + '</strong> files/hr';
    }

    if (bDone && oDone) {
      showResults();
      return;
    }
    animId = requestAnimationFrame(tick);
  }
  animId = requestAnimationFrame(tick);
}

// ── Show results ──────────────────────────────────────────────────────────────
function showResults() {
  running = false;
  document.getElementById('start-btn').disabled    = false;
  document.getElementById('start-btn').textContent = '↺ Run again';

  // Scale stats
  var fphB  = cd.baseline.files_per_hour;    // 5000
  var fphO  = cd.optimized.files_per_hour;   // 6575
  var pct   = cd.improvement_pct;            // 31.5
  var ref   = cd.scale_reference_audio_hours; // 1000

  // ref audio-hours → how many 5-min files? ref*60/fileDur
  var refFiles = ref * 60 * 60 / fileDur;    // 1000*3600/300 = 12000 files
  var gpuHrsB  = (refFiles / fphB).toFixed(1);  // 2.4h
  var gpuHrsO  = (refFiles / fphO).toFixed(1);  // 1.8h
  var saved    = ((refFiles / fphB) - (refFiles / fphO)).toFixed(1);

  document.getElementById('s-ref').textContent    = ref.toLocaleString() + 'h';
  document.getElementById('s-pct').textContent    = '+' + pct + '%';
  document.getElementById('s-old').textContent    = fphB.toLocaleString() + '/hr';
  document.getElementById('s-new').textContent    = fphO.toLocaleString() + '/hr';
  document.getElementById('s-saved').textContent  = '−' + saved + 'h';
  document.getElementById('s-saved-sub').textContent = gpuHrsB + 'h → ' + gpuHrsO + 'h GPU time';

  // Transcript
  var clip = CFG.demo_clips[0];
  document.getElementById('transcript-text').textContent = clip.transcript;

  // Callout
  document.getElementById('callout').innerHTML =
    CFG.callout_note.replace(/\n/g, '<br>');

  renderCrossHw();

  document.getElementById('concurrent-results').style.display = '';
  document.getElementById('transcript-results').style.display = 'none';
  document.getElementById('results-panel').style.display = 'block';
}

function renderCrossHw() {
  if (CFG.cross_hardware && CFG.cross_hardware.length) {
    var xhCards = document.getElementById('xhw-cards');
    xhCards.innerHTML = '';
    CFG.cross_hardware.forEach(function(hw) {
      var h = '<div class="xhw-card">';
      h += '<div class="xhw-hw-name">' + hw.hardware + '</div>';
      h += '<div class="xhw-hw-sub">' + hw.compute_type + ' · ' + hw.hardware_class + '</div>';
      hw.clips.forEach(function(c) {
        h += '<div class="xhw-clip"><span class="xhw-clip-lbl">' + c.label + '</span>';
        h += '<span class="xhw-clip-val">−' + c.improvement_pct.toFixed(1) + '%</span></div>';
      });
      h += '</div>';
      xhCards.innerHTML += h;
    });
    document.getElementById('cross-hw').style.display = 'block';
  }
}

// ── Live transcription race ────────────────────────────────────────────────────
function startTranscriptRace() {
  if (running) return;
  running = true;
  document.getElementById('start-btn').disabled = true;
  document.getElementById('results-panel').style.display = 'none';

  var clip = CFG.demo_clips[curClip];
  var bMs = clip.baseline.latency_ms, oMs = clip.optimized.latency_ms;
  var TARGET = 8000; // ms, visual pacing only
  var animB = TARGET;
  var animO = TARGET * (oMs / bMs);
  var text = clip.transcript;

  ['b','o'].forEach(function(s) {
    document.getElementById('tbadge-' + s).className = 'footer-badge badge-running';
    document.getElementById('tbadge-' + s).textContent = 'Transcribing…';
    document.getElementById('ttext-' + s).textContent = '';
    document.getElementById('tfoot-' + s).innerHTML = '—';
  });

  var t0 = performance.now();
  var bDone = false, oDone = false;

  function tick() {
    var elapsed = performance.now() - t0;

    if (!bDone) {
      var fracB = Math.min(elapsed / animB, 1);
      document.getElementById('ttext-b').textContent = text.slice(0, Math.floor(text.length * fracB));
      if (fracB >= 1) {
        bDone = true;
        document.getElementById('ttext-b').textContent = text;
        document.getElementById('tbadge-b').className = 'footer-badge badge-done';
        document.getElementById('tbadge-b').textContent = '✓ Done';
        document.getElementById('tfoot-b').innerHTML =
          '<strong>' + bMs.toLocaleString() + ' ms</strong> · RTF ' + clip.baseline.rtf.toFixed(4);
      }
    }
    if (!oDone) {
      var fracO = Math.min(elapsed / animO, 1);
      document.getElementById('ttext-o').textContent = text.slice(0, Math.floor(text.length * fracO));
      if (fracO >= 1) {
        oDone = true;
        document.getElementById('ttext-o').textContent = text;
        document.getElementById('tbadge-o').className = 'footer-badge badge-done';
        document.getElementById('tbadge-o').textContent = '✓ Done';
        document.getElementById('tfoot-o').innerHTML =
          '<strong>' + oMs.toLocaleString() + ' ms</strong> · RTF ' + clip.optimized.rtf.toFixed(4);
      }
    }

    if (bDone && oDone) {
      showTranscriptResults(clip);
      return;
    }
    animId = requestAnimationFrame(tick);
  }
  animId = requestAnimationFrame(tick);
}

function showTranscriptResults(clip) {
  running = false;
  document.getElementById('start-btn').disabled    = false;
  document.getElementById('start-btn').textContent = '↺ Run again';

  var bMs = clip.baseline.latency_ms, oMs = clip.optimized.latency_ms;
  var pct = Math.round((bMs - oMs) / bMs * 100);
  document.getElementById('tr-pct').textContent = '−' + pct + '%';
  document.getElementById('tr-old').textContent = bMs.toLocaleString() + ' ms';
  document.getElementById('tr-new').textContent = oMs.toLocaleString() + ' ms';

  var rtfB = clip.baseline.rtf, rtfO = clip.optimized.rtf;
  var rtfPct = Math.round((rtfB - rtfO) / rtfB * 100);
  document.getElementById('tr-rtf-pct').textContent = '−' + rtfPct + '%';
  document.getElementById('tr-rtf-old').textContent = rtfB.toFixed(4);
  document.getElementById('tr-rtf-new').textContent = rtfO.toFixed(4);

  document.getElementById('callout').innerHTML =
    CFG.callout_note.replace(/\n/g, '<br>');

  renderCrossHw();

  document.getElementById('concurrent-results').style.display = 'none';
  document.getElementById('transcript-results').style.display = 'block';
  document.getElementById('results-panel').style.display = 'block';
}

// ── Reset ─────────────────────────────────────────────────────────────────────
function resetUI() {
  if (animId) cancelAnimationFrame(animId);
  running = false;
  buildLanes('lanes-b', false);
  buildLanes('lanes-o', true);
  ['b','o'].forEach(function(s) {
    document.getElementById('tally-' + s).innerHTML = '<strong>0</strong>/' + (nStreams*nFiles) + ' files';
    document.getElementById('elapsed-' + s).textContent = '0.00s';
    document.getElementById('thr-' + s).innerHTML = '—';
    document.getElementById('badge-' + s).className = 'footer-badge badge-idle';
    document.getElementById('badge-' + s).textContent = 'Idle';
  });
  ['b','o'].forEach(function(s) {
    document.getElementById('ttext-' + s).innerHTML = '<span class="ttext-placeholder">Awaiting transcription…</span>';
    document.getElementById('tbadge-' + s).className = 'footer-badge badge-idle';
    document.getElementById('tbadge-' + s).textContent = 'Idle';
    document.getElementById('tfoot-' + s).innerHTML = '—';
  });
  document.getElementById('results-panel').style.display = 'none';
  document.getElementById('cross-hw').style.display = 'none';
  document.getElementById('concurrent-results').style.display = '';
  document.getElementById('transcript-results').style.display = 'none';
  document.getElementById('start-btn').disabled    = false;
  document.getElementById('start-btn').textContent = '▶ Run benchmark';
}

// ── Init ──────────────────────────────────────────────────────────────────────
buildLanes('lanes-b', false);
buildLanes('lanes-o', true);
initClipSel();
</script>
</body></html>"""


def render_asr_demo():
    cfg = _load_cfg()
    if not cfg:
        st.error(f"Config not found: {_ASR_CFG_ID}")
        st.stop()

    art_src = "data:image/png;base64," + base64.b64encode(
        (_LOGOS_DIR / "artemis-logo-wordmark.png").read_bytes()).decode()

    hack_r = hack_b = ""
    if _DESIGN_FONTS.exists():
        hr = _DESIGN_FONTS / "Hack-Regular.ttf"
        hb = _DESIGN_FONTS / "Hack-Bold.ttf"
        if hr.exists(): hack_r = "data:font/ttf;base64," + base64.b64encode(hr.read_bytes()).decode()
        if hb.exists(): hack_b = "data:font/ttf;base64," + base64.b64encode(hb.read_bytes()).decode()

    html = (
        _ASR_HTML
        .replace("__CONFIG_JSON__",  json.dumps(cfg))
        .replace("__ARTEMIS_LOGO__", art_src)
        .replace("__HACK_REGULAR__", hack_r)
        .replace("__HACK_BOLD__",    hack_b)
    )
    st.components.v1.html(html, height=1340, scrolling=False)


render_asr_demo()

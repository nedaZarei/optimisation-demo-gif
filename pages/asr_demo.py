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
@font-face { font-family:'Hack'; src:url('__HACK_REGULAR__') format('truetype'); font-weight:400; font-style:normal; font-display:swap; }
@font-face { font-family:'Hack'; src:url('__HACK_BOLD__')    format('truetype'); font-weight:700; font-style:normal; font-display:swap; }
:root {
  --font-sans:'Archivo',system-ui,-apple-system,Segoe UI,sans-serif;
  --font-mono:'Hack',ui-monospace,SFMono-Regular,Menlo,monospace;
  --color-brand-400:#7b66ff; --color-brand-500:#6350dc;
  --color-slate-100:#f1f5f9; --color-slate-200:#e2e8f0; --color-slate-300:#cbd5e1;
  --color-slate-400:#94a3b8; --color-slate-500:#64748b; --color-slate-600:#475569;
  --color-slate-700:#334155; --color-slate-800:#1e293b; --color-slate-900:#0f172a;
  --color-slate-950:#020617;
  --color-background:var(--color-slate-950); --color-card:var(--color-slate-900);
  --color-border:rgba(255,255,255,0.1); --color-primary:var(--color-brand-400);
  --color-success:#4ade80;
  --radius-lg:10px; --radius-xl:12px; --radius-full:9999px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:var(--font-sans);background:var(--color-background);padding:2px 2px 16px;-webkit-font-smoothing:antialiased;color:var(--color-slate-100);}
.logo-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.logo-bar img{display:block;}
.bar-base{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:10px 20px;display:flex;align-items:center;gap:6px;font-size:0.81rem;flex-wrap:wrap;}
.spec-bar{margin-bottom:8px;}
.clip-bar{margin-bottom:12px;gap:10px;}
.bar-lbl{font-size:0.70rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:var(--color-slate-500);white-space:nowrap;}
.clip-divider{width:1px;height:16px;background:var(--color-slate-700);flex-shrink:0;}
.clip-desc-inline{font-size:0.76rem;color:var(--color-slate-500);font-style:italic;margin-left:4px;}
.spec-lbl{color:var(--color-slate-500);margin-right:2px;}
.spec-sep{color:var(--color-slate-700);margin:0 10px;font-size:1rem;}
.sb-sel{border:none;background:transparent;color:var(--color-slate-200);font-weight:700;font-size:0.81rem;font-family:var(--font-sans);cursor:pointer;outline:none;padding:0 18px 0 0;-webkit-appearance:none;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237b66ff' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 2px center;background-size:10px 6px;}
.sb-sel:hover{color:var(--color-primary);}
.sb-sel option{background:var(--color-card);color:var(--color-slate-200);}
.scenario-chips{display:flex;align-items:center;gap:6px;margin-bottom:12px;flex-wrap:wrap;}
.chip{background:rgba(123,102,255,0.12);color:var(--color-brand-400);border:1px solid rgba(123,102,255,0.25);border-radius:var(--radius-full);padding:2px 10px;font-size:0.70rem;font-weight:600;letter-spacing:0.04em;}
.start-btn{display:block;width:100%;padding:12px;background:var(--color-brand-400);color:white;font-family:var(--font-sans);font-size:0.875rem;font-weight:700;border:none;border-radius:var(--radius-lg);cursor:pointer;letter-spacing:0.03em;transition:background 0.2s,opacity 0.2s;margin-bottom:14px;}
.start-btn:hover:not(:disabled){background:var(--color-brand-500);}
.start-btn:disabled{opacity:0.45;cursor:not-allowed;}
.race-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}
.proc-card{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--radius-xl);padding:16px 18px;}
.proc-card-opt{background:#0b1a11;border-color:rgba(74,222,128,0.25);}
.proc-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
.proc-label{font-size:0.70rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--color-slate-400);}
.proc-badge{font-size:0.68rem;font-weight:700;padding:3px 9px;border-radius:var(--radius-full);letter-spacing:0.04em;}
.badge-idle      {background:rgba(100,116,139,0.15);color:var(--color-slate-500);}
.badge-processing{background:rgba(123,102,255,0.18);color:var(--color-brand-400);}
.badge-done      {background:rgba(74,222,128,0.15); color:var(--color-success);}
.waveform{display:flex;align-items:center;gap:2px;height:40px;margin-bottom:12px;}
.wbar{flex:1;background:var(--color-brand-400);border-radius:2px;opacity:0.55;transform-origin:bottom;height:4px;transition:opacity 0.3s;}
.proc-card-opt .wbar{background:var(--color-success);}
.waveform.playing .wbar{animation:waveplay var(--dur,1.1s) ease-in-out infinite alternate;}
@keyframes waveplay{from{transform:scaleY(0.15);opacity:0.4;}to{transform:scaleY(1);opacity:0.75;}}
.waveform.done .wbar{animation:none;height:3px!important;opacity:0.2;}
.proc-timer{font-family:var(--font-mono);font-size:1.6rem;font-weight:700;color:var(--color-slate-100);line-height:1;margin-bottom:4px;}
.proc-timer .unit{font-size:0.85rem;font-weight:400;color:var(--color-slate-500);margin-left:3px;}
.proc-rtf{font-family:var(--font-mono);font-size:0.72rem;color:var(--color-slate-500);margin-bottom:12px;}
.proc-rtf .rtf-val{color:var(--color-slate-300);font-weight:600;}
.progress-track{height:5px;background:var(--color-slate-800);border-radius:var(--radius-full);overflow:hidden;}
.progress-fill{height:100%;border-radius:var(--radius-full);width:0%;}
.fill-stock{background:var(--color-slate-600);}
.fill-opt{background:linear-gradient(90deg,var(--color-brand-400),#a78bfa);}
#transcript-panel{display:none;background:var(--color-card);border:1px solid rgba(74,222,128,0.2);border-radius:var(--radius-xl);padding:20px 22px;margin-bottom:12px;}
.transcript-accuracy-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(74,222,128,0.10);color:var(--color-success);border:1px solid rgba(74,222,128,0.25);border-radius:var(--radius-full);padding:4px 14px;font-size:0.70rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:14px;}
.transcript-subhead{font-size:0.75rem;color:var(--color-slate-500);margin-bottom:12px;font-style:italic;}
.transcript-text{font-size:0.845rem;line-height:1.75;color:var(--color-slate-300);max-height:220px;overflow-y:auto;padding-right:8px;white-space:pre-wrap;}
.transcript-text::-webkit-scrollbar{width:4px;}
.transcript-text::-webkit-scrollbar-track{background:transparent;}
.transcript-text::-webkit-scrollbar-thumb{background:var(--color-slate-700);border-radius:4px;}
.metrics-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;}
.metric-card{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:14px 16px;text-align:center;}
.metric-label{font-size:0.65rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--color-slate-500);margin-bottom:6px;}
.metric-value{font-family:var(--font-mono);font-size:1.4rem;font-weight:700;color:var(--color-success);line-height:1;margin-bottom:4px;}
.metric-sub{font-size:0.67rem;color:var(--color-slate-500);}
.callout{background:rgba(123,102,255,0.06);border:1px solid rgba(123,102,255,0.18);border-radius:var(--radius-lg);padding:16px 20px;font-size:0.76rem;color:var(--color-slate-400);line-height:1.6;display:flex;align-items:center;justify-content:center;text-align:center;min-height:64px;}
</style>
</head>
<body>
<div class="logo-bar">
  <img src="__ARTEMIS_LOGO__" height="28" alt="Artemis">
</div>
<div class="bar-base spec-bar">
  <span class="spec-lbl">Framework</span>
  <select class="sb-sel"><option>faster-whisper</option></select>
  <span class="spec-sep">|</span>
  <span class="spec-lbl">Model</span>
  <select class="sb-sel"><option>whisper-large-v3</option></select>
  <span class="spec-sep">|</span>
  <span class="spec-lbl">Hardware</span>
  <select class="sb-sel"><option>NVIDIA RTX 3090 (Beast3)</option></select>
</div>
<div class="bar-base clip-bar">
  <span class="bar-lbl">Audio clip</span>
  <div class="clip-divider"></div>
  <select class="sb-sel" id="sel-clip" onchange="onClipChange()"></select>
  <span class="clip-desc-inline" id="clip-desc-inline"></span>
</div>
<div class="scenario-chips" id="scenario-chips"></div>
<button class="start-btn" id="start-btn" onclick="startRace()">&#9654; Run Demo</button>
<div class="race-row">
  <div class="proc-card">
    <div class="proc-header"><span class="proc-label">Stock</span><span class="proc-badge badge-idle" id="b-badge">Idle</span></div>
    <div class="waveform" id="b-wave"></div>
    <div class="proc-timer" id="b-timer">0.000<span class="unit">s</span></div>
    <div class="proc-rtf" id="b-rtf">RTF <span class="rtf-val">&#8212;</span></div>
    <div class="progress-track"><div class="progress-fill fill-stock" id="b-progress"></div></div>
  </div>
  <div class="proc-card proc-card-opt">
    <div class="proc-header"><span class="proc-label">Optimized</span><span class="proc-badge badge-idle" id="o-badge">Idle</span></div>
    <div class="waveform" id="o-wave"></div>
    <div class="proc-timer" id="o-timer">0.000<span class="unit">s</span></div>
    <div class="proc-rtf" id="o-rtf">RTF <span class="rtf-val">&#8212;</span></div>
    <div class="progress-track"><div class="progress-fill fill-opt" id="o-progress"></div></div>
  </div>
</div>
<div id="transcript-panel">
  <div class="transcript-accuracy-badge">&#10003; Both produced identical output &#xB7; WER delta &#8776; 0%</div>
  <div class="transcript-subhead" id="transcript-subhead"></div>
  <div class="transcript-text" id="transcript-text"></div>
</div>
<div class="metrics-row" id="metrics-row" style="display:none">
  <div class="metric-card"><div class="metric-label">RTF Improvement</div><div class="metric-value" id="m-rtf">&#8212;</div><div class="metric-sub" id="m-rtf-sub">real-time factor</div></div>
  <div class="metric-card"><div class="metric-label">Latency Reduction</div><div class="metric-value" id="m-lat">&#8212;</div><div class="metric-sub" id="m-lat-sub">processing time</div></div>
  <div class="metric-card"><div class="metric-label">Accuracy</div><div class="metric-value">6/6</div><div class="metric-sub">noise conditions pass</div></div>
</div>
<div class="callout" id="callout-note" style="display:none"></div>
<script>
var CFG=__CONFIG_JSON__;
var clips=CFG.demo_clips,curClip=0,running=false,animId=null,ANIM_MS=7200;
var HEIGHTS=[18,24,32,38,44,50,44,52,46,40,54,46,40,32,44,50,42,34,26,18];
function buildWave(el){el.innerHTML='';HEIGHTS.forEach(function(h,i){var b=document.createElement('div');b.className='wbar';b.style.setProperty('--dur',(0.7+Math.random()*0.8).toFixed(2)+'s');b.style.animationDelay=(i*0.04).toFixed(2)+'s';b.style.height=h+'px';el.appendChild(b);});}
buildWave(document.getElementById('b-wave'));
buildWave(document.getElementById('o-wave'));
var clipSel=document.getElementById('sel-clip');
clips.forEach(function(c,i){var opt=document.createElement('option');opt.value=i;opt.textContent=c.label;clipSel.appendChild(opt);});
function updateClipInfo(){
  var c=clips[curClip];
  var mins=Math.floor(c.audio_duration_s/60),secs=c.audio_duration_s%60;
  var dur=mins+' min'+(secs?' '+secs+' s':'');
  document.getElementById('clip-desc-inline').textContent='— '+c.description;
  document.getElementById('scenario-chips').innerHTML='<span class="chip">Duration: '+dur+'</span><span class="chip">faster-whisper 1.2.1</span><span class="chip">int8_float16 · beam=5 · batch=32</span>';
  var rtfPct=((c.baseline.rtf-c.optimized.rtf)/c.baseline.rtf*100).toFixed(1);
  var latDelta=(c.baseline.latency_ms-c.optimized.latency_ms)/1000;
  document.getElementById('m-rtf').textContent='−'+rtfPct+'%';
  document.getElementById('m-rtf-sub').textContent=c.baseline.rtf.toFixed(4)+' → '+c.optimized.rtf.toFixed(4);
  document.getElementById('m-lat').textContent='−'+latDelta.toFixed(2)+' s';
  document.getElementById('m-lat-sub').textContent=(c.baseline.latency_ms/1000).toFixed(2)+' s → '+(c.optimized.latency_ms/1000).toFixed(2)+' s';
  document.getElementById('b-rtf').innerHTML='RTF <span class="rtf-val">'+c.baseline.rtf.toFixed(4)+'</span>';
  document.getElementById('o-rtf').innerHTML='RTF <span class="rtf-val">'+c.optimized.rtf.toFixed(4)+'</span>';
  document.getElementById('transcript-subhead').textContent='Transcript — '+c.label+' · '+c.description;
  document.getElementById('callout-note').innerHTML=CFG.callout_note.replace(/\n/g,'<br>');
}
function onClipChange(){curClip=parseInt(document.getElementById('sel-clip').value,10);resetUI();updateClipInfo();}
function resetUI(){
  if(animId)cancelAnimationFrame(animId);running=false;
  ['b','o'].forEach(function(p){
    document.getElementById(p+'-badge').className='proc-badge badge-idle';
    document.getElementById(p+'-badge').textContent='Idle';
    document.getElementById(p+'-timer').innerHTML='0.000<span class="unit">s</span>';
    document.getElementById(p+'-progress').style.width='0%';
    var w=document.getElementById(p+'-wave');w.classList.remove('playing','done');
  });
  document.getElementById('transcript-panel').style.display='none';
  document.getElementById('metrics-row').style.display='none';
  document.getElementById('callout-note').style.display='none';
  document.getElementById('start-btn').disabled=false;
  document.getElementById('start-btn').textContent='▶ Run Demo';
}
function startRace(){
  if(running)return;running=true;
  var c=clips[curClip];
  var bTotal=c.baseline.latency_ms,oTotal=c.optimized.latency_ms;
  var scale=ANIM_MS/Math.max(bTotal,oTotal);
  document.getElementById('start-btn').disabled=true;
  ['b','o'].forEach(function(p){
    document.getElementById(p+'-badge').className='proc-badge badge-processing';
    document.getElementById(p+'-badge').textContent='Processing…';
    document.getElementById(p+'-wave').classList.add('playing');
  });
  document.getElementById('transcript-panel').style.display='none';
  var bDone=false,oDone=false,t0=performance.now();
  function tick(){
    var elapsed=performance.now()-t0;
    document.getElementById('b-timer').innerHTML=(Math.min(elapsed/scale,bTotal)/1000).toFixed(3)+'<span class="unit">s</span>';
    document.getElementById('o-timer').innerHTML=(Math.min(elapsed/scale,oTotal)/1000).toFixed(3)+'<span class="unit">s</span>';
    document.getElementById('b-progress').style.width=Math.min(elapsed/scale/bTotal*100,100)+'%';
    document.getElementById('o-progress').style.width=Math.min(elapsed/scale/oTotal*100,100)+'%';
    if(!oDone&&elapsed>=oTotal*scale){oDone=true;document.getElementById('o-badge').className='proc-badge badge-done';document.getElementById('o-badge').textContent='✓ Done';document.getElementById('o-timer').innerHTML=(oTotal/1000).toFixed(3)+'<span class="unit">s</span>';document.getElementById('o-progress').style.width='100%';var ow=document.getElementById('o-wave');ow.classList.remove('playing');ow.classList.add('done');}
    if(!bDone&&elapsed>=bTotal*scale){bDone=true;document.getElementById('b-badge').className='proc-badge badge-done';document.getElementById('b-badge').textContent='✓ Done';document.getElementById('b-timer').innerHTML=(bTotal/1000).toFixed(3)+'<span class="unit">s</span>';document.getElementById('b-progress').style.width='100%';var bw=document.getElementById('b-wave');bw.classList.remove('playing');bw.classList.add('done');}
    if(bDone&&oDone){document.getElementById('transcript-text').textContent=c.transcript;document.getElementById('transcript-panel').style.display='block';document.getElementById('metrics-row').style.display='grid';document.getElementById('callout-note').style.display='flex';running=false;document.getElementById('start-btn').disabled=false;document.getElementById('start-btn').textContent='↺ Run again';return;}
    animId=requestAnimationFrame(tick);
  }
  animId=requestAnimationFrame(tick);
}
updateClipInfo();
</script>
</body></html>"""


def render_asr_demo():
    cfg = _load_cfg()
    if not cfg:
        st.error(f"Config not found: {_ASR_CFG_ID}")
        st.stop()

    tt_src  = "data:image/svg+xml;base64," + base64.b64encode(
        (_LOGOS_DIR / "TurinTech-light-no Background.svg").read_bytes()).decode()
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
        .replace("__CONFIG_JSON__",    json.dumps(cfg))
        .replace("__TURINTECH_LOGO__", tt_src)
        .replace("__ARTEMIS_LOGO__",   art_src)
        .replace("__HACK_REGULAR__",   hack_r)
        .replace("__HACK_BOLD__",      hack_b)
    )
    st.components.v1.html(html, height=1060, scrolling=False)


render_asr_demo()

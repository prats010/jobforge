<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>JobForge — AI-Powered Job Search Pipeline</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap" rel="stylesheet"/>
<style>
  :root {
    --neon: #00ffe7;
    --neon2: #7b2fff;
    --accent: #ff2d78;
    --gold: #f5c518;
    --bg: #030810;
    --panel: #080f1e;
    --border: rgba(0,255,231,0.15);
    --text: #c8e0f0;
    --muted: #4a6480;
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    line-height: 1.7;
    overflow-x: hidden;
  }

  /* Scanline overlay */
  body::before {
    content:'';
    position:fixed;
    inset:0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,255,231,0.018) 2px,
      rgba(0,255,231,0.018) 4px
    );
    pointer-events:none;
    z-index:9999;
  }

  /* Animated grid background */
  .grid-bg {
    position:fixed;
    inset:0;
    background-image:
      linear-gradient(rgba(0,255,231,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,231,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridShift 20s linear infinite;
    pointer-events:none;
    z-index:0;
  }
  @keyframes gridShift {
    from { background-position: 0 0; }
    to   { background-position: 60px 60px; }
  }

  .container {
    position:relative;
    z-index:1;
    max-width: 960px;
    margin: 0 auto;
    padding: 0 2rem 6rem;
  }

  /* ── HERO ── */
  .hero {
    text-align: center;
    padding: 5rem 0 3rem;
    position: relative;
  }

  .hero-glow {
    position:absolute;
    top:50%;
    left:50%;
    transform: translate(-50%,-50%);
    width: 700px;
    height: 400px;
    background: radial-gradient(ellipse, rgba(0,255,231,0.07) 0%, transparent 70%);
    pointer-events:none;
  }

  .badge-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 2rem;
    animation: fadeSlideDown 0.8s ease both;
  }
  .badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    padding: 4px 12px;
    border: 1px solid var(--neon);
    border-radius: 2px;
    color: var(--neon);
    background: rgba(0,255,231,0.06);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    animation: pulse-border 3s ease infinite;
  }
  .badge.accent { border-color: var(--accent); color: var(--accent); background: rgba(255,45,120,0.06); }
  .badge.purple { border-color: var(--neon2); color: var(--neon2); background: rgba(123,47,255,0.06); }

  @keyframes pulse-border {
    0%,100% { box-shadow: 0 0 4px currentColor; }
    50%      { box-shadow: 0 0 14px currentColor; }
  }

  .logo-ascii {
    font-family: 'Share Tech Mono', monospace;
    font-size: clamp(8px, 1.5vw, 13px);
    line-height: 1.2;
    color: var(--neon);
    text-shadow: 0 0 18px rgba(0,255,231,0.7);
    animation: fadeSlideDown 1s 0.2s ease both, glitchText 8s 2s infinite;
    white-space: pre;
    margin: 0 auto 1.5rem;
    display: inline-block;
  }

  @keyframes glitchText {
    0%,94%,100% { transform: translate(0); filter: none; }
    95% { transform: translate(-3px, 1px); filter: hue-rotate(90deg); }
    96% { transform: translate(3px, -1px); }
    97% { transform: translate(0); }
    98% { transform: translate(-2px, 2px); filter: hue-rotate(180deg); }
  }

  .hero-tagline {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.4rem, 3.5vw, 2.4rem);
    font-weight: 900;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    animation: fadeSlideDown 1s 0.4s ease both;
    background: linear-gradient(90deg, var(--neon), #fff, var(--neon2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-sub {
    font-size: 1.1rem;
    color: var(--muted);
    animation: fadeSlideDown 1s 0.6s ease both;
    margin-bottom: 2.5rem;
    letter-spacing: 0.04em;
  }
  .hero-sub span { color: var(--neon); }

  .cta-btn {
    display: inline-block;
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 12px 36px;
    border: 1px solid var(--neon);
    color: var(--neon);
    text-decoration: none;
    background: rgba(0,255,231,0.05);
    position: relative;
    overflow: hidden;
    transition: color 0.3s;
    animation: fadeSlideDown 1s 0.8s ease both;
  }
  .cta-btn::before {
    content:'';
    position:absolute;
    inset:0;
    background: var(--neon);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
    z-index:-1;
  }
  .cta-btn:hover { color: var(--bg); }
  .cta-btn:hover::before { transform: scaleX(1); }

  /* ── SECTION ── */
  .section {
    margin: 4rem 0;
  }

  .section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--neon);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    opacity: 0.7;
  }

  .section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    margin-bottom: 2rem;
    position: relative;
    display: inline-block;
  }
  .section-title::after {
    content:'';
    position:absolute;
    bottom:-6px;
    left:0;
    width:100%;
    height:1px;
    background: linear-gradient(90deg, var(--neon), transparent);
  }

  /* ── FEATURES GRID ── */
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.25rem;
  }

  .feature-card {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.3s;
    cursor: default;
  }
  .feature-card::before {
    content:'';
    position:absolute;
    top:0; left:0;
    width:3px; height:100%;
    background: var(--neon);
    transform: scaleY(0);
    transform-origin: top;
    transition: transform 0.3s ease;
  }
  .feature-card:hover { border-color: rgba(0,255,231,0.4); transform: translateY(-3px); }
  .feature-card:hover::before { transform: scaleY(1); }
  .feature-card.accent-card::before { background: var(--accent); }
  .feature-card.purple-card::before { background: var(--neon2); }
  .feature-card.gold-card::before { background: var(--gold); }

  .feature-icon {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    display: block;
  }
  .feature-name {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--neon);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }
  .feature-card.accent-card .feature-name { color: var(--accent); }
  .feature-card.purple-card .feature-name { color: var(--neon2); }
  .feature-card.gold-card .feature-name { color: var(--gold); }
  .feature-desc { font-size: 0.9rem; color: var(--muted); line-height: 1.6; }

  /* ── ARCHITECTURE ── */
  .arch-diagram {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 2rem;
    position: relative;
    overflow: hidden;
  }
  .arch-diagram::after {
    content: 'SYS.ARCH v2.1';
    position:absolute;
    top:12px; right:16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.1em;
  }

  .arch-nodes {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }

  .arch-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    justify-content: center;
  }

  .arch-box {
    background: rgba(0,255,231,0.06);
    border: 1px solid rgba(0,255,231,0.25);
    padding: 0.6rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: var(--neon);
    text-align: center;
    min-width: 140px;
    position: relative;
    letter-spacing: 0.06em;
  }
  .arch-box .sub {
    display: block;
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 2px;
  }
  .arch-box.purple {
    border-color: rgba(123,47,255,0.4);
    background: rgba(123,47,255,0.07);
    color: var(--neon2);
  }
  .arch-box.accent {
    border-color: rgba(255,45,120,0.4);
    background: rgba(255,45,120,0.07);
    color: var(--accent);
  }
  .arch-box.gold {
    border-color: rgba(245,197,24,0.4);
    background: rgba(245,197,24,0.07);
    color: var(--gold);
  }

  .arch-arrow {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.4rem 0;
    color: var(--muted);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.06em;
    gap: 0.5rem;
    position: relative;
  }
  .arch-arrow::before, .arch-arrow::after {
    content:'';
    height:1px;
    width:30px;
    background: linear-gradient(90deg, transparent, var(--muted));
  }
  .arch-arrow::after { background: linear-gradient(90deg, var(--muted), transparent); }

  /* ── TECH STACK ── */
  .stack-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
  }
  .stack-item {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 1rem;
    text-align: center;
    transition: border-color 0.3s, transform 0.3s;
  }
  .stack-item:hover { border-color: rgba(0,255,231,0.4); transform: translateY(-2px); }
  .stack-layer {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .stack-tech {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--neon);
    letter-spacing: 0.06em;
  }

  /* ── API ENDPOINTS ── */
  .endpoints {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .endpoint {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 0.6rem 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    transition: border-color 0.2s;
  }
  .endpoint:hover { border-color: rgba(0,255,231,0.35); }
  .method {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 7px;
    border-radius: 2px;
    min-width: 38px;
    text-align: center;
  }
  .method.get { background: rgba(0,255,231,0.12); color: var(--neon); border: 1px solid rgba(0,255,231,0.3); }
  .method.post { background: rgba(245,197,24,0.12); color: var(--gold); border: 1px solid rgba(245,197,24,0.3); }
  .endpoint-path { color: #e0f0ff; flex:1; }
  .endpoint-desc { color: var(--muted); font-size: 0.72rem; }

  /* ── SETUP ── */
  .steps {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  .step {
    display: flex;
    gap: 1.25rem;
  }
  .step-num {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--bg);
    background: var(--neon);
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .step-body {}
  .step-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--neon);
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
  }
  .step-desc { font-size: 0.9rem; color: var(--muted); }

  pre.code-block {
    background: rgba(0,255,231,0.04);
    border: 1px solid rgba(0,255,231,0.12);
    border-left: 3px solid var(--neon);
    padding: 1rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #9fd;
    overflow-x: auto;
    margin-top: 0.75rem;
    line-height: 1.7;
  }
  pre.code-block .c { color: var(--muted); }
  pre.code-block .k { color: var(--neon); }
  pre.code-block .s { color: var(--gold); }

  /* ── DEPLOYMENT STATUS ── */
  .deploy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  .deploy-card {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .deploy-service {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #fff;
    text-transform: uppercase;
  }
  .deploy-platform {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.06em;
  }
  .status-dot {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #00ff88;
    letter-spacing: 0.08em;
  }
  .status-dot::before {
    content:'';
    width:8px; height:8px;
    border-radius:50%;
    background: #00ff88;
    box-shadow: 0 0 8px #00ff88;
    animation: blink 2s ease infinite;
  }
  @keyframes blink {
    0%,100% { opacity:1; }
    50%      { opacity:0.3; }
  }

  /* ── FOOTER ── */
  .footer {
    text-align: center;
    padding: 3rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 5rem;
  }
  .footer-name {
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--neon);
    margin-bottom: 0.5rem;
    text-shadow: 0 0 10px rgba(0,255,231,0.4);
  }
  .footer-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.15em;
  }
  .footer-link {
    color: var(--neon);
    text-decoration: none;
  }

  /* ── DIVIDER ── */
  .divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 3rem 0;
  }
  .divider::before, .divider::after {
    content:'';
    flex:1;
    height:1px;
    background: linear-gradient(90deg, transparent, var(--border));
  }
  .divider::after { background: linear-gradient(90deg, var(--border), transparent); }
  .divider-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.15em;
    white-space: nowrap;
  }

  /* ── ANIMATIONS ── */
  @keyframes fadeSlideDown {
    from { opacity:0; transform: translateY(-20px); }
    to   { opacity:1; transform: translateY(0); }
  }

  .reveal {
    opacity:0;
    transform: translateY(24px);
    transition: opacity 0.7s ease, transform 0.7s ease;
  }
  .reveal.visible {
    opacity:1;
    transform: translateY(0);
  }

  /* ── CORNER ACCENT ── */
  .corner-box {
    position: relative;
  }
  .corner-box::before, .corner-box::after {
    content:'';
    position:absolute;
    width:12px; height:12px;
  }
  .corner-box::before {
    top:-1px; left:-1px;
    border-top: 2px solid var(--neon);
    border-left: 2px solid var(--neon);
  }
  .corner-box::after {
    bottom:-1px; right:-1px;
    border-bottom: 2px solid var(--neon);
    border-right: 2px solid var(--neon);
  }
</style>
</head>
<body>

<div class="grid-bg"></div>

<div class="container">

  <!-- HERO -->
  <div class="hero">
    <div class="hero-glow"></div>

    <div class="badge-row">
      <span class="badge">🚀 Live at jobforge-snowy.vercel.app</span>
      <span class="badge accent">⚡ Backend — Railway</span>
      <span class="badge purple">🤖 AI — Groq LLM</span>
    </div>

    <div class="logo-ascii">
  ██╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  ██║██║   ██║██████╔╝█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
  ██║██║   ██║██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
  ██║╚██████╔╝██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝</div>

    <div class="hero-tagline">AI-Powered Job Search Pipeline</div>
    <p class="hero-sub">Stop applying blindly. <span>Start forging your career.</span></p>

    <a href="https://jobforge-snowy.vercel.app" class="cta-btn" target="_blank">LAUNCH DEMO →</a>
  </div>

  <div class="divider"><span class="divider-label">// SYSTEM.OVERVIEW</span></div>

  <!-- WHAT IS -->
  <div class="section reveal">
    <div class="section-label">// MODULE_01</div>
    <div class="section-title">WHAT IS JOBFORGE?</div>
    <p style="color:var(--muted); max-width:700px; line-height:1.8;">
      JobForge is your <span style="color:var(--neon);">personal AI job search engine</span>. It doesn't just list jobs — it actively hunts them, scores your fit, rewrites your CV for each role, and tracks your entire application pipeline. Built specifically for <span style="color:var(--neon2);">Data Science, ML, and AI roles</span>.
    </p>
  </div>

  <div class="divider"><span class="divider-label">// FEATURE.MODULES</span></div>

  <!-- FEATURES -->
  <div class="section reveal">
    <div class="section-label">// MODULE_02</div>
    <div class="section-title">CORE FEATURES</div>

    <div class="features-grid">
      <div class="feature-card">
        <span class="feature-icon">🔍</span>
        <div class="feature-name">Job Scanner</div>
        <p class="feature-desc">Automatically scans multiple job sources and discovers new opportunities. Run on demand or let it work in the background. Full scan history logged.</p>
      </div>
      <div class="feature-card accent-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-name">AI Evaluator</div>
        <p class="feature-desc">Powered by Groq LLM — each job gets scored based on your profile, skills, and preferences. No more reading 50 JDs manually.</p>
      </div>
      <div class="feature-card purple-card">
        <span class="feature-icon">📄</span>
        <div class="feature-name">CV Tailor</div>
        <p class="feature-desc">Upload your base resume and let AI rewrite it for each job posting. Keyword-optimized, ATS-friendly, and ready to send.</p>
      </div>
      <div class="feature-card gold-card">
        <span class="feature-icon">📋</span>
        <div class="feature-name">App Tracker</div>
        <p class="feature-desc">Kanban-style board: Discovered → Applied → Interview → Offer. Never lose track of an application again.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">🎤</span>
        <div class="feature-name">Interview Prep</div>
        <p class="feature-desc">AI-generated interview questions tailored to each specific job posting. Practice before you walk in the door.</p>
      </div>
      <div class="feature-card accent-card">
        <span class="feature-icon">⚙️</span>
        <div class="feature-name">Settings</div>
        <p class="feature-desc">Configure target roles, locations, salary expectations, and more. JobForge adapts entirely to you.</p>
      </div>
    </div>
  </div>

  <div class="divider"><span class="divider-label">// SYSTEM.ARCHITECTURE</span></div>

  <!-- ARCHITECTURE -->
  <div class="section reveal">
    <div class="section-label">// MODULE_03</div>
    <div class="section-title">ARCHITECTURE</div>

    <div class="arch-diagram corner-box">
      <div class="arch-nodes">
        <div class="arch-row">
          <div class="arch-box">
            REACT / VITE
            <span class="sub">Frontend · Vercel</span>
          </div>
          <div style="color:var(--muted); font-family:'Share Tech Mono',monospace; font-size:0.8rem;">◄──HTTP──►</div>
          <div class="arch-box purple">
            FASTAPI
            <span class="sub">Backend · Railway</span>
          </div>
        </div>
        <div class="arch-arrow">↓ DB QUERY</div>
        <div class="arch-row">
          <div class="arch-box accent">
            POSTGRESQL
            <span class="sub">Database · Railway</span>
          </div>
        </div>
        <div class="arch-arrow">↓ LLM CALL</div>
        <div class="arch-row">
          <div class="arch-box gold">
            GROQ AI API
            <span class="sub">LLM Inference Engine</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="divider"><span class="divider-label">// TECH.STACK</span></div>

  <!-- TECH STACK -->
  <div class="section reveal">
    <div class="section-label">// MODULE_04</div>
    <div class="section-title">TECH STACK</div>

    <div class="stack-grid">
      <div class="stack-item">
        <div class="stack-layer">Frontend</div>
        <div class="stack-tech">React 18 · Vite · Tailwind</div>
      </div>
      <div class="stack-item">
        <div class="stack-layer">Backend</div>
        <div class="stack-tech">Python · FastAPI</div>
      </div>
      <div class="stack-item">
        <div class="stack-layer">Database</div>
        <div class="stack-tech">PostgreSQL</div>
      </div>
      <div class="stack-item">
        <div class="stack-layer">AI / LLM</div>
        <div class="stack-tech">Groq API</div>
      </div>
      <div class="stack-item">
        <div class="stack-layer">Deploy FE</div>
        <div class="stack-tech">Vercel</div>
      </div>
      <div class="stack-item">
        <div class="stack-layer">Deploy BE</div>
        <div class="stack-tech">Railway</div>
      </div>
    </div>
  </div>

  <div class="divider"><span class="divider-label">// SETUP.SEQUENCE</span></div>

  <!-- GETTING STARTED -->
  <div class="section reveal">
    <div class="section-label">// MODULE_05</div>
    <div class="section-title">GETTING STARTED</div>

    <div class="steps">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-body">
          <div class="step-title">Clone the repo</div>
          <pre class="code-block"><span class="k">git clone</span> https://github.com/prats010/jobforge.git
<span class="k">cd</span> jobforge</pre>
        </div>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-body">
          <div class="step-title">Backend setup</div>
          <pre class="code-block"><span class="k">cd</span> backend
pip install -r requirements.txt

<span class="c"># .env</span>
<span class="s">DATABASE_URL</span>=postgresql://user:pass@localhost:5432/jobforge
<span class="s">GROQ_API_KEY</span>=your_groq_key_here

uvicorn main:app --reload
<span class="c"># → API docs at http://localhost:8000/docs</span></pre>
        </div>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-body">
          <div class="step-title">Frontend setup</div>
          <pre class="code-block"><span class="k">cd</span> frontend
npm install

<span class="c"># .env</span>
<span class="s">VITE_API_URL</span>=http://localhost:8000

npm run dev
<span class="c"># → App at http://localhost:5173</span></pre>
        </div>
      </div>
    </div>
  </div>

  <div class="divider"><span class="divider-label">// API.ENDPOINTS</span></div>

  <!-- API -->
  <div class="section reveal">
    <div class="section-label">// MODULE_06</div>
    <div class="section-title">API ENDPOINTS</div>

    <div class="endpoints">
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/jobs</span><span class="endpoint-desc">Fetch all discovered jobs</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/jobs/stats</span><span class="endpoint-desc">Pipeline statistics</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="endpoint-path">/api/scanner/run</span><span class="endpoint-desc">Trigger a new job scan</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/scanner/history</span><span class="endpoint-desc">Full scan history</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/scanner/sources</span><span class="endpoint-desc">Configured job sources</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="endpoint-path">/api/evaluator</span><span class="endpoint-desc">AI evaluation of jobs</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/cv/base</span><span class="endpoint-desc">Fetch base resume</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="endpoint-path">/api/cv/tailor</span><span class="endpoint-desc">AI-tailored CV for a job</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/tracker/board</span><span class="endpoint-desc">Kanban board data</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/interview</span><span class="endpoint-desc">Interview prep questions</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/api/settings</span><span class="endpoint-desc">User settings</span></div>
    </div>
  </div>

  <div class="divider"><span class="divider-label">// DEPLOYMENT.STATUS</span></div>

  <!-- DEPLOYMENT -->
  <div class="section reveal">
    <div class="section-label">// MODULE_07</div>
    <div class="section-title">DEPLOYMENT STATUS</div>

    <div class="deploy-grid">
      <div class="deploy-card">
        <div class="deploy-service">Frontend</div>
        <div class="deploy-platform">Vercel · jobforge-snowy.vercel.app</div>
        <div class="status-dot">ONLINE</div>
      </div>
      <div class="deploy-card">
        <div class="deploy-service">Backend</div>
        <div class="deploy-platform">Railway · FastAPI</div>
        <div class="status-dot">ONLINE</div>
      </div>
      <div class="deploy-card">
        <div class="deploy-service">Database</div>
        <div class="deploy-platform">Railway PostgreSQL</div>
        <div class="status-dot">CONNECTED</div>
      </div>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer reveal">
    <div class="footer-name">PRATHAMESH BHAMARE</div>
    <div class="footer-sub">
      <a href="https://github.com/prats010" class="footer-link">github.com/prats010</a>
      &nbsp;·&nbsp; Built with 🔥 &nbsp;·&nbsp; JobForge © 2025
    </div>
  </div>

</div><!-- /container -->

<script>
  const reveals = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  reveals.forEach(r => io.observe(r));
</script>
</body>
</html>

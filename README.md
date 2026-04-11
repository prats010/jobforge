<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:030810,30:0d1f3c,60:0a3d2e,100:030810&height=220&section=header&text=JOBFORGE&fontSize=90&fontColor=00ffe7&fontAlignY=40&desc=AI-Powered%20Job%20Search%20Pipeline&descAlignY=62&descSize=18&descColor=4a6480&animation=fadeIn&stroke=00ffe7&strokeWidth=1" width="100%"/>

<br/>

![Typing SVG](https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&size=16&duration=3000&pause=1000&color=00FFE7&center=true&vCenter=true&multiline=true&width=600&height=60&lines=Stop+applying+blindly.+Start+forging+your+career.;AI+%7C+FastAPI+%7C+React+%7C+PostgreSQL+%7C+Groq+LLM)

<br/>

[![Live Demo](https://img.shields.io/badge/🚀_LIVE_DEMO-jobforge--snowy.vercel.app-00ffe7?style=for-the-badge&labelColor=030810)](https://jobforge-snowy.vercel.app)
[![Backend](https://img.shields.io/badge/⚡_BACKEND-Railway-7b2fff?style=for-the-badge&labelColor=030810&logo=railway&logoColor=7b2fff)](https://railway.app)
[![Frontend](https://img.shields.io/badge/▲_FRONTEND-Vercel-ffffff?style=for-the-badge&labelColor=030810&logo=vercel)](https://vercel.com)
[![AI](https://img.shields.io/badge/🤖_AI-Groq_LLM-ff2d78?style=for-the-badge&labelColor=030810)](https://groq.com)
[![License](https://img.shields.io/badge/LICENSE-MIT-00ffe7?style=for-the-badge&labelColor=030810)](LICENSE)

<br/>

```
  ██╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  ██║██║   ██║██████╔╝█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
  ██║██║   ██║██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
  ██║╚██████╔╝██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

</div>

---

<div align="center">

```
╔══════════════════════════════════════════════════════════╗
║  JOBFORGE doesn't just list jobs — it hunts them,       ║
║  scores your fit, rewrites your CV, and tracks every    ║
║  application. Built for Data Science · ML · AI roles.   ║
╚══════════════════════════════════════════════════════════╝
```

</div>

---

## `// 01` — FEATURES

<br/>

<div align="center">

| MODULE | DESCRIPTION |
|:---:|:---|
| 🔍 **JOB SCANNER** | Automatically scans multiple sources & discovers opportunities. Run on demand or in the background. Full scan history logged. |
| 🧠 **AI EVALUATOR** | Powered by **Groq LLM** — every job gets scored against your profile & skills. No more reading 50 JDs manually. |
| 📄 **CV TAILOR** | Upload your base resume. AI rewrites it per job posting — keyword-optimized, ATS-friendly, and ready to fire. |
| 📋 **APP TRACKER** | Kanban board: `Discovered` → `Applied` → `Interview` → `Offer`. Never lose track of an opportunity again. |
| 🎤 **INTERVIEW PREP** | AI-generated interview questions tailored to each specific job posting. Practice before you walk in. |
| ⚙️ **SETTINGS** | Configure target roles, locations, salary expectations. JobForge adapts entirely to you. |

</div>

---

## `// 02` — ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│         CLIENT                          SERVER                  │
│   ┌───────────────┐   ◄── HTTP ──►  ┌──────────────────┐       │
│   │  React / Vite │                 │ FastAPI (Python)  │       │
│   │  Vercel CDN   │                 │ Railway Hosted    │       │
│   └───────────────┘                 └────────┬─────────┘       │
│                                              │                  │
│                                    ┌─────────▼──────────┐      │
│                                    │   PostgreSQL DB     │      │
│                                    │   Railway Hosted    │      │
│                                    └─────────┬──────────┘      │
│                                              │                  │
│                                    ┌─────────▼──────────┐      │
│                                    │    Groq AI API      │      │
│                                    │    LLM Inference    │      │
│                                    └────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## `// 03` — TECH STACK

<div align="center">

![React](https://img.shields.io/badge/React_18-030810?style=flat-square&logo=react&logoColor=00ffe7)
![Vite](https://img.shields.io/badge/Vite-030810?style=flat-square&logo=vite&logoColor=7b2fff)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-030810?style=flat-square&logo=tailwindcss&logoColor=00ffe7)
![Python](https://img.shields.io/badge/Python-030810?style=flat-square&logo=python&logoColor=ff2d78)
![FastAPI](https://img.shields.io/badge/FastAPI-030810?style=flat-square&logo=fastapi&logoColor=00ffe7)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-030810?style=flat-square&logo=postgresql&logoColor=7b2fff)
![Groq](https://img.shields.io/badge/Groq_AI-030810?style=flat-square&logoColor=ff2d78)
![Vercel](https://img.shields.io/badge/Vercel-030810?style=flat-square&logo=vercel&logoColor=ffffff)
![Railway](https://img.shields.io/badge/Railway-030810?style=flat-square&logo=railway&logoColor=7b2fff)

</div>

<br/>

| LAYER | TECHNOLOGY |
|:---|:---|
| **Frontend** | React 18, Vite, TailwindCSS |
| **Backend** | Python, FastAPI |
| **Database** | PostgreSQL |
| **AI / LLM** | Groq API |
| **Deploy — FE** | Vercel |
| **Deploy — BE** | Railway |

---

## `// 04` — GETTING STARTED

### Prerequisites

```
  Python 3.10+   ·   Node.js 18+   ·   PostgreSQL   ·   Groq API Key
```

> Get your Groq key → [console.groq.com](https://console.groq.com)

---

### `STEP 01` — Clone

```bash
git clone https://github.com/prats010/jobforge.git
cd jobforge
```

### `STEP 02` — Backend

```bash
cd backend
pip install -r requirements.txt
```

```env
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/jobforge
GROQ_API_KEY=your_groq_api_key_here
```

```bash
uvicorn main:app --reload
# API docs → http://localhost:8000/docs
```

### `STEP 03` — Frontend

```bash
cd frontend
npm install
```

```env
# .env
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
# App → http://localhost:5173
```

---

## `// 05` — API ENDPOINTS

| METHOD | ROUTE | DESCRIPTION |
|:---:|:---|:---|
| `GET` | `/api/jobs` | Fetch all discovered jobs |
| `GET` | `/api/jobs/stats` | Pipeline statistics |
| `POST` | `/api/scanner/run` | Trigger a new job scan |
| `GET` | `/api/scanner/history` | Full scan history |
| `GET` | `/api/scanner/sources` | Configured job sources |
| `POST` | `/api/evaluator` | AI evaluation of jobs |
| `GET` | `/api/cv/base` | Fetch base resume |
| `POST` | `/api/cv/tailor` | AI-tailored CV for a job |
| `GET` | `/api/tracker/board` | Kanban board data |
| `GET` | `/api/interview` | Interview prep questions |
| `GET` | `/api/settings` | User settings |

---

## `// 06` — PROJECT STRUCTURE

```
jobforge/
├── backend/
│   ├── main.py               ← FastAPI entry point
│   ├── config.py             ← App configuration
│   ├── database.py           ← DB connection
│   ├── models.py             ← SQLAlchemy models
│   ├── requirements.txt
│   ├── routers/
│   │   ├── jobs.py
│   │   ├── scanner.py
│   │   ├── evaluator.py
│   │   ├── cv.py
│   │   ├── tracker.py
│   │   ├── interview.py
│   │   └── settings.py
│   └── services/
│       └── groq_service.py   ← Groq AI integration
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   └── main.jsx
    ├── index.html
    └── vite.config.js
```

---

## `// 07` — DEPLOYMENT STATUS

| SERVICE | PLATFORM | STATUS |
|:---|:---|:---:|
| **Frontend** | Vercel | ![status](https://img.shields.io/badge/ONLINE-00ff88?style=flat-square) |
| **Backend** | Railway | ![status](https://img.shields.io/badge/ONLINE-00ff88?style=flat-square) |
| **Database** | Railway PostgreSQL | ![status](https://img.shields.io/badge/CONNECTED-00ff88?style=flat-square) |

---

## `// 08` — CONTRIBUTING

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

Pull requests are welcome. For major changes, open an issue first.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:030810,40:0a3d2e,70:0d1f3c,100:030810&height=140&section=footer&text=Built%20with%20🔥%20by%20Prathamesh%20Bhamare&fontSize=16&fontColor=4a6480&fontAlignY=55&animation=fadeIn" width="100%"/>

[![GitHub](https://img.shields.io/badge/github.com/prats010-030810?style=for-the-badge&logo=github&logoColor=00ffe7)](https://github.com/prats010)

</div>

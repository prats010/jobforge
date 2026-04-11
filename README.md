<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=JobForge&fontSize=80&fontColor=ffffff&fontAlignY=38&desc=AI-Powered%20Job%20Search%20Pipeline&descAlignY=58&descSize=20&animation=fadeIn" width="100%"/>

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-jobforge--snowy.vercel.app-6c63ff?style=for-the-badge&logoColor=white)](https://jobforge-snowy.vercel.app)
[![Backend](https://img.shields.io/badge/⚡%20Backend-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![Frontend](https://img.shields.io/badge/▲%20Frontend-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
[![AI](https://img.shields.io/badge/🤖%20AI-Groq-F55036?style=for-the-badge)](https://groq.com)

<br/>

```
  ██╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  ██║██║   ██║██████╔╝█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
  ██║██║   ██║██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
  ██║╚██████╔╝██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

> **Stop applying blindly. Start forging your career.**  
> JobForge is a full-stack AI-powered job search pipeline that scans, evaluates, tailors your CV, and tracks applications — all in one place.

<br/>

</div>

---

## ✨ What is JobForge?

JobForge is your **personal AI job search engine**. It doesn't just list jobs — it actively hunts them, scores your fit, rewrites your CV for each role, and tracks your entire application pipeline. Built for Data Science, ML, and AI roles.

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🔍 Job Scanner
Automatically scans multiple job sources and discovers new opportunities. Run on demand or let it work in the background. Keeps a full history of every scan.

</td>
<td width="50%">

### 🧠 AI Evaluator
Powered by **Groq LLM**, each job gets scored based on your profile, skills, and preferences. No more manually reading 50 JDs — get ranked results instantly.

</td>
</tr>
<tr>
<td width="50%">

### 📄 CV Tailor
Upload your base resume and let AI rewrite it specifically for each job posting. Keyword-optimized, ATS-friendly, and ready to send.

</td>
<td width="50%">

### 📋 Application Tracker
Kanban-style board to track every application — from `Discovered` → `Applied` → `Interview` → `Offer`. Never lose track of a job again.

</td>
</tr>
<tr>
<td width="50%">

### 🎤 Interview Prep
AI-generated interview questions tailored to each job posting. Practice before you walk in.

</td>
<td width="50%">

### ⚙️ Settings & Preferences
Configure your job preferences, target roles, locations, salary expectations, and more. JobForge adapts to you.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌──────────────┐          ┌──────────────────────┐   │
│   │   Frontend   │  HTTP    │   Backend (FastAPI)  │   │
│   │  React/Vite  │◄────────►│   Railway Hosted     │   │
│   │   Vercel     │          │                      │   │
│   └──────────────┘          └──────────┬───────────┘   │
│                                        │               │
│                             ┌──────────▼───────────┐   │
│                             │   PostgreSQL DB       │   │
│                             │   Railway Hosted      │   │
│                             └──────────────────────┘   │
│                                        │               │
│                             ┌──────────▼───────────┐   │
│                             │   Groq AI API        │   │
│                             │   LLM Inference      │   │
│                             └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TailwindCSS |
| **Backend** | Python, FastAPI |
| **Database** | PostgreSQL |
| **AI / LLM** | Groq API |
| **Frontend Deploy** | Vercel |
| **Backend Deploy** | Railway |

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Groq API Key → [console.groq.com](https://console.groq.com)

### 1. Clone the repo

```bash
git clone https://github.com/prats010/jobforge.git
cd jobforge
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/jobforge
GROQ_API_KEY=your_groq_api_key_here
```

Run the backend:
```bash
uvicorn main:app --reload
```

API docs available at → `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

Run the frontend:
```bash
npm run dev
```

App runs at → `http://localhost:5173`

---

## 🌐 API Endpoints

| Route | Description |
|---|---|
| `GET /api/jobs` | Fetch all discovered jobs |
| `GET /api/jobs/stats` | Job pipeline statistics |
| `POST /api/scanner/run` | Trigger a new job scan |
| `GET /api/scanner/history` | Scan history |
| `GET /api/scanner/sources` | Configured job sources |
| `POST /api/evaluator` | AI evaluation of jobs |
| `GET /api/cv/base` | Fetch base resume |
| `POST /api/cv/tailor` | AI-tailored CV for a job |
| `GET /api/tracker/board` | Kanban board data |
| `GET /api/interview` | Interview prep questions |
| `GET /api/settings` | User settings |

---

## 🚢 Deployment

| Service | Platform | Status |
|---|---|---|
| Frontend | Vercel | [![Vercel](https://img.shields.io/badge/deployed-success-brightgreen?style=flat-square)](https://jobforge-snowy.vercel.app) |
| Backend | Railway | [![Railway](https://img.shields.io/badge/deployed-success-brightgreen?style=flat-square)](https://railway.app) |
| Database | Railway PostgreSQL | [![DB](https://img.shields.io/badge/connected-success-brightgreen?style=flat-square)]() |

---

## 📁 Project Structure

```
jobforge/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # App configuration
│   ├── database.py          # DB connection
│   ├── models.py            # SQLAlchemy models
│   ├── requirements.txt     # Python dependencies
│   ├── routers/
│   │   ├── jobs.py
│   │   ├── scanner.py
│   │   ├── evaluator.py
│   │   ├── cv.py
│   │   ├── tracker.py
│   │   ├── interview.py
│   │   └── settings.py
│   └── services/
│       └── groq_service.py  # Groq AI integration
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

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

<div align="center">

**Built with 🔥 by [Prathamesh Bhamare](https://github.com/prats010)**

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer" width="100%"/>

</div>

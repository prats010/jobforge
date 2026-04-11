# Quick Start: Deployment Checklist

## Phase 1: GitHub Setup (5 min)
- [ ] Initialize git: `git init`
- [ ] Add .gitignore (created)
- [ ] Commit: `git commit -m "Initial commit"`
- [ ] Create GitHub repo
- [ ] Push: `git push -u origin main`

## Phase 2: Railway Backend (10 min)
- [ ] Create Railway account at https://railway.app
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Run `railway login` and `railway init`
- [ ] Add PostgreSQL: `railway add --plugin postgres`
- [ ] Set environment variables:
  ```
  railway variables set GROQ_API_KEY=your_key
  railway variables set CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
  ```
- [ ] Deploy: `railway up`
- [ ] Copy the Railway URL from logs (https://jobforge-prod-xxxx.railway.app)

## Phase 3: Vercel Frontend (5 min)
- [ ] Go to https://vercel.com
- [ ] Import your GitHub repo
- [ ] Settings:
  - Root Directory: `frontend`
  - Build Command: `npm run build`
  - Output: `dist`
- [ ] Add Environment Variable: `VITE_API_URL=<RAILWAY_URL>`
- [ ] Deploy
- [ ] Copy Vercel URL (https://jobforge.vercel.app)

## Phase 4: Update CORS (2 min)
- [ ] Go back to Railway dashboard
- [ ] Update `CORS_ORIGINS` to: `http://localhost:5173,<VERCEL_URL>`
- [ ] Railway auto-redeplojs

## Phase 5: Test (5 min)
- [ ] Visit https://jobforge.vercel.app
- [ ] Try adding Groq API key in Settings
- [ ] Try scanning a job

---

## Useful Links
- Railway Dashboard: https://railway.app/dashboard
- Vercel Dashboard: https://vercel.com/dashboard
- See logs: Railway → Project → Deployments → View Logs

**Estimated Total Time**: 25-30 minutes

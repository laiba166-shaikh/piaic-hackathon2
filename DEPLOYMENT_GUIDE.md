# Deployment Guide

This guide covers deploying Phase II (frontend on Vercel, backend on Railway) and Phase III (AI Chatbot) of the Task Mate application.

---

## Table of Contents

1. [Phase II — Full-Stack Web App](#phase-ii--full-stack-web-app)
   - [Prerequisites](#prerequisites)
   - [Step 1: Set Up Neon Database](#step-1-set-up-neon-database)
   - [Step 2: Deploy Backend on Railway](#step-2-deploy-backend-on-railway)
   - [Step 3: Deploy Frontend on Vercel](#step-3-deploy-frontend-on-vercel)
   - [Step 4: Wire Everything Together](#step-4-wire-everything-together)
   - [Environment Variables Reference](#environment-variables-reference)
   - [Key Notes & Things to Consider](#key-notes--things-to-consider)
2. [Phase III — AI Chatbot](#phase-iii--ai-chatbot)

---

## Phase II — Full-Stack Web App

### Prerequisites

- GitHub account with your repo pushed
- [Neon](https://neon.tech) account (free tier works)
- [Railway](https://railway.app) account
- [Vercel](https://vercel.com) account

---

### Step 1: Set Up Neon Database

This project uses **two separate sets of tables** in the database:
- **Tasks tables** — managed by the FastAPI backend (Alembic migrations)
- **Auth tables** — managed by Better Auth (`user`, `session`, `account`, `verification`)

You can use a **single Neon database** for both — they use different table names and never conflict.

1. Go to [neon.tech](https://neon.tech) → create a new project
2. Copy the connection string from the dashboard — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
3. Keep this handy — you will use it in both Railway and Vercel

> **Note:** If you want strict isolation, create two Neon branches (same project, different branches). Use one connection string for Railway and another for Vercel. For a hackathon, a single database is fine.

---

### Step 2: Deploy Backend on Railway

#### 2a. Create the service

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your repository
3. Go to service → **Settings** → set **Root Directory** to `src/core/backend`
4. Set the following in **Settings → Deploy**:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Pre-deploy Command:** `alembic upgrade head`

> Setting root directory to `src/core/backend` ensures Railway only sees the backend — CLI code, specs, and other project files are ignored entirely.

#### 2b. Set environment variables on Railway

Go to your service → **Variables** tab and add:

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | Your Neon connection string | Tasks tables will be created here |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Set after Vercel deploy (see Step 4) |
| `DEBUG` | `False` | Always False in production |

> Do **not** set `PORT` manually — Railway injects it automatically.

#### 2c. Get your Railway backend URL

After a successful deploy:  
**Service → Settings → Networking → Generate Domain**

You will get a URL like `https://your-service.up.railway.app`. Save this — you need it for Vercel.

---

### Step 3: Deploy Frontend on Vercel

#### 3a. Create the project

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your GitHub repo
2. Set **Root Directory** to `src/core/frontend`
3. Framework will be auto-detected as **Next.js**
4. Click **Deploy** — let the first deploy run (it will fail on env vars, that is expected)

#### 3b. Set environment variables on Vercel

Go to project → **Settings** → **Environment Variables** and add:

| Variable | Value | Visible in browser? | Notes |
|---|---|---|---|
| `DATABASE_URL` | Your Neon connection string | No | Better Auth user/session tables |
| `BETTER_AUTH_SECRET` | Random 32+ char string | No | Signs/encrypts sessions |
| `BETTER_AUTH_URL` | `https://your-app.vercel.app` | No | Better Auth internal base URL |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | `https://your-app.vercel.app` | Yes | Auth client in browser |
| `NEXT_PUBLIC_API_URL` | `https://your-service.up.railway.app` | Yes | Backend URL for browser API calls |

> Generate a secret: `openssl rand -base64 32`

> `NEXT_PUBLIC_*` variables are the only ones readable in the browser. Never add `NEXT_PUBLIC_` to `DATABASE_URL`, `BETTER_AUTH_SECRET`, or any other secret.

#### 3c. Redeploy

After setting env vars, go to **Deployments** → click the latest → **Redeploy**. Vercel does not automatically redeploy when you add env vars.

#### 3d. Run Better Auth migrations

Better Auth needs to create its auth tables (`user`, `session`, `account`, `verification`) in your Neon database. Run this once locally pointing at your production DB:

```bash
cd src/core/frontend
DATABASE_URL="your-neon-connection-string" npx @better-auth/cli migrate
```

---

### Step 4: Wire Everything Together

Now that both services are deployed, update the cross-references:

1. **Update Railway → `FRONTEND_URL`** with your actual Vercel URL (e.g. `https://task-mate-hazel.vercel.app`)
   - This is used by the backend to fetch JWKS public keys for JWT verification
   - This is also used for CORS — `settings.FRONTEND_URL` is in `allow_origins`

2. **Verify the Railway deployment** picks up the new env var (Railway auto-redeploys on variable changes)

3. **Test the connection** — visit `https://your-backend.up.railway.app/health` and confirm you get `{"status": "ok"}`

---

### Environment Variables Reference

#### When to set each variable

| Timing | Action |
|---|---|
| Before Railway deploy | `DATABASE_URL`, `DEBUG` on Railway |
| After Vercel deploy | `FRONTEND_URL` on Railway (now you have the real URL) |
| Before Vercel redeploy | All 5 Vercel variables |
| Once (local CLI) | Run Better Auth migration with prod `DATABASE_URL` |

#### Why two `DATABASE_URL` values?

Both Railway and Vercel have a `DATABASE_URL` but they store different things:

| Service | Tables stored | Who manages migrations |
|---|---|---|
| Railway (backend) | `tasks` | Alembic (`alembic upgrade head`) |
| Vercel (frontend) | `user`, `session`, `account`, `verification` | Better Auth CLI (`npx @better-auth/cli migrate`) |

They can point to the same Neon database — just ensure both migration tools have run before you use the app.

#### Why `BETTER_AUTH_URL` vs `NEXT_PUBLIC_BETTER_AUTH_URL`?

| Variable | Used in | Why |
|---|---|---|
| `BETTER_AUTH_URL` | `lib/auth.ts` (server-side) | Tells Better Auth its own base URL for building callback/redirect URLs |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | `lib/auth-client.ts` (browser) | Browser can only read `NEXT_PUBLIC_*` variables — without this it defaults to `localhost:3000` |

Both must be set to the same Vercel production URL.

---

### Key Notes & Things to Consider

**CORS**
- `FRONTEND_URL` in Railway must have **no trailing slash** — `https://your-app.vercel.app` not `https://your-app.vercel.app/`
- CORS `allow_origins` in `main.py` uses `settings.FRONTEND_URL` — so updating the Railway env var is all you need to do

**JWT Verification**
- The backend fetches JWKS public keys from `FRONTEND_URL/.well-known/jwks.json` to verify JWT tokens issued by Better Auth
- If `FRONTEND_URL` is wrong or missing, all authenticated API calls will fail with 401

**CI/CD on Railway**
- Railway has a "Wait for CI" option that blocks deploys until GitHub Actions passes
- If your CI is failing, either fix it or disable this option: service → Settings → Deploy → disable CI check suite

**Secrets**
- Never commit `.env` or `.env.local` files — they are git-ignored
- Never use `NEXT_PUBLIC_` prefix on secrets — anything with that prefix is embedded in the client bundle and visible to anyone

**Database migrations**
- Alembic runs automatically on Railway via the pre-deploy command
- Better Auth migrations must be run manually once from your local machine
- If you add new Alembic migrations, Railway will apply them automatically on next deploy

**Vercel redeploys**
- Vercel auto-redeploys on every `git push` to your connected branch
- Vercel does **not** auto-redeploy when you change environment variables — trigger manually via Deployments → Redeploy

---

## Phase III — AI Chatbot

Phase III adds an AI-powered chat interface using OpenAI Agents SDK and MCP tools. The backend is the same FastAPI service — extended with new chat endpoints. The frontend replaces the current UI with OpenAI ChatKit.

### New Components

| Component | Technology | Deployed On |
|---|---|---|
| ChatKit UI | OpenAI ChatKit (Next.js) | Vercel |
| Chat API | FastAPI + OpenAI Agents SDK | Railway (same service) |
| MCP Server | Official MCP SDK | Railway (same service) |
| Database | Neon PostgreSQL (same DB, new tables) | Neon |

### New Database Tables

Three new tables are needed alongside the existing `tasks` table:

| Table | Fields | Purpose |
|---|---|---|
| `conversation` | user_id, id, created_at, updated_at | Chat session |
| `message` | user_id, id, conversation_id, role, content, created_at | Chat history |

Create Alembic migrations for these before deploying. Railway will run them automatically via `alembic upgrade head`.

### Deploying Phase III Backend (Railway)

No new Railway service needed — extend the existing one:

1. Add new chat routes to FastAPI (`POST /api/{user_id}/chat`)
2. Add MCP tools for `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
3. Create Alembic migrations for `conversation` and `message` tables
4. Add new environment variables on Railway:

| Variable | Value | Notes |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | Required for Agents SDK |

Push to GitHub — Railway auto-redeploys.

### Deploying Phase III Frontend (Vercel)

OpenAI ChatKit requires domain allowlist configuration before it works in production:

#### Step 1 — Add your domain to OpenAI's allowlist

1. Go to [platform.openai.com/settings/organization/security/domain-allowlist](https://platform.openai.com/settings/organization/security/domain-allowlist)
2. Click **Add domain**
3. Enter your Vercel URL without trailing slash: `https://your-app.vercel.app`
4. Save — OpenAI will provide a **domain key**

> This step is mandatory. ChatKit hosted mode will not work without it. Local `localhost` development works without a domain key.

#### Step 2 — Add new environment variable on Vercel

| Variable | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | Your domain key from OpenAI | Required for ChatKit hosted mode |

#### Step 3 — Redeploy Vercel

Go to Deployments → Redeploy after adding the env var.

### Phase III Environment Variables — Full Reference

#### Railway (Backend)

| Variable | Value |
|---|---|
| `DATABASE_URL` | Neon connection string (same as Phase II) |
| `FRONTEND_URL` | `https://your-app.vercel.app` (same as Phase II) |
| `DEBUG` | `False` |
| `OPENAI_API_KEY` | Your OpenAI API key |

#### Vercel (Frontend)

| Variable | Value |
|---|---|
| `DATABASE_URL` | Neon connection string (same as Phase II) |
| `BETTER_AUTH_SECRET` | Same secret as Phase II |
| `BETTER_AUTH_URL` | `https://your-app.vercel.app` (same as Phase II) |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | `https://your-app.vercel.app` (same as Phase II) |
| `NEXT_PUBLIC_API_URL` | `https://your-backend.up.railway.app` (same as Phase II) |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | Your OpenAI ChatKit domain key |

### Key Notes for Phase III

**Stateless architecture** — The FastAPI server holds no conversation state between requests. All state (conversation history) lives in the database. This means:
- Any Railway instance can handle any request
- Server restarts do not lose conversations
- Horizontal scaling works without sticky sessions

**MCP tools run inside the same process** — The MCP server is not a separate deployment. It runs as an in-process tool provider within the FastAPI server. No additional service or port needed.

**OpenAI Agents SDK vs API key costs** — Every chat message triggers the Agents SDK which calls OpenAI's API. Monitor your OpenAI usage dashboard to avoid unexpected costs.

**ChatKit domain key is per-domain** — If you use a custom domain or a different Vercel URL, you must add it separately to OpenAI's allowlist and get a new domain key.

**Conversation context** — The stateless request cycle fetches full conversation history from the database on every request. For long conversations this grows — consider adding a message limit (e.g. last 20 messages) to keep token usage bounded.

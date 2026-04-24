# Bright AEO Engine — Azure Deployment Guide

This guide takes the app from GitHub to a live Azure App Service URL that Bright internal users can access with their Microsoft login. Estimated time: 30–45 minutes.

For the current live deployment state (what's running, what's configured, what's pending), see **[INSTALL.md](INSTALL.md)**.

---

## Overview

The app runs as a single Python process on Azure App Service. FastAPI serves both the API and the built React frontend, so there is only one service to provision. User data (run results, config changes) is stored on Azure's persistent `/home/` filesystem — it survives restarts and new deployments.

GitHub Actions builds the frontend and deploys to Azure automatically on every push to `main`.

---

## Prerequisites

- Azure subscription with permission to create App Services
- Owner/Contributor access to the GitHub repository (`bcwb/bright-aeo-engine`)
- At least one AI model API key (Anthropic, OpenAI, Google, or Perplexity) — models without a key are skipped automatically

---

## Step 1 — Create the Azure App Service

1. In the Azure portal search bar, type **App Services** and open it
2. Click **+ Create → Web App**
3. Fill in the form:

   | Field | Value |
   |---|---|
   | **Subscription** | Bright Internal |
   | **Resource Group** | Marketing (or create new) |
   | **Name** | e.g. `Bright-AEO` (becomes the URL — must be globally unique) |
   | **Publish** | Code |
   | **Runtime stack** | Python 3.11 |
   | **Operating System** | Linux |
   | **Region** | West Europe (UK South may have quota limits) |
   | **Plan** | B1 Basic is sufficient for internal use |

4. Click **Review + create → Create**

> **Quota note:** If you see "operation cannot be completed without additional quota", switch region to West Europe or North Europe.

---

## Step 2 — Configure App Settings

Go to **Settings → Environment variables → App settings** and add each of the following using **+ Add**. Click **Apply** when done.

### API keys

All keys are optional — models without a key are skipped. Add whichever you have.

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `OPENAI_API_KEY` | Your OpenAI key |
| `GOOGLE_API_KEY` | Your Google AI key |
| `PERPLEXITY_API_KEY` | Your Perplexity key |

You can add missing keys later — the app picks them up on restart without redeployment.

### Runtime paths (required)

| Name | Value |
|---|---|
| `CONFIG_PATH` | `/home/data/config.json` |
| `RESULTS_DIR` | `/home/data/results` |

These point config and run results at `/home/data/`, which persists across deployments. Without these, a new deployment would reset your config and delete saved runs.

### Deployment settings (required)

| Name | Value |
|---|---|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `false` |
| `WEBSITES_PORT` | `8000` |

---

## Step 3 — Set the Startup Command

Go to **Settings → Configuration → General settings**.

Set the **Startup command** to:

```
bash /home/site/wwwroot/startup.sh
```

Click **Save**.

---

## Step 4 — Restrict access to Bright staff (Easy Auth)

This locks the app to Microsoft accounts in your Azure AD tenant — only people with a `@brightsg.com` Microsoft login can open it.

1. Go to **Settings → Authentication**
2. Click **Add identity provider**
3. Choose **Microsoft**
4. Set **Tenant type** to **Workforce** (Azure AD)
5. Leave all defaults — Azure fills in the app registration automatically
6. Under **Unauthenticated requests**, select **HTTP 302 Found — redirect to login page**
7. Click **Add**

Users who aren't logged in are redirected to the Microsoft login page automatically.

---

## Step 5 — Connect GitHub Actions for automatic deployments

### 5a — Get the publish profile

1. In the App Service, go to **Overview**
2. Click **Download publish profile** — this downloads an XML file
3. Open the file in a text editor and copy the entire contents

### 5b — Add GitHub secrets and variables

In the GitHub repository, go to **Settings → Secrets and variables → Actions**.

Add a **Secret**:

| Name | Value |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Paste the full contents of the publish profile XML |

Add a **Variable** (Variables tab, not Secrets):

| Name | Value |
|---|---|
| `AZURE_WEBAPP_NAME` | Your App Service name, e.g. `Bright-AEO` |

---

## Step 6 — Trigger the first deployment

Go to the GitHub repository → **Actions → Deploy to Azure App Service → Run workflow → Run workflow**.

The workflow will:
1. Check out the code
2. Build the React frontend (`npm ci && npm run build`)
3. Deploy the full package (including the built frontend) to App Service

First deployment: ~3–4 minutes. Subsequent deployments: ~1–2 minutes.

After that, every push to `main` deploys automatically.

---

## Step 7 — Verify

1. Open your App Service URL (shown in the Overview blade, or `https://<name>.azurewebsites.net`)
2. You'll be redirected to the Microsoft login page — sign in with your Bright account
3. The AEO Engine dashboard should load

If you see a 503 error, check: **Monitoring → Log stream**.

---

## How data persists

| Data | Location | Behaviour |
|---|---|---|
| Run results | `/home/data/results/` | Persists forever — never touched by deployments |
| Config (prompts, peer sets) | `/home/data/config.json` | Copied from the repo on first deploy only — UI changes persist |
| Asset files (tone of voice, brand guidelines) | `/home/site/wwwroot/backend/assets/` | Overwritten on each deployment — edit in the repo |

---

## Local development (unchanged)

```bash
# Terminal 1 — backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

The `frontend/dist/` folder only exists after `npm run build`. In local dev it's absent, so FastAPI skips static file serving and Vite's proxy handles the frontend as usual.

---

## Updating the app

Push to `main` — GitHub Actions deploys automatically. Existing run results and config are preserved.

---

## Adding a missing API key

1. In the App Service go to **Settings → Environment variables**
2. Add or update the key
3. Click **Apply** — the app restarts and the model becomes available immediately

---

## Troubleshooting

| Symptom | Check |
|---|---|
| 503 on startup | Log stream — likely a startup.sh error or missing env var |
| Runs disappear after deployment | Confirm `RESULTS_DIR=/home/data/results` and `CONFIG_PATH=/home/data/config.json` are set |
| GitHub Actions failing | Actions tab — usually a missing secret or wrong app name variable |
| Login loop / auth error | Easy Auth configured and app restarted after saving |
| `POST /assets/open` returns 500 | Expected on Azure — this opens files in a local editor and is dev-only |
| Quota error creating App Service | Switch region to West Europe or North Europe |

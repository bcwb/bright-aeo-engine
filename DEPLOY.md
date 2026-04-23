# Bright AEO Engine — Azure Deployment Guide

This guide takes the app from GitHub to a live Azure App Service URL that Bright internal users can access with their Microsoft login. Estimated time: 30–45 minutes.

---

## Overview

The app runs as a single Python process on Azure App Service. FastAPI serves both the API and the built React frontend, so there is only one service to provision. User data (run results, config changes) is stored on Azure's persistent `/home/` filesystem — it survives restarts and new deployments.

GitHub Actions builds the frontend and deploys to Azure automatically on every push to `main`.

---

## Prerequisites

- Azure subscription with permission to create App Services
- Owner/Contributor access to the GitHub repository (`bcwb/bright-aeo-engine`)
- Your four API keys: Anthropic, OpenAI, Google, Perplexity

---

## Step 1 — Create the Azure App Service

1. In the Azure portal, go to **App Services → Create → Web App**
2. Fill in the form:

   | Field | Value |
   |---|---|
   | **Resource Group** | Create new, e.g. `rg-bright-aeo` |
   | **Name** | e.g. `bright-aeo-engine` (must be globally unique — becomes the URL) |
   | **Publish** | Code |
   | **Runtime stack** | Python 3.11 |
   | **Operating System** | Linux |
   | **Region** | UK South (or nearest to your users) |
   | **Plan** | B1 Basic is sufficient for internal use |

3. Click **Review + create → Create**

---

## Step 2 — Configure App Settings

Once the App Service is created, go to **Settings → Environment variables → App settings** and add all of the following. Click **Add** for each one.

### API keys (required)

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `OPENAI_API_KEY` | Your OpenAI key |
| `GOOGLE_API_KEY` | Your Google AI key |
| `PERPLEXITY_API_KEY` | Your Perplexity key (optional — omit to skip Perplexity) |

### Runtime paths (required)

| Name | Value |
|---|---|
| `CONFIG_PATH` | `/home/data/config.json` |
| `RESULTS_DIR` | `/home/data/results` |

These point config and run results at `/home/data/`, which persists across deployments. Without these, a new deployment would reset your config and delete saved runs.

### Deployment setting (required)

| Name | Value |
|---|---|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `false` |
| `WEBSITES_PORT` | `8000` |

Click **Apply** to save all settings.

---

## Step 3 — Set the Startup Command

In the App Service, go to **Settings → Configuration → General settings**.

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

In your GitHub repository, go to **Settings → Secrets and variables → Actions**.

Add a **Secret**:

| Name | Value |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Paste the full contents of the publish profile XML |

Add a **Variable** (under the Variables tab, not Secrets):

| Name | Value |
|---|---|
| `AZURE_WEBAPP_NAME` | The App Service name you chose in Step 1, e.g. `bright-aeo-engine` |

---

## Step 6 — Trigger the first deployment

Push any change to `main` — or go to **Actions → Deploy to Azure App Service → Run workflow** to trigger it manually.

The workflow will:
1. Check out the code
2. Build the React frontend (`npm ci && npm run build`)
3. Deploy the entire package (including the built frontend) to App Service

The first deployment takes about 3–4 minutes. Subsequent deployments are faster (~1–2 minutes).

---

## Step 7 — Verify

1. Open `https://<your-app-name>.azurewebsites.net`
2. You'll be redirected to the Microsoft login page — sign in with your Bright account
3. The AEO Engine dashboard should load

If you see a 500 error, check the App Service logs: **Monitoring → Log stream**.

---

## How data persists

| Data | Location | Behaviour |
|---|---|---|
| Run results | `/home/data/results/` | Persists forever — never touched by deployments |
| Config (prompts, peer sets) | `/home/data/config.json` | Copied from the repo on first deploy only — UI changes persist |
| Asset files (tone of voice, brand guidelines) | `/home/site/wwwroot/backend/assets/` | Overwritten on each deployment — edit these in the repo |

---

## Local development (unchanged)

Local dev still works exactly as before — no Azure account needed:

```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

The `frontend/dist/` folder only exists after `npm run build`. In local dev it's absent, so FastAPI doesn't try to serve static files and Vite's proxy handles the frontend as usual.

---

## Updating the app

To deploy a new version:
1. Push to `main` — the GitHub Actions workflow runs automatically
2. The new code is live in ~2 minutes
3. Existing run results and config are preserved (they're on `/home/data/`, not in wwwroot)

---

## Troubleshooting

| Symptom | Check |
|---|---|
| App won't start — 503 error | Log stream → likely a missing API key or startup.sh error |
| Runs disappear after deployment | Confirm `RESULTS_DIR=/home/data/results` and `CONFIG_PATH=/home/data/config.json` are set |
| GitHub Actions failing | Check the Actions tab — usually a missing secret or wrong app name |
| Login loop / auth error | Check Easy Auth is configured and the App Service has restarted after saving |
| `POST /assets/open` returns 500 | Expected on Azure — this feature opens files in a local editor and is dev-only |

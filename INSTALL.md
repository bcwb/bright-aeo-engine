# Bright AEO Engine — Current Installation State

This document records the live deployment. Update it whenever infrastructure changes, keys are added, or the deployment state changes. For setup instructions see [DEPLOY.md](DEPLOY.md).

---

## Live deployment

| | |
|---|---|
| **URL** | https://bright-aeo.azurewebsites.net |
| **App Service name** | Bright-AEO |
| **Subscription** | Bright Internal |
| **Resource Group** | Marketing |
| **Region** | West Europe |
| **Runtime** | Python 3.11 |
| **Plan** | B1 Basic |
| **Deployed version** | v1.4.1 (pending first deployment) |

---

## App Settings configured

| Setting | Status | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Set | |
| `OPENAI_API_KEY` | ⏳ Pending | Add when key is available |
| `GOOGLE_API_KEY` | ⏳ Pending | Add when key is available |
| `PERPLEXITY_API_KEY` | ⏳ Pending | Add when key is available |
| `CONFIG_PATH` | ✅ Set | `/home/data/config.json` |
| `RESULTS_DIR` | ✅ Set | `/home/data/results` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | ✅ Set | `false` |
| `WEBSITES_PORT` | ✅ Set | `8000` |

---

## GitHub Actions

| | |
|---|---|
| **Workflow** | `.github/workflows/deploy.yml` |
| **Trigger** | Push to `main` + manual `workflow_dispatch` |
| **`AZURE_WEBAPP_NAME` variable** | ⏳ Pending — add to GitHub repo variables |
| **`AZURE_WEBAPP_PUBLISH_PROFILE` secret** | ⏳ Pending — download from Azure and add to GitHub secrets |
| **Status** | Not yet wired up |

---

## Access control

| | |
|---|---|
| **Easy Auth** | ⏳ Pending — Microsoft identity provider not yet configured |
| **Access** | Currently open (no auth) |

---

## Startup command

| | |
|---|---|
| **Command** | `bash /home/site/wwwroot/startup.sh` |
| **Status** | ⏳ Pending — not yet set in App Service configuration |

---

## Known pending actions

- [ ] Set startup command in App Service → Configuration → General settings
- [ ] Configure Easy Auth (Microsoft identity provider)
- [ ] Download publish profile from Azure and add `AZURE_WEBAPP_PUBLISH_PROFILE` secret to GitHub
- [ ] Add `AZURE_WEBAPP_NAME` variable to GitHub repo
- [ ] Trigger first deployment via GitHub Actions
- [ ] Verify app loads at https://bright-aeo.azurewebsites.net
- [ ] Add remaining API keys (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, `PERPLEXITY_API_KEY`) when available

---

## Local development

| | |
|---|---|
| **Backend** | `cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000` |
| **Frontend** | `cd frontend && npm run dev` |
| **Local URL** | http://localhost:5173 |

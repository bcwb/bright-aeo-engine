const BASE = ''  // proxied via Vite to http://localhost:8000

async function json(res) {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  return res.json()
}

// ── Config ────────────────────────────────────────────────────────────────

export const getConfig = () =>
  fetch(`${BASE}/config`).then(json)

export const addPrompt = (prompt) =>
  fetch(`${BASE}/config/prompts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prompt),
  }).then(json)

export const updatePrompt = (id, updates) =>
  fetch(`${BASE}/config/prompts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  }).then(json)

export const deletePrompt = (id) =>
  fetch(`${BASE}/config/prompts/${id}`, { method: 'DELETE' }).then(json)

export const addCompetitor = (competitor) =>
  fetch(`${BASE}/config/competitors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(competitor),
  }).then(json)

export const updateCompetitor = (id, updates) =>
  fetch(`${BASE}/config/competitors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  }).then(json)

export const deleteCompetitor = (id) =>
  fetch(`${BASE}/config/competitors/${id}`, { method: 'DELETE' }).then(json)

export const addPeerSet = (label) =>
  fetch(`${BASE}/config/peer_sets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label }),
  }).then(json)

export const deletePeerSet = (key) =>
  fetch(`${BASE}/config/peer_sets/${key}`, { method: 'DELETE' }).then(json)

export const updateModels = (updates) =>
  fetch(`${BASE}/config/models`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  }).then(json)

export const updateBenchmarkBrand = (name) =>
  fetch(`${BASE}/config/benchmark_brand`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  }).then(json)

// ── Runs ──────────────────────────────────────────────────────────────────

export const triggerRun = (body = {}) =>
  fetch(`${BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(json)

export const getRuns = () =>
  fetch(`${BASE}/runs`).then(json)

export const getRun = (runId) =>
  fetch(`${BASE}/runs/${runId}`).then(json)

export const createRunStream = (runId) =>
  new EventSource(`${BASE}/runs/${runId}/stream`)

// ── Recommendations ───────────────────────────────────────────────────────

export const getRecommendations = (runId) =>
  fetch(`${BASE}/recommendations/${runId}`).then(r => r.ok ? r.json() : null)

// ── Content ───────────────────────────────────────────────────────────────

export const triggerContent = (body) =>
  fetch(`${BASE}/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(json)

export const getContent = (runId) =>
  fetch(`${BASE}/content/${runId}`).then(json)

export const approveContent = (contentId, reviewerName) =>
  fetch(`${BASE}/content/${contentId}/approve`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewer_name: reviewerName }),
  }).then(json)

// ── Targeting ─────────────────────────────────────────────────────────────

export const getTargeting = (runId) =>
  fetch(`${BASE}/targeting/${runId}`).then(json)

// ── Logs ──────────────────────────────────────────────────────────────────

export const getLogs = (level = null, limit = 200) => {
  const params = new URLSearchParams()
  if (level) params.set('level', level)
  params.set('limit', limit)
  return fetch(`${BASE}/logs?${params}`).then(json)
}

export const clearLogs = () =>
  fetch(`${BASE}/logs`, { method: 'DELETE' })

// ── Assets ────────────────────────────────────────────────────────────────

export const openAsset = (file) =>
  fetch(`${BASE}/assets/open`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file }),
  }).then(json)

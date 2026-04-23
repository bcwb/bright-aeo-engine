import { useState, useEffect, useRef, useCallback } from 'react'
import { getLogs, clearLogs } from '../api'

const LEVELS = ['ALL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

const LEVEL_STYLES = {
  ERROR:    'bg-red-100 text-red-700 border border-red-200',
  WARNING:  'bg-brand-orange/10 text-brand-orange border border-brand-orange/20',
  INFO:     'bg-brand-blue/10 text-brand-blue border border-brand-blue/20',
  DEBUG:    'bg-gray-100 text-gray-500 border border-gray-200',
  CRITICAL: 'bg-red-200 text-red-800 border border-red-300',
}

const LEVEL_DOT = {
  ERROR:    'bg-red-500',
  WARNING:  'bg-brand-orange',
  INFO:     'bg-brand-blue',
  DEBUG:    'bg-gray-400',
  CRITICAL: 'bg-red-700',
}

// Known fields that are always shown in the main row — everything else is context
const RESERVED_FIELDS = new Set(['ts', 'level', 'logger', 'event'])

function formatTime(ts) {
  try {
    return new Date(ts).toLocaleTimeString('en-GB', { hour12: false })
  } catch {
    return ts
  }
}

function formatLogger(name) {
  // 'agents.orchestrator' → 'orchestrator', 'main' → 'api'
  const parts = name.split('.')
  return parts[parts.length - 1] === '__main__' ? 'api' : parts[parts.length - 1]
}

function ContextPill({ k, v }) {
  return (
    <span className="inline-flex items-center gap-1 font-mono text-xs bg-gray-100 text-gray-600 rounded px-1.5 py-0.5">
      <span className="text-gray-400">{k}</span>
      <span>=</span>
      <span className="text-gray-700">{String(v)}</span>
    </span>
  )
}

function LogRow({ entry }) {
  const [expanded, setExpanded] = useState(false)

  const ctx = Object.entries(entry).filter(([k]) => !RESERVED_FIELDS.has(k))
  const hasCtx = ctx.length > 0
  const isError = entry.level === 'ERROR' || entry.level === 'CRITICAL'

  return (
    <div
      className={`border-b border-gray-100 last:border-0 ${isError ? 'bg-red-50/40' : 'hover:bg-gray-50/60'}`}
    >
      {/* Main row */}
      <button
        className="w-full text-left px-4 py-2.5 flex items-start gap-3"
        onClick={() => hasCtx && setExpanded(e => !e)}
        disabled={!hasCtx}
      >
        {/* Level badge */}
        <span className={`shrink-0 mt-0.5 text-xs font-semibold px-1.5 py-0.5 rounded font-mono ${LEVEL_STYLES[entry.level] || LEVEL_STYLES.DEBUG}`}>
          {entry.level}
        </span>

        {/* Time */}
        <span className="shrink-0 font-mono text-xs text-gray-400 mt-0.5 w-16">
          {formatTime(entry.ts)}
        </span>

        {/* Logger */}
        <span className="shrink-0 text-xs text-gray-400 mt-0.5 w-28 truncate font-mono">
          {formatLogger(entry.logger || '')}
        </span>

        {/* Event message */}
        <span className={`flex-1 min-w-0 text-xs ${isError ? 'text-red-700 font-medium' : 'text-gray-700'}`}>
          {entry.event}
        </span>

        {/* Context pills — collapsed preview (first 2) */}
        {!expanded && ctx.length > 0 && (
          <div className="shrink-0 flex items-center gap-1 ml-2">
            {ctx.slice(0, 2).map(([k, v]) => (
              <ContextPill key={k} k={k} v={v} />
            ))}
            {ctx.length > 2 && (
              <span className="text-xs text-gray-400">+{ctx.length - 2}</span>
            )}
          </div>
        )}

        {hasCtx && (
          <span className="shrink-0 text-gray-300 text-xs mt-0.5 ml-1">
            {expanded ? '▲' : '▼'}
          </span>
        )}
      </button>

      {/* Expanded context */}
      {expanded && (
        <div className="px-4 pb-3 pt-0 bg-gray-50 border-t border-gray-100">
          <div className="flex flex-wrap gap-1.5">
            {ctx.map(([k, v]) => (
              <ContextPill key={k} k={k} v={v} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Monitor() {
  const [events, setEvents]         = useState([])
  const [levelFilter, setLevel]     = useState('ALL')
  const [autoRefresh, setAuto]      = useState(true)
  const [loading, setLoading]       = useState(false)
  const [lastRefresh, setLastRefresh] = useState(null)
  const intervalRef = useRef(null)

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    try {
      const level = levelFilter === 'ALL' ? null : levelFilter
      const data = await getLogs(level, 500)
      setEvents(data)
      setLastRefresh(new Date())
    } finally {
      setLoading(false)
    }
  }, [levelFilter])

  // Fetch on mount and when filter changes
  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  // Auto-refresh every 5 seconds
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchLogs, 5000)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [autoRefresh, fetchLogs])

  async function handleClear() {
    if (!confirm('Clear all log events from the buffer?')) return
    await clearLogs()
    setEvents([])
  }

  // Summary counts from the full unfiltered fetch — count by level
  const errorCount   = events.filter(e => e.level === 'ERROR' || e.level === 'CRITICAL').length
  const warningCount = events.filter(e => e.level === 'WARNING').length
  const infoCount    = events.filter(e => e.level === 'INFO').length
  const debugCount   = events.filter(e => e.level === 'DEBUG').length

  // Apply client-side level filter for display (backend also filters, but
  // keeping this means we can show summary counts for ALL even when filtered)
  const displayed = levelFilter === 'ALL'
    ? events
    : events.filter(e => e.level === levelFilter)

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="text-2xl font-bold text-brand-navy font-heading mb-1">Monitor</h1>
      <p className="text-sm text-gray-500 mb-6">
        Live backend log stream — errors, warnings, and audit events.
        Buffer holds the last 500 events.
      </p>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <SummaryCard
          label="Errors"
          count={errorCount}
          dot="bg-red-500"
          highlight={errorCount > 0}
          alertStyle
        />
        <SummaryCard
          label="Warnings"
          count={warningCount}
          dot={LEVEL_DOT.WARNING}
        />
        <SummaryCard
          label="Info events"
          count={infoCount}
          dot={LEVEL_DOT.INFO}
        />
        <SummaryCard
          label="Debug events"
          count={debugCount}
          dot={LEVEL_DOT.DEBUG}
        />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {/* Level filter */}
        <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
          {LEVELS.map(l => (
            <button
              key={l}
              onClick={() => setLevel(l)}
              className={`text-xs px-2.5 py-1 rounded font-medium transition-colors ${
                levelFilter === l
                  ? 'bg-brand-navy text-white'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              {l}
            </button>
          ))}
        </div>

        <span className="text-xs text-gray-400 font-mono">
          {displayed.length} event{displayed.length !== 1 ? 's' : ''}
        </span>

        <div className="ml-auto flex items-center gap-3">
          {/* Auto-refresh toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <button
              onClick={() => setAuto(a => !a)}
              className={`w-8 h-4 rounded-full transition-colors ${autoRefresh ? 'bg-brand-blue' : 'bg-gray-300'}`}
            />
            <span className="text-xs text-gray-500">
              Auto-refresh {autoRefresh ? 'on' : 'off'}
            </span>
          </label>

          {/* Manual refresh */}
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="text-xs text-brand-blue hover:text-brand-blue/80 disabled:opacity-50"
          >
            {loading ? 'Refreshing…' : '↻ Refresh'}
          </button>

          {/* Clear */}
          <button
            onClick={handleClear}
            className="text-xs text-gray-400 hover:text-red-500 transition-colors"
          >
            Clear buffer
          </button>
        </div>
      </div>

      {lastRefresh && (
        <div className="text-xs text-gray-400 font-mono mb-3">
          Last updated {lastRefresh.toLocaleTimeString('en-GB', { hour12: false })}
        </div>
      )}

      {/* Log table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Column headers */}
        <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 border-b border-gray-200">
          <span className="text-xs font-medium text-gray-500 w-16">Level</span>
          <span className="text-xs font-medium text-gray-500 w-16">Time</span>
          <span className="text-xs font-medium text-gray-500 w-28">Source</span>
          <span className="text-xs font-medium text-gray-500 flex-1">Event</span>
          <span className="text-xs font-medium text-gray-500">Context</span>
        </div>

        {displayed.length === 0 ? (
          <div className="px-4 py-10 text-center text-sm text-gray-400">
            {loading ? 'Loading…' : 'No events yet. Start a run or make a config change to see activity.'}
          </div>
        ) : (
          <div>
            {displayed.map((entry, i) => (
              <LogRow key={`${entry.ts}-${i}`} entry={entry} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function SummaryCard({ label, count, dot, highlight, alertStyle }) {
  return (
    <div className={`bg-white border rounded-lg p-4 ${
      alertStyle && count > 0 ? 'border-red-300' :
      highlight ? 'border-brand-blue/40' : 'border-gray-200'
    }`}>
      <div className="flex items-center gap-2 mb-1">
        <span className={`w-2 h-2 rounded-full ${dot}`} />
        <span className="text-xs font-medium text-gray-500">{label}</span>
      </div>
      <div className={`font-heading font-bold text-2xl ${
        alertStyle && count > 0 ? 'text-red-600' :
        highlight ? 'text-brand-blue' : 'text-brand-navy'
      }`}>
        {count}
      </div>
    </div>
  )
}

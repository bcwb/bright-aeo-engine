import { useState, useEffect, useRef } from 'react'
import { getConfig, triggerRun, getRuns, createRunStream } from '../api'
import LiveFeed from '../components/LiveFeed'
import RunHistory from '../components/RunHistory'

const MODELS = ['All', 'claude', 'openai', 'gemini', 'perplexity']

export default function Run({ onRunComplete }) {
  const [config, setConfig]         = useState(null)
  const [topicFilter, setTopic]     = useState('All')
  const [modelFilter, setModel]     = useState('All')
  const [running, setRunning]       = useState(false)
  const [events, setEvents]         = useState([])
  const [phase, setPhase]           = useState(null)   // 'querying' | 'analysing' | 'recommending'
  const [summary, setSummary]       = useState(null)
  const [runError, setRunError]     = useState(null)
  const [runs, setRuns]             = useState([])
  const [runId, setRunId]           = useState(null)
  const esRef = useRef(null)

  useEffect(() => {
    getConfig().then(setConfig)
    getRuns().then(setRuns)
  }, [])

  const topics = config
    ? ['All', ...[...new Set(config.prompts.map(p => p.topic))].sort()]
    : ['All']

  const estimatedCalls = config
    ? config.prompts.filter(p =>
        p.active && (topicFilter === 'All' || p.topic === topicFilter)
      ).length *
      Object.values(config.models).filter(m =>
        m.enabled && (modelFilter === 'All' || Object.keys(config.models).find(k => config.models[k] === m) === modelFilter)
      ).length
    : 0

  async function startRun() {
    setRunning(true)
    setEvents([])
    setSummary(null)
    setRunError(null)
    setPhase('querying')

    const body = {}
    if (topicFilter !== 'All') body.topic = topicFilter
    if (modelFilter !== 'All') body.model = modelFilter

    const run = await triggerRun(body)
    setRunId(run.run_id)

    const es = createRunStream(run.run_id)
    esRef.current = es

    es.onmessage = (e) => {
      const event = JSON.parse(e.data)
      if (event.type === 'keepalive') return
      setEvents(prev => [...prev, event])

      if (event.type === 'analysing')    setPhase('analysing')
      if (event.type === 'recommending') setPhase('recommending')

      if (event.type === 'complete') {
        setSummary(event)
        setRunning(false)
        es.close()
        getRuns().then(setRuns)
        onRunComplete?.(run.run_id)
      }
      if (event.type === 'error') {
        setRunError(event.message || 'Run failed — check the backend terminal for details.')
        setRunning(false)
        es.close()
        getRuns().then(setRuns)
      }
    }
    es.onerror = () => {
      setRunError('Lost connection to backend. Is the server running?')
      setRunning(false)
      es.close()
    }
  }

  const progressEvents = events.filter(e => e.type === 'progress')
  const phaseMessage   = [...events].reverse().find(e => e.type === 'analysing' || e.type === 'recommending')
  const total          = events.find(e => e.type === 'started')?.total ?? 0
  const completed      = progressEvents.length
  const latestCost     = [...progressEvents].reverse().find(e => e.running_cost_usd != null)?.running_cost_usd ?? 0

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-xl font-semibold text-brand-navy mb-1">Run</h1>
      <p className="text-sm text-gray-500 mb-8">Trigger an analysis run and watch live results.</p>

      {/* Controls */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1.5">Topic</label>
            <select
              value={topicFilter}
              onChange={e => setTopic(e.target.value)}
              disabled={running}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm bg-white text-gray-700"
            >
              {topics.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1.5">Model</label>
            <select
              value={modelFilter}
              onChange={e => setModel(e.target.value)}
              disabled={running}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm bg-white text-gray-700"
            >
              {MODELS.map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div className="text-xs text-gray-400 font-mono pb-1">
            ~{estimatedCalls} calls
          </div>
          <button
            onClick={startRun}
            disabled={running}
            className={`ml-auto px-6 py-2 rounded font-medium text-sm transition-colors ${
              running
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-brand-blue text-brand-navy font-semibold hover:bg-brand-blue/90'
            }`}
          >
            {running
              ? phase === 'analysing'    ? 'Analysing…'
              : phase === 'recommending' ? 'Generating recommendations…'
              : 'Querying models…'
              : 'Run Analysis'
            }
          </button>
        </div>

        {/* Progress bar */}
        {running && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-400 font-mono mb-1">
              {phase === 'analysing' ? (
                <span className="text-brand-blue">Analysing responses…</span>
              ) : phase === 'recommending' ? (
                <span className="text-brand-blue">Generating recommendations (may take ~30s)…</span>
              ) : (
                <span>{completed} / {total} queries</span>
              )}
              <span>${latestCost.toFixed(4)}</span>
            </div>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  phase === 'recommending' ? 'bg-brand-orange animate-pulse w-full' :
                  phase === 'analysing'    ? 'bg-brand-blue/70 animate-pulse w-full' :
                  'bg-brand-blue'
                }`}
                style={phase === 'querying' ? { width: `${total ? (completed / total) * 100 : 0}%` } : undefined}
              />
            </div>
          </div>
        )}
      </div>

      {/* Summary banner */}
      {summary && (
        <div className="bg-brand-blue/10 border border-brand-blue/20 rounded-lg p-4 mb-6 flex items-start gap-4">
          <span className="text-brand-blue text-lg">✓</span>
          <div>
            <div className="font-medium text-brand-navy text-sm">Run complete</div>
            <div className="text-brand-navy/70 text-xs mt-0.5 font-mono">
              {summary.benchmark_brand || config?.benchmark_brand || 'Bright'} rate: {(summary.bright_overall_rate * 100).toFixed(0)}% ·
              {' '}{summary.total_responses} responses ·
              {' '}{summary.recommendation_count} recommendations ·
              {' '}${summary.estimated_cost_usd?.toFixed(4)} ·
              {' '}{summary.duration_seconds}s
            </div>
            {summary.watchouts?.length > 0 && (
              <div className="mt-1 text-xs text-brand-orange">
                ⚠ Watch-outs: {summary.watchouts.join(' · ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error banner */}
      {runError && (
        <div className="bg-brand-orange/10 border border-brand-orange/20 rounded-lg p-4 mb-6 flex items-start gap-3">
          <span className="text-brand-orange text-lg shrink-0">✕</span>
          <div>
            <div className="font-medium text-brand-navy text-sm">Run failed</div>
            <div className="text-brand-orange text-xs mt-0.5">{runError}</div>
          </div>
        </div>
      )}

      {/* Live feed */}
      {events.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Live Feed</h2>
          <LiveFeed events={progressEvents} benchmarkBrand={config?.benchmark_brand || 'Bright'} />
          {running && phaseMessage && (
            <div className="mt-2 px-4 py-2 bg-brand-blue/10 border border-brand-blue/20 rounded text-xs text-brand-blue font-mono animate-pulse">
              ⟳ {phaseMessage.message}
            </div>
          )}
        </div>
      )}

      {/* Run history */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Run History</h2>
        <RunHistory runs={runs} activeRunId={runId} />
      </div>
    </div>
  )
}

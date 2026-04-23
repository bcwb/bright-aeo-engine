import { useState, useEffect } from 'react'
import { getRuns, getRun, getRecommendations, getContent, triggerContent, approveContent } from '../api'
import SummaryCards from '../components/SummaryCards'
import TrendChart from '../components/TrendChart'
import CompetitorRankings from '../components/CompetitorRankings'
import RecommendationCard from '../components/RecommendationCard'
import ContentQueue from '../components/ContentQueue'
import SentimentSnippets from '../components/SentimentSnippets'

export default function Insights({ selectedRunId, onSelectRun }) {
  const [runs, setRuns]             = useState([])
  const [runData, setRunData]       = useState(null)
  const [recs, setRecs]             = useState(null)
  const [content, setContent]       = useState([])
  const [loading, setLoading]       = useState(false)
  const [generating, setGenerating] = useState(null)  // rec priority generating for

  // Load run list
  useEffect(() => { getRuns().then(setRuns) }, [])

  // Load selected run
  useEffect(() => {
    if (!selectedRunId) return
    setLoading(true)
    Promise.all([
      getRun(selectedRunId),
      getRecommendations(selectedRunId),
      getContent(selectedRunId),
    ]).then(([rd, rc, ct]) => {
      setRunData(rd)
      setRecs(rc)
      setContent(ct || [])
      setLoading(false)
    })
  }, [selectedRunId])

  async function handleGenerateContent(recPriority, channels) {
    setGenerating(recPriority)
    try {
      await triggerContent({
        run_id: selectedRunId,
        recommendation_priority: recPriority,
        channels,
      })
      const ct = await getContent(selectedRunId)
      setContent(ct || [])
    } finally {
      setGenerating(null)
    }
  }

  async function handleApprove(contentId, reviewerName) {
    await approveContent(contentId, reviewerName)
    const ct = await getContent(selectedRunId)
    setContent(ct || [])
  }

  const analysis = runData?.analysis
  const benchmarkBrand = runData?.analysis?.benchmark_brand
    || runData?.config_snapshot?.benchmark_brand
    || 'Bright'

  if (runs.length === 0 && !loading) {
    return (
      <div className="p-8 text-gray-400 text-sm">
        No runs yet. Go to the <strong className="text-gray-600">Run</strong> tab to trigger your first analysis.
      </div>
    )
  }

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-brand-navy font-heading">Insights</h1>
        <select
          value={selectedRunId || ''}
          onChange={e => onSelectRun(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm bg-white text-gray-700"
        >
          <option value="">Select a run…</option>
          {runs.map(r => (
            <option key={r.run_id} value={r.run_id}>
              {r.run_name}
            </option>
          ))}
        </select>
      </div>

      {loading && <div className="text-gray-400 text-sm">Loading run data…</div>}

      {!loading && analysis && (
        <>
          {/* Summary cards */}
          <div className="mb-8">
            <SummaryCards analysis={analysis} runs={runs} benchmarkBrand={benchmarkBrand} />
          </div>

          {/* Trend chart */}
          {runs.length > 1 && (
            <section className="mb-8">
              <SectionTitle>{benchmarkBrand} Citation Rate — Trend</SectionTitle>
              <TrendChart runs={runs} benchmarkBrand={benchmarkBrand} />
            </section>
          )}

          {/* Competitor rankings */}
          <section className="mb-8">
            <SectionTitle>Competitor Rankings</SectionTitle>
            <CompetitorRankings analysis={analysis} benchmarkBrand={benchmarkBrand} />
          </section>

          {/* Sentiment snippets */}
          <section className="mb-8">
            <SectionTitle>Sentiment Snippets</SectionTitle>
            <SentimentSnippets analysis={analysis} queryResults={runData?.query_results || []} benchmarkBrand={benchmarkBrand} />
          </section>

          {/* Recommendations */}
          <section className="mb-8">
            <SectionTitle>
              Recommendations
              {recs && (
                <span className="ml-2 font-mono text-gray-400 text-xs normal-case font-normal">
                  {recs.recommendations.length} actions
                </span>
              )}
            </SectionTitle>
            {recs ? (
              <>
                {recs.summary && (
                  <p className="text-sm text-gray-600 mb-4">{recs.summary}</p>
                )}
                <div className="space-y-4">
                  {recs.recommendations.map(rec => (
                    <RecommendationCard
                      key={rec.priority}
                      rec={rec}
                      generating={generating === rec.priority}
                      onGenerate={(channels) => handleGenerateContent(rec.priority, channels)}
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="p-4 bg-bright-red-1 border border-bright-red-2/40 rounded-lg text-sm text-bright-red-3">
                Recommendations failed to generate for this run.
                {runData?.recommendations_error && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-xs text-bright-red-3/70">Show error</summary>
                    <pre className="mt-1 text-xs whitespace-pre-wrap break-all text-bright-red-3/80">
                      {runData.recommendations_error}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </section>

          {/* Content queue */}
          {content.length > 0 && (
            <section className="mb-8">
              <SectionTitle>Content Queue</SectionTitle>
              <ContentQueue
                items={content}
                runId={selectedRunId}
                onApprove={handleApprove}
              />
            </section>
          )}
        </>
      )}
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <h2 className="text-xs font-semibold text-gray-500 mb-4 flex items-center gap-2">
      {children}
    </h2>
  )
}

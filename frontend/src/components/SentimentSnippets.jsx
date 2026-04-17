import { useState } from 'react'

const MODEL_COLORS = {
  perplexity: 'bg-brand-navy/10 text-brand-navy',
  claude:     'bg-brand-orange/10 text-brand-orange',
  openai:     'bg-brand-blue/10 text-brand-blue',
  gemini:     'bg-brand-navy/10 text-brand-navy',
}

export default function SentimentSnippets({ analysis, queryResults = [], benchmarkBrand = 'Bright' }) {
  const [filterTopic,    setFilterTopic]    = useState('all')
  const [expandedBrands, setExpandedBrands] = useState({})   // brand → bool
  const [expandedSnippets, setExpandedSnippets] = useState({}) // key → bool

  // Flatten all snippets from by_topic
  const byTopic = analysis?.by_topic || {}
  const allSnippets = []

  Object.entries(byTopic).forEach(([topic, brands]) => {
    Object.entries(brands).forEach(([brand, citation]) => {
      ;(citation.sentiment_snippets || []).forEach((snippet, i) => {
        allSnippets.push({ topic, brand, snippet, key: `${topic}-${brand}-${i}` })
      })
    })
  })

  const topics = [...new Set(allSnippets.map(s => s.topic))].sort()

  const filtered = filterTopic === 'all'
    ? allSnippets
    : allSnippets.filter(s => s.topic === filterTopic)

  // Group filtered snippets by brand — benchmark brand first, then alphabetical
  const groupMap = {}
  filtered.forEach(s => {
    if (!groupMap[s.brand]) groupMap[s.brand] = []
    groupMap[s.brand].push(s)
  })
  const brandGroups = Object.entries(groupMap).sort(([a], [b]) => {
    if (a === benchmarkBrand) return -1
    if (b === benchmarkBrand) return 1
    return a.localeCompare(b)
  })

  function toggleBrand(brand) {
    setExpandedBrands(prev => ({ ...prev, [brand]: !prev[brand] }))
  }

  function toggleSnippet(key) {
    setExpandedSnippets(prev => ({ ...prev, [key]: !prev[key] }))
  }

  // Find which query results contain a given snippet
  function findSources(snippetText) {
    if (!queryResults.length || !snippetText) return []
    const lower   = snippetText.toLowerCase()
    const partial = lower.slice(0, 60)
    return queryResults
      .filter(r =>
        r.status !== 'error' &&
        r.response_text &&
        (r.response_text.toLowerCase().includes(lower) ||
         (partial.length >= 20 && r.response_text.toLowerCase().includes(partial)))
      )
      .map(r => ({ model: r.model, prompt: r.prompt }))
      .filter((v, i, arr) => arr.findIndex(x => x.model === v.model && x.prompt === v.prompt) === i)
  }

  if (allSnippets.length === 0) {
    return (
      <div className="text-sm text-gray-400 py-4 text-center">
        No sentiment snippets available for this run.
      </div>
    )
  }

  return (
    <div>
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <select
          value={filterTopic}
          onChange={e => setFilterTopic(e.target.value)}
          className="text-xs border border-gray-200 rounded px-2 py-1 focus:outline-none focus:border-brand-blue"
        >
          <option value="all">All topics</option>
          {topics.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <span className="text-xs text-gray-400">
          {brandGroups.length} brand{brandGroups.length !== 1 ? 's' : ''} · {filtered.length} snippet{filtered.length !== 1 ? 's' : ''}
        </span>
        <button
          onClick={() => setExpandedBrands({})}
          className="text-xs text-gray-400 hover:text-gray-600 ml-auto"
        >
          Collapse all
        </button>
      </div>

      {/* Brand groups */}
      <div className="space-y-2">
        {brandGroups.map(([brand, snippets]) => {
          const isExpanded   = !!expandedBrands[brand]
          const isBright     = brand === benchmarkBrand
          const topicsInGroup = [...new Set(snippets.map(s => s.topic))].sort()
          const firstSnippet  = snippets[0]?.snippet || ''

          return (
            <div
              key={brand}
              className={`border rounded-lg overflow-hidden ${
                isBright ? 'border-brand-blue/30' : 'border-gray-200'
              }`}
            >
              {/* Collapsed header — always visible */}
              <button
                className={`w-full text-left px-4 py-3 flex items-start gap-3 hover:bg-gray-50 transition-colors ${
                  isBright ? 'bg-brand-blue/10 hover:bg-brand-blue/[0.08]' : 'bg-white'
                }`}
                onClick={() => toggleBrand(brand)}
              >
                {/* Brand name */}
                <span className={`shrink-0 mt-0.5 text-xs font-semibold px-2 py-0.5 rounded border ${
                  isBright
                    ? 'bg-brand-blue/15 text-brand-navy border-brand-blue/40'
                    : 'bg-gray-100 text-gray-700 border-gray-300'
                }`}>
                  {brand}
                </span>

                {/* Summary info */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-600">
                      {snippets.length} snippet{snippets.length !== 1 ? 's' : ''}
                    </span>
                    <span className="text-gray-300 text-xs">·</span>
                    {topicsInGroup.map(t => (
                      <span key={t} className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{t}</span>
                    ))}
                  </div>
                  {/* First snippet preview — only shown when collapsed */}
                  {!isExpanded && (
                    <p className="text-xs text-gray-500 italic truncate">
                      "{firstSnippet}"
                    </p>
                  )}
                </div>

                <span className="shrink-0 text-gray-400 text-xs mt-0.5">
                  {isExpanded ? '▲' : '▼'}
                </span>
              </button>

              {/* Expanded snippet list */}
              {isExpanded && (
                <div className="divide-y divide-gray-100 border-t border-gray-100">
                  {snippets.map(s => {
                    const isSnippetOpen = !!expandedSnippets[s.key]
                    const sources = isSnippetOpen ? findSources(s.snippet) : []

                    return (
                      <div key={s.key}>
                        <button
                          className="w-full text-left px-4 py-2.5 flex items-start gap-2 hover:bg-gray-50 transition-colors"
                          onClick={() => toggleSnippet(s.key)}
                        >
                          <span className="shrink-0 mt-0.5 text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                            {s.topic}
                          </span>
                          <span className="flex-1 min-w-0 text-xs text-gray-600 italic truncate">
                            "{s.snippet}"
                          </span>
                          <span className="shrink-0 text-gray-300 text-xs mt-0.5">
                            {isSnippetOpen ? '▲' : '▼'}
                          </span>
                        </button>

                        {isSnippetOpen && (
                          <div className="px-4 pb-3 pt-1 bg-gray-50 border-t border-gray-100">
                            <p className="text-sm text-gray-700 leading-relaxed italic mb-3">
                              "{s.snippet}"
                            </p>
                            {sources.length > 0 && (
                              <div>
                                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                                  Sources
                                </div>
                                <div className="flex flex-col gap-1.5">
                                  {sources.map((src, i) => (
                                    <div key={i} className="flex items-start gap-2 text-xs">
                                      <span className={`shrink-0 px-1.5 py-0.5 rounded font-medium ${MODEL_COLORS[src.model] || 'bg-gray-100 text-gray-600'}`}>
                                        {src.model}
                                      </span>
                                      <span className="text-gray-500 flex-1 min-w-0 truncate" title={src.prompt}>
                                        {src.prompt.length > 90 ? src.prompt.slice(0, 90) + '…' : src.prompt}
                                      </span>
                                      {src.model === 'perplexity' && (
                                        <a
                                          href={`https://www.perplexity.ai/search?q=${encodeURIComponent(src.prompt)}`}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="shrink-0 text-brand-blue hover:text-brand-blue/80 hover:underline"
                                          onClick={e => e.stopPropagation()}
                                        >
                                          View ↗
                                        </a>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

import { useState } from 'react'

const CATEGORY_COLORS = {
  'Content Gap':       'bg-brand-blue/10 text-brand-navy border-brand-blue/30',
  'Narrative Risk':    'bg-brand-orange/10 text-brand-orange border-brand-orange/30',
  'Technical':         'bg-brand-navy/10 text-brand-navy border-brand-navy/20',
  'Domain Authority':  'bg-brand-orange/10 text-brand-orange border-brand-orange/30',
  'Review Signal':     'bg-brand-blue/10 text-brand-navy border-brand-blue/30',
}

const EFFORT_COLORS = {
  Low:    'text-brand-blue',
  Medium: 'text-brand-orange',
  High:   'text-brand-orange',
}

const ALL_CHANNELS = [
  'linkedin', 'reddit', 'accountingweb', 'wikipedia',
  'g2_outreach', 'trustpilot_outreach', 'pr_pitch', 'web_page',
]

// Normalise a free-form channel name from the recommender to a valid key
function normaliseChannel(ch) {
  const c = ch.toLowerCase().trim()
  if (ALL_CHANNELS.includes(c)) return c
  if (c.includes('linkedin'))    return 'linkedin'
  if (c.includes('reddit'))      return 'reddit'
  if (c.includes('wikipedia') || c.includes('wikidata')) return 'wikipedia'
  if (c.includes('accountingweb') || c.includes('accounting web')) return 'accountingweb'
  if (c.includes('trustpilot'))  return 'trustpilot_outreach'
  if (c.includes('g2') && !c.includes('capterra')) return 'g2_outreach'
  if (c.includes('pr') && (c.includes('pitch') || c.includes('press') || c.includes('release'))) return 'pr_pitch'
  if (['brightsg.com','brightpay','blog','faq','web page','webpage','website','landing page','product page','schema'].some(x => c.includes(x))) return 'web_page'
  return null
}

export default function RecommendationCard({ rec, generating, onGenerate }) {
  const [expanded, setExpanded]     = useState(false)
  const [actioned, setActioned]     = useState(false)
  // Normalise rec.channels to valid keys; deduplicate
  const [channels, setChannels]     = useState(() => {
    const mapped = (rec.channels || []).map(normaliseChannel).filter(Boolean)
    return [...new Set(mapped)]
  })
  const [showChannels, setShowChannels] = useState(false)

  function toggleChannel(ch) {
    setChannels(prev =>
      prev.includes(ch) ? prev.filter(c => c !== ch) : [...prev, ch]
    )
  }

  return (
    <div className={`bg-white border rounded-lg overflow-hidden ${actioned ? 'opacity-50' : ''}`}>
      <div
        className="px-5 py-4 cursor-pointer hover:bg-gray-50"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex items-start gap-3">
          {/* Priority badge */}
          <span className="mt-0.5 w-7 h-7 rounded-full bg-brand-navy text-white text-xs font-mono font-medium flex items-center justify-center shrink-0">
            {rec.priority}
          </span>

          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className={`text-xs font-medium px-2 py-0.5 rounded border ${CATEGORY_COLORS[rec.category] || 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                {rec.category}
              </span>
              <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{rec.topic}</span>
              <span className={`text-xs font-medium ${EFFORT_COLORS[rec.effort] || ''}`}>
                Effort: {rec.effort}
              </span>
              <span className="text-xs text-gray-500">Impact: {rec.impact}</span>
              <span className="text-xs text-gray-400">{rec.timeframe}</span>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">{rec.finding}</p>
          </div>

          <span className="text-gray-300 text-xs mt-1">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {expanded && (
        <div className="px-5 pb-4 border-t border-gray-100">
          <div className="py-3">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Action</div>
            <p className="text-sm text-gray-900 font-medium">{rec.action}</p>
          </div>

          <div className="py-2 border-t border-gray-100">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Channels</div>
            <div className="flex flex-wrap gap-1.5">
              {ALL_CHANNELS.map(ch => (
                <button
                  key={ch}
                  onClick={() => toggleChannel(ch)}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    channels.includes(ch)
                      ? 'bg-brand-blue text-brand-navy font-semibold'
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                >
                  {ch}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100">
            <button
              onClick={() => onGenerate(channels)}
              disabled={generating || channels.length === 0}
              className="px-4 py-1.5 bg-brand-blue text-brand-navy rounded text-sm font-semibold hover:bg-brand-blue/90 disabled:opacity-50 transition-colors"
            >
              {generating ? 'Generating…' : `Generate content (${channels.length} channels)`}
            </button>
            <button
              onClick={() => setActioned(a => !a)}
              className="text-sm text-gray-400 hover:text-gray-600"
            >
              {actioned ? 'Mark as not actioned' : 'Mark as actioned'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState } from 'react'

const FIT_COLORS = {
  High:   'text-brand-blue',
  Medium: 'text-brand-orange',
  Low:    'text-brand-orange',
}

export default function PRPlacements({ placements }) {
  const [expanded, setExpanded] = useState({})
  const [copied, setCopied]     = useState({})

  function copyPitch(i, text) {
    navigator.clipboard.writeText(text)
    setCopied(prev => ({ ...prev, [i]: true }))
    setTimeout(() => setCopied(prev => ({ ...prev, [i]: false })), 2000)
  }

  if (!placements?.length) {
    return (
      <div className="text-sm text-gray-400 py-3 text-center">No PR placements generated.</div>
    )
  }

  return (
    <div className="space-y-2">
      {placements.map((p, i) => {
        const isOpen = !!expanded[i]
        return (
          <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
            <div
              className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50"
              onClick={() => setExpanded(prev => ({ ...prev, [i]: !isOpen }))}
            >
              <span className="w-6 h-6 rounded-full bg-brand-navy text-white text-xs font-mono font-medium flex items-center justify-center shrink-0">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-800">{p.outlet}</div>
                {p.lead_time && (
                  <div className="text-xs text-gray-400 mt-0.5">Lead time: {p.lead_time}</div>
                )}
              </div>
              {p.audience_fit && (
                <div className={`text-xs font-medium shrink-0 ${FIT_COLORS[p.audience_fit] || 'text-gray-500'}`}>
                  {p.audience_fit} fit
                </div>
              )}
              {p.citation_frequency != null && (
                <div className="text-xs font-mono text-gray-400 shrink-0">
                  cited {p.citation_frequency}×
                </div>
              )}
              <span className="text-gray-300 text-xs">{isOpen ? '▲' : '▼'}</span>
            </div>

            {isOpen && (
              <div className="border-t border-gray-100 bg-gray-50 px-4 py-3 space-y-3">
                {p.pitch_angle && (
                  <div>
                    <div className="text-xs font-medium text-gray-400 mb-1">Angle</div>
                    <p className="text-sm text-gray-700">{p.pitch_angle}</p>
                  </div>
                )}

                {p.draft_pitch && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <div className="text-xs font-medium text-gray-400">Draft pitch</div>
                      <button
                        onClick={() => copyPitch(i, p.draft_pitch)}
                        className="text-xs text-brand-blue hover:text-brand-blue/80 font-medium"
                      >
                        {copied[i] ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <p className="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed bg-white border border-gray-200 rounded p-2">
                      {p.draft_pitch}
                    </p>
                  </div>
                )}

                {p.contact_approach && (
                  <div>
                    <div className="text-xs font-medium text-gray-400 mb-1">Contact approach</div>
                    <p className="text-xs text-gray-700">{p.contact_approach}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

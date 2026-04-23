import { useState } from 'react'
import ContentPreview from './ContentPreview'
import TargetingPanel from './TargetingPanel'

const STATUS_COLORS = {
  draft:    'bg-gray-100 text-gray-600',
  reviewed: 'bg-brand-blue/10 text-brand-navy',
  approved: 'bg-brand-blue/10 text-brand-blue',
  posted:   'bg-brand-navy/10 text-brand-navy',
  error:    'bg-brand-orange/10 text-brand-orange',
}

const CHANNEL_COLORS = {
  linkedin:            'bg-brand-blue text-brand-navy',
  reddit:              'bg-brand-orange text-brand-navy',
  wikipedia:           'bg-gray-500 text-white',
  accountingweb:       'bg-brand-navy text-white',
  g2_outreach:         'bg-brand-navy text-white',
  trustpilot_outreach: 'bg-brand-blue text-brand-navy',
  pr_pitch:            'bg-brand-orange text-brand-navy',
  web_page:            'bg-gray-500 text-white',
}

export default function ContentQueue({ items, runId, onApprove }) {
  const [openId, setOpenId] = useState(null)

  // Group by recommendation priority
  const grouped = items.reduce((acc, item) => {
    const key = item.recommendation_priority
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      {Object.entries(grouped).sort(([a], [b]) => Number(a) - Number(b)).map(([priority, group]) => (
        <div key={priority}>
          <div className="text-xs font-semibold text-gray-500 mb-2">
            Recommendation #{priority}
          </div>
          <div className="space-y-2">
            {group.map(item => (
              <div key={item.content_id}>
                <div
                  className="bg-white border border-gray-200 rounded-lg overflow-hidden cursor-pointer hover:border-gray-300"
                  onClick={() => setOpenId(openId === item.content_id ? null : item.content_id)}
                >
                  {/* Reddit review gate */}
                  {item.human_review_required && item.status !== 'approved' && (
                    <div className="flex items-center gap-2 px-4 py-2 bg-brand-orange/10 border-b border-brand-orange/20">
                      <span className="text-brand-orange text-sm">⚠</span>
                      <span className="text-xs font-medium text-brand-orange">
                        Human review required before posting
                      </span>
                    </div>
                  )}

                  <div className="flex items-center gap-3 px-4 py-3 min-w-0">
                    <span className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${CHANNEL_COLORS[item.channel] || 'bg-gray-500 text-white'}`}>
                      {item.channel}
                    </span>
                    <span className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[item.status] || ''}`}>
                      {item.status}
                    </span>
                    {item.status !== 'error' && (
                      <span className="shrink-0 text-xs text-gray-400 font-mono">{item.word_count}w</span>
                    )}
                    <span className="flex-1 min-w-0 text-sm text-gray-600 truncate">
                      {item.status === 'error'
                        ? (item.error || 'Generation failed')
                        : (item.content?.slice(0, 120) || '—')}
                    </span>
                    <span className="shrink-0 text-gray-300 text-xs">{openId === item.content_id ? '▲' : '▼'}</span>
                  </div>
                </div>

                {openId === item.content_id && (
                  <div className="border border-t-0 border-gray-200 rounded-b-lg">
                    <ContentPreview item={item} onApprove={onApprove} />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Targeting panel per recommendation group */}
          {runId && <TargetingPanel runId={runId} recPriority={Number(priority)} />}
        </div>
      ))}
    </div>
  )
}

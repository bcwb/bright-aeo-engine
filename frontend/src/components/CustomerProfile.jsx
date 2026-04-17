import { useState } from 'react'

export default function CustomerProfile({ profile }) {
  const [copied, setCopied] = useState(false)

  function copyTemplate() {
    navigator.clipboard.writeText(profile.outreach_template || '')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3 text-sm">

      {/* Product + company */}
      <div>
        <div className="font-semibold text-gray-800 break-words">{profile.product}</div>
        <div className="text-xs text-gray-500 mt-0.5 break-words">
          {[profile.company_type, profile.company_size_range].filter(Boolean).join(' · ')}
        </div>
      </div>

      {/* Pool / Yield / Migration — inline stats */}
      <div className="flex flex-wrap gap-4">
        {profile.expected_pool_size != null && (
          <div>
            <div className="text-xs text-gray-400">Est. pool</div>
            <div className="text-sm font-medium text-gray-700 break-words">{profile.expected_pool_size}</div>
          </div>
        )}
        {profile.expected_yield != null && (
          <div>
            <div className="text-xs text-gray-400">Est. yield</div>
            <div className="text-sm font-medium text-brand-blue break-words">{profile.expected_yield}</div>
          </div>
        )}
        {profile.migration_window && (
          <div>
            <div className="text-xs text-gray-400">Migration window</div>
            <div className="text-sm text-gray-700 break-words">{profile.migration_window}</div>
          </div>
        )}
      </div>

      {/* Target roles */}
      {profile.role_titles?.length > 0 && (
        <div>
          <div className="text-xs font-medium text-gray-400 mb-1">Target roles</div>
          <div className="flex flex-wrap gap-1">
            {profile.role_titles.map(r => (
              <span key={r} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded break-words">{r}</span>
            ))}
          </div>
        </div>
      )}

      {/* CRM filter */}
      {profile.crm_query && (
        <div>
          <div className="text-xs font-medium text-gray-400 mb-1">CRM filter</div>
          <pre className="text-xs bg-gray-50 border border-gray-200 rounded px-2 py-1.5 text-gray-700 whitespace-pre-wrap break-all overflow-auto max-h-32 font-mono">
            {profile.crm_query}
          </pre>
        </div>
      )}

      {/* Review ask */}
      {profile.review_ask && (
        <div className="text-xs text-gray-600 bg-brand-blue/10 border border-brand-blue/20 rounded px-2 py-1.5 break-words">
          <span className="font-medium text-brand-blue">Review ask:</span> {profile.review_ask}
        </div>
      )}

      {/* Outreach template */}
      {profile.outreach_template && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <div className="text-xs font-medium text-gray-400">Outreach template</div>
            <button
              onClick={copyTemplate}
              className="text-xs text-brand-blue hover:text-brand-blue/80 font-medium"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded p-2">
            <p className="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed break-words">{profile.outreach_template}</p>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState } from 'react'

export default function ContentPreview({ item, onApprove }) {
  const [reviewer, setReviewer]   = useState(item.reviewer_name || '')
  const [approving, setApproving] = useState(false)
  const [content, setContent]     = useState(item.content || '')
  const [confirmed, setConfirmed] = useState(false)

  const isReddit   = item.channel === 'reddit'
  const isApproved = item.status === 'approved'

  async function handleApprove() {
    if (isReddit && !confirmed) {
      setConfirmed(true)
      return
    }
    if (!reviewer.trim()) return
    setApproving(true)
    await onApprove(item.content_id, reviewer)
    setApproving(false)
    setConfirmed(false)
  }

  if (item.status === 'error') {
    return (
      <div className="p-5 bg-white">
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 break-words">
          {item.error || 'Generation failed'}
        </div>
      </div>
    )
  }

  return (
    <div className="p-5 bg-white">
      {/* Content editor */}
      <textarea
        value={content}
        onChange={e => setContent(e.target.value)}
        rows={Math.max(10, content.split('\n').length + 2)}
        className="w-full text-sm text-gray-800 leading-relaxed border border-gray-200 rounded p-3 resize-y focus:outline-none focus:border-brand-blue font-sans break-words"
        style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
        readOnly={isApproved}
      />

      <div className="mt-3 flex items-end gap-3">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Reviewer name {isReddit && <span className="text-brand-orange font-semibold">(required for Reddit)</span>}
          </label>
          <input
            type="text"
            value={reviewer}
            onChange={e => setReviewer(e.target.value)}
            placeholder="Enter your name to approve"
            disabled={isApproved}
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-brand-blue disabled:bg-gray-50 disabled:text-gray-400"
          />
        </div>

        {!isApproved && (
          <button
            onClick={handleApprove}
            disabled={approving || !reviewer.trim()}
            className="px-4 py-1.5 bg-brand-blue text-brand-navy rounded text-sm font-semibold hover:bg-brand-blue/90 disabled:opacity-50 transition-colors whitespace-nowrap"
          >
            {approving ? 'Approving…' : confirmed ? 'Confirm approval' : 'Approve'}
          </button>
        )}

        {isApproved && (
          <div className="text-xs text-green-700 font-medium pb-1.5">
            ✓ Approved by {item.reviewer_name} on {item.reviewer_date}
          </div>
        )}
      </div>

      {/* Reddit confirmation dialog */}
      {isReddit && confirmed && !isApproved && (
        <div className="mt-3 p-3 bg-brand-orange/10 border border-brand-orange/30 rounded text-xs text-brand-navy">
          I confirm I have read this content and it complies with Reddit community guidelines.
          Posting unapproved vendor content may result in account bans.
        </div>
      )}

      <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
        <span className="font-mono">{content.split(/\s+/).filter(Boolean).length} words</span>
        {item.reviewer_name && <span>Reviewer: {item.reviewer_name}</span>}
      </div>
    </div>
  )
}

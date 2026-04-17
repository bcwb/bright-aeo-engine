import { useState, useEffect } from 'react'
import CustomerProfile from './CustomerProfile'
import PRPlacements from './PRPlacements'
import { getTargeting } from '../api'

export default function TargetingPanel({ runId, recPriority }) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [tab, setTab]         = useState('customers')

  useEffect(() => {
    if (!runId) return
    setLoading(true)
    getTargeting(runId)
      .then(results => {
        const mine    = results.filter(r => r.recommendation_priority === recPriority)
        const cpEntry = mine.find(r => r.mode === 'customer_profile')
        const prEntry = mine.find(r => r.mode === 'pr_placement')
        setData({
          customer_profile: cpEntry?.customer_profile || null,
          pr_placements:    prEntry?.pr_placements    || [],
        })
        setLoading(false)
      })
      .catch(() => setLoading(false))   // silently ignore errors (e.g. run predates targeting)
  }, [runId, recPriority])

  if (loading || !data) return null

  const hasCustomer = !!data.customer_profile
  const hasPR       = (data.pr_placements?.length ?? 0) > 0

  if (!hasCustomer && !hasPR) return null

  return (
    <div className="mt-2 border border-gray-200 rounded-lg overflow-hidden">
      <div className="flex border-b border-gray-200 bg-white">
        {[
          { key: 'customers', label: 'Customer profile',                                   show: hasCustomer },
          { key: 'pr',        label: `PR placements (${data.pr_placements?.length ?? 0})`, show: hasPR },
        ].filter(t => t.show).map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2.5 text-xs font-medium transition-colors ${
              tab === t.key
                ? 'text-brand-blue border-b-2 border-brand-blue'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="p-4 bg-gray-50">
        {tab === 'customers' && hasCustomer && (
          <CustomerProfile profile={data.customer_profile} />
        )}
        {tab === 'pr' && hasPR && (
          <PRPlacements placements={data.pr_placements} />
        )}
      </div>
    </div>
  )
}

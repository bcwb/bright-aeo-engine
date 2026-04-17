export default function RunHistory({ runs, activeRunId }) {
  if (runs.length === 0) {
    return <div className="text-sm text-gray-400">No runs yet.</div>
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50">
            <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500">Run</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500 text-right font-mono">Responses</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500 text-right font-mono">Cost</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500">Status</th>
          </tr>
        </thead>
        <tbody>
          {runs.map(r => (
            <tr
              key={r.run_id}
              className={`border-b border-gray-50 ${r.run_id === activeRunId ? 'bg-brand-blue/10' : 'hover:bg-gray-50'}`}
            >
              <td className="px-4 py-2.5 text-gray-700 text-xs">{r.run_name}</td>
              <td className="px-4 py-2.5 text-right font-mono text-xs text-gray-600">
                {r.total_responses}
                {r.failed_calls > 0 && (
                  <span className="text-brand-orange ml-1">({r.failed_calls} failed)</span>
                )}
              </td>
              <td className="px-4 py-2.5 text-right font-mono text-xs text-gray-400">
                {r.estimated_cost_usd != null ? `$${r.estimated_cost_usd.toFixed(3)}` : '—'}
              </td>
              <td className="px-4 py-2.5">
                <StatusBadge status={r.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function StatusBadge({ status }) {
  const styles = {
    complete: 'bg-brand-blue/10 text-brand-blue',
    aborted:  'bg-brand-orange/10 text-brand-orange',
    running:  'bg-brand-blue/10 text-brand-blue',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${styles[status] || 'bg-gray-50 text-gray-500'}`}>
      {status}
    </span>
  )
}

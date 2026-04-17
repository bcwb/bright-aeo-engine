const MODEL_ICONS = {
  claude:     '◆',
  openai:     '○',
  gemini:     '◇',
  perplexity: '◉',
}

export default function LiveFeed({ events, benchmarkBrand = 'Bright' }) {
  if (events.length === 0) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50">
            <th className="text-left px-4 py-2 font-medium text-gray-500 w-24">Model</th>
            <th className="text-left px-4 py-2 font-medium text-gray-500">Prompt</th>
            <th className="px-4 py-2 font-medium text-gray-500 w-20 text-center">{benchmarkBrand}</th>
            <th className="text-left px-4 py-2 font-medium text-gray-500">Top brands</th>
            <th className="px-4 py-2 font-medium text-gray-500 w-16 text-right font-mono">ms</th>
          </tr>
        </thead>
        <tbody>
          {[...events].reverse().map(e => (
            <tr key={e.job_id} className="border-b border-gray-50 hover:bg-gray-50">
              <td className="px-4 py-2 font-mono text-gray-500">
                <span className="mr-1">{MODEL_ICONS[e.model] || '·'}</span>
                {e.model}
              </td>
              <td className="px-4 py-2 text-gray-600 max-w-xs truncate">{e.prompt}</td>
              <td className="px-4 py-2 text-center">
                {e.status === 'error' ? (
                  <span className="text-brand-orange" title={e.error}>✗ err</span>
                ) : e.bright_mentioned ? (
                  <span className="text-brand-blue font-medium">✓</span>
                ) : (
                  <span className="text-gray-300">✗</span>
                )}
              </td>
              <td className="px-4 py-2 text-gray-500">
                {e.top_brands?.join(' · ') || '—'}
              </td>
              <td className="px-4 py-2 text-right font-mono text-gray-400">{e.latency_ms}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

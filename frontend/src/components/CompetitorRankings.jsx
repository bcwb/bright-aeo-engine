export default function CompetitorRankings({ analysis, benchmarkBrand = 'Bright' }) {
  const citations = analysis.brand_citations || {}
  const brightRate = analysis.bright_overall_rate ?? 0

  const sorted = Object.values(citations).sort((a, b) => b.rate - a.rate)

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50">
            <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 w-8">#</th>
            <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500">Brand</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500 text-right font-mono w-28">Citation rate</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500 w-48">Visual</th>
            <th className="px-4 py-2.5 text-xs font-medium text-gray-500 text-right font-mono w-16">Count</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((c, i) => {
            const isBright = c.brand === benchmarkBrand
            const isAbove  = !isBright && c.rate > brightRate
            return (
              <tr
                key={c.brand}
                className={`border-b border-gray-50 ${isBright ? 'bg-brand-blue/10' : 'hover:bg-gray-50'}`}
              >
                <td className="px-4 py-2.5 font-mono text-xs text-gray-400">{i + 1}</td>
                <td className="px-4 py-2.5">
                  <span className={`font-medium ${isBright ? 'text-brand-navy font-semibold' : 'text-gray-800'}`}>
                    {c.brand}
                  </span>
                  {isBright && <span className="ml-2 text-xs text-brand-blue/60">← benchmark</span>}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-xs">
                  <span className={
                    isBright ? 'text-brand-blue font-medium' :
                    isAbove  ? 'text-brand-orange' :
                    'text-gray-500'
                  }>
                    {(c.rate * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isBright ? 'bg-brand-blue' : isAbove ? 'bg-brand-orange/50' : 'bg-gray-200'}`}
                      style={{ width: `${c.rate * 100}%` }}
                    />
                  </div>
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-xs text-gray-400">{c.count}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default function SummaryCards({ analysis, runs, benchmarkBrand = 'Bright' }) {
  const citations = analysis.brand_citations || {}
  const byTopic   = analysis.by_topic || {}

  const topicRates = Object.entries(byTopic).map(([topic, cits]) => ({
    topic,
    rate: cits?.[benchmarkBrand]?.rate ?? 0,
  }))
  const best  = topicRates.sort((a, b) => b.rate - a.rate)[0]
  const worst = [...topicRates].sort((a, b) => a.rate - b.rate)[0]

  const byModel  = analysis.by_model || {}
  const bestModel = Object.entries(byModel)
    .map(([m, cits]) => ({ model: m, rate: cits?.[benchmarkBrand]?.rate ?? 0 }))
    .sort((a, b) => b.rate - a.rate)[0]

  const prev = runs?.length > 1 ? runs[1] : null
  const delta = prev?.bright_overall_rate != null
    ? analysis.bright_overall_rate - prev.bright_overall_rate
    : null

  return (
    <div className="grid grid-cols-4 gap-4">
      <Card
        label={`${benchmarkBrand} citation rate`}
        value={`${(analysis.bright_overall_rate * 100).toFixed(0)}%`}
        sub={delta != null
          ? `${delta >= 0 ? '↑' : '↓'} ${Math.abs(delta * 100).toFixed(0)}pp vs prev run`
          : `${analysis.total_responses} responses`}
        highlight={analysis.bright_overall_rate >= 0.5}
      />
      <Card
        label="Best topic"
        value={best?.topic ?? '—'}
        sub={best ? `${(best.rate * 100).toFixed(0)}% citation rate` : ''}
      />
      <Card
        label="Worst topic"
        value={worst?.topic ?? '—'}
        sub={worst ? `${(worst.rate * 100).toFixed(0)}% citation rate` : ''}
        warn={worst?.rate === 0}
      />
      <Card
        label={`Best model for ${benchmarkBrand}`}
        value={bestModel?.model ?? '—'}
        sub={bestModel ? `${(bestModel.rate * 100).toFixed(0)}% citation rate` : ''}
      />
    </div>
  )
}

function Card({ label, value, sub, highlight, warn }) {
  return (
    <div className={`bg-white border rounded-lg p-4 ${
      warn ? 'border-brand-orange/40' : highlight ? 'border-brand-blue/40' : 'border-gray-200'
    }`}>
      <div className="text-xs font-medium text-gray-500 mb-1">{label}</div>
      <div className={`font-mono text-2xl font-medium ${
        warn ? 'text-brand-orange' : highlight ? 'text-brand-blue' : 'text-brand-navy'
      }`}>
        {value}
      </div>
      {sub && <div className="text-xs text-gray-400 mt-0.5">{sub}</div>}
    </div>
  )
}

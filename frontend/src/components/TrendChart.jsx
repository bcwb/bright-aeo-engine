import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const TOPIC_COLORS = [
  '#009FC7', // brand-blue
  '#E39400', // brand-orange
  '#0F2B3D', // brand-navy
  '#E6D600', // brand-yellow
  '#006f8a', // deep brand-blue
  '#a06a00', // deep brand-orange
  '#1e4a63', // mid brand-navy
  '#b3a800', // deep brand-yellow
]

// Shorten a run_name like "2026-04-15 — Payroll v2 — 50% cited"
// to a compact x-axis tick label
function shortLabel(run) {
  if (!run.run_name) return run.run_date || '—'
  // Extract just the scope + version part (between the first and last "—")
  const parts = run.run_name.split(' — ')
  if (parts.length >= 2) {
    // "2026-04-15 — Payroll v2 — 50% cited" → "Payroll v2\n2026-04-15"
    const scope = parts[1]
    const date  = parts[0]
    return `${scope}\n${date}`
  }
  return run.run_name
}

export default function TrendChart({ runs, benchmarkBrand = 'Bright' }) {
  const allTopics = []
  const topicSet  = new Set()

  const points = runs
    .filter(r => r.run_date && r.status === 'complete')
    .sort((a, b) => {
      // Sort by date first, then by run_name for same-date runs
      const d = a.run_date.localeCompare(b.run_date)
      return d !== 0 ? d : (a.run_name || '').localeCompare(b.run_name || '')
    })
    .map((r, i) => {
      const label   = shortLabel(r)
      const point   = { label, _runId: r.run_id, _idx: i }
      const byTopic = r.by_topic || {}
      Object.entries(byTopic).forEach(([topic, cits]) => {
        const rate = cits?.[benchmarkBrand]?.rate
        if (rate != null) {           // only plot when benchmark brand actually appeared
          if (!topicSet.has(topic)) {
            topicSet.add(topic)
            allTopics.push(topic)
          }
          point[topic] = Math.round(rate * 100)
        }
      })
      return point
    })

  if (points.length < 2) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-sm text-gray-400">
        Run at least two analyses to see trends.
      </div>
    )
  }

  // Custom tick renderer for multi-line labels
  function CustomTick({ x, y, payload }) {
    const lines = (payload.value || '').split('\n')
    return (
      <g transform={`translate(${x},${y})`}>
        {lines.map((line, i) => (
          <text
            key={i}
            x={0}
            y={0}
            dy={14 + i * 13}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize={10}
            fontFamily="JetBrains Mono, monospace"
          >
            {line}
          </text>
        ))}
      </g>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={points} margin={{ top: 4, right: 16, bottom: 40, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="label"
            tick={<CustomTick />}
            axisLine={false}
            tickLine={false}
            interval={0}
          />
          <YAxis
            domain={[0, 100]}
            tickFormatter={v => `${v}%`}
            tick={{ fontSize: 11, fontFamily: 'JetBrains Mono, monospace', fill: '#94a3b8' }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            formatter={(v, name) => [`${v}%`, name]}
            contentStyle={{ fontSize: 12, fontFamily: 'JetBrains Mono, monospace', border: '1px solid #e2e8f0' }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {allTopics.map((topic, i) => (
            <Line
              key={topic}
              type="monotone"
              dataKey={topic}
              stroke={TOPIC_COLORS[i % TOPIC_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

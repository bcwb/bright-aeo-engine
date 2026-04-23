import { useState, useEffect } from 'react'
import { getConfig, deletePeerSet, openAsset, updateBenchmarkBrand } from '../api'
import PromptTable from '../components/PromptTable'
import CompetitorTable from '../components/CompetitorTable'
import ModelConfig from '../components/ModelConfig'

function topicToKey(topic) {
  return topic.trim().toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_')
}

export default function Configure() {
  const [config, setConfig]           = useState(null)
  const [expanded, setExpanded]       = useState({})   // topic → bool; empty = all collapsed

  const reload = () => getConfig().then(setConfig)
  useEffect(() => { reload() }, [])

  function toggleTopic(topic) {
    setExpanded(prev => ({ ...prev, [topic]: !prev[topic] }))
  }

  if (!config) {
    return <div className="p-8 text-gray-400 text-sm">Loading configuration…</div>
  }

  // Derive ordered topic list from prompts (preserves insertion order, deduped)
  const topics = [...new Set(config.prompts.map(p => p.topic))].sort()

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="text-2xl font-bold text-brand-navy font-heading mb-1">Configure</h1>
      <p className="text-sm text-gray-500 mb-8">
        Manage prompts, competitors, models, and brand assets.
      </p>

      {/* Per-topic sections: prompts + peer set together */}
      <section className="mb-10">
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-xs font-semibold text-gray-500">Topics</h2>
          <span className="font-mono text-xs text-gray-400">{topics.length}</span>
        </div>
        <p className="text-xs text-gray-400 mb-5">
          Each topic groups prompts with a competitor peer set. Adding a prompt with a new topic automatically creates its peer set.
        </p>

        <div className="space-y-2">
          {topics.map(topic => {
            const key   = topicToKey(topic)
            const peers = config.peer_sets[key] || []
            const promptsForTopic = config.prompts.filter(p => p.topic === topic)

            const isExpanded = !!expanded[topic]
            return (
              <div key={topic} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Topic header — click to expand/collapse */}
                <button
                  className="w-full flex items-center justify-between px-5 py-3 text-left transition-opacity hover:opacity-90 bg-brand-navy"
                  onClick={() => toggleTopic(topic)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-sm font-semibold text-white">{topic}</span>
                    <span className="text-xs text-white/60 font-mono">
                      {promptsForTopic.filter(p => p.active).length} active prompt{promptsForTopic.filter(p => p.active).length !== 1 ? 's' : ''} · {peers.length} competitor{peers.length !== 1 ? 's' : ''}
                    </span>
                    {peers.length === 0 && (
                      <span className="text-xs text-brand-yellow font-medium">⚠ No competitors</span>
                    )}
                  </div>
                  <span className="shrink-0 text-white/60 text-xs ml-3">{isExpanded ? '▲' : '▼'}</span>
                </button>

                {isExpanded && (
                  <div className="p-5 grid grid-cols-2 gap-6">
                    {/* Prompts for this topic */}
                    <div>
                      <div className="text-xs font-semibold text-gray-500 mb-3">Prompts</div>
                      <PromptTable
                        prompts={promptsForTopic}
                        allPrompts={config.prompts}
                        onChange={reload}
                      />
                    </div>

                    {/* Peer set for this topic */}
                    <div>
                      <div className="text-xs font-semibold text-gray-500 mb-3">Competitor peer set</div>
                      <CompetitorTable
                        title={topic}
                        peerSetKey={key}
                        peers={peers}
                        onChange={reload}
                      />
                    </div>
                  </div>
                )}
              </div>
            )
          })}

          {topics.length === 0 && (
            <div className="text-sm text-gray-400 text-center py-8 border border-dashed border-gray-200 rounded-lg">
              No topics yet. Add a prompt below to create your first topic.
            </div>
          )}
        </div>

        {/* Add prompt outside any topic card — for new topics */}
        <div className="mt-4">
          <PromptTable
            prompts={[]}
            allPrompts={config.prompts}
            addOnly
            onChange={reload}
          />
        </div>
      </section>

      {/* Benchmark Brand */}
      <Section title="Benchmark Brand">
        <BenchmarkBrandConfig
          value={config.benchmark_brand || 'Bright'}
          brandVariants={config.brand_variants || {}}
          onChange={reload}
        />
      </Section>

      {/* Models */}
      <Section title="Models">
        <ModelConfig models={config.models} onChange={reload} />
      </Section>

      {/* Assets */}
      <Section title="Brand Assets">
        <p className="text-xs text-gray-400 mb-5">
          Core assets are loaded for every content generation request.
          Topic assets are loaded only when generating content for that topic.
          Click <strong className="text-gray-500">Open</strong> to edit in your default editor.
        </p>

        {/* Core assets — always loaded */}
        <div className="mb-6">
          <div className="text-xs font-semibold text-gray-500 mb-3">Core — loaded for every topic</div>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            {[
              { file: 'tone-of-voice.md',               label: 'Tone of Voice' },
              { file: 'brand-guidelines.md',             label: 'Brand Guidelines' },
              { file: 'competitive-positioning.md',      label: 'Competitive Positioning' },
              { file: 'customer-proof/stats.md',         label: 'Customer Stats' },
              { file: 'customer-proof/case-studies.md',  label: 'Case Studies' },
            ].map(a => (
              <AssetRow key={a.file} file={a.file} label={a.label} />
            ))}
          </div>
        </div>

        {/* Topic assets — one per topic, loaded alongside core assets */}
        <div>
          <div className="text-xs font-semibold text-gray-500 mb-3">Topic — loaded per topic</div>
          {topics.length === 0 ? (
            <div className="text-sm text-gray-400">No topics yet — add a prompt above to create one.</div>
          ) : (
            <div className="space-y-2">
              {topics.map(topic => {
                const key  = topicToKey(topic)
                const file = config.topic_assets?.[key]
                return (
                  <div key={topic} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-100">
                      <span className="text-xs font-semibold text-gray-700">{topic}</span>
                      {!file && (
                        <span className="text-xs text-brand-orange">⚠ No asset file — reload to create</span>
                      )}
                    </div>
                    {file && <AssetRow file={file} label={`${topic} product & domain details`} />}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </Section>
    </div>
  )
}

function BenchmarkBrandConfig({ value, brandVariants, onChange }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft]     = useState(value)
  const [saving, setSaving]   = useState(false)

  const knownBrands = Object.keys(brandVariants)

  async function handleSave() {
    if (!draft.trim()) return
    setSaving(true)
    await updateBenchmarkBrand(draft.trim())
    setSaving(false)
    setEditing(false)
    onChange()
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 max-w-lg">
      <p className="text-xs text-gray-400 mb-4">
        The brand being measured. Analysis results, rankings, and watch-outs are all relative to this brand.
        The brand must have an entry in <strong className="text-gray-500">brand_variants</strong> in config to be detected in AI responses.
      </p>
      {editing ? (
        <div className="flex items-center gap-2">
          {knownBrands.length > 0 ? (
            <select
              value={draft}
              onChange={e => setDraft(e.target.value)}
              className="flex-1 border border-brand-blue/50 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-brand-blue"
              autoFocus
            >
              {knownBrands.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          ) : (
            <input
              type="text"
              value={draft}
              onChange={e => setDraft(e.target.value)}
              className="flex-1 border border-brand-blue/50 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-brand-blue"
              autoFocus
            />
          )}
          <button
            onClick={handleSave}
            disabled={saving || !draft.trim()}
            className="px-3 py-1.5 text-sm bg-brand-blue text-brand-navy font-semibold rounded hover:bg-brand-blue/90 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button onClick={() => { setEditing(false); setDraft(value) }} className="text-sm text-gray-400 hover:text-gray-600">Cancel</button>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-brand-navy">{value}</span>
          <button onClick={() => { setEditing(true); setDraft(value) }} className="text-xs text-brand-blue hover:text-brand-blue/80">Change</button>
        </div>
      )}
    </div>
  )
}

function Section({ title, children }) {
  return (
    <section className="mb-10">
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-xs font-semibold text-gray-500">{title}</h2>
      </div>
      {children}
    </section>
  )
}

function AssetRow({ file, label }) {
  const [status, setStatus] = useState(null)  // null | 'opening' | 'ok' | 'err'

  async function handleOpen() {
    setStatus('opening')
    try {
      await openAsset(file)
      setStatus('ok')
      setTimeout(() => setStatus(null), 2000)
    } catch {
      setStatus('err')
      setTimeout(() => setStatus(null), 3000)
    }
  }

  return (
    <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 last:border-0 gap-3">
      <span className="text-sm text-gray-700 min-w-0">{label}</span>
      <div className="flex items-center gap-3 shrink-0">
        <span className="font-mono text-xs text-gray-400 hidden sm:block">backend/assets/{file}</span>
        <button
          onClick={handleOpen}
          disabled={status === 'opening'}
          className={`text-xs font-medium px-2.5 py-1 rounded border transition-colors ${
            status === 'ok'  ? 'border-brand-blue/30 text-brand-blue bg-brand-blue/10' :
            status === 'err' ? 'border-brand-orange/30 text-brand-orange bg-brand-orange/10' :
            'border-gray-200 text-brand-blue hover:border-brand-blue/50 hover:bg-brand-blue/10'
          }`}
        >
          {status === 'opening' ? '…' : status === 'ok' ? 'Opened ✓' : status === 'err' ? 'Not found' : 'Open'}
        </button>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { updateModels } from '../api'

const MODEL_LABELS = {
  claude:     { label: 'Claude',     model: 'claude-opus-4-6',                  key: 'ANTHROPIC_API_KEY' },
  openai:     { label: 'GPT-4o',     model: 'gpt-4o',                           key: 'OPENAI_API_KEY' },
  gemini:     { label: 'Gemini',     model: 'gemini-1.5-pro',                   key: 'GOOGLE_API_KEY' },
  perplexity: { label: 'Perplexity', model: 'llama-3.1-sonar-large-128k-online', key: 'PERPLEXITY_API_KEY' },
}

export default function ModelConfig({ models, onChange }) {
  const [saving, setSaving] = useState(null)

  async function toggleModel(key, current) {
    setSaving(key)
    await updateModels({ [key]: { enabled: !current } })
    setSaving(null)
    onChange()
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {Object.entries(models).map(([key, cfg]) => {
        const meta = MODEL_LABELS[key] || { label: key, model: cfg.model_string, key: '' }
        return (
          <div key={key} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-medium text-gray-900 text-sm">{meta.label}</div>
                <div className="font-mono text-xs text-gray-400 mt-0.5">{meta.model}</div>
              </div>
              <button
                onClick={() => toggleModel(key, cfg.enabled)}
                disabled={saving === key}
                className={`w-10 h-5 rounded-full transition-colors mt-0.5 ${cfg.enabled ? 'bg-brand-blue' : 'bg-gray-300'}`}
                title={cfg.enabled ? 'Enabled' : 'Disabled'}
              />
            </div>
            <div className="mt-3 flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${cfg.enabled ? 'bg-brand-blue' : 'bg-gray-300'}`} />
              <span className="text-xs text-gray-400">
                {cfg.enabled ? 'Enabled' : 'Disabled'}
              </span>
              <span className="text-gray-200 mx-1">·</span>
              <span className="text-xs text-gray-400">API key: check .env</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

import { useState } from 'react'
import { addPrompt, updatePrompt, deletePrompt } from '../api'

// addOnly=true renders just the "+ Add prompt" button/form (used to add the first prompt for a new topic)
// allPrompts is the full list used to derive the available topic suggestions
export default function PromptTable({ prompts, allPrompts = [], addOnly = false, onChange }) {
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm]   = useState({})
  const [showAdd, setShowAdd]     = useState(false)
  const [addForm, setAddForm]     = useState({ topic: '', newTopic: '', text: '' })
  const [saving, setSaving]       = useState(false)

  const existingTopics = [...new Set(allPrompts.map(p => p.topic))].sort()

  function startEdit(p) {
    setEditingId(p.id)
    setEditForm({ topic: p.topic, newTopic: '', text: p.text })
  }

  function cancelEdit() {
    setEditingId(null)
  }

  async function saveEdit(id) {
    const topic = editForm.topic === '__new__' ? editForm.newTopic.trim() : editForm.topic
    if (!topic || !editForm.text.trim()) return
    setSaving(true)
    await updatePrompt(id, { topic, text: editForm.text.trim() })
    setEditingId(null)
    setSaving(false)
    onChange()
  }

  async function handleToggle(p) {
    await updatePrompt(p.id, { active: !p.active })
    onChange()
  }

  async function handleDelete(id) {
    if (!confirm('Delete this prompt?')) return
    await deletePrompt(id)
    onChange()
  }

  async function handleAdd() {
    // When inside a topic card, fixedTopic is shown as display text but addForm.topic is empty
    const fixedTopic = prompts[0]?.topic
    const topic = fixedTopic
      || (addForm.topic === '__new__' ? addForm.newTopic.trim() : addForm.topic)
    if (!topic || !addForm.text.trim()) return
    setSaving(true)
    await addPrompt({ topic, text: addForm.text.trim(), active: true })
    setAddForm({ topic: '', newTopic: '', text: '' })
    setShowAdd(false)
    setSaving(false)
    onChange()
  }

  if (addOnly) {
    return (
      <>
        <button
          onClick={() => setShowAdd(true)}
          className="text-sm text-brand-blue hover:text-brand-blue/80"
        >
          + Add prompt / new topic
        </button>
        <AddModal
          show={showAdd}
          form={addForm}
          topics={existingTopics}
          saving={saving}
          onChange={setAddForm}
          onAdd={handleAdd}
          onClose={() => { setShowAdd(false); setAddForm({ topic: '', newTopic: '', text: '' }) }}
        />
      </>
    )
  }

  return (
    <div>
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left px-3 py-2 text-xs font-medium text-gray-500">Prompt</th>
              <th className="px-3 py-2 text-xs font-medium text-gray-500 w-12 text-center">On</th>
              <th className="px-3 py-2 w-16" />
            </tr>
          </thead>
          <tbody>
            {prompts.map(p => (
              editingId === p.id ? (
                <tr key={p.id} className="border-b border-gray-100 bg-brand-blue/10">
                  <td className="px-3 py-2" colSpan={2}>
                    <input
                      value={editForm.text}
                      onChange={e => setEditForm(f => ({ ...f, text: e.target.value }))}
                      onKeyDown={e => e.key === 'Enter' && saveEdit(p.id)}
                      className="w-full border border-brand-blue/50 rounded px-2 py-1 text-xs focus:outline-none focus:border-brand-blue"
                      autoFocus
                    />
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex gap-2">
                      <button onClick={() => saveEdit(p.id)} disabled={saving} className="text-xs text-brand-blue font-medium">Save</button>
                      <button onClick={cancelEdit} className="text-xs text-gray-400">Cancel</button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-700 text-xs">{p.text}</td>
                  <td className="px-3 py-2 text-center">
                    <button
                      onClick={() => handleToggle(p)}
                      className={`w-7 h-3.5 rounded-full transition-colors ${p.active ? 'bg-brand-blue' : 'bg-gray-300'}`}
                    />
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex gap-2 justify-end">
                      <button onClick={() => startEdit(p)} className="text-gray-400 hover:text-brand-blue text-xs">Edit</button>
                      <button onClick={() => handleDelete(p.id)} className="text-gray-300 hover:text-red-500 text-xs">×</button>
                    </div>
                  </td>
                </tr>
              )
            ))}
          </tbody>
        </table>
      </div>

      <button onClick={() => setShowAdd(true)} className="mt-2 text-xs text-brand-blue hover:text-brand-blue/80">
        + Add prompt
      </button>

      <AddModal
        show={showAdd}
        form={addForm}
        topics={existingTopics}
        saving={saving}
        onChange={setAddForm}
        onAdd={handleAdd}
        onClose={() => { setShowAdd(false); setAddForm({ topic: '', newTopic: '', text: '' }) }}
        fixedTopic={prompts[0]?.topic}
      />
    </div>
  )
}

function AddModal({ show, form, topics, saving, onChange, onAdd, onClose, fixedTopic }) {
  if (!show) return null
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h3 className="font-semibold text-gray-900 mb-4">Add Prompt</h3>

        {fixedTopic ? (
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-500 mb-1">Topic</label>
            <div className="px-3 py-1.5 border border-gray-200 rounded text-sm text-gray-600 bg-gray-50">{fixedTopic}</div>
          </div>
        ) : (
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-500 mb-1">Topic</label>
            <TopicInput
              value={form.topic}
              newValue={form.newTopic}
              topics={topics}
              onChange={v => onChange(f => ({ ...f, topic: v }))}
              onNewChange={v => onChange(f => ({ ...f, newTopic: v }))}
            />
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-500 mb-1">Prompt text</label>
          <input
            type="text"
            value={form.text}
            onChange={e => onChange(f => ({ ...f, text: e.target.value }))}
            placeholder="e.g. best payroll software for uk accountants 2026"
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-brand-blue"
            onKeyDown={e => e.key === 'Enter' && onAdd()}
            autoFocus
          />
        </div>
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-1.5 text-sm text-gray-600 hover:text-gray-800">Cancel</button>
          <button onClick={onAdd} disabled={saving} className="px-4 py-1.5 text-sm bg-brand-blue text-brand-navy font-semibold rounded hover:bg-brand-blue/90 disabled:opacity-50">
            {saving ? 'Saving…' : 'Add'}
          </button>
        </div>
      </div>
    </div>
  )
}

function TopicInput({ value, newValue, topics, onChange, onNewChange }) {
  return (
    <div className="flex flex-col gap-1">
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-brand-blue"
      >
        <option value="">Select topic…</option>
        {topics.map(t => <option key={t} value={t}>{t}</option>)}
        <option value="__new__">+ New topic…</option>
      </select>
      {value === '__new__' && (
        <input
          type="text"
          value={newValue}
          onChange={e => onNewChange(e.target.value)}
          placeholder="New topic name"
          className="w-full border border-brand-blue/50 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-brand-blue"
          autoFocus
        />
      )}
    </div>
  )
}

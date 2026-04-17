import { useState } from 'react'
import { addCompetitor, updateCompetitor, deleteCompetitor } from '../api'

export default function CompetitorTable({ title, peerSetKey, peers, onChange }) {
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm]   = useState({ name: '', variants: '' })
  const [addForm, setAddForm]     = useState({ name: '', variants: '' })
  const [saving, setSaving]       = useState(false)

  function startEdit(p) {
    setEditingId(p.id)
    setEditForm({ name: p.name, variants: p.variants?.join(', ') || '' })
  }

  function cancelEdit() {
    setEditingId(null)
  }

  async function saveEdit(id) {
    if (!editForm.name.trim()) return
    const variants = editForm.variants
      ? editForm.variants.split(',').map(v => v.trim()).filter(Boolean)
      : [editForm.name.trim()]
    setSaving(true)
    await updateCompetitor(id, { name: editForm.name.trim(), variants })
    setEditingId(null)
    setSaving(false)
    onChange()
  }

  async function handleAdd() {
    if (!addForm.name.trim()) return
    const variants = addForm.variants
      ? addForm.variants.split(',').map(v => v.trim()).filter(Boolean)
      : [addForm.name.trim()]
    setSaving(true)
    await addCompetitor({ name: addForm.name.trim(), variants, peer_set: peerSetKey })
    setAddForm({ name: '', variants: '' })
    setSaving(false)
    onChange()
  }

  async function handleDelete(id) {
    if (!confirm('Remove this competitor?')) return
    await deleteCompetitor(id)
    onChange()
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="px-4 py-2.5 border-b border-gray-100 bg-gray-50">
        <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">{title}</span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100">
            <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 w-36">Brand</th>
            <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Variants</th>
            <th className="px-4 py-2 w-20" />
          </tr>
        </thead>
        <tbody>
          {peers.map(p => (
            editingId === p.id ? (
              <tr key={p.id} className="border-b border-gray-50 bg-brand-blue/10">
                <td className="px-4 py-2">
                  <input
                    value={editForm.name}
                    onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
                    className="w-full border border-brand-blue/50 rounded px-2 py-1 text-xs focus:outline-none focus:border-brand-blue"
                    autoFocus
                  />
                </td>
                <td className="px-4 py-2">
                  <input
                    value={editForm.variants}
                    onChange={e => setEditForm(f => ({ ...f, variants: e.target.value }))}
                    placeholder="Variant1, Variant2"
                    className="w-full border border-brand-blue/50 rounded px-2 py-1 text-xs focus:outline-none focus:border-brand-blue"
                    onKeyDown={e => e.key === 'Enter' && saveEdit(p.id)}
                  />
                </td>
                <td className="px-4 py-2">
                  <div className="flex gap-2">
                    <button
                      onClick={() => saveEdit(p.id)}
                      disabled={saving}
                      className="text-xs text-brand-blue hover:text-brand-blue/80 font-medium"
                    >
                      Save
                    </button>
                    <button onClick={cancelEdit} className="text-xs text-gray-400 hover:text-gray-600">
                      Cancel
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-800 font-medium text-xs">{p.name}</td>
                <td className="px-4 py-2 text-gray-400 text-xs font-mono">{p.variants?.join(', ')}</td>
                <td className="px-4 py-2">
                  <div className="flex gap-2 justify-end">
                    <button
                      onClick={() => startEdit(p)}
                      className="text-gray-400 hover:text-brand-blue text-xs"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="text-gray-300 hover:text-red-500 text-xs"
                    >
                      ×
                    </button>
                  </div>
                </td>
              </tr>
            )
          ))}
          {/* Add row */}
          <tr className="border-t border-gray-100 bg-gray-50">
            <td className="px-4 py-2">
              <input
                value={addForm.name}
                onChange={e => setAddForm(f => ({ ...f, name: e.target.value }))}
                placeholder="Brand name"
                className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:border-brand-blue"
              />
            </td>
            <td className="px-4 py-2">
              <input
                value={addForm.variants}
                onChange={e => setAddForm(f => ({ ...f, variants: e.target.value }))}
                placeholder="Variant1, Variant2 (optional)"
                className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:border-brand-blue"
                onKeyDown={e => e.key === 'Enter' && handleAdd()}
              />
            </td>
            <td className="px-4 py-2">
              <button
                onClick={handleAdd}
                disabled={saving}
                className="text-brand-blue hover:text-brand-blue/80 text-xs font-medium disabled:opacity-50"
              >
                Add
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}

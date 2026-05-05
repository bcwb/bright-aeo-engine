import { useState, useEffect } from 'react'
import Configure from './tabs/Configure'
import Run from './tabs/Run'
import Insights from './tabs/Insights'
import Monitor from './tabs/Monitor'
import { getMe } from './api'

const TABS = [
  { id: 'configure', label: 'Configure' },
  { id: 'run',       label: 'Run' },
  { id: 'insights',  label: 'Insights' },
  { id: 'monitor',   label: 'Monitor' },
]

// WCAG AA contrast rules for brand palette:
//   bg-brand-navy  → text-white       ✓ 14.3:1
//   bg-brand-blue  → text-brand-navy  ✓ 4.8:1  (white fails at 3.0:1)
//   bg-brand-orange→ text-brand-navy  ✓ 6.2:1  (white fails at 2.4:1)
//   bg-brand-yellow→ text-brand-navy  ✓ 9.7:1  (white fails at 1.5:1)

function BrightLogo() {
  return (
    <div className="px-4 py-4">
      <img
        src="/bright-logo.png"
        alt="Bright"
        className="h-8 w-auto"
      />
      <div className="text-white/50 text-xs font-mono mt-1.5">AEO Engine</div>
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab]         = useState('run')
  const [selectedRunId, setSelectedRunId] = useState(null)
  const [currentUser, setCurrentUser]     = useState(null)

  useEffect(() => { getMe().then(setCurrentUser) }, [])

  function handleRunComplete(runId) {
    setSelectedRunId(runId)
    setActiveTab('insights')
  }

  return (
    <div className="flex h-screen bg-gray-50 font-sans overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="w-52 flex flex-col shrink-0 bg-brand-navy">
        <BrightLogo />
        {/* Brand gradient accent bar under logo */}
        <div
          className="h-0.5 shrink-0"
          style={{ background: 'linear-gradient(90deg, #009FC7 0%, #E39400 60%, #E6D600 100%)' }}
        />

        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-l-2 border-white bg-white/15 text-white font-semibold pl-2.5'
                  : 'text-white/75 hover:text-white hover:bg-white/10 rounded border-l-2 border-transparent pl-2.5'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-white/10">
          {currentUser ? (
            <>
              <div className="text-white/80 text-xs font-medium truncate">{currentUser.name}</div>
              <div className="text-white/40 text-xs truncate mt-0.5">{currentUser.email}</div>
              {currentUser.source === 'dev_fallback' && (
                <div className="text-brand-yellow text-xs mt-1">dev mode</div>
              )}
            </>
          ) : (
            <>
              <div className="text-white/40 text-xs">Bright Software Group</div>
              <div className="text-white/30 text-xs mt-0.5">Internal</div>
            </>
          )}
        </div>
      </aside>

      {/* ── Content ── */}
      <main className="flex-1 overflow-auto flex flex-col">
        {/* Brand gradient accent bar — mirrors sidebar */}
        <div
          className="h-1 shrink-0"
          style={{ background: 'linear-gradient(90deg, #009FC7 0%, #E39400 60%, #E6D600 100%)' }}
        />
        <div className="flex-1 overflow-auto">
          {activeTab === 'configure' && <Configure />}
          {activeTab === 'run'       && <Run onRunComplete={handleRunComplete} />}
          {activeTab === 'insights'  && (
            <Insights
              selectedRunId={selectedRunId}
              onSelectRun={setSelectedRunId}
            />
          )}
          {activeTab === 'monitor'   && <Monitor />}
        </div>
      </main>
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'

type Host = {
  id: string
  name: string
  base_url: string
  status: string
  last_seen: string | null
  operation_map: Record<string, string | null>
}

type Run = {
  id: string
  host_id: string
  status: string
  created_at: string
  remote?: unknown
}

const API = 'http://localhost:8000/api'

export default function App() {
  const [hosts, setHosts] = useState<Host[]>([])
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedHost, setSelectedHost] = useState<string>('')
  const [hostName, setHostName] = useState('Lab PC 01')
  const [hostUrl, setHostUrl] = useState('http://localhost:8000')
  const [message, setMessage] = useState('Ready')

  const activeHost = useMemo(
    () => hosts.find((host) => host.id === selectedHost) ?? hosts[0],
    [hosts, selectedHost],
  )

  async function refresh() {
    const [hostResponse, runResponse] = await Promise.all([
      fetch(`${API}/hosts`),
      fetch(`${API}/runs`),
    ])
    const hostData = await hostResponse.json()
    const runData = await runResponse.json()
    setHosts(hostData)
    setRuns(runData)
    if (!selectedHost && hostData.length) setSelectedHost(hostData[0].id)
  }

  useEffect(() => {
    refresh().catch(() => setMessage('Backend unavailable'))
  }, [])

  async function addHost() {
    setMessage('Adding host…')
    const response = await fetch(`${API}/hosts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: hostName, base_url: hostUrl }),
    })
    if (!response.ok) {
      setMessage(await response.text())
      return
    }
    const host = await response.json()
    setSelectedHost(host.id)
    setMessage('Host added')
    await refresh()
  }

  async function discover() {
    if (!activeHost) return
    setMessage('Discovering ATS API…')
    const response = await fetch(`${API}/hosts/${activeHost.id}/discover`, { method: 'POST' })
    if (!response.ok) {
      setMessage(await response.text())
      await refresh()
      return
    }
    const data = await response.json()
    setMessage(`ATS online · ${data.operations.length} API operations discovered`)
    await refresh()
  }

  const online = hosts.filter((host) => host.status === 'ONLINE').length
  const running = runs.filter((run) => ['SUBMITTING', 'SUBMITTED', 'RUNNING'].includes(run.status)).length

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">X</div>
          <div><strong>XTS Command Center</strong><span>Next</span></div>
        </div>
        <nav>
          <button className="nav-active">Overview</button>
          <button>Test Console</button>
          <button>Lab Resources</button>
          <button>Runs & Results</button>
          <button>Retry Center</button>
          <button>Projects</button>
          <button>Administration</button>
        </nav>
        <div className="sidebar-foot">Execution backend: OmniLab ATS 2</div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <p className="eyebrow">LAB OPERATIONS</p>
            <h1>Command Center</h1>
            <p>Prepare, launch and follow xTS runs across Linux ATS hosts.</p>
          </div>
          <div className="status-pill"><span /> {message}</div>
        </header>

        <section className="stats-grid">
          <article><span>ATS Hosts</span><strong>{hosts.length}</strong><small>{online} online</small></article>
          <article><span>Active Runs</span><strong>{running}</strong><small>{runs.length} total tracked</small></article>
          <article><span>Execution Layer</span><strong>ATS 2</strong><small>Tradefed-backed</small></article>
          <article><span>Control Plane</span><strong>Ready</strong><small>API adapter isolated</small></article>
        </section>

        <section className="workspace-grid">
          <div className="panel primary-panel">
            <div className="panel-head">
              <div><p className="eyebrow">TESTER FLOW</p><h2>Launch readiness</h2></div>
              <button className="ghost" onClick={() => refresh()}>Refresh</button>
            </div>

            <div className="flow-row">
              <div className="flow-step complete"><b>1</b><span>Host</span><small>{activeHost?.status ?? 'Not configured'}</small></div>
              <div className="flow-line" />
              <div className="flow-step"><b>2</b><span>Device</span><small>ATS inventory</small></div>
              <div className="flow-line" />
              <div className="flow-step"><b>3</b><span>Test</span><small>CTS / GTS / VTS</small></div>
              <div className="flow-line" />
              <div className="flow-step"><b>4</b><span>Run</span><small>Live status</small></div>
            </div>

            <div className="host-list">
              {hosts.length === 0 ? (
                <div className="empty-state">No ATS host registered yet.</div>
              ) : hosts.map((host) => (
                <button key={host.id} className={`host-card ${activeHost?.id === host.id ? 'selected' : ''}`} onClick={() => setSelectedHost(host.id)}>
                  <div className={`host-dot ${host.status.toLowerCase()}`} />
                  <div><strong>{host.name}</strong><small>{host.base_url}</small></div>
                  <span>{host.status}</span>
                </button>
              ))}
            </div>

            <div className="action-row">
              <button className="primary" disabled={!activeHost} onClick={discover}>Check ATS & Discover API</button>
              <button className="secondary" disabled={!activeHost}>Open Test Console</button>
            </div>
          </div>

          <div className="panel add-host">
            <p className="eyebrow">LINUX TEST HOST</p>
            <h2>Add ATS host</h2>
            <label>Name<input value={hostName} onChange={(e) => setHostName(e.target.value)} /></label>
            <label>ATS base URL<input value={hostUrl} onChange={(e) => setHostUrl(e.target.value)} /></label>
            <button className="primary" onClick={addHost}>Register host</button>
            <p className="hint">Command Center talks to ATS through its published OpenAPI surface. No custom Linux runner is required for normal ATS-backed execution.</p>
          </div>
        </section>

        <section className="panel runs-panel">
          <div className="panel-head"><div><p className="eyebrow">RECENT ACTIVITY</p><h2>Runs</h2></div></div>
          {runs.length === 0 ? <div className="empty-state">No runs submitted yet.</div> : (
            <div className="run-table">
              <div className="run-row run-header"><span>Run</span><span>Host</span><span>Status</span><span>Created</span></div>
              {runs.slice(0, 8).map((run) => (
                <div className="run-row" key={run.id}>
                  <span>{run.id.slice(0, 8)}</span>
                  <span>{hosts.find((h) => h.id === run.host_id)?.name ?? run.host_id.slice(0, 8)}</span>
                  <span><i className={`state ${run.status.toLowerCase()}`} />{run.status}</span>
                  <span>{new Date(run.created_at).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

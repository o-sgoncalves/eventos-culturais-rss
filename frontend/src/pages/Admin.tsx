import { useEffect, useState } from 'react'
import { login, logout, isLoggedIn, fetchPending, approveEvent, rejectEvent, fetchStats, fetchSources, addSource, removeSource, triggerScrape } from '../api/admin'
import type { Event, Source, Stats } from '../types'

export default function Admin() {
  const [authed, setAuthed] = useState(isLoggedIn())
  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [loginError, setLoginError] = useState('')
  const [pending, setPending] = useState<Event[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [sources, setSources] = useState<Source[]>([])
  const [newSource, setNewSource] = useState('')
  const [tab, setTab] = useState<'pending' | 'sources'>('pending')

  const doLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(loginForm.username, loginForm.password)
      setAuthed(true)
    } catch {
      setLoginError('Usuário ou senha incorretos')
    }
  }

  const loadData = async () => {
    const [p, s, src] = await Promise.all([fetchPending(), fetchStats(), fetchSources()])
    setPending(p)
    setStats(s)
    setSources(src)
  }

  useEffect(() => {
    if (authed) loadData()
  }, [authed])

  const handleApprove = async (id: number) => {
    await approveEvent(id)
    setPending((prev) => prev.filter((e) => e.id !== id))
  }

  const handleReject = async (id: number) => {
    await rejectEvent(id)
    setPending((prev) => prev.filter((e) => e.id !== id))
  }

  const handleAddSource = async () => {
    if (!newSource.trim()) return
    const src = await addSource(newSource.trim())
    setSources((prev) => [...prev, src])
    setNewSource('')
  }

  if (!authed) {
    return (
      <div className="min-h-screen bg-brand-dark flex items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-bold text-gray-100 mb-6 text-center">Admin — Goiânia Cultural</h1>
          <form onSubmit={doLogin} className="flex flex-col gap-4">
            <input
              required
              placeholder="Usuário"
              value={loginForm.username}
              onChange={(e) => setLoginForm((p) => ({ ...p, username: e.target.value }))}
              className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-brand-muted focus:outline-none focus:border-brand-purple"
            />
            <input
              required type="password"
              placeholder="Senha"
              value={loginForm.password}
              onChange={(e) => setLoginForm((p) => ({ ...p, password: e.target.value }))}
              className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-brand-muted focus:outline-none focus:border-brand-purple"
            />
            {loginError && <p className="text-red-400 text-sm">{loginError}</p>}
            <button type="submit" className="bg-brand-purple text-white font-semibold py-2.5 rounded-lg hover:bg-brand-purple/90">
              Entrar
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-brand-dark px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-xl font-bold text-gray-100">Painel Admin</h1>
          <div className="flex gap-3">
            <button onClick={() => triggerScrape()} className="text-xs border border-brand-border text-brand-muted px-3 py-1.5 rounded hover:text-gray-100">
              ↻ Scrape agora
            </button>
            <button onClick={() => { logout(); setAuthed(false) }} className="text-xs text-red-400 hover:text-red-300">
              Sair
            </button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-brand-card border border-brand-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-brand-purple">{stats.pending_events}</p>
              <p className="text-xs text-brand-muted mt-1">Pendentes</p>
            </div>
            <div className="bg-brand-card border border-brand-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-brand-teal">{stats.approved_events}</p>
              <p className="text-xs text-brand-muted mt-1">Publicados</p>
            </div>
            <div className="bg-brand-card border border-brand-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-gray-100">{stats.total_events}</p>
              <p className="text-xs text-brand-muted mt-1">Total</p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-4 border-b border-brand-border">
          {(['pending', 'sources'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`pb-2 text-sm font-medium transition-colors ${tab === t ? 'text-brand-purple border-b-2 border-brand-purple' : 'text-brand-muted'}`}
            >
              {t === 'pending' ? `Pendentes (${pending.length})` : 'Fontes Instagram'}
            </button>
          ))}
        </div>

        {tab === 'pending' && (
          <div className="flex flex-col gap-3">
            {pending.length === 0 && <p className="text-brand-muted text-sm py-8 text-center">Nenhum evento pendente ✓</p>}
            {pending.map((event) => (
              <div key={event.id} className="bg-brand-card border border-brand-border rounded-xl p-4 flex gap-4 items-start">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-100 mb-1 truncate">{event.title}</p>
                  <p className="text-xs text-brand-muted line-clamp-2">{event.description}</p>
                  {event.source_url && (
                    <a href={event.source_url} target="_blank" rel="noreferrer" className="text-xs text-brand-purple hover:underline mt-1 block">
                      Ver fonte ↗
                    </a>
                  )}
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button onClick={() => handleApprove(event.id)} className="bg-emerald-600 text-white text-xs px-3 py-1.5 rounded hover:bg-emerald-700">
                    Aprovar
                  </button>
                  <button onClick={() => handleReject(event.id)} className="bg-red-700/50 text-red-300 text-xs px-3 py-1.5 rounded hover:bg-red-700">
                    Rejeitar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === 'sources' && (
          <div>
            <div className="flex gap-2 mb-4">
              <input
                placeholder="@novaconta"
                value={newSource}
                onChange={(e) => setNewSource(e.target.value.replace('@', ''))}
                className="flex-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-brand-muted focus:outline-none focus:border-brand-purple"
              />
              <button onClick={handleAddSource} className="bg-brand-purple text-white text-sm px-4 py-2 rounded-lg hover:bg-brand-purple/90">
                Adicionar
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {sources.map((src) => (
                <div key={src.id} className="bg-brand-card border border-brand-border rounded-lg px-4 py-3 flex justify-between items-center">
                  <div>
                    <span className="text-sm text-gray-100 font-medium">@{src.username}</span>
                    {src.last_scraped && (
                      <span className="text-xs text-brand-muted ml-3">
                        Último scrape: {new Date(src.last_scraped).toLocaleDateString('pt-BR')}
                      </span>
                    )}
                    {src.error_count > 0 && (
                      <span className="text-xs text-red-400 ml-2">{src.error_count} erros</span>
                    )}
                  </div>
                  <button onClick={() => removeSource(src.id).then(() => setSources((p) => p.filter((s) => s.id !== src.id)))}
                    className="text-red-400 text-xs hover:text-red-300">
                    Remover
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

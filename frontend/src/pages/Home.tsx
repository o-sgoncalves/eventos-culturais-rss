import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import EventCard from '../components/EventCard'
import Filters from '../components/Filters'
import { fetchEvents } from '../api/events'
import type { Event, EventFilters } from '../types'

export default function Home() {
  const [events, setEvents] = useState<Event[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<EventFilters>({})
  const [search, setSearch] = useState('')

  const load = useCallback(async (f: EventFilters) => {
    setLoading(true)
    try {
      const res = await fetchEvents(f)
      setEvents(res.items)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const timeout = setTimeout(() => {
      load({ ...filters, q: search || undefined })
    }, 300)
    return () => clearTimeout(timeout)
  }, [filters, search, load])

  return (
    <div className="min-h-screen bg-brand-dark">
      {/* Header */}
      <header className="bg-brand-dark/80 backdrop-blur sticky top-0 z-10 border-b border-brand-border">
        <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
          <div>
            <span className="text-brand-purple font-black text-lg tracking-tight">Goiânia</span>
            <span className="text-gray-100 font-black text-lg ml-1">Cultural</span>
          </div>
          <Link
            to="/sugerir"
            className="bg-brand-purple text-white text-xs font-semibold px-4 py-2 rounded-full hover:bg-brand-purple/90 transition-colors"
          >
            + Sugerir Evento
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Buscar eventos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-brand-card border border-brand-border rounded-xl px-4 py-2.5 text-sm text-gray-100 placeholder-brand-muted focus:outline-none focus:border-brand-purple"
          />
        </div>

        <div className="flex gap-6">
          {/* Sidebar filters (desktop) */}
          <Filters filters={filters} onChange={setFilters} />

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Mobile chips */}
            <Filters filters={filters} onChange={setFilters} />

            {loading ? (
              <div className="text-center py-16 text-brand-muted">Carregando eventos...</div>
            ) : events.length === 0 ? (
              <div className="text-center py-16 text-brand-muted">
                <p className="text-lg mb-2">Nenhum evento encontrado</p>
                <p className="text-sm">Tente outros filtros ou{' '}
                  <Link to="/sugerir" className="text-brand-purple hover:underline">sugira um evento</Link>
                </p>
              </div>
            ) : (
              <>
                <p className="text-xs text-brand-muted mb-4">{total} evento{total !== 1 ? 's' : ''} encontrado{total !== 1 ? 's' : ''}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {events.map((event) => (
                    <EventCard key={event.id} event={event} />
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

import { CATEGORIES } from '../types'
import type { EventFilters } from '../types'

interface Props {
  filters: EventFilters
  onChange: (filters: EventFilters) => void
}

const DATE_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'hoje', label: 'Hoje' },
  { value: 'semana', label: 'Esta semana' },
  { value: 'mes', label: 'Este mês' },
]

export default function Filters({ filters, onChange }: Props) {
  const set = (patch: Partial<EventFilters>) => onChange({ ...filters, ...patch, page: 1 })

  return (
    <>
      {/* Mobile: horizontal chips */}
      <div className="md:hidden">
        <div className="flex gap-2 overflow-x-auto pb-2 mb-2">
          {DATE_OPTIONS.map((_opt) => (
            <button
              key={_opt.value}
              onClick={() => set({ q: filters.q })}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                !filters.category && !_opt.value
                  ? 'bg-brand-purple text-white'
                  : 'bg-brand-card border border-brand-border text-brand-muted hover:text-gray-100'
              }`}
            >
              {_opt.label}
            </button>
          ))}
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => set({ category: filters.category === cat.value ? undefined : cat.value })}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filters.category === cat.value
                  ? 'bg-brand-purple text-white'
                  : 'bg-brand-card border border-brand-border text-brand-muted hover:text-gray-100'
              }`}
            >
              {cat.label}
            </button>
          ))}
          <button
            onClick={() => set({ free: !filters.free })}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filters.free
                ? 'bg-emerald-600 text-white'
                : 'bg-brand-card border border-brand-border text-brand-muted hover:text-gray-100'
            }`}
          >
            Gratuitos
          </button>
        </div>
      </div>

      {/* Desktop: sidebar */}
      <aside className="hidden md:flex flex-col gap-6 w-44 flex-shrink-0">
        <div>
          <p className="text-xs uppercase tracking-widest text-brand-muted mb-2">Data</p>
          <div className="flex flex-col gap-1">
            {DATE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={`text-left px-3 py-1.5 rounded text-sm transition-colors ${
                  !opt.value ? 'bg-brand-purple text-white font-semibold' : 'text-brand-muted hover:text-gray-100'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-widest text-brand-muted mb-2">Categoria</p>
          <div className="flex flex-col gap-1">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                onClick={() => set({ category: filters.category === cat.value ? undefined : cat.value })}
                className={`text-left px-3 py-1.5 rounded text-sm transition-colors ${
                  filters.category === cat.value
                    ? 'text-brand-purple font-semibold'
                    : 'text-brand-muted hover:text-gray-100'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-widest text-brand-muted mb-2">Opções</p>
          <label className="flex items-center gap-2 text-sm text-brand-muted cursor-pointer hover:text-gray-100">
            <input
              type="checkbox"
              checked={!!filters.free}
              onChange={(e) => set({ free: e.target.checked })}
              className="accent-brand-purple"
            />
            Só gratuitos
          </label>
        </div>
      </aside>
    </>
  )
}

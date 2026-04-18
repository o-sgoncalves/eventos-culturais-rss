import type { Event } from '../types'
import { CATEGORY_COLORS, CATEGORIES } from '../types'

interface Props {
  event: Event
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Data a confirmar'
  const d = new Date(dateStr)
  return d.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' })
}

function shareEvent(event: Event): void {
  const url = `${window.location.origin}/eventos/${event.id}`
  if (navigator.share) {
    navigator.share({ title: event.title, url })
  } else {
    navigator.clipboard.writeText(url)
  }
}

export default function EventCard({ event }: Props) {
  const gradient = CATEGORY_COLORS[event.category ?? 'outros'] ?? CATEGORY_COLORS['outros']
  const categoryLabel = CATEGORIES.find((c) => c.value === event.category)?.label ?? '📌 Outros'

  return (
    <article className="bg-brand-card rounded-xl overflow-hidden border border-brand-border hover:border-brand-purple/50 transition-colors">
      {/* Image / gradient header */}
      <div className={`relative h-28 bg-gradient-to-br ${gradient}`}>
        {event.image_url && (
          <img
            src={event.image_url}
            alt={event.title}
            className="absolute inset-0 w-full h-full object-cover opacity-60"
          />
        )}
        <span className="absolute top-2 left-2 bg-black/50 backdrop-blur-sm text-white text-xs font-bold px-2 py-1 rounded-full">
          {categoryLabel}
        </span>
        {event.is_free ? (
          <span className="absolute top-2 right-2 bg-emerald-600 text-white text-xs font-bold px-2 py-1 rounded-full">
            GRATUITO
          </span>
        ) : event.price ? (
          <span className="absolute top-2 right-2 bg-brand-dark/80 border border-brand-purple text-brand-purple text-xs font-bold px-2 py-1 rounded-full">
            {event.price}
          </span>
        ) : null}
      </div>

      {/* Content */}
      <div className="p-3">
        <h3 className="text-sm font-bold text-gray-100 leading-tight mb-1 line-clamp-2">
          {event.title}
        </h3>
        <div className="flex flex-wrap gap-2 text-xs text-brand-muted mb-2">
          <span>📅 {formatDate(event.event_date)}</span>
          {event.event_time && <span>🕗 {event.event_time}</span>}
          {event.location && <span>📍 {event.location}</span>}
        </div>
        <div className="flex justify-between items-center">
          {event.region && (
            <span className="bg-brand-dark text-brand-purple text-xs px-2 py-0.5 rounded">
              {event.region}
            </span>
          )}
          <div className="flex gap-3 ml-auto">
            <button
              onClick={() => shareEvent(event)}
              className="text-brand-muted hover:text-gray-100 transition-colors text-sm"
              title="Compartilhar"
            >
              📤
            </button>
            {event.id && (
              <a
                href={`/api/events/${event.id}/ics`}
                className="text-brand-muted hover:text-gray-100 transition-colors text-sm"
                title="Adicionar ao calendário"
                download
              >
                📅
              </a>
            )}
          </div>
        </div>
      </div>
    </article>
  )
}

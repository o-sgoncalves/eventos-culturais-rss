export interface Event {
  id: number
  title: string
  description: string | null
  event_date: string | null
  event_time: string | null
  location: string | null
  address: string | null
  region: string | null
  price: string | null
  is_free: boolean
  category: string | null
  source_url: string | null
  image_url: string | null
  approved: boolean
  submitted_by_user: boolean
  created_at: string
}

export interface EventsResponse {
  items: Event[]
  total: number
  page: number
  page_size: number
}

export interface EventFilters {
  category?: string
  free?: boolean
  region?: string
  q?: string
  page?: number
}

export interface Source {
  id: number
  platform: string
  username: string
  active: boolean
  last_scraped: string | null
  error_count: number
  created_at: string
}

export interface Stats {
  total_events: number
  pending_events: number
  approved_events: number
  by_category: Record<string, number>
}

export const CATEGORIES = [
  { value: 'musica', label: '🎵 Música' },
  { value: 'teatro', label: '🎭 Teatro' },
  { value: 'cinema', label: '🎬 Cinema' },
  { value: 'festa', label: '🎉 Festa' },
  { value: 'exposicao', label: '🖼 Exposição' },
  { value: 'arte', label: '🎨 Arte' },
  { value: 'workshop', label: '🛠 Workshop' },
  { value: 'palestra', label: '📢 Palestra' },
  { value: 'esporte', label: '⚽ Esporte' },
  { value: 'gastronomia', label: '🍽 Gastronomia' },
  { value: 'outros', label: '📌 Outros' },
]

export const CATEGORY_COLORS: Record<string, string> = {
  musica: 'from-brand-purple to-brand-teal',
  teatro: 'from-amber-500 to-red-500',
  cinema: 'from-blue-500 to-indigo-600',
  festa: 'from-pink-500 to-rose-500',
  exposicao: 'from-teal-400 to-cyan-500',
  arte: 'from-violet-500 to-purple-700',
  workshop: 'from-orange-400 to-amber-500',
  palestra: 'from-sky-400 to-blue-500',
  esporte: 'from-green-400 to-emerald-600',
  gastronomia: 'from-yellow-400 to-orange-500',
  outros: 'from-gray-500 to-gray-700',
}

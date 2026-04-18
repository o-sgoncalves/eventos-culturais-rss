import client from './client'
import type { Event, EventFilters, EventsResponse } from '../types'

export async function fetchEvents(filters: EventFilters = {}): Promise<EventsResponse> {
  const params = new URLSearchParams()
  if (filters.category) params.set('category', filters.category)
  if (filters.free) params.set('free', 'true')
  if (filters.region) params.set('region', filters.region)
  if (filters.q) params.set('q', filters.q)
  if (filters.page) params.set('page', String(filters.page))
  const { data } = await client.get(`/api/events?${params}`)
  return data
}

export async function fetchEvent(id: number): Promise<Event> {
  const { data } = await client.get(`/api/events/${id}`)
  return data
}

export async function suggestEvent(payload: {
  title: string
  description?: string
  event_date?: string
  location?: string
  price?: string
  category?: string
}): Promise<Event> {
  const { data } = await client.post('/api/events/suggest', payload)
  return data
}

export function buildIcsUrl(id: number): string {
  return `/api/events/${id}/ics`
}

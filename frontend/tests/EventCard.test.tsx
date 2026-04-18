import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import EventCard from '../src/components/EventCard'
import type { Event } from '../src/types'

const baseEvent: Event = {
  id: 1,
  title: 'Show da Banda Xpto',
  description: 'Grande show!',
  event_date: '2026-04-25T20:00:00',
  event_time: '20:00',
  location: 'Casarão Cultural',
  address: null,
  region: 'Centro',
  price: 'R$ 40',
  is_free: false,
  category: 'musica',
  source_url: 'https://instagram.com/p/abc',
  image_url: null,
  approved: true,
  submitted_by_user: false,
  created_at: '2026-04-18T00:00:00',
}

describe('EventCard', () => {
  it('renders event title', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText('Show da Banda Xpto')).toBeInTheDocument()
  })

  it('renders price', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText('R$ 40')).toBeInTheDocument()
  })

  it('renders GRATUITO badge when is_free', () => {
    render(<EventCard event={{ ...baseEvent, is_free: true, price: 'Gratuito' }} />)
    expect(screen.getByText('GRATUITO')).toBeInTheDocument()
  })

  it('renders location', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText(/Casarão Cultural/)).toBeInTheDocument()
  })
})

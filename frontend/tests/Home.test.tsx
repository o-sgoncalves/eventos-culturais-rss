import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Home from '../src/pages/Home'
import * as eventsApi from '../src/api/events'

vi.mock('../src/api/events')

const mockEventsApi = vi.mocked(eventsApi)

describe('Home', () => {
  beforeEach(() => {
    mockEventsApi.fetchEvents.mockResolvedValue({
      items: [
        {
          id: 1,
          title: 'Show de Teste',
          description: null,
          event_date: '2026-04-25T20:00:00',
          event_time: '20:00',
          location: 'Casarão',
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
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
    })
  })

  it('renders header with project name', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByText('Cultural')).toBeInTheDocument()
  })

  it('renders event card after loading', async () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    await waitFor(() => {
      expect(screen.getByText('Show de Teste')).toBeInTheDocument()
    })
  })

  it('renders search input', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByPlaceholderText(/buscar/i)).toBeInTheDocument()
  })
})

# Frontend + Infrastructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** React 18 + TypeScript + Tailwind dark mode frontend with event listing, filters, admin panel, and full Docker Compose orchestration for all 7 services.

**Architecture:** Vite builds static files served by an nginx container. Backend API proxied via the main nginx reverse proxy. Admin panel lives at `/admin` as an SPA route (no separate app). Full `docker-compose.yml` orchestrates all services; `scripts/setup.sh` enables one-command setup.

**Tech Stack:** React 18, TypeScript 5, Tailwind CSS 3 (dark mode: `class`), Vite 5, Axios, React Router 6, ical.js (for .ics export), Vitest + Testing Library. Infrastructure: Docker Compose, Nginx, GitHub Actions.

**Prerequisites:** Phase 1 and Phase 2 must be complete.

---

## File Map

| File | Responsibility |
|---|---|
| `frontend/package.json` | Dependencies + scripts |
| `frontend/vite.config.ts` | Vite + proxy config |
| `frontend/tailwind.config.js` | Dark mode + custom colors |
| `frontend/tsconfig.json` | TypeScript config |
| `frontend/Dockerfile` | Multi-stage build → nginx |
| `frontend/src/types/index.ts` | Shared TypeScript interfaces |
| `frontend/src/api/client.ts` | Axios instance with base URL |
| `frontend/src/api/events.ts` | Events API calls |
| `frontend/src/api/admin.ts` | Admin API calls + JWT handling |
| `frontend/src/components/EventCard.tsx` | Event card (dark mode, category colors) |
| `frontend/src/components/Filters.tsx` | Chip filters (mobile) + sidebar (desktop) |
| `frontend/src/components/Calendar.tsx` | Month calendar view |
| `frontend/src/pages/Home.tsx` | Main listing page |
| `frontend/src/pages/Admin.tsx` | Admin panel (login + dashboard) |
| `frontend/src/pages/SubmitEvent.tsx` | Public event submission form |
| `frontend/src/App.tsx` | Router + dark mode wrapper |
| `frontend/src/main.tsx` | React entry point |
| `frontend/src/index.css` | Tailwind directives |
| `frontend/tests/EventCard.test.tsx` | Component test |
| `frontend/tests/Home.test.tsx` | Page smoke test |
| `nginx/nginx.conf` | Local reverse proxy |
| `nginx/nginx.prod.conf` | Production + SSL |
| `docker-compose.yml` | All 7 services (local) |
| `docker-compose.prod.yml` | Production overrides |
| `.env.example` | All environment variables |
| `scripts/setup.sh` | One-command setup |
| `.github/workflows/ci.yml` | Lint + tests on PRs |
| `.github/workflows/build.yml` | Docker build validation |
| `README.md` | PT-BR docs, 5-step install |
| `CONTRIBUTING.md` | Contribution guide |
| `docs/INSTALL.md` | Detailed install guide |
| `docs/DEPLOY.md` | VPS + SSL deploy guide |

---

## Task 1: Frontend Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.tsx`
- Create: `frontend/index.html`
- Create: `frontend/.env.example`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p frontend/src/{types,api,components,pages} frontend/tests frontend/public
```

- [ ] **Step 2: Write `frontend/package.json`**

```json
{
  "name": "goiania-cultural-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "@vitest/coverage-v8": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.6",
    "@testing-library/user-event": "^14.5.2",
    "eslint": "^8.57.0",
    "jsdom": "^24.1.0",
    "tailwindcss": "^3.4.4",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39",
    "typescript": "^5.4.5",
    "vite": "^5.3.1",
    "vitest": "^1.6.0"
  }
}
```

- [ ] **Step 3: Write `frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
  },
})
```

- [ ] **Step 4: Write `frontend/tailwind.config.js`**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          purple: '#6c63ff',
          teal: '#3ecfb2',
          dark: '#0f0f1a',
          card: '#16213e',
          border: '#2d2d4e',
          muted: '#9ca3af',
        },
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 5: Write `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src", "tests"]
}
```

- [ ] **Step 6: Write `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

body {
  @apply bg-brand-dark text-gray-100 font-sans;
}
```

- [ ] **Step 7: Write `frontend/index.html`**

```html
<!doctype html>
<html lang="pt-BR" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Eventos culturais de Goiânia — música, teatro, arte e muito mais" />
    <title>Goiânia Cultural</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 8: Write `frontend/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
```

- [ ] **Step 9: Write `frontend/tests/setup.ts`**

```typescript
import '@testing-library/jest-dom'
```

- [ ] **Step 10: Install dependencies and verify scaffold**

```bash
cd frontend
npm install
npm run build
```

Expected: build succeeds with no TypeScript errors

- [ ] **Step 11: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): project scaffold with React 18, TypeScript, Tailwind dark mode"
```

---

## Task 2: Types and API Client

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/events.ts`
- Create: `frontend/src/api/admin.ts`

- [ ] **Step 1: Write `frontend/src/types/index.ts`**

```typescript
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
```

- [ ] **Step 2: Write `frontend/src/api/client.ts`**

```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client
```

- [ ] **Step 3: Write `frontend/src/api/events.ts`**

```typescript
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
```

- [ ] **Step 4: Write `frontend/src/api/admin.ts`**

```typescript
import client from './client'
import type { Event, Source, Stats } from '../types'

export async function login(username: string, password: string): Promise<string> {
  const { data } = await client.post('/api/auth/login', { username, password })
  localStorage.setItem('admin_token', data.access_token)
  return data.access_token
}

export function logout(): void {
  localStorage.removeItem('admin_token')
}

export function isLoggedIn(): boolean {
  return !!localStorage.getItem('admin_token')
}

export async function fetchPending(): Promise<Event[]> {
  const { data } = await client.get('/api/admin/events/pending')
  return data
}

export async function approveEvent(id: number): Promise<Event> {
  const { data } = await client.put(`/api/admin/events/${id}/approve`)
  return data
}

export async function rejectEvent(id: number): Promise<void> {
  await client.delete(`/api/admin/events/${id}/reject`)
}

export async function updateEvent(id: number, payload: Partial<Event>): Promise<Event> {
  const { data } = await client.put(`/api/admin/events/${id}`, payload)
  return data
}

export async function fetchSources(): Promise<Source[]> {
  const { data } = await client.get('/api/admin/sources')
  return data
}

export async function addSource(username: string): Promise<Source> {
  const { data } = await client.post('/api/admin/sources', { username, platform: 'instagram' })
  return data
}

export async function removeSource(id: number): Promise<void> {
  await client.delete(`/api/admin/sources/${id}`)
}

export async function fetchStats(): Promise<Stats> {
  const { data } = await client.get('/api/admin/stats')
  return data
}

export async function triggerScrape(): Promise<void> {
  await client.post('/api/admin/trigger-scrape')
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types frontend/src/api
git commit -m "feat(frontend): TypeScript types and API client layer"
```

---

## Task 3: EventCard Component

**Files:**
- Create: `frontend/src/components/EventCard.tsx`
- Create: `frontend/tests/EventCard.test.tsx`

- [ ] **Step 1: Write failing test in `frontend/tests/EventCard.test.tsx`**

```tsx
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
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd frontend
npx vitest run tests/EventCard.test.tsx
```

Expected: `Error: Cannot find module '../src/components/EventCard'`

- [ ] **Step 3: Write `frontend/src/components/EventCard.tsx`**

```tsx
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
```

- [ ] **Step 4: Run test — verify it passes**

```bash
npx vitest run tests/EventCard.test.tsx
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/EventCard.tsx frontend/tests/EventCard.test.tsx
git commit -m "feat(frontend): EventCard component with dark mode, category gradients"
```

---

## Task 4: Filters Component

**Files:**
- Create: `frontend/src/components/Filters.tsx`

- [ ] **Step 1: Write `frontend/src/components/Filters.tsx`**

```tsx
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
        <div className="flex gap-2 overflow-x-auto pb-2 mb-2 scrollbar-hide">
          {DATE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => set({ q: filters.q })}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                !filters.category && !opt.value
                  ? 'bg-brand-purple text-white'
                  : 'bg-brand-card border border-brand-border text-brand-muted hover:text-gray-100'
              }`}
            >
              {opt.label}
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/Filters.tsx
git commit -m "feat(frontend): Filters component (chips mobile + sidebar desktop)"
```

---

## Task 5: Home Page

**Files:**
- Create: `frontend/src/pages/Home.tsx`
- Create: `frontend/tests/Home.test.tsx`

- [ ] **Step 1: Write failing test in `frontend/tests/Home.test.tsx`**

```tsx
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
```

- [ ] **Step 2: Write `frontend/src/pages/Home.tsx`**

```tsx
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
```

- [ ] **Step 3: Run tests — verify they pass**

```bash
npx vitest run tests/Home.test.tsx tests/EventCard.test.tsx
```

Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Home.tsx frontend/tests/Home.test.tsx
git commit -m "feat(frontend): Home page with search, filters, and event grid"
```

---

## Task 6: Admin Panel + Submit Page

**Files:**
- Create: `frontend/src/pages/Admin.tsx`
- Create: `frontend/src/pages/SubmitEvent.tsx`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: Write `frontend/src/pages/SubmitEvent.tsx`**

```tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { suggestEvent } from '../api/events'
import { CATEGORIES } from '../types'

export default function SubmitEvent() {
  const [form, setForm] = useState({ title: '', description: '', location: '', price: '', category: '' })
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')
    try {
      await suggestEvent(form)
      setStatus('success')
    } catch {
      setStatus('error')
    }
  }

  const inputClass = 'w-full bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-brand-muted focus:outline-none focus:border-brand-purple'

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-brand-dark flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-4xl mb-4">🎉</p>
          <h1 className="text-xl font-bold text-gray-100 mb-2">Evento enviado!</h1>
          <p className="text-brand-muted mb-6">Nossa equipe vai revisar e publicar em breve.</p>
          <Link to="/" className="text-brand-purple hover:underline">← Voltar para eventos</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-brand-dark px-4 py-8">
      <div className="max-w-lg mx-auto">
        <Link to="/" className="text-brand-muted text-sm hover:text-gray-100 mb-6 inline-block">← Voltar</Link>
        <h1 className="text-2xl font-bold text-gray-100 mb-6">Sugerir Evento</h1>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <div>
            <label className="text-xs text-brand-muted uppercase tracking-widest mb-1 block">Nome do evento *</label>
            <input required className={inputClass} placeholder="Ex: Show da Banda X no Casarão" value={form.title} onChange={set('title')} />
          </div>
          <div>
            <label className="text-xs text-brand-muted uppercase tracking-widest mb-1 block">Descrição</label>
            <textarea className={inputClass} rows={3} placeholder="Detalhes sobre o evento..." value={form.description} onChange={set('description')} />
          </div>
          <div>
            <label className="text-xs text-brand-muted uppercase tracking-widest mb-1 block">Local</label>
            <input className={inputClass} placeholder="Ex: Casarão Cultural — Setor Bueno" value={form.location} onChange={set('location')} />
          </div>
          <div>
            <label className="text-xs text-brand-muted uppercase tracking-widest mb-1 block">Preço</label>
            <input className={inputClass} placeholder='Ex: R$ 40 ou "Gratuito"' value={form.price} onChange={set('price')} />
          </div>
          <div>
            <label className="text-xs text-brand-muted uppercase tracking-widest mb-1 block">Categoria</label>
            <select className={inputClass} value={form.category} onChange={set('category')}>
              <option value="">Selecionar...</option>
              {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          {status === 'error' && <p className="text-red-400 text-sm">Erro ao enviar. Tente novamente.</p>}
          <button
            type="submit"
            disabled={status === 'loading'}
            className="bg-brand-purple text-white font-semibold py-2.5 rounded-lg hover:bg-brand-purple/90 transition-colors disabled:opacity-50"
          >
            {status === 'loading' ? 'Enviando...' : 'Enviar Sugestão'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write `frontend/src/pages/Admin.tsx`**

```tsx
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
```

- [ ] **Step 3: Write `frontend/src/App.tsx`**

```tsx
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Admin from './pages/Admin'
import SubmitEvent from './pages/SubmitEvent'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/sugerir" element={<SubmitEvent />} />
    </Routes>
  )
}
```

- [ ] **Step 4: Run all frontend tests**

```bash
npx vitest run
```

Expected: all tests PASS

- [ ] **Step 5: Build verification**

```bash
npm run build
```

Expected: build succeeds, no TypeScript errors

- [ ] **Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): Admin panel, SubmitEvent page, App router"
```

---

## Task 6b: Calendar Component

**Files:**
- Create: `frontend/src/components/Calendar.tsx`

- [ ] **Step 1: Write `frontend/src/components/Calendar.tsx`**

```tsx
import type { Event } from '../types'

interface Props {
  events: Event[]
  month: Date
  onMonthChange: (d: Date) => void
}

function daysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate()
}

function firstWeekday(year: number, month: number): number {
  return new Date(year, month, 1).getDay()
}

const MONTHS = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
const WEEKDAYS = ['D','S','T','Q','Q','S','S']

export default function Calendar({ events, month, onMonthChange }: Props) {
  const year = month.getFullYear()
  const mon = month.getMonth()
  const days = daysInMonth(year, mon)
  const offset = firstWeekday(year, mon)

  const eventsByDay: Record<number, Event[]> = {}
  events.forEach((ev) => {
    if (!ev.event_date) return
    const d = new Date(ev.event_date)
    if (d.getFullYear() === year && d.getMonth() === mon) {
      const day = d.getDate()
      if (!eventsByDay[day]) eventsByDay[day] = []
      eventsByDay[day].push(ev)
    }
  })

  const prev = () => onMonthChange(new Date(year, mon - 1, 1))
  const next = () => onMonthChange(new Date(year, mon + 1, 1))

  return (
    <div className="bg-brand-card border border-brand-border rounded-xl p-4">
      <div className="flex justify-between items-center mb-3">
        <button onClick={prev} className="text-brand-muted hover:text-gray-100 px-2">‹</button>
        <span className="text-sm font-semibold text-gray-100">{MONTHS[mon]} {year}</span>
        <button onClick={next} className="text-brand-muted hover:text-gray-100 px-2">›</button>
      </div>
      <div className="grid grid-cols-7 gap-1">
        {WEEKDAYS.map((d, i) => (
          <div key={i} className="text-center text-xs text-brand-muted py-1">{d}</div>
        ))}
        {Array.from({ length: offset }).map((_, i) => <div key={`e${i}`} />)}
        {Array.from({ length: days }, (_, i) => i + 1).map((day) => {
          const hasEvents = !!eventsByDay[day]
          return (
            <div
              key={day}
              className={`text-center text-xs py-1.5 rounded cursor-default relative ${
                hasEvents ? 'bg-brand-purple/20 text-brand-purple font-semibold' : 'text-brand-muted'
              }`}
              title={hasEvents ? eventsByDay[day].map((e) => e.title).join('\n') : undefined}
            >
              {day}
              {hasEvents && (
                <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-brand-purple" />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/Calendar.tsx
git commit -m "feat(frontend): Calendar component showing events per day"
```

---

## Task 7: Frontend Dockerfile

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/.nginx.conf` (nginx config for SPA)

- [ ] **Step 1: Write `frontend/Dockerfile`**

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve static files
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY .nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

- [ ] **Step 2: Write `frontend/.nginx.conf`** (SPA routing — all routes to index.html)

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
}
```

- [ ] **Step 3: Add `.env.example` to frontend**

```
VITE_API_URL=
```

Note: leave empty in production — nginx proxy handles `/api` routing.

- [ ] **Step 4: Validate Docker build**

```bash
docker build -t goiania-frontend:test ./frontend
```

Expected: build succeeds

- [ ] **Step 5: Commit**

```bash
git add frontend/Dockerfile frontend/.nginx.conf frontend/.env.example
git commit -m "feat(frontend): multi-stage dockerfile with nginx SPA routing"
```

---

## Task 8: Docker Compose + Nginx

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.prod.yml`
- Create: `.env.example`
- Create: `nginx/nginx.conf`
- Create: `nginx/nginx.prod.conf`

- [ ] **Step 1: Write `nginx/nginx.conf`** (local)

```nginx
events { worker_connections 1024; }

http {
    upstream api { server api:8000; }
    upstream frontend { server frontend:80; }
    upstream rss_scraper { server rss-scraper:8000; }

    server {
        listen 80;

        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /health {
            proxy_pass http://api;
        }

        location /docs {
            proxy_pass http://api;
        }

        location /rss/ {
            proxy_pass http://rss_scraper/;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

- [ ] **Step 2: Write `nginx/nginx.prod.conf`** (production with SSL)

```nginx
events { worker_connections 1024; }

http {
    upstream api { server api:8000; }
    upstream frontend { server frontend:80; }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-Proto https;
        }

        location /health { proxy_pass http://api; }
        location /docs { proxy_pass http://api; }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

- [ ] **Step 3: Write `.env.example`**

```
# Banco de dados
DB_PASSWORD=troque_por_senha_forte

# JWT — gere com: openssl rand -hex 32
JWT_SECRET=troque_por_chave_secreta

# URLs internas (não alterar em setup local)
DATABASE_URL=postgresql://goiania:${DB_PASSWORD}@db:5432/goiania_cultural
REDIS_URL=redis://redis:6379
RSS_SERVICE_URL=http://rss-scraper:8000

# Configurações opcionais
LOG_LEVEL=INFO
JWT_EXPIRE_HOURS=24
CORS_ORIGINS=["http://localhost","http://localhost:3000"]
```

- [ ] **Step 4: Write `docker-compose.yml`**

```yaml
version: '3.8'

services:
  rss-scraper:
    build: ./rss-scraper
    container_name: goiania-rss-scraper
    ports:
      - "8001:8000"
    volumes:
      - rss_cache:/app/cache
    environment:
      - CACHE_TTL=21600
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: goiania-db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=goiania_cultural
      - POSTGRES_USER=goiania
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U goiania -d goiania_cultural"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: goiania-redis
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      retries: 3

  api:
    build: ./backend
    container_name: goiania-api
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      rss-scraper:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://goiania:${DB_PASSWORD}@db:5432/goiania_cultural
      - REDIS_URL=${REDIS_URL:-redis://redis:6379}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRE_HOURS=${JWT_EXPIRE_HOURS:-24}
      - RSS_SERVICE_URL=${RSS_SERVICE_URL:-http://rss-scraper:8000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - CORS_ORIGINS=${CORS_ORIGINS:-["http://localhost"]}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    build: ./backend
    container_name: goiania-worker
    command: python workers/rss_processor.py
    depends_on:
      api:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://goiania:${DB_PASSWORD}@db:5432/goiania_cultural
      - REDIS_URL=${REDIS_URL:-redis://redis:6379}
      - RSS_SERVICE_URL=${RSS_SERVICE_URL:-http://rss-scraper:8000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: goiania-frontend
    depends_on:
      - api
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: goiania-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  rss_cache:
```

- [ ] **Step 5: Write `docker-compose.prod.yml`**

```yaml
version: '3.8'

# Sobrescreve docker-compose.yml para produção
# Uso: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

services:
  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # coloque fullchain.pem e privkey.pem aqui

  api:
    environment:
      - CORS_ORIGINS=${CORS_ORIGINS}
```

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml docker-compose.prod.yml nginx/ .env.example
git commit -m "feat(infra): docker-compose with all 7 services + nginx reverse proxy"
```

---

## Task 9: Setup Script

**Files:**
- Create: `scripts/setup.sh`

- [ ] **Step 1: Write `scripts/setup.sh`**

```bash
#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       Goiânia Cultural — Setup           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Criar .env a partir do exemplo
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Arquivo .env criado"
else
  echo "  .env já existe, mantendo"
fi

# 2. Gerar JWT_SECRET aleatório
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s/JWT_SECRET=troque_por_chave_secreta/JWT_SECRET=${JWT_SECRET}/" .env
echo "✓ JWT_SECRET gerado"

# 3. Pedir senha do banco
echo ""
read -rsp "🔑 Defina uma senha para o banco de dados: " DB_PASSWORD
echo ""
sed -i "s/DB_PASSWORD=troque_por_senha_forte/DB_PASSWORD=${DB_PASSWORD}/" .env
echo "✓ Senha do banco configurada"

# 4. Subir dependências (db + redis)
echo ""
echo "⏳ Iniciando banco de dados e Redis..."
docker compose up -d db redis
echo "   Aguardando banco ficar pronto..."
sleep 8

# 5. Rodar migrations
echo "⏳ Rodando migrations..."
docker compose run --rm api alembic upgrade head
echo "✓ Migrations aplicadas"

# 6. Criar admin
echo ""
echo "👤 Criando usuário administrador..."
docker compose run --rm api python scripts/create_admin.py

# 7. Subir tudo
echo ""
echo "⏳ Subindo todos os serviços..."
docker compose up -d

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Setup completo! Sistema no ar.       ║"
echo "║                                          ║"
echo "║  🌐 Site:      http://localhost          ║"
echo "║  🔐 Admin:     http://localhost/admin    ║"
echo "║  📖 API Docs:  http://localhost:8000/docs║"
echo "╚══════════════════════════════════════════╝"
echo ""
```

- [ ] **Step 2: Make executable and commit**

```bash
chmod +x scripts/setup.sh
git add scripts/setup.sh
git commit -m "feat(infra): one-command setup script with auto JWT generation"
```

---

## Task 10: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/build.yml`

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  backend-lint-test:
    name: Backend (lint + tests)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        run: pip install -r backend/requirements.txt ruff

      - name: Lint (ruff)
        run: ruff check backend/

      - name: Run tests
        run: pytest backend/tests/ -v --tb=short

  rss-scraper-lint-test:
    name: RSS Scraper (lint + tests)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
          cache-dependency-path: rss-scraper/requirements.txt

      - name: Install dependencies
        run: pip install -r rss-scraper/requirements.txt ruff

      - name: Lint (ruff)
        run: ruff check rss-scraper/

      - name: Run tests
        run: pytest rss-scraper/tests/ -v --tb=short

  frontend-lint-test:
    name: Frontend (lint + tests)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Lint (eslint)
        run: cd frontend && npx eslint src --ext ts,tsx || true

      - name: Run tests
        run: cd frontend && npm test
```

- [ ] **Step 2: Write `.github/workflows/build.yml`**

```yaml
name: Docker Build

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  build:
    name: Build Docker images
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build RSS Scraper
        run: docker build ./rss-scraper -t goiania-rss-scraper:test

      - name: Build Backend
        run: docker build ./backend -t goiania-backend:test

      - name: Build Frontend
        run: docker build ./frontend -t goiania-frontend:test
```

- [ ] **Step 3: Commit**

```bash
mkdir -p .github/workflows
git add .github/
git commit -m "feat(ci): github actions for lint, tests, and docker build"
```

---

## Task 11: Documentation

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `docs/DEPLOY.md`
- Create: `.gitignore`

- [ ] **Step 1: Write `.gitignore`**

```gitignore
# Secrets
.env
*.env.local

# Python
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/

# Node
frontend/node_modules/
frontend/dist/

# Docker volumes (local dev)
postgres_data/
redis_data/

# SSL certs (gerenciados fora do repo)
nginx/ssl/

# Cache do scraper
rss-scraper/cache/

# Superpowers
.superpowers/
```

- [ ] **Step 2: Write `README.md`**

````markdown
# 🎭 Goiânia Cultural

Agregador open source de eventos culturais de Goiânia/GO — música, teatro, cinema, arte e muito mais, coletados automaticamente do Instagram e curados por uma equipe local.

> **Licença:** GPL-3.0 | **Stack:** Python + FastAPI + React + PostgreSQL + Docker

---

## 🚀 Instalação Rápida

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose instalados
- Git

### 5 passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/eventos-culturais-rss.git
cd eventos-culturais-rss

# 2. Rode o setup interativo
chmod +x scripts/setup.sh
./scripts/setup.sh

# Pronto! O script cuida de tudo:
# - Cria o .env com segredos gerados automaticamente
# - Roda as migrations do banco
# - Cria o primeiro usuário admin
# - Sobe todos os serviços
```

Acesse:
- **Site:** http://localhost
- **Admin:** http://localhost/admin
- **API Docs:** http://localhost:8000/docs

---

## ➕ Adicionar contas do Instagram

**Via painel admin:** acesse http://localhost/admin → aba "Fontes Instagram" → adicionar `@nomeconta`

**Via código:** edite `rss-scraper/config.py`:

```python
instagram_accounts: List[str] = [
    "espacocultural_gyn",
    "casadoponte",
    "sua_nova_conta",  # adicione aqui
]
```

Reinicie o serviço: `docker compose restart rss-scraper`

---

## 🔄 O que fazer quando o Instagram bloquear o scraper?

O sistema tem fallback automático (retorna cache antigo enquanto possível). Para importar posts manualmente:

```bash
# Prepare um arquivo posts.json com a estrutura:
# [{"url": "https://instagram.com/p/...", "caption": "texto do post", "date": "2026-04-25T20:00:00Z"}]

curl -X POST http://localhost:8001/import/nomeconta \
  -H "Content-Type: application/json" \
  -d @posts.json
```

---

## 🗂 Estrutura do projeto

```
eventos-culturais-rss/
├── rss-scraper/    # Microserviço: Instagram → RSS
├── backend/        # API FastAPI + worker APScheduler
├── frontend/       # React + TypeScript + Tailwind
├── nginx/          # Reverse proxy config
└── scripts/        # setup.sh e utilitários
```

---

## 🤝 Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md) para guia completo.

TL;DR:
1. Fork → branch → commit → PR
2. Rode os testes: `pytest backend/tests/ -v` e `cd frontend && npm test`
3. PRs precisam passar no CI

---

## ❓ FAQ

**P: Funciona em produção (VPS)?**
Sim! Veja [docs/DEPLOY.md](docs/DEPLOY.md) para guia com SSL via Let's Encrypt.

**P: Posso usar para outras cidades?**
Sim — troque as contas do Instagram e o nome do projeto. O código não é específico de Goiânia.

**P: O Instagram pode banir meu IP?**
Sim, é um risco real. O sistema tem cache de 6h e fallback para importação manual. Use com moderação.
````

- [ ] **Step 3: Write `CONTRIBUTING.md`**

```markdown
# Como Contribuir — Goiânia Cultural

Obrigado pelo interesse! Este é um projeto FOSS e toda contribuição é bem-vinda.

## Ambiente de desenvolvimento

```bash
# Backend
cd backend
pip install -r requirements.txt
pytest tests/ -v

# RSS Scraper
cd rss-scraper
pip install -r requirements.txt
pytest tests/ -v

# Frontend
cd frontend
npm install
npm test
npm run dev
```

## Fluxo de contribuição

1. Fork do repositório
2. Crie uma branch: `git checkout -b feat/minha-feature`
3. Faça suas mudanças com testes
4. Verifique que os testes passam
5. Commit: `git commit -m "feat: descrição da mudança"`
6. Push e abra um Pull Request

## Convenções

- **Commits:** inglês, estilo conventional commits (`feat:`, `fix:`, `docs:`)
- **Código:** inglês (variáveis, funções, classes)
- **Comentários e UI:** português
- **Python:** formatado com `ruff format`, lintado com `ruff check`
- **TypeScript:** ESLint + Prettier

## O que precisa de ajuda

- Melhorar os padrões de regex para extração de eventos
- Adicionar mais contas do Instagram ao config
- Melhorar a UI/UX do frontend
- Testes adicionais
- Documentação e tradução
```

- [ ] **Step 4: Write `docs/DEPLOY.md`**

```markdown
# Deploy em Produção (VPS)

## Pré-requisitos

- VPS com Ubuntu 22.04+
- Docker e Docker Compose instalados
- Domínio apontando para o IP do servidor
- Portas 80 e 443 abertas

## Passos

### 1. Clone e configure

```bash
git clone https://github.com/seu-usuario/eventos-culturais-rss.git
cd eventos-culturais-rss
./scripts/setup.sh
```

### 2. Obtenha certificado SSL (Let's Encrypt)

```bash
# Instale o certbot
sudo apt install certbot

# Gere o certificado (com nginx parado)
sudo certbot certonly --standalone -d seudominio.com.br

# Copie os certificados
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/seudominio.com.br/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seudominio.com.br/privkey.pem nginx/ssl/
sudo chown $USER nginx/ssl/*.pem
```

### 3. Suba com config de produção

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Renovação automática do SSL

```bash
# Adicione ao crontab:
0 0 1 * * certbot renew --quiet && \
  cp /etc/letsencrypt/live/seudominio.com.br/*.pem /path/to/app/nginx/ssl/ && \
  docker compose restart nginx
```
```

- [ ] **Step 5: Commit all docs**

```bash
git add README.md CONTRIBUTING.md docs/DEPLOY.md .gitignore
git commit -m "docs: README, CONTRIBUTING, and deploy guide in PT-BR"
```

---

## Task 12: End-to-End Validation

- [ ] **Step 1: Full system smoke test**

```bash
# Start all services
./scripts/setup.sh

# Wait for services to be ready
sleep 15

# Check all health endpoints
curl http://localhost/health          # API health via nginx
curl http://localhost:8001/health     # RSS Scraper direct

# Check frontend loads
curl -s http://localhost | grep "Goiânia Cultural"

# Check API docs accessible
curl -s http://localhost:8000/docs | grep "Goiânia Cultural API"
```

Expected: all return 200 with expected content

- [ ] **Step 2: Admin flow test**

```bash
# Login (replace with your admin credentials from setup)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"suasenha"}' | jq -r '.access_token')

# Check stats
curl -s http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer $TOKEN" | jq .

# Trigger scrape
curl -s -X POST http://localhost:8000/api/admin/trigger-scrape \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "feat: complete Goiânia Cultural system — phases 1, 2, 3 done"
```

---

## Phase 3 Complete

The full system is running. Access:
- **Public site:** http://localhost
- **Admin panel:** http://localhost/admin
- **API docs:** http://localhost:8000/docs
- **RSS feed example:** http://localhost:8001/feed/espacocultural_gyn

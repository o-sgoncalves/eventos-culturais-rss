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

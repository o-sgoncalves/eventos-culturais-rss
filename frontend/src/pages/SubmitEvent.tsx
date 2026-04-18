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

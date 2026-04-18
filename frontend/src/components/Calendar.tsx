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

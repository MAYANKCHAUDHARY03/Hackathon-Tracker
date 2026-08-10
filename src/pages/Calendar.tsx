import { useEffect, useState, useMemo, useCallback } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { calendarApi, type CalendarEvent } from '@/api/calendarApi';
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
} from 'date-fns';
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock,
  AlertTriangle,
  Zap,
  Trophy,
  X,
} from 'lucide-react';

const EVENT_TYPE_META: Record<string, { label: string; icon: typeof Clock }> = {
  hackathon_start: { label: 'Program Start', icon: Zap },
  hackathon_end: { label: 'Program End', icon: Trophy },
  registration_deadline: { label: 'Reg. Deadline', icon: AlertTriangle },
  round_start: { label: 'Round Start', icon: Zap },
  round_end: { label: 'Round End', icon: Clock },
  round_result: { label: 'Results', icon: Trophy },
  deadline: { label: 'Deadline', icon: AlertTriangle },
};

const WEEKDAY_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function Calendar() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);

  // Calculate the full grid range (includes days from prev/next month to fill weeks)
  const gridStart = useMemo(() => startOfWeek(startOfMonth(currentMonth)), [currentMonth]);
  const gridEnd = useMemo(() => endOfWeek(endOfMonth(currentMonth)), [currentMonth]);
  const calendarDays = useMemo(() => eachDayOfInterval({ start: gridStart, end: gridEnd }), [gridStart, gridEnd]);

  const fetchEvents = useCallback(async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const data = await calendarApi.getEvents(
        activeWorkspaceId,
        gridStart.toISOString(),
        gridEnd.toISOString()
      );
      setEvents(data);
    } catch (err) {
      console.error('Failed to fetch calendar events', err);
    } finally {
      setLoading(false);
    }
  }, [activeWorkspaceId, gridStart, gridEnd]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  // Group events by day (YYYY-MM-DD key)
  const eventsByDay = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const evt of events) {
      const key = format(new Date(evt.date), 'yyyy-MM-dd');
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(evt);
    }
    return map;
  }, [events]);

  const selectedDayEvents = useMemo(() => {
    if (!selectedDay) return [];
    const key = format(selectedDay, 'yyyy-MM-dd');
    return eventsByDay.get(key) || [];
  }, [selectedDay, eventsByDay]);

  const goToPrevMonth = () => {
    setCurrentMonth(prev => subMonths(prev, 1));
    setSelectedDay(null);
  };
  const goToNextMonth = () => {
    setCurrentMonth(prev => addMonths(prev, 1));
    setSelectedDay(null);
  };
  const goToToday = () => {
    setCurrentMonth(new Date());
    setSelectedDay(new Date());
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent pb-1">
            Global Calendar
          </h1>
          <p className="text-muted-foreground mt-1 text-lg">
            All hackathon rounds, deadlines &amp; key dates at a glance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevMonth}
            className="p-2 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
            aria-label="Previous month"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={goToToday}
            className="px-4 py-2 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary font-medium text-sm transition-colors"
          >
            Today
          </button>
          <button
            onClick={goToNextMonth}
            className="p-2 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
            aria-label="Next month"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
          <span className="ml-3 text-xl font-semibold min-w-[180px]">
            {format(currentMonth, 'MMMM yyyy')}
          </span>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Calendar Grid */}
        <div className="flex-1 glass-panel rounded-2xl p-4 sm:p-6">
          {/* Weekday headers */}
          <div className="grid grid-cols-7 mb-2">
            {WEEKDAY_HEADERS.map(d => (
              <div key={d} className="text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider py-2">
                {d}
              </div>
            ))}
          </div>

          {/* Day cells */}
          <div className="grid grid-cols-7 gap-px bg-border/30 rounded-xl overflow-hidden">
            {calendarDays.map(day => {
              const key = format(day, 'yyyy-MM-dd');
              const dayEvents = eventsByDay.get(key) || [];
              const inMonth = isSameMonth(day, currentMonth);
              const today = isToday(day);
              const isSelected = selectedDay && isSameDay(day, selectedDay);

              return (
                <button
                  key={key}
                  onClick={() => setSelectedDay(day)}
                  className={`
                    relative min-h-[80px] sm:min-h-[100px] p-1.5 sm:p-2 flex flex-col items-start
                    transition-all duration-150 text-left
                    ${inMonth ? 'bg-card hover:bg-secondary/30' : 'bg-card/40'}
                    ${isSelected ? 'ring-2 ring-primary ring-inset z-10' : ''}
                  `}
                >
                  <span
                    className={`
                      text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full
                      ${today ? 'bg-primary text-primary-foreground font-bold' : ''}
                      ${!inMonth ? 'text-muted-foreground/40' : 'text-foreground'}
                    `}
                  >
                    {format(day, 'd')}
                  </span>

                  {/* Event dots */}
                  <div className="flex flex-wrap gap-1 mt-1">
                    {dayEvents.slice(0, 3).map(evt => (
                      <span
                        key={evt.id}
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ backgroundColor: evt.color }}
                        title={evt.title}
                      />
                    ))}
                    {dayEvents.length > 3 && (
                      <span className="text-[10px] text-muted-foreground font-medium">
                        +{dayEvents.length - 3}
                      </span>
                    )}
                  </div>

                  {/* First event preview (desktop only) */}
                  {dayEvents.length > 0 && (
                    <div className="hidden sm:block mt-1 w-full">
                      <div
                        className="text-[11px] leading-tight truncate rounded px-1 py-0.5 font-medium"
                        style={{
                          backgroundColor: dayEvents[0].color + '20',
                          color: dayEvents[0].color,
                        }}
                      >
                        {dayEvents[0].title}
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {loading && (
            <div className="flex items-center justify-center py-4 text-muted-foreground text-sm gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              Loading events...
            </div>
          )}
        </div>

        {/* Day Detail Panel */}
        <div className="w-full lg:w-80 xl:w-96 shrink-0">
          <div className="glass-panel rounded-2xl p-6 sticky top-6">
            {selectedDay ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold">
                      {format(selectedDay, 'EEEE')}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                      {format(selectedDay, 'MMMM d, yyyy')}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedDay(null)}
                    className="p-1.5 rounded-lg hover:bg-secondary/50 transition-colors"
                    aria-label="Close panel"
                  >
                    <X className="h-4 w-4 text-muted-foreground" />
                  </button>
                </div>

                {selectedDayEvents.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                    <CalendarDays className="h-10 w-10 mb-3 opacity-40" />
                    <p className="text-sm">No events on this day</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedDayEvents.map(evt => {
                      const meta = EVENT_TYPE_META[evt.event_type] || {
                        label: evt.event_type,
                        icon: Clock,
                      };
                      const Icon = meta.icon;
                      return (
                        <div
                          key={evt.id}
                          className="p-3 rounded-xl border border-border/50 hover:border-border transition-colors bg-card/50"
                        >
                          <div className="flex items-start gap-3">
                            <div
                              className="p-2 rounded-lg shrink-0 mt-0.5"
                              style={{ backgroundColor: evt.color + '18' }}
                            >
                              <Icon
                                className="h-4 w-4"
                                style={{ color: evt.color }}
                              />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-semibold text-sm truncate">
                                {evt.title}
                              </p>
                              <p className="text-xs text-muted-foreground mt-0.5">
                                {evt.hackathon_name}
                              </p>
                              <div className="flex items-center gap-2 mt-1.5">
                                <span
                                  className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded"
                                  style={{
                                    backgroundColor: evt.color + '20',
                                    color: evt.color,
                                  }}
                                >
                                  {meta.label}
                                </span>
                                <span className="text-[11px] text-muted-foreground">
                                  {format(new Date(evt.date), 'h:mm a')}
                                </span>
                              </div>
                              {evt.description && (
                                <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                                  {evt.description}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <CalendarDays className="h-12 w-12 mb-4 opacity-30" />
                <p className="font-medium">Select a day</p>
                <p className="text-sm mt-1">Click any date to see its events</p>
              </div>
            )}
          </div>

          {/* Legend */}
          <div className="glass-panel rounded-2xl p-4 mt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Event Types
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { color: '#3b82f6', label: 'Program Start' },
                { color: '#60a5fa', label: 'Program End' },
                { color: '#f43f5e', label: 'Reg. Deadline' },
                { color: '#f59e0b', label: 'Round Start' },
                { color: '#fbbf24', label: 'Round End' },
                { color: '#22c55e', label: 'Results' },
                { color: '#a855f7', label: 'Hard Deadline' },
                { color: '#6b7280', label: 'Soft Deadline' },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-muted-foreground">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

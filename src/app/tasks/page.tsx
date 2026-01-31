'use client';

import { useState, useEffect } from 'react';

interface Task {
  id: string;
  content: string;
  due?: {
    date: string;
    datetime?: string;
  };
  priority: number;
  is_completed: boolean;
}

function getDaysArray(startDate: Date, numDays: number): Date[] {
  const days: Date[] = [];
  for (let i = 0; i < numDays; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    days.push(date);
  }
  return days;
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

function formatDayHeader(date: Date): { day: string; weekday: string; isToday: boolean } {
  const today = new Date();
  const isToday = formatDate(date) === formatDate(today);
  return {
    day: date.getDate().toString(),
    weekday: date.toLocaleDateString('en-US', { weekday: 'short' }),
    isToday,
  };
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(() => {
    const today = new Date();
    today.setDate(today.getDate() - 1); // Start from yesterday
    return today;
  });

  const days = getDaysArray(startDate, 7);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await fetch('/api/todoist/tasks');
      if (!res.ok) throw new Error('Failed to fetch tasks');
      const data = await res.json();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getTasksForDate = (date: Date): Task[] => {
    const dateStr = formatDate(date);
    return tasks.filter(task => {
      if (!task.due) return false;
      return task.due.date === dateStr;
    });
  };

  const getOverdueTasks = (): Task[] => {
    const today = formatDate(new Date());
    return tasks.filter(task => {
      if (!task.due || task.is_completed) return false;
      return task.due.date < today;
    });
  };

  const getNoDateTasks = (): Task[] => {
    return tasks.filter(task => !task.due && !task.is_completed);
  };

  const navigateDays = (direction: number) => {
    const newStart = new Date(startDate);
    newStart.setDate(startDate.getDate() + direction * 7);
    setStartDate(newStart);
  };

  const goToToday = () => {
    const today = new Date();
    today.setDate(today.getDate() - 1);
    setStartDate(today);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
        <h1 className="text-xl font-bold text-neutral-900 dark:text-white flex items-center gap-2">
          <span>✅</span> Tasks
        </h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigateDays(-1)}
            className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
          >
            ←
          </button>
          <button
            onClick={goToToday}
            className="px-3 py-1.5 text-sm rounded-lg bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
          >
            Today
          </button>
          <button
            onClick={() => navigateDays(1)}
            className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
          >
            →
          </button>
        </div>
      </div>

      {/* TeuxDeux Style Calendar */}
      <div className="flex-1 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-neutral-500">Loading tasks...</div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="text-neutral-500">{error}</div>
            <p className="text-sm text-neutral-400 max-w-md text-center">
              Configure the Todoist API to see your tasks here.
              Add TODOIST_API_KEY to your environment variables.
            </p>
          </div>
        ) : (
          <div className="flex h-full">
            {/* Overdue + No Date Column */}
            <div className="w-48 flex-shrink-0 border-r border-neutral-200 dark:border-neutral-800 flex flex-col">
              {/* Overdue */}
              <div className="flex-1 border-b border-neutral-200 dark:border-neutral-800 overflow-y-auto">
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border-b border-red-100 dark:border-red-900/30">
                  <h3 className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase">
                    Overdue
                  </h3>
                </div>
                <div className="p-2 space-y-1">
                  {getOverdueTasks().map(task => (
                    <div
                      key={task.id}
                      className="p-2 text-sm bg-red-50 dark:bg-red-900/10 rounded border border-red-100 dark:border-red-900/20 text-neutral-700 dark:text-neutral-300"
                    >
                      {task.content}
                    </div>
                  ))}
                </div>
              </div>
              {/* No Date */}
              <div className="flex-1 overflow-y-auto">
                <div className="p-3 bg-neutral-50 dark:bg-neutral-800/50 border-b border-neutral-200 dark:border-neutral-700">
                  <h3 className="text-xs font-semibold text-neutral-500 uppercase">
                    Someday
                  </h3>
                </div>
                <div className="p-2 space-y-1">
                  {getNoDateTasks().map(task => (
                    <div
                      key={task.id}
                      className="p-2 text-sm bg-neutral-50 dark:bg-neutral-800/50 rounded border border-neutral-200 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300"
                    >
                      {task.content}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Days Grid */}
            <div className="flex-1 flex overflow-x-auto">
              {days.map(date => {
                const { day, weekday, isToday } = formatDayHeader(date);
                const dayTasks = getTasksForDate(date);
                
                return (
                  <div
                    key={formatDate(date)}
                    className={`
                      flex-1 min-w-[140px] border-r border-neutral-200 dark:border-neutral-800 last:border-r-0
                      flex flex-col
                      ${isToday ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}
                    `}
                  >
                    {/* Day Header */}
                    <div className={`
                      p-3 border-b border-neutral-200 dark:border-neutral-800 text-center
                      ${isToday ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-neutral-50 dark:bg-neutral-800/50'}
                    `}>
                      <div className={`
                        text-xs font-medium uppercase
                        ${isToday ? 'text-blue-600 dark:text-blue-400' : 'text-neutral-500'}
                      `}>
                        {weekday}
                      </div>
                      <div className={`
                        text-2xl font-bold
                        ${isToday ? 'text-blue-600 dark:text-blue-400' : 'text-neutral-700 dark:text-neutral-300'}
                      `}>
                        {day}
                      </div>
                    </div>
                    
                    {/* Tasks */}
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                      {dayTasks.map(task => (
                        <div
                          key={task.id}
                          className={`
                            p-2 text-sm rounded border transition-colors
                            ${task.priority === 4 
                              ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' 
                              : task.priority === 3
                              ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
                              : 'bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700'
                            }
                            text-neutral-700 dark:text-neutral-300
                          `}
                        >
                          {task.content}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

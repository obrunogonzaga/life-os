'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Capture {
  id: string;
  content: string;
  createdAt: string;
  processed: boolean;
}

export default function CapturesPage() {
  const [captures, setCaptures] = useState<Capture[]>([]);
  const [newCapture, setNewCapture] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Load captures from localStorage for now
    const saved = localStorage.getItem('life-os-captures');
    if (saved) {
      setCaptures(JSON.parse(saved));
    }
  }, []);

  const saveCaptures = (newCaptures: Capture[]) => {
    setCaptures(newCaptures);
    localStorage.setItem('life-os-captures', JSON.stringify(newCaptures));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCapture.trim()) return;

    setIsSubmitting(true);
    
    const capture: Capture = {
      id: Date.now().toString(),
      content: newCapture.trim(),
      createdAt: new Date().toISOString(),
      processed: false,
    };

    saveCaptures([capture, ...captures]);
    setNewCapture('');
    setIsSubmitting(false);
  };

  const handleDelete = (id: string) => {
    saveCaptures(captures.filter(c => c.id !== id));
  };

  const handleToggleProcessed = (id: string) => {
    saveCaptures(
      captures.map(c => 
        c.id === id ? { ...c, processed: !c.processed } : c
      )
    );
  };

  const unprocessed = captures.filter(c => !c.processed);
  const processed = captures.filter(c => c.processed);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('pt-BR');
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-2 flex items-center gap-2">
          <span>📥</span> Captures
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400">
          Quick thoughts, ideas, and notes to process later
        </p>
      </header>

      {/* Quick Capture Form */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-4">
          <textarea
            value={newCapture}
            onChange={(e) => setNewCapture(e.target.value)}
            placeholder="Capture a thought, idea, or quick note..."
            rows={3}
            className="w-full bg-transparent text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none resize-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleSubmit(e);
              }
            }}
          />
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-800">
            <span className="text-xs text-neutral-500">
              ⌘/Ctrl + Enter to save
            </span>
            <button
              type="submit"
              disabled={isSubmitting || !newCapture.trim()}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-neutral-300 dark:disabled:bg-neutral-700 text-white disabled:text-neutral-500 text-sm font-medium rounded-lg transition-colors"
            >
              Capture
            </button>
          </div>
        </div>
      </form>

      {/* Inbox */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
          <span>📬</span> Inbox
          {unprocessed.length > 0 && (
            <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
              {unprocessed.length}
            </span>
          )}
        </h2>
        
        {unprocessed.length === 0 ? (
          <div className="bg-neutral-50 dark:bg-neutral-900/50 rounded-xl border border-dashed border-neutral-200 dark:border-neutral-800 p-8 text-center">
            <p className="text-neutral-500 dark:text-neutral-400">
              No captures yet. Start typing above!
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {unprocessed.map((capture) => (
              <div
                key={capture.id}
                className="bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4 group"
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleProcessed(capture.id)}
                    className="mt-1 w-5 h-5 rounded border-2 border-neutral-300 dark:border-neutral-600 hover:border-blue-500 dark:hover:border-blue-400 transition-colors flex-shrink-0"
                    title="Mark as processed"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-neutral-800 dark:text-neutral-200 whitespace-pre-wrap">
                      {capture.content}
                    </p>
                    <p className="text-xs text-neutral-400 mt-2">
                      {formatDate(capture.createdAt)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(capture.id)}
                    className="text-neutral-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18" />
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Processed */}
      {processed.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
            <span>✅</span> Processed
            <span className="px-2 py-0.5 text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-500 rounded-full">
              {processed.length}
            </span>
          </h2>
          <div className="space-y-2">
            {processed.map((capture) => (
              <div
                key={capture.id}
                className="bg-neutral-50 dark:bg-neutral-900/50 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4 group opacity-60"
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleProcessed(capture.id)}
                    className="mt-1 w-5 h-5 rounded border-2 border-green-500 bg-green-500 flex items-center justify-center flex-shrink-0"
                    title="Mark as unprocessed"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-neutral-600 dark:text-neutral-400 whitespace-pre-wrap line-through">
                      {capture.content}
                    </p>
                    <p className="text-xs text-neutral-400 mt-2">
                      {formatDate(capture.createdAt)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(capture.id)}
                    className="text-neutral-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18" />
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Info */}
      <div className="mt-8 p-4 bg-neutral-50 dark:bg-neutral-900/50 rounded-xl border border-dashed border-neutral-200 dark:border-neutral-700 text-center">
        <p className="text-sm text-neutral-500 dark:text-neutral-400">
          💡 Tip: Process captures by turning them into documents in Memory,
          or tasks in your Todoist.
        </p>
      </div>
    </div>
  );
}

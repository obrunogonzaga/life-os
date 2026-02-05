'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { DocumentMeta, DocumentType } from '@/lib/types';
import { ThemeToggle } from './ThemeToggle';

interface SidebarProps {
  documents: DocumentMeta[];
}

const typeIcons: Record<DocumentType, string> = {
  concept: '💡',
  decision: '⚖️',
  journal: '📓',
  note: '📝',
  reference: '📚',
};

const typeLabels: Record<DocumentType, string> = {
  concept: 'Concepts',
  decision: 'Decisions',
  journal: 'Journals',
  note: 'Notes',
  reference: 'References',
};

export function Sidebar({ documents }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved === 'true') setCollapsed(true);
    setMounted(true);
  }, []);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem('sidebar-collapsed', String(next));
  };
  
  // Group documents by type
  const grouped = documents.reduce((acc, doc) => {
    const type = doc.type || 'note';
    if (!acc[type]) acc[type] = [];
    acc[type].push(doc);
    return acc;
  }, {} as Record<DocumentType, DocumentMeta[]>);

  const typeOrder: DocumentType[] = ['journal', 'concept', 'decision', 'note', 'reference'];

  return (
    <aside
      className={`
        h-screen bg-neutral-100 dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800
        flex flex-col transition-all duration-300 ease-in-out flex-shrink-0
        ${mounted ? (collapsed ? 'w-16' : 'w-64') : 'w-64'}
      `}
    >
      {/* Header */}
      <div className="p-3 border-b border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center justify-between mb-2">
          <Link href="/" className="flex items-center gap-2 text-neutral-900 dark:text-white font-semibold min-w-0">
            <span className="text-xl flex-shrink-0">🧠</span>
            {!collapsed && <span className="truncate">life-os</span>}
          </Link>
          {!collapsed && <ThemeToggle />}
        </div>

        {/* Toggle button */}
        <button
          onClick={toggle}
          className="w-full flex items-center justify-center gap-2 px-2 py-1.5 rounded text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/50 dark:hover:bg-neutral-800/50 transition-colors"
          title={collapsed ? 'Expandir sidebar' : 'Minimizar sidebar'}
        >
          <span className="flex-shrink-0">{collapsed ? '▶' : '◀'}</span>
          {!collapsed && <span>Minimizar</span>}
        </button>

        {/* Canvas link */}
        <Link
          href="/canvas"
          className={`
            flex items-center gap-2 px-2 py-1.5 rounded text-sm font-medium transition-colors mt-1
            ${collapsed ? 'justify-center' : ''}
            ${pathname === '/canvas'
              ? 'bg-yellow-500/15 text-yellow-700 dark:text-yellow-400'
              : 'text-neutral-600 dark:text-neutral-400 hover:text-yellow-700 dark:hover:text-yellow-400 hover:bg-yellow-500/10'
            }
          `}
          title="Canvas"
        >
          <span className="flex-shrink-0">📊</span>
          {!collapsed && <span>Canvas</span>}
        </Link>

        {/* Faturas link */}
        <Link
          href="/faturas"
          className={`
            flex items-center gap-2 px-2 py-1.5 rounded text-sm font-medium transition-colors mt-1
            ${collapsed ? 'justify-center' : ''}
            ${pathname?.startsWith('/faturas')
              ? 'bg-pink-500/15 text-pink-700 dark:text-pink-400'
              : 'text-neutral-600 dark:text-neutral-400 hover:text-pink-700 dark:hover:text-pink-400 hover:bg-pink-500/10'
            }
          `}
          title="Faturas"
        >
          <span className="flex-shrink-0">💳</span>
          {!collapsed && <span>Faturas</span>}
        </Link>
      </div>

      {/* Document List */}
      <nav className={`flex-1 overflow-y-auto overflow-x-hidden p-2 ${collapsed ? 'hidden' : ''}`}>
        {typeOrder.map((type) => {
          const docs = grouped[type];
          if (!docs || docs.length === 0) return null;

          return (
            <div key={type} className="mb-4">
              <h3 className="px-2 py-1 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                {typeIcons[type]} {typeLabels[type]}
              </h3>
              <ul className="mt-1 space-y-0.5">
                {docs.map((doc) => {
                  const href = `/doc/${doc.slug}`;
                  const isActive = pathname === href;

                  return (
                    <li key={doc.slug}>
                      <Link
                        href={href}
                        className={`
                          block px-2 py-1.5 rounded text-sm transition-colors truncate
                          ${isActive
                            ? 'bg-neutral-200 dark:bg-neutral-800 text-neutral-900 dark:text-white'
                            : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/50 dark:hover:bg-neutral-800/50'
                          }
                        `}
                      >
                        {doc.title}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </nav>

      {/* Collapsed: show type icons only */}
      {collapsed && (
        <nav className="flex-1 overflow-y-auto p-2 flex flex-col items-center gap-2 pt-4">
          {typeOrder.map((type) => {
            const docs = grouped[type];
            if (!docs || docs.length === 0) return null;
            return (
              <span key={type} className="text-lg cursor-default" title={`${typeLabels[type]} (${docs.length})`}>
                {typeIcons[type]}
              </span>
            );
          })}
        </nav>
      )}

      {/* Footer */}
      <div className="p-3 border-t border-neutral-200 dark:border-neutral-800 text-xs text-neutral-500 text-center">
        {collapsed ? documents.length : `${documents.length} documents`}
      </div>
    </aside>
  );
}

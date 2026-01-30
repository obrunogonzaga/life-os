'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
  
  // Group documents by type
  const grouped = documents.reduce((acc, doc) => {
    const type = doc.type || 'note';
    if (!acc[type]) acc[type] = [];
    acc[type].push(doc);
    return acc;
  }, {} as Record<DocumentType, DocumentMeta[]>);

  const typeOrder: DocumentType[] = ['journal', 'concept', 'decision', 'note', 'reference'];

  return (
    <aside className="w-64 h-screen bg-neutral-100 dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 flex flex-col transition-colors">
      {/* Header */}
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-neutral-900 dark:text-white font-semibold">
          <span className="text-xl">🧠</span>
          <span>life-os</span>
        </Link>
        <ThemeToggle />
      </div>

      {/* Document List */}
      <nav className="flex-1 overflow-y-auto p-2">
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
                          block px-2 py-1.5 rounded text-sm transition-colors
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

      {/* Footer */}
      <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 text-xs text-neutral-500">
        {documents.length} documents
      </div>
    </aside>
  );
}

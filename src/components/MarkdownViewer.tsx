'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Document } from '@/lib/types';

interface MarkdownViewerProps {
  document: Document;
}

const typeColors: Record<string, string> = {
  concept: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  decision: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  journal: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  note: 'bg-green-500/10 text-green-400 border-green-500/30',
  reference: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
};

export function MarkdownViewer({ document }: MarkdownViewerProps) {
  const typeColor = typeColors[document.type] || typeColors.note;

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const weekday = date.toLocaleDateString('en-US', { weekday: 'long' });
    const formatted = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    return `${formatted} — ${weekday}`;
  };

  return (
    <article className="max-w-3xl mx-auto py-10 px-8">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <span className={`px-2.5 py-1 text-xs font-medium rounded-md border ${typeColor}`}>
            {document.type}
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white tracking-tight">{document.title}</h1>
        {document.date && (
          <time className="block mt-2 text-base text-neutral-400">
            {formatDate(document.date)}
          </time>
        )}
        {document.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {document.tags.map((tag) => (
              <span
                key={tag}
                className="px-2.5 py-1 text-xs bg-neutral-800/50 text-neutral-400 rounded-md"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* Content */}
      <div className="document-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            // H1 - Main title (usually skipped, shown in header)
            h1: ({ children }) => (
              <h1 className="text-2xl font-bold text-white mt-0 mb-8 tracking-tight">
                {children}
              </h1>
            ),
            // H2 - Major sections (time entries)
            h2: ({ children }) => (
              <h2 className="text-xl font-semibold text-white mt-12 mb-4 tracking-tight">
                {children}
              </h2>
            ),
            // H3 - Subsections (Key highlights, etc)
            h3: ({ children }) => (
              <h3 className="text-base font-semibold text-neutral-200 mt-8 mb-3 uppercase tracking-wide">
                {children}
              </h3>
            ),
            // H4 - Minor subsections
            h4: ({ children }) => (
              <h4 className="text-sm font-semibold text-neutral-300 mt-6 mb-2">
                {children}
              </h4>
            ),
            // Paragraphs
            p: ({ children }) => (
              <p className="text-neutral-300 leading-7 mb-5">{children}</p>
            ),
            // Strong/Bold
            strong: ({ children }) => (
              <strong className="text-neutral-100 font-semibold">{children}</strong>
            ),
            // Horizontal rules - visual separator
            hr: () => (
              <hr className="border-0 border-t border-neutral-800 my-10" />
            ),
            // Unordered lists
            ul: ({ children }) => (
              <ul className="my-4 space-y-2 list-disc list-outside ml-5">
                {children}
              </ul>
            ),
            // Ordered lists
            ol: ({ children }) => (
              <ol className="my-4 space-y-2 list-decimal list-outside ml-5">
                {children}
              </ol>
            ),
            // List items
            li: ({ children }) => (
              <li className="text-neutral-300 leading-7 pl-1">{children}</li>
            ),
            // Blockquotes
            blockquote: ({ children }) => (
              <blockquote className="border-l-2 border-blue-500 pl-6 my-6 text-neutral-400 italic">
                {children}
              </blockquote>
            ),
            // Code blocks
            pre: ({ children }) => (
              <pre className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 my-6 overflow-x-auto">
                {children}
              </pre>
            ),
            // Inline code
            code: ({ className, children }) => {
              const isBlock = className?.includes('language-');
              if (isBlock) {
                return <code className={className}>{children}</code>;
              }
              return (
                <code className="text-pink-400 bg-neutral-800/70 px-1.5 py-0.5 rounded text-sm">
                  {children}
                </code>
              );
            },
            // Links
            a: ({ href, children }) => (
              <a
                href={href}
                className="text-blue-400 hover:underline"
                target={href?.startsWith('http') ? '_blank' : undefined}
                rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
              >
                {children}
              </a>
            ),
          }}
        >
          {document.content}
        </ReactMarkdown>
      </div>
    </article>
  );
}

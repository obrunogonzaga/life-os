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

  // Format date nicely
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
    <article className="max-w-3xl mx-auto py-8 px-6">
      {/* Header */}
      <header className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <span className={`px-2.5 py-1 text-xs font-medium rounded-md border ${typeColor}`}>
            {document.type}
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">{document.title}</h1>
        {document.date && (
          <time className="text-base text-neutral-400">
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

      {/* Divider */}
      <hr className="border-neutral-800 mb-10" />

      {/* Content */}
      <div className="
        prose prose-invert prose-neutral max-w-none
        
        /* Headings - more spacing */
        prose-headings:font-semibold prose-headings:tracking-tight
        prose-h1:text-2xl prose-h1:mt-12 prose-h1:mb-6
        prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-neutral-100
        prose-h3:text-lg prose-h3:mt-8 prose-h3:mb-3 prose-h3:text-neutral-200
        prose-h4:text-base prose-h4:mt-6 prose-h4:mb-2 prose-h4:text-neutral-300
        
        /* Paragraphs - better line height and spacing */
        prose-p:text-neutral-300 prose-p:leading-7 prose-p:mb-6
        
        /* Links */
        prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
        
        /* Strong/Bold - stand out more */
        prose-strong:text-white prose-strong:font-semibold
        
        /* Code */
        prose-code:text-pink-400 prose-code:bg-neutral-800/70 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-normal
        prose-code:before:content-none prose-code:after:content-none
        prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-800 prose-pre:rounded-lg
        
        /* Blockquotes */
        prose-blockquote:border-l-2 prose-blockquote:border-blue-500 prose-blockquote:text-neutral-400 prose-blockquote:pl-6 prose-blockquote:italic prose-blockquote:my-8
        
        /* Lists - better spacing */
        prose-ul:my-6 prose-ul:space-y-2
        prose-ol:my-6 prose-ol:space-y-2
        prose-li:text-neutral-300 prose-li:leading-7
        prose-li:marker:text-neutral-500
        
        /* Horizontal rules */
        prose-hr:border-neutral-800 prose-hr:my-10
        
        /* Tables */
        prose-table:my-8
        prose-th:text-neutral-200 prose-th:font-semibold prose-th:border-neutral-700 prose-th:px-4 prose-th:py-3
        prose-td:text-neutral-300 prose-td:border-neutral-800 prose-td:px-4 prose-td:py-3
      ">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            // Custom rendering for horizontal rules (entry separators)
            hr: () => (
              <div className="my-12 flex items-center gap-4">
                <div className="flex-1 border-t border-neutral-800"></div>
                <span className="text-neutral-600 text-sm">•••</span>
                <div className="flex-1 border-t border-neutral-800"></div>
              </div>
            ),
            // Better paragraph handling
            p: ({ children }) => (
              <p className="text-neutral-300 leading-7 mb-5">{children}</p>
            ),
            // Style strong text as labels
            strong: ({ children }) => (
              <strong className="text-neutral-100 font-semibold">{children}</strong>
            ),
          }}
        >
          {document.content}
        </ReactMarkdown>
      </div>
    </article>
  );
}

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

  return (
    <article className="max-w-3xl mx-auto">
      {/* Header */}
      <header className="mb-8 pb-6 border-b border-neutral-800">
        <div className="flex items-center gap-3 mb-3">
          <span className={`px-2 py-0.5 text-xs font-medium rounded border ${typeColor}`}>
            {document.type}
          </span>
          {document.date && (
            <time className="text-sm text-neutral-500">
              {new Date(document.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </time>
          )}
        </div>
        <h1 className="text-3xl font-bold text-white">{document.title}</h1>
        {document.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {document.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 text-xs bg-neutral-800 text-neutral-400 rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* Content */}
      <div className="prose prose-invert prose-neutral max-w-none
        prose-headings:font-semibold
        prose-h1:text-2xl prose-h1:mt-8 prose-h1:mb-4
        prose-h2:text-xl prose-h2:mt-6 prose-h2:mb-3
        prose-h3:text-lg prose-h3:mt-4 prose-h3:mb-2
        prose-p:text-neutral-300 prose-p:leading-relaxed
        prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
        prose-strong:text-white
        prose-code:text-pink-400 prose-code:bg-neutral-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
        prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-800
        prose-blockquote:border-l-blue-500 prose-blockquote:text-neutral-400
        prose-li:text-neutral-300
        prose-hr:border-neutral-800
      ">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
        >
          {document.content}
        </ReactMarkdown>
      </div>
    </article>
  );
}

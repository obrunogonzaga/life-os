'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Document } from '@/lib/types';

interface MarkdownViewerProps {
  document: Document;
  basePath?: string;
}

const typeColors: Record<string, string> = {
  concept: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30',
  decision: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30',
  journal: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30',
  note: 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/30',
  reference: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/30',
};

export function MarkdownViewer({ document, basePath = '' }: MarkdownViewerProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const typeColor = typeColors[document.type] || typeColors.note;

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      const response = await fetch('/api/documents', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: document.slug }),
      });

      if (response.ok) {
        router.push(basePath || '/memory');
        router.refresh();
      } else {
        const data = await response.json();
        alert(`Erro ao deletar: ${data.error}`);
      }
    } catch (error) {
      alert('Erro ao deletar documento');
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <article className="max-w-3xl mx-auto">
      {/* Header */}
      <header className="mb-8 pb-6 border-b border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
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
          
          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            {/* Edit Button */}
            <Link
              href={`${basePath}/edit/${document.slug}`}
              className="p-2 text-neutral-500 hover:text-blue-500 hover:bg-blue-500/10 rounded transition-colors"
              title="Editar documento"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                <path d="m15 5 4 4" />
              </svg>
            </Link>
            
            {/* Delete Button */}
            {!showConfirm ? (
              <button
                onClick={() => setShowConfirm(true)}
                className="p-2 text-neutral-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                title="Deletar documento"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 6h18" />
                  <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                  <line x1="10" y1="11" x2="10" y2="17" />
                  <line x1="14" y1="11" x2="14" y2="17" />
                </svg>
              </button>
            ) : (
            <div className="flex items-center gap-2">
              <span className="text-sm text-neutral-400">Deletar?</span>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-3 py-1 text-sm bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded transition-colors disabled:opacity-50"
              >
                {isDeleting ? '...' : 'Sim'}
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                className="px-3 py-1 text-sm bg-neutral-200 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-300 dark:hover:bg-neutral-700 rounded transition-colors"
              >
                Não
              </button>
            </div>
          )}
          </div>
        </div>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">{document.title}</h1>
        {document.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {document.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 text-xs bg-neutral-200 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* Content */}
      <div className="prose prose-neutral dark:prose-invert max-w-none
        prose-headings:font-semibold
        prose-h1:text-2xl prose-h1:mt-8 prose-h1:mb-4
        prose-h2:text-xl prose-h2:mt-6 prose-h2:mb-3
        prose-h3:text-lg prose-h3:mt-4 prose-h3:mb-2
        prose-p:text-neutral-700 dark:prose-p:text-neutral-300 prose-p:leading-relaxed
        prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
        prose-strong:text-neutral-900 dark:prose-strong:text-white
        prose-code:text-pink-600 dark:prose-code:text-pink-400 prose-code:bg-neutral-100 dark:prose-code:bg-neutral-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
        prose-pre:bg-neutral-100 dark:prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-200 dark:prose-pre:border-neutral-800
        prose-blockquote:border-l-blue-500 prose-blockquote:text-neutral-500 dark:prose-blockquote:text-neutral-400
        prose-li:text-neutral-700 dark:prose-li:text-neutral-300
        prose-hr:border-neutral-200 dark:prose-hr:border-neutral-800
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

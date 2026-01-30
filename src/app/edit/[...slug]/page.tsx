'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';

const documentTypes = [
  { value: 'journal', label: '📓 Journal' },
  { value: 'concept', label: '💡 Concept' },
  { value: 'decision', label: '⚖️ Decision' },
  { value: 'note', label: '📝 Note' },
  { value: 'reference', label: '📚 Reference' },
];

export default function EditDocumentPage() {
  const router = useRouter();
  const params = useParams();
  const slug = Array.isArray(params.slug) ? params.slug.join('/') : params.slug;
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const [form, setForm] = useState({
    title: '',
    type: 'note',
    tags: '',
    content: '',
    date: '',
  });

  useEffect(() => {
    async function loadDocument() {
      try {
        const response = await fetch(`/api/documents/${slug}`);
        if (!response.ok) throw new Error('Document not found');
        
        const data = await response.json();
        setForm({
          title: data.title || '',
          type: data.type || 'note',
          tags: (data.tags || []).join(', '),
          content: data.content || '',
          date: data.date || '',
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document');
      } finally {
        setIsLoading(false);
      }
    }
    
    if (slug) loadDocument();
  }, [slug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch(`/api/documents/${slug}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update document');
      }

      router.push(`/doc/${slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-10 px-8">
        <div className="text-neutral-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-10 px-8">
      <header className="mb-8">
        <Link 
          href={`/doc/${slug}`}
          className="text-sm text-neutral-500 hover:text-neutral-300 mb-4 inline-block"
        >
          ← Back to document
        </Link>
        <h1 className="text-3xl font-bold text-white">Edit Document</h1>
        <p className="text-neutral-400 mt-2">{slug}.md</p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-neutral-300 mb-2">
            Title
          </label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-lg text-white focus:outline-none focus:border-neutral-700"
            required
          />
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-neutral-300 mb-2">
            Type
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {documentTypes.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setForm({ ...form, type: type.value })}
                className={`px-4 py-3 rounded-lg border text-left transition-colors ${
                  form.type === type.value
                    ? 'bg-neutral-800 border-neutral-600 text-white'
                    : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:border-neutral-700'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-neutral-300 mb-2">
            Tags
          </label>
          <input
            type="text"
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
            placeholder="tag1, tag2, tag3"
            className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:border-neutral-700"
          />
        </div>

        {/* Content */}
        <div>
          <label className="block text-sm font-medium text-neutral-300 mb-2">
            Content
          </label>
          <textarea
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            rows={20}
            className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-lg text-white focus:outline-none focus:border-neutral-700 font-mono text-sm"
            required
          />
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white font-medium rounded-lg transition-colors"
          >
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </button>
          <Link
            href={`/doc/${slug}`}
            className="px-6 py-3 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 font-medium rounded-lg transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

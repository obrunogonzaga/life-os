'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const documentTypes = [
  { value: 'journal', label: '📓 Journal', folder: 'journals' },
  { value: 'concept', label: '💡 Concept', folder: 'concepts' },
  { value: 'decision', label: '⚖️ Decision', folder: 'decisions' },
  { value: 'note', label: '📝 Note', folder: 'notes' },
  { value: 'reference', label: '📚 Reference', folder: 'references' },
];

export default function NewDocumentPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const [form, setForm] = useState({
    title: '',
    type: 'note',
    tags: '',
    content: '',
  });

  const today = new Date().toISOString().split('T')[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
          date: today,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create document');
      }

      router.push(`/memory/doc/${data.slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  };

  const selectedType = documentTypes.find(t => t.value === form.type);
  const previewSlug = `${selectedType?.folder}/${generateSlug(form.title) || 'untitled'}`;

  return (
    <div className="max-w-3xl mx-auto py-10 px-8">
      <header className="mb-8">
        <Link 
          href="/memory" 
          className="text-sm text-neutral-500 hover:text-neutral-300 mb-4 inline-block"
        >
          ← Back to Memory
        </Link>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">New Document</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-2">Create a new document in your brain</p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Title
          </label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Document title..."
            className="w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none focus:border-neutral-400 dark:focus:border-neutral-700"
            required
          />
          <p className="mt-1 text-xs text-neutral-500">
            Will be saved as: <code className="text-neutral-600 dark:text-neutral-400">{previewSlug}.md</code>
          </p>
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
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
                    ? 'bg-neutral-100 dark:bg-neutral-800 border-neutral-300 dark:border-neutral-600 text-neutral-900 dark:text-white'
                    : 'bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 hover:border-neutral-300 dark:hover:border-neutral-700'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Tags
          </label>
          <input
            type="text"
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
            placeholder="tag1, tag2, tag3"
            className="w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none focus:border-neutral-400 dark:focus:border-neutral-700"
          />
          <p className="mt-1 text-xs text-neutral-500">
            Separate tags with commas (without #)
          </p>
        </div>

        {/* Content */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Content
          </label>
          <textarea
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            placeholder="Write your document in Markdown..."
            rows={15}
            className="w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none focus:border-neutral-400 dark:focus:border-neutral-700 font-mono text-sm"
            required
          />
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-lg text-red-600 dark:text-red-400 text-sm">
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
            {isSubmitting ? 'Creating...' : 'Create Document'}
          </button>
          <Link
            href="/memory"
            className="px-6 py-3 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 text-neutral-700 dark:text-neutral-300 font-medium rounded-lg transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

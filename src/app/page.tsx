import { getAllDocuments } from '@/lib/documents';
import Link from 'next/link';

export default function Home() {
  const documents = getAllDocuments();
  const recentDocs = documents.slice(0, 5);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-neutral-900 dark:text-white mb-2">🧠 life-os</h1>
        <p className="text-neutral-500 dark:text-neutral-400 text-lg">
          Your personal Second Brain
        </p>
      </header>

      <section className="mb-12">
        <blockquote className="border-l-4 border-blue-500 pl-4 py-2 text-neutral-600 dark:text-neutral-300 italic">
          If something is important enough to remember, it must become a document.
        </blockquote>
      </section>

      <section className="mb-12">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-white mb-4">Recent Documents</h2>
        <div className="space-y-2">
          {recentDocs.map((doc) => (
            <Link
              key={doc.slug}
              href={`/doc/${doc.slug}`}
              className="block p-4 bg-neutral-100 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 dark:hover:border-neutral-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-neutral-900 dark:text-white font-medium">{doc.title}</span>
                <span className="text-xs text-neutral-500">{doc.type}</span>
              </div>
              {doc.date && (
                <span className="text-sm text-neutral-500">
                  {new Date(doc.date).toLocaleDateString()}
                </span>
              )}
            </Link>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-neutral-100 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 text-center">
          <div className="text-2xl font-bold text-neutral-900 dark:text-white">{documents.length}</div>
          <div className="text-sm text-neutral-500">Documents</div>
        </div>
        <div className="p-4 bg-neutral-100 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 text-center">
          <div className="text-2xl font-bold text-neutral-900 dark:text-white">
            {documents.filter(d => d.type === 'journal').length}
          </div>
          <div className="text-sm text-neutral-500">Journals</div>
        </div>
        <div className="p-4 bg-neutral-100 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 text-center">
          <div className="text-2xl font-bold text-neutral-900 dark:text-white">
            {documents.filter(d => d.type === 'concept').length}
          </div>
          <div className="text-sm text-neutral-500">Concepts</div>
        </div>
        <div className="p-4 bg-neutral-100 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 text-center">
          <div className="text-2xl font-bold text-neutral-900 dark:text-white">
            {new Set(documents.flatMap(d => d.tags)).size}
          </div>
          <div className="text-sm text-neutral-500">Tags</div>
        </div>
      </section>
    </div>
  );
}

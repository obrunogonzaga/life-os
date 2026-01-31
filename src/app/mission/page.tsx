import { getAllDocuments } from '@/lib/documents';
import Link from 'next/link';

export default function MissionControlPage() {
  const documents = getAllDocuments();
  const recentDocs = documents.slice(0, 3);
  const journals = documents.filter(d => d.type === 'journal');
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-2">
          🎯 Mission Control
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400">
          {new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Focus & Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Daily Focus */}
          <section className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
              <span>🎯</span> Daily Focus
            </h2>
            <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
              <p className="text-neutral-500 dark:text-neutral-400 italic text-center py-4">
                Set your focus for the day in the daily brief
              </p>
            </div>
          </section>

          {/* Tasks Widget */}
          <section className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white flex items-center gap-2">
                <span>✅</span> Today's Tasks
              </h2>
              <Link href="/tasks" className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400">
                View all →
              </Link>
            </div>
            <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
              <p className="text-neutral-500 dark:text-neutral-400 text-center py-4">
                Connect to Todoist to see your tasks
              </p>
            </div>
          </section>

          {/* Quick Capture */}
          <section className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white flex items-center gap-2">
                <span>📥</span> Quick Capture
              </h2>
              <Link href="/captures" className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400">
                View all →
              </Link>
            </div>
            <Link 
              href="/captures/new"
              className="block w-full bg-white dark:bg-neutral-800 rounded-lg p-4 border border-dashed border-neutral-300 dark:border-neutral-600 hover:border-neutral-400 dark:hover:border-neutral-500 transition-colors text-center text-neutral-500 dark:text-neutral-400"
            >
              + Capture a thought...
            </Link>
          </section>
        </div>

        {/* Right Column - Stats & Recent */}
        <div className="space-y-6">
          {/* Stats */}
          <section className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
              <span>📊</span> Memory Stats
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">{documents.length}</div>
                <div className="text-xs text-neutral-500">Documents</div>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">{journals.length}</div>
                <div className="text-xs text-neutral-500">Journals</div>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">
                  {documents.filter(d => d.type === 'concept').length}
                </div>
                <div className="text-xs text-neutral-500">Concepts</div>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">
                  {documents.filter(d => d.type === 'decision').length}
                </div>
                <div className="text-xs text-neutral-500">Decisions</div>
              </div>
            </div>
          </section>

          {/* Recent Documents */}
          <section className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white flex items-center gap-2">
                <span>🧠</span> Recent
              </h2>
              <Link href="/memory" className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400">
                View all →
              </Link>
            </div>
            <div className="space-y-2">
              {recentDocs.map((doc) => (
                <Link
                  key={doc.slug}
                  href={`/memory/doc/${doc.slug}`}
                  className="block bg-white dark:bg-neutral-800 rounded-lg p-3 border border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600 transition-colors"
                >
                  <div className="font-medium text-sm text-neutral-900 dark:text-white truncate">
                    {doc.title}
                  </div>
                  <div className="text-xs text-neutral-500 mt-1">{doc.type}</div>
                </Link>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

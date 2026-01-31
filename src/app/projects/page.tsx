import Link from 'next/link';

interface Project {
  id: string;
  name: string;
  emoji: string;
  status: 'active' | 'paused' | 'completed';
  description: string;
  links?: { label: string; url: string }[];
}

// TODO: Move to database or markdown files
const projects: Project[] = [
  {
    id: 'life-os',
    name: 'life-os',
    emoji: '🧠',
    status: 'active',
    description: 'Personal Second Brain system',
    links: [
      { label: 'Repo', url: 'https://github.com/obrunogonzaga/life-os' },
      { label: 'Live', url: 'http://life-os.89.167.22.57.nip.io' },
    ],
  },
  {
    id: 'meuflip',
    name: 'MeuFlip',
    emoji: '🏠',
    status: 'active',
    description: 'SaaS para house flippers - meta R$ 3k/mês em 90 dias',
    links: [],
  },
  {
    id: 'widia-clinica',
    name: 'Widia/Clínica Fabiano',
    emoji: '🩺',
    status: 'active',
    description: 'Sistema agendamento + integração Google Calendar',
    links: [],
  },
];

const statusColors = {
  active: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
  paused: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
  completed: 'bg-neutral-100 dark:bg-neutral-800 text-neutral-500',
};

const statusLabels = {
  active: 'Active',
  paused: 'Paused',
  completed: 'Completed',
};

export default function ProjectsPage() {
  const activeProjects = projects.filter(p => p.status === 'active');
  const otherProjects = projects.filter(p => p.status !== 'active');

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-2 flex items-center gap-2">
          <span>📁</span> Projects
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400">
          {activeProjects.length} active projects
        </p>
      </header>

      {/* Active Projects */}
      <section className="mb-12">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Active
        </h2>
        <div className="grid gap-4">
          {activeProjects.map(project => (
            <div
              key={project.id}
              className="bg-neutral-100 dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 p-6"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{project.emoji}</span>
                  <div>
                    <h3 className="font-semibold text-neutral-900 dark:text-white">
                      {project.name}
                    </h3>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400">
                      {project.description}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[project.status]}`}>
                  {statusLabels[project.status]}
                </span>
              </div>
              
              {project.links && project.links.length > 0 && (
                <div className="flex gap-2 mt-4">
                  {project.links.map(link => (
                    <a
                      key={link.url}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm px-3 py-1.5 rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-blue-600 dark:text-blue-400 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                    >
                      {link.label} ↗
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Other Projects */}
      {otherProjects.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
            Other
          </h2>
          <div className="grid gap-4">
            {otherProjects.map(project => (
              <div
                key={project.id}
                className="bg-neutral-50 dark:bg-neutral-900/50 rounded-xl border border-neutral-200 dark:border-neutral-800 p-4 opacity-75"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{project.emoji}</span>
                  <div className="flex-1">
                    <h3 className="font-medium text-neutral-700 dark:text-neutral-300">
                      {project.name}
                    </h3>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[project.status]}`}>
                    {statusLabels[project.status]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Add Project CTA */}
      <div className="mt-8 p-6 border-2 border-dashed border-neutral-200 dark:border-neutral-700 rounded-xl text-center">
        <p className="text-neutral-500 dark:text-neutral-400 mb-2">
          Projects are currently hardcoded
        </p>
        <p className="text-sm text-neutral-400 dark:text-neutral-500">
          Future: Add projects via markdown files in /brain/projects/
        </p>
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect, useCallback } from 'react';

interface CanvasSection {
  id: string;
  title: string;
  placeholder: string;
}

const SECTIONS: CanvasSection[] = [
  {
    id: 'objetivo',
    title: 'Objetivo Principal',
    placeholder:
      'Comece definindo o que você deseja alcançar. Pode ser algo como aumentar a produtividade da equipe ou melhorar a precisão dos relatórios financeiros.',
  },
  {
    id: 'stakeholders',
    title: 'Stakeholders',
    placeholder:
      'Identifique as partes interessadas e o impacto do plano sobre elas, como líderes de departamento, equipe de TI, clientes.',
  },
  {
    id: 'desafios',
    title: 'Desafios',
    placeholder:
      'Identifique quais problemas precisam ser superados. Pode ser a resistência à mudança ou a falta de recursos tecnológicos.',
  },
  {
    id: 'ganhos',
    title: 'Ganhos',
    placeholder:
      'Descreva os resultados esperados, como maior eficiência operacional ou melhoria na tomada de decisão.',
  },
  {
    id: 'metas',
    title: 'Metas e Objetivos',
    placeholder:
      'Defina metas específicas e de curto/médio prazo, como aumentar a taxa de conversão em 10% nos próximos três meses.',
  },
  {
    id: 'plano',
    title: 'Plano de Ação',
    placeholder:
      'Detalhe as ações necessárias, incluindo quem será responsável por cada tarefa. Ex: treinar a equipe de vendas ou implementar sistema de acompanhamento.',
  },
  {
    id: 'kpis',
    title: 'KPIs',
    placeholder:
      'Escolha os indicadores que você vai usar para medir o sucesso. Lembre-se de que esses indicadores precisam ser mensuráveis e alinhados aos objetivos.',
  },
  {
    id: 'recursos',
    title: 'Recursos',
    placeholder:
      'Liste tudo o que você vai precisar para implementar o plano: tecnologia, pessoas, orçamento, treinamento, etc.',
  },
];

const STORAGE_KEY = 'life-os-canvas';

interface CanvasData {
  title: string;
  sections: Record<string, string>;
}

function loadCanvas(): CanvasData {
  if (typeof window === 'undefined') return { title: '', sections: {} };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { title: '', sections: {} };
}

function saveCanvas(data: CanvasData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {}
}

function CanvasCard({
  section,
  value,
  onChange,
}: {
  section: CanvasSection;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-col bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg overflow-hidden transition-colors hover:border-yellow-500/40 dark:hover:border-yellow-500/40">
      {/* Yellow accent header */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-yellow-500/10 dark:bg-yellow-500/10 border-b border-yellow-500/20">
        <div className="w-1 h-5 rounded-full bg-yellow-500" />
        <h3 className="text-sm font-semibold text-yellow-700 dark:text-yellow-400 uppercase tracking-wide">
          {section.title}
        </h3>
      </div>
      {/* Textarea */}
      <textarea
        className="flex-1 w-full p-4 bg-transparent text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 dark:placeholder-neutral-600 text-sm leading-relaxed resize-none focus:outline-none min-h-[140px]"
        placeholder={section.placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function CanvasPage() {
  const [data, setData] = useState<CanvasData>({ title: '', sections: {} });
  const [mounted, setMounted] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  useEffect(() => {
    setData(loadCanvas());
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) saveCanvas(data);
  }, [data, mounted]);

  const updateSection = useCallback((id: string, value: string) => {
    setData((prev) => ({
      ...prev,
      sections: { ...prev.sections, [id]: value },
    }));
  }, []);

  const updateTitle = useCallback((title: string) => {
    setData((prev) => ({ ...prev, title }));
  }, []);

  const handleClearAll = () => {
    setData({ title: '', sections: {} });
    setShowClearConfirm(false);
  };

  const handleExport = async () => {
    const lines: string[] = [];
    const canvasTitle = data.title?.trim() || 'Canvas de Gestão de Resultados';
    lines.push(`# ${canvasTitle}`);
    lines.push(`Exportado em ${new Date().toLocaleDateString('pt-BR')} às ${new Date().toLocaleTimeString('pt-BR')}`);
    lines.push('');

    for (const section of SECTIONS) {
      const content = data.sections[section.id]?.trim();
      lines.push(`## ${section.title}`);
      lines.push(content || '(vazio)');
      lines.push('');
    }

    const text = lines.join('\n');

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Get section helpers
  const sectionValue = (id: string) => data.sections[id] || '';
  const objetivo = SECTIONS[0]; // full width top
  const middlePairs = [
    [SECTIONS[1], SECTIONS[2]], // Stakeholders / Desafios
    [SECTIONS[3], SECTIONS[4]], // Ganhos / Metas
    [SECTIONS[5], SECTIONS[6]], // Plano de Ação / KPIs
  ];
  const recursos = SECTIONS[7]; // full width bottom

  if (!mounted) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-neutral-200 dark:bg-neutral-800 rounded w-1/3" />
          <div className="h-48 bg-neutral-200 dark:bg-neutral-800 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
      {/* Page header */}
      <header className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <span>📊</span>
              <span>Canvas de Gestão de Resultados</span>
            </h1>
            <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
              Preencha cada seção para estruturar seu plano de gestão
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border border-yellow-500/20 hover:bg-yellow-500/20 transition-colors cursor-pointer"
            >
              {copied ? (
                <>
                  <span>✓</span> Copiado!
                </>
              ) : (
                <>
                  <span>📋</span> Exportar
                </>
              )}
            </button>

            {showClearConfirm ? (
              <div className="flex items-center gap-1">
                <button
                  onClick={handleClearAll}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-md bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors cursor-pointer"
                >
                  Confirmar
                </button>
                <button
                  onClick={() => setShowClearConfirm(false)}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowClearConfirm(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 border border-neutral-200 dark:border-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors cursor-pointer"
              >
                <span>🗑️</span> Limpar tudo
              </button>
            )}
          </div>
        </div>

        {/* Canvas title input */}
        <input
          type="text"
          placeholder="Nome do projeto ou iniciativa..."
          value={data.title}
          onChange={(e) => updateTitle(e.target.value)}
          className="w-full px-4 py-2.5 text-lg font-medium bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-600 focus:outline-none focus:border-yellow-500/50 dark:focus:border-yellow-500/50 transition-colors"
        />
      </header>

      {/* Canvas grid */}
      <div className="space-y-4">
        {/* Top: Objetivo Principal — full width */}
        <CanvasCard
          section={objetivo}
          value={sectionValue(objetivo.id)}
          onChange={(v) => updateSection(objetivo.id, v)}
        />

        {/* Middle: 3 rows of 2 columns */}
        {middlePairs.map((pair, i) => (
          <div key={i} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pair.map((section) => (
              <CanvasCard
                key={section.id}
                section={section}
                value={sectionValue(section.id)}
                onChange={(v) => updateSection(section.id, v)}
              />
            ))}
          </div>
        ))}

        {/* Bottom: Recursos — full width */}
        <CanvasCard
          section={recursos}
          value={sectionValue(recursos.id)}
          onChange={(v) => updateSection(recursos.id, v)}
        />
      </div>
    </div>
  );
}

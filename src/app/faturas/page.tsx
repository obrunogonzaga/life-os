'use client';

import Link from 'next/link';

interface FaturaMonth {
  month: string;
  label: string;
  file: string;
  total: string;
  banks: string[];
}

const faturas: FaturaMonth[] = [
  {
    month: '2026-03',
    label: 'Março 2026',
    file: '/faturas-2026-03.html',
    total: 'R$ 3.916,46',
    banks: ['Itaú Black', 'PicPay', 'Bradesco 8429', 'Bradesco 5969', 'Nubank'],
  },
  {
    month: '2026-02',
    label: 'Fevereiro 2026',
    file: '/faturas-2026-02.html',
    total: 'R$ 4.592,46',
    banks: ['Itaú Black', 'Bradesco 8429', 'Bradesco 5969'],
  },
];

export default function FaturasPage() {
  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">
          💳 Faturas
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 mb-6">
          Selecione o mês para visualizar e marcar transações
        </p>

        <div className="space-y-3">
          {faturas.map((f) => (
            <a
              key={f.month}
              href={f.file}
              className="block bg-white dark:bg-neutral-900 rounded-xl p-4 border border-neutral-200 dark:border-neutral-800 hover:border-pink-500/50 hover:shadow-lg transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  {f.label}
                </h2>
                <span className="text-pink-600 dark:text-pink-400 font-bold">
                  {f.total}
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {f.banks.map((bank) => (
                  <span
                    key={bank}
                    className="text-xs px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                  >
                    {bank}
                  </span>
                ))}
              </div>
            </a>
          ))}
        </div>

        <div className="mt-8 p-4 bg-neutral-100 dark:bg-neutral-900 rounded-xl text-sm text-neutral-500 dark:text-neutral-400">
          <p className="font-medium text-neutral-700 dark:text-neutral-300 mb-1">💡 Dica</p>
          <p>
            Clique nas transações para marcar como da Alzi. As marcações são
            salvas automaticamente no navegador.
          </p>
        </div>
      </div>
    </div>
  );
}

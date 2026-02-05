'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Month {
  id: number;
  year: number;
  month: number;
  label: string;
  total: number | null;
  wife_total: number | null;
  tx_count: number;
  banks: string | null;
}

const bankColors: Record<string, string> = {
  'itau': 'bg-orange-500',
  'picpay': 'bg-green-500',
  'bradesco-8429': 'bg-red-500',
  'bradesco-5969': 'bg-purple-500',
  'nubank': 'bg-purple-700',
};

const bankLabels: Record<string, string> = {
  'itau': 'Itaú Black',
  'picpay': 'PicPay',
  'bradesco-8429': 'Bradesco 8429',
  'bradesco-5969': 'Bradesco 5969',
  'nubank': 'Nubank',
};

export default function FaturasPage() {
  const [months, setMonths] = useState<Month[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/faturas/months')
      .then((res) => res.json())
      .then((data) => {
        setMonths(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const formatCurrency = (value: number | null) => {
    if (value === null) return 'R$ 0,00';
    return `R$ ${value.toFixed(2).replace('.', ',')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 flex items-center justify-center">
        <p className="text-neutral-500">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">
          💳 Faturas
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 mb-6">
          Selecione o mês para visualizar e marcar transações
        </p>

        {months.length === 0 ? (
          <div className="text-center py-12 text-neutral-500">
            <p>Nenhuma fatura encontrada.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {months.map((m) => (
              <Link
                key={m.id}
                href={`/faturas/${m.id}`}
                className="block bg-white dark:bg-neutral-900 rounded-xl p-4 border border-neutral-200 dark:border-neutral-800 hover:border-pink-500/50 hover:shadow-lg transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                    {m.label}
                  </h2>
                  <span className="text-pink-600 dark:text-pink-400 font-bold">
                    {formatCurrency(m.total)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm text-neutral-500 mb-2">
                  <span>{m.tx_count} transações</span>
                  {m.wife_total && m.wife_total > 0 && (
                    <span className="text-pink-500">
                      🩷 Alzi: {formatCurrency(m.wife_total)}
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {m.banks?.split(',').map((bank) => (
                    <span
                      key={bank}
                      className={`text-xs px-2 py-0.5 rounded-full text-white ${bankColors[bank] || 'bg-neutral-500'}`}
                    >
                      {bankLabels[bank] || bank}
                    </span>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-neutral-100 dark:bg-neutral-900 rounded-xl text-sm text-neutral-500 dark:text-neutral-400">
          <p className="font-medium text-neutral-700 dark:text-neutral-300 mb-1">💡 Dica</p>
          <p>
            Clique nas transações para marcar como da Alzi. Os dados são salvos
            automaticamente no banco de dados.
          </p>
        </div>
      </div>
    </div>
  );
}

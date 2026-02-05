'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';

interface Transaction {
  id: number;
  date: string;
  date_label: string;
  name: string;
  category: string | null;
  amount: number;
  bank: string;
  installment: string | null;
  is_wife: number;
}

interface Stats {
  total: number;
  wife_total: number;
  wife_half: number;
  bruno_pays: number;
  tx_count: number;
  wife_count: number;
  split_percent: number;
}

interface BankStat {
  bank: string;
  total: number;
  count: number;
}

interface MonthData {
  month: { id: number; label: string; year: number; month: number };
  transactions: Transaction[];
  stats: Stats;
  bankStats: BankStat[];
}

const bankColors: Record<string, string> = {
  'itau': 'bg-orange-500',
  'picpay': 'bg-green-500',
  'bradesco-8429': 'bg-red-500',
  'bradesco-5969': 'bg-purple-500',
  'nubank': 'bg-purple-700',
};

const bankLabels: Record<string, string> = {
  'itau': 'Itaú',
  'picpay': 'PicPay',
  'bradesco-8429': 'Brad 8429',
  'bradesco-5969': 'Brad 5969',
  'nubank': 'Nubank',
};

export default function FaturaDetailPage() {
  const params = useParams();
  const id = params.id as string;
  
  const [data, setData] = useState<MonthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [updating, setUpdating] = useState<Set<number>>(new Set());

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`/api/faturas/months/${id}`);
      if (!res.ok) throw new Error('Failed to fetch');
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError('Erro ao carregar fatura');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleWife = async (txId: number) => {
    if (updating.has(txId)) return;
    
    setUpdating((prev) => new Set(prev).add(txId));
    
    try {
      const res = await fetch(`/api/faturas/transactions/${txId}/toggle`, {
        method: 'POST',
      });
      if (res.ok) {
        // Update local state
        setData((prev) => {
          if (!prev) return prev;
          const newTx = prev.transactions.map((t) =>
            t.id === txId ? { ...t, is_wife: t.is_wife ? 0 : 1 } : t
          );
          // Recalculate stats
          const wifeTotal = newTx.filter((t) => t.is_wife).reduce((s, t) => s + t.amount, 0);
          const total = newTx.reduce((s, t) => s + t.amount, 0);
          const wifeHalf = wifeTotal * (prev.stats.split_percent / 100);
          return {
            ...prev,
            transactions: newTx,
            stats: {
              ...prev.stats,
              wife_total: wifeTotal,
              wife_half: wifeHalf,
              bruno_pays: total - wifeHalf,
              wife_count: newTx.filter((t) => t.is_wife).length,
            },
          };
        });
      }
    } finally {
      setUpdating((prev) => {
        const next = new Set(prev);
        next.delete(txId);
        return next;
      });
    }
  };

  const selectAllVisible = async () => {
    const visible = filteredTransactions.filter((t) => !t.is_wife);
    if (visible.length === 0) return;
    
    const ids = visible.map((t) => t.id);
    await fetch('/api/faturas/transactions/bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids, is_wife: true }),
    });
    fetchData();
  };

  const deselectAllVisible = async () => {
    const visible = filteredTransactions.filter((t) => t.is_wife);
    if (visible.length === 0) return;
    
    const ids = visible.map((t) => t.id);
    await fetch('/api/faturas/transactions/bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids, is_wife: false }),
    });
    fetchData();
  };

  const formatCurrency = (value: number) => {
    return `R$ ${value.toFixed(2).replace('.', ',')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <p className="text-neutral-500">Carregando...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Fatura não encontrada'}</p>
          <Link href="/faturas" className="text-pink-500 hover:underline">
            ← Voltar
          </Link>
        </div>
      </div>
    );
  }

  const { month, transactions, stats, bankStats } = data;
  const filteredTransactions = filter === 'all' 
    ? transactions 
    : transactions.filter((t) => t.bank === filter);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-neutral-200 p-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <Link href="/faturas" className="text-neutral-500 hover:text-white">
            ←
          </Link>
          <h1 className="text-xl font-bold">💳 {month.label}</h1>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="bg-[#1a1a1a] rounded-xl p-3">
            <div className="text-xs text-neutral-500 uppercase">Total geral</div>
            <div className="text-lg font-bold text-yellow-400">{formatCurrency(stats.total)}</div>
          </div>
          <div className="bg-[#1a1a1a] rounded-xl p-3">
            <div className="text-xs text-neutral-500 uppercase">🩷 Alzi (total)</div>
            <div className="text-lg font-bold text-pink-400">{formatCurrency(stats.wife_total)}</div>
          </div>
          <div className="bg-[#1a1a1a] rounded-xl p-3">
            <div className="text-xs text-neutral-500 uppercase">🩷 Alzi paga ({stats.split_percent}%)</div>
            <div className="text-lg font-bold text-pink-400 opacity-70">{formatCurrency(stats.wife_half)}</div>
          </div>
          <div className="bg-[#1a1a1a] rounded-xl p-3">
            <div className="text-xs text-neutral-500 uppercase">🔵 Bruno paga</div>
            <div className="text-lg font-bold text-blue-400">{formatCurrency(stats.bruno_pays)}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              filter === 'all' 
                ? 'bg-neutral-700 text-white' 
                : 'bg-[#1a1a1a] text-neutral-400 hover:bg-neutral-800'
            }`}
          >
            📋 Todos ({transactions.length})
          </button>
          {bankStats.map((bs) => (
            <button
              key={bs.bank}
              onClick={() => setFilter(bs.bank)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                filter === bs.bank 
                  ? `${bankColors[bs.bank]} text-white` 
                  : 'bg-[#1a1a1a] text-neutral-400 hover:bg-neutral-800'
              }`}
            >
              {bankLabels[bs.bank] || bs.bank} ({bs.count})
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={selectAllVisible}
            className="px-3 py-1.5 bg-[#222] border border-neutral-700 rounded-lg text-sm text-neutral-400 hover:bg-neutral-800"
          >
            Selecionar visíveis
          </button>
          <button
            onClick={deselectAllVisible}
            className="px-3 py-1.5 bg-[#222] border border-neutral-700 rounded-lg text-sm text-neutral-400 hover:bg-neutral-800"
          >
            Limpar visíveis
          </button>
        </div>

        {/* Transaction List */}
        <div className="bg-[#1a1a1a] rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-neutral-500 uppercase border-b border-neutral-800">
                <th className="p-3 text-center w-12">🩷</th>
                <th className="p-3 text-left">Data</th>
                <th className="p-3 text-left">Estabelecimento</th>
                <th className="p-3 text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((tx) => (
                <tr
                  key={tx.id}
                  onClick={() => toggleWife(tx.id)}
                  className={`border-b border-neutral-800/50 cursor-pointer transition-colors ${
                    tx.is_wife ? 'bg-pink-950/30' : 'hover:bg-neutral-800/50'
                  } ${updating.has(tx.id) ? 'opacity-50' : ''}`}
                >
                  <td className="p-3 text-center">
                    <input
                      type="checkbox"
                      checked={!!tx.is_wife}
                      onChange={() => {}}
                      className="w-4 h-4 accent-pink-500 cursor-pointer"
                    />
                  </td>
                  <td className="p-3 text-sm">
                    {tx.date_label}
                    {tx.installment && (
                      <span className="text-xs text-neutral-600 ml-1">
                        p.{tx.installment}
                      </span>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{tx.name}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full text-white ${bankColors[tx.bank] || 'bg-neutral-600'}`}>
                        {bankLabels[tx.bank] || tx.bank}
                      </span>
                    </div>
                    {tx.category && (
                      <div className="text-xs text-neutral-600">{tx.category}</div>
                    )}
                  </td>
                  <td className="p-3 text-right font-medium tabular-nums">
                    {formatCurrency(tx.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

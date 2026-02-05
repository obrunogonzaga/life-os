'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function FaturaMonthPage() {
  const params = useParams();
  const month = params.month as string;
  const [html, setHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/faturas/${month}`)
      .then((res) => {
        if (!res.ok) throw new Error('Fatura não encontrada');
        return res.text();
      })
      .then(setHtml)
      .catch((e) => setError(e.message));
  }, [month]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-950 text-white">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">❌ Erro</h1>
          <p className="text-neutral-400">{error}</p>
        </div>
      </div>
    );
  }

  if (!html) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-950 text-white">
        <p>Carregando...</p>
      </div>
    );
  }

  return (
    <iframe
      srcDoc={html}
      className="w-full h-screen border-0"
      title={`Fatura ${month}`}
    />
  );
}

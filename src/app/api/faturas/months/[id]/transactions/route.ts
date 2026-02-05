import { NextRequest, NextResponse } from 'next/server';
import { createTransaction, getMonthById } from '@/lib/db';

// POST /api/faturas/months/[id]/transactions - Add transaction(s)
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const monthId = parseInt(id);
    
    if (isNaN(monthId)) {
      return NextResponse.json({ error: 'Invalid month ID' }, { status: 400 });
    }
    
    const month = getMonthById(monthId);
    if (!month) {
      return NextResponse.json({ error: 'Month not found' }, { status: 404 });
    }
    
    const body = await request.json();
    const transactions = Array.isArray(body) ? body : [body];
    
    const created = [];
    for (const tx of transactions) {
      const txId = createTransaction({
        month_id: monthId,
        date: tx.date,
        date_label: tx.date_label || tx.dateLabel,
        name: tx.name,
        category: tx.category || tx.cat,
        amount: tx.amount,
        bank: tx.bank,
        installment: tx.installment,
        is_wife: tx.is_wife || tx.checked ? 1 : 0,
      });
      created.push({ id: txId, ...tx });
    }
    
    return NextResponse.json({ created: created.length, transactions: created }, { status: 201 });
  } catch (error) {
    console.error('Error creating transactions:', error);
    return NextResponse.json({ error: 'Failed to create transactions' }, { status: 500 });
  }
}

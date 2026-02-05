import { NextRequest, NextResponse } from 'next/server';
import { updateTransactionWife, getDb } from '@/lib/db';

// POST /api/faturas/transactions/[id]/toggle - Toggle is_wife
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const txId = parseInt(id);
    
    if (isNaN(txId)) {
      return NextResponse.json({ error: 'Invalid transaction ID' }, { status: 400 });
    }
    
    // Get current state
    const db = getDb();
    const tx = db.prepare('SELECT is_wife FROM transactions WHERE id = ?').get(txId) as { is_wife: number } | undefined;
    
    if (!tx) {
      return NextResponse.json({ error: 'Transaction not found' }, { status: 404 });
    }
    
    const newState = !tx.is_wife;
    updateTransactionWife(txId, newState);
    
    return NextResponse.json({ id: txId, is_wife: newState });
  } catch (error) {
    console.error('Error toggling transaction:', error);
    return NextResponse.json({ error: 'Failed to toggle transaction' }, { status: 500 });
  }
}

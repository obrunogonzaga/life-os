import { NextRequest, NextResponse } from 'next/server';
import { getMonthById, getTransactionsByMonth, getMonthStats, getBankStats } from '@/lib/db';

// GET /api/faturas/months/[id] - Get month with transactions
export async function GET(
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
    
    const transactions = getTransactionsByMonth(monthId);
    const stats = getMonthStats(monthId);
    const bankStats = getBankStats(monthId);
    
    return NextResponse.json({
      month,
      transactions,
      stats,
      bankStats,
    });
  } catch (error) {
    console.error('Error fetching month:', error);
    return NextResponse.json({ error: 'Failed to fetch month' }, { status: 500 });
  }
}

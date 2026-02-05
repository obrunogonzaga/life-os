import { NextRequest, NextResponse } from 'next/server';
import { bulkUpdateWife } from '@/lib/db';

// POST /api/faturas/transactions/bulk - Bulk update is_wife
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { ids, is_wife } = body;
    
    if (!Array.isArray(ids) || ids.length === 0) {
      return NextResponse.json({ error: 'ids must be a non-empty array' }, { status: 400 });
    }
    
    if (typeof is_wife !== 'boolean') {
      return NextResponse.json({ error: 'is_wife must be a boolean' }, { status: 400 });
    }
    
    bulkUpdateWife(ids, is_wife);
    
    return NextResponse.json({ updated: ids.length, is_wife });
  } catch (error) {
    console.error('Error bulk updating transactions:', error);
    return NextResponse.json({ error: 'Failed to update transactions' }, { status: 500 });
  }
}

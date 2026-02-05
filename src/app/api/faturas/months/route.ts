import { NextRequest, NextResponse } from 'next/server';
import { getAllMonths, createMonth } from '@/lib/db';

// GET /api/faturas/months - List all months
export async function GET() {
  try {
    const months = getAllMonths();
    return NextResponse.json(months);
  } catch (error) {
    console.error('Error fetching months:', error);
    return NextResponse.json({ error: 'Failed to fetch months' }, { status: 500 });
  }
}

// POST /api/faturas/months - Create new month
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { year, month, label } = body;
    
    if (!year || !month || !label) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    
    const id = createMonth(year, month, label);
    return NextResponse.json({ id, year, month, label }, { status: 201 });
  } catch (error: any) {
    if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      return NextResponse.json({ error: 'Month already exists' }, { status: 409 });
    }
    console.error('Error creating month:', error);
    return NextResponse.json({ error: 'Failed to create month' }, { status: 500 });
  }
}

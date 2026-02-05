import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ month: string }> }
) {
  const { month } = await params;
  
  // Sanitize month param to prevent path traversal
  const safeMonth = month.replace(/[^a-zA-Z0-9-]/g, '');
  
  const filePath = path.join(process.cwd(), 'brain', 'notes', `faturas-${safeMonth}.html`);
  
  try {
    const content = await readFile(filePath, 'utf-8');
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    });
  } catch (e) {
    return NextResponse.json(
      { error: 'Fatura não encontrada' },
      { status: 404 }
    );
  }
}

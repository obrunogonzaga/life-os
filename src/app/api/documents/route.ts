import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const BRAIN_DIR = path.join(process.cwd(), 'brain');

export async function DELETE(request: NextRequest) {
  try {
    const { slug } = await request.json();
    
    if (!slug || typeof slug !== 'string') {
      return NextResponse.json(
        { error: 'Slug is required' },
        { status: 400 }
      );
    }

    // Sanitize slug to prevent directory traversal
    const sanitizedSlug = slug.replace(/\.\./g, '').replace(/^\/+/, '');
    const filePath = path.join(BRAIN_DIR, `${sanitizedSlug}.md`);

    // Verify file is within BRAIN_DIR
    const resolvedPath = path.resolve(filePath);
    if (!resolvedPath.startsWith(path.resolve(BRAIN_DIR))) {
      return NextResponse.json(
        { error: 'Invalid path' },
        { status: 400 }
      );
    }

    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }

    // Delete the file
    fs.unlinkSync(filePath);

    // Clean up empty directories
    const dir = path.dirname(filePath);
    if (dir !== BRAIN_DIR) {
      try {
        const entries = fs.readdirSync(dir);
        if (entries.length === 0) {
          fs.rmdirSync(dir);
        }
      } catch {
        // Ignore errors when cleaning up directories
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Delete error:', error);
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}

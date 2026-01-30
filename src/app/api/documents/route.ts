import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const BRAIN_DIR = path.join(process.cwd(), 'brain');

function generateSlug(title: string, type: string): string {
  const slug = title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  return `${type}s/${slug}`;
}

function generateFrontmatter(data: {
  title: string;
  date: string;
  type: string;
  tags: string[];
}): string {
  const sanitizedTags = data.tags.map(t => t.replace(/^#/, '').trim()).filter(Boolean);
  return `---
title: "${data.title}"
date: ${data.date}
type: ${data.type}
tags: [${sanitizedTags.join(', ')}]
---`;
}

// POST - Create new document
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, type, tags, content } = body;

    if (!title || !content) {
      return NextResponse.json(
        { error: 'Title and content are required' },
        { status: 400 }
      );
    }

    const slug = generateSlug(title, type || 'note');
    const filePath = path.join(BRAIN_DIR, `${slug}.md`);
    const date = new Date().toISOString().split('T')[0];

    // Ensure directory exists
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Check if file already exists
    if (fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Document already exists', slug },
        { status: 409 }
      );
    }

    const frontmatter = generateFrontmatter({
      title,
      date,
      type: type || 'note',
      tags: tags || [],
    });

    const fullContent = `${frontmatter}\n\n${content}`;

    // Write file
    fs.writeFileSync(filePath, fullContent, 'utf-8');

    return NextResponse.json({
      success: true,
      slug,
      message: 'Document created successfully',
    });
  } catch (error) {
    console.error('Error creating document:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// DELETE - Delete document
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

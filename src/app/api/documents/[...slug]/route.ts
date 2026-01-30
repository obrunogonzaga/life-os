import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const BRAIN_DIR = path.join(process.cwd(), 'brain');

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

function parseFrontmatter(content: string) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { metadata: {}, content };
  
  const frontmatter = match[1];
  const body = match[2];
  
  const metadata: Record<string, unknown> = {};
  
  // Parse title
  const titleMatch = frontmatter.match(/title:\s*"([^"]+)"/);
  if (titleMatch) metadata.title = titleMatch[1];
  
  // Parse date
  const dateMatch = frontmatter.match(/date:\s*(\S+)/);
  if (dateMatch) metadata.date = dateMatch[1];
  
  // Parse type
  const typeMatch = frontmatter.match(/type:\s*(\S+)/);
  if (typeMatch) metadata.type = typeMatch[1];
  
  // Parse tags
  const tagsMatch = frontmatter.match(/tags:\s*\[([^\]]*)\]/);
  if (tagsMatch) {
    metadata.tags = tagsMatch[1].split(',').map(t => t.trim()).filter(Boolean);
  }
  
  return { metadata, content: body.trim() };
}

// GET - Fetch document content
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  try {
    const { slug } = await params;
    const filePath = path.join(BRAIN_DIR, `${slug.join('/')}.md`);

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

    const content = fs.readFileSync(filePath, 'utf-8');
    const parsed = parseFrontmatter(content);
    
    return NextResponse.json({
      ...parsed.metadata,
      content: parsed.content,
    });
  } catch (error) {
    console.error('Error fetching document:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// PUT - Update document
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  try {
    const { slug } = await params;
    const body = await request.json();
    const { title, type, tags, content, date } = body;

    if (!title || !content) {
      return NextResponse.json(
        { error: 'Title and content are required' },
        { status: 400 }
      );
    }

    const filePath = path.join(BRAIN_DIR, `${slug.join('/')}.md`);

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

    const frontmatter = generateFrontmatter({
      title,
      date: date || new Date().toISOString().split('T')[0],
      type: type || 'note',
      tags: tags || [],
    });

    const fullContent = `${frontmatter}\n\n${content}`;

    // Write file
    fs.writeFileSync(filePath, fullContent, 'utf-8');

    return NextResponse.json({
      success: true,
      slug: slug.join('/'),
      message: 'Document updated successfully',
    });
  } catch (error) {
    console.error('Error updating document:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

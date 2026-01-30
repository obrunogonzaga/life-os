import { NextRequest, NextResponse } from 'next/server';

const GH_PAT = process.env.GH_PAT;
const REPO_OWNER = 'obrunogonzaga';
const REPO_NAME = 'life-os';

function generateFrontmatter(data: {
  title: string;
  date: string;
  type: string;
  tags: string[];
}): string {
  return `---
title: "${data.title}"
date: ${data.date}
type: ${data.type}
tags: [${data.tags.join(', ')}]
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
    const filePath = `brain/${slug.join('/')}.md`;
    
    const response = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        headers: {
          Authorization: GH_PAT ? `Bearer ${GH_PAT}` : '',
          Accept: 'application/vnd.github.v3+json',
        },
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }

    const data = await response.json();
    const content = Buffer.from(data.content, 'base64').toString('utf-8');
    const parsed = parseFrontmatter(content);
    
    return NextResponse.json({
      ...parsed.metadata,
      content: parsed.content,
      sha: data.sha,
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

    if (!GH_PAT) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    const filePath = `brain/${slug.join('/')}.md`;
    
    // First get the current file to get SHA
    const getResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        headers: {
          Authorization: `Bearer ${GH_PAT}`,
          Accept: 'application/vnd.github.v3+json',
        },
      }
    );

    if (!getResponse.ok) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }

    const currentFile = await getResponse.json();
    
    const frontmatter = generateFrontmatter({
      title,
      date: date || new Date().toISOString().split('T')[0],
      type: type || 'note',
      tags: tags || [],
    });

    const fullContent = `${frontmatter}\n\n${content}`;

    // Update file via GitHub API
    const updateResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${GH_PAT}`,
          'Content-Type': 'application/json',
          Accept: 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          message: `📝 Update ${type}: ${title}`,
          content: Buffer.from(fullContent).toString('base64'),
          sha: currentFile.sha,
          branch: 'main',
        }),
      }
    );

    if (!updateResponse.ok) {
      const error = await updateResponse.json();
      console.error('GitHub API error:', error);
      return NextResponse.json(
        { error: 'Failed to update document' },
        { status: updateResponse.status }
      );
    }

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

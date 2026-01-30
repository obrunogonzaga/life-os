import { NextRequest, NextResponse } from 'next/server';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'obrunogonzaga';
const REPO_NAME = 'life-os';

const typeToFolder: Record<string, string> = {
  journal: 'journals',
  concept: 'concepts',
  decision: 'decisions',
  note: 'notes',
  reference: 'references',
};

function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

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

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, type, tags, content, date } = body;

    if (!title || !content) {
      return NextResponse.json(
        { error: 'Title and content are required' },
        { status: 400 }
      );
    }

    if (!GITHUB_TOKEN) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    const folder = typeToFolder[type] || 'notes';
    const slug = generateSlug(title);
    const filePath = `brain/${folder}/${slug}.md`;
    
    const frontmatter = generateFrontmatter({
      title,
      date: date || new Date().toISOString().split('T')[0],
      type,
      tags: tags || [],
    });

    const fullContent = `${frontmatter}\n\n${content}`;

    // Create file via GitHub API
    const response = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          'Content-Type': 'application/json',
          Accept: 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          message: `📝 Add ${type}: ${title}`,
          content: Buffer.from(fullContent).toString('base64'),
          branch: 'main',
        }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      console.error('GitHub API error:', error);
      
      if (response.status === 422) {
        return NextResponse.json(
          { error: 'A document with this name already exists' },
          { status: 422 }
        );
      }
      
      return NextResponse.json(
        { error: 'Failed to create document' },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: true,
      slug: `${folder}/${slug}`,
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

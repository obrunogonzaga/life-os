import { NextRequest, NextResponse } from 'next/server';

const GH_PAT = process.env.GH_PAT;
const REPO_OWNER = 'obrunogonzaga';
const REPO_NAME = 'life-os';

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

    if (!GH_PAT) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    const slug = generateSlug(title, type || 'note');
    const filePath = `brain/${slug}.md`;
    const date = new Date().toISOString().split('T')[0];

    const frontmatter = generateFrontmatter({
      title,
      date,
      type: type || 'note',
      tags: tags || [],
    });

    const fullContent = `${frontmatter}\n\n${content}`;

    // Check if file already exists
    const checkResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        headers: {
          Authorization: `Bearer ${GH_PAT}`,
          Accept: 'application/vnd.github.v3+json',
        },
      }
    );

    if (checkResponse.ok) {
      return NextResponse.json(
        { error: 'Document already exists', slug },
        { status: 409 }
      );
    }

    // Create file via GitHub API
    const createResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${GH_PAT}`,
          'Content-Type': 'application/json',
          Accept: 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          message: `📝 Add ${type || 'note'}: ${title}`,
          content: Buffer.from(fullContent).toString('base64'),
          branch: 'main',
        }),
      }
    );

    if (!createResponse.ok) {
      const error = await createResponse.json();
      console.error('GitHub API error:', error);
      return NextResponse.json(
        { error: 'Failed to create document' },
        { status: createResponse.status }
      );
    }

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

    if (!GH_PAT) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    const sanitizedSlug = slug.replace(/\.\./g, '').replace(/^\/+/, '');
    const filePath = `brain/${sanitizedSlug}.md`;

    // Get file SHA first
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

    const fileData = await getResponse.json();

    // Delete file via GitHub API
    const deleteResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${GH_PAT}`,
          'Content-Type': 'application/json',
          Accept: 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          message: `🗑️ Delete: ${sanitizedSlug}`,
          sha: fileData.sha,
          branch: 'main',
        }),
      }
    );

    if (!deleteResponse.ok) {
      const error = await deleteResponse.json();
      console.error('GitHub API error:', error);
      return NextResponse.json(
        { error: 'Failed to delete document' },
        { status: deleteResponse.status }
      );
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

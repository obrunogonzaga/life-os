import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const GH_PAT = process.env.GH_PAT;
const SYNC_SECRET = process.env.SYNC_SECRET || 'life-os-sync-2026';
const REPO_OWNER = 'obrunogonzaga';
const REPO_NAME = 'life-os';
const BRAIN_DIR = path.join(process.cwd(), 'brain');

interface GitHubFile {
  path: string;
  sha: string;
}

async function getGitHubFiles(): Promise<Map<string, string>> {
  const files = new Map<string, string>();
  
  async function fetchDir(dirPath: string) {
    const response = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${dirPath}`,
      {
        headers: {
          Authorization: GH_PAT ? `Bearer ${GH_PAT}` : '',
          Accept: 'application/vnd.github.v3+json',
        },
      }
    );

    if (!response.ok) return;

    const items = await response.json();
    for (const item of items) {
      if (item.type === 'file' && item.name.endsWith('.md')) {
        files.set(item.path, item.sha);
      } else if (item.type === 'dir') {
        await fetchDir(item.path);
      }
    }
  }

  await fetchDir('brain');
  return files;
}

function getLocalFiles(): Map<string, string> {
  const files = new Map<string, string>();

  function walkDir(dir: string, prefix: string) {
    if (!fs.existsSync(dir)) return;
    
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(prefix, entry.name);
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else if (entry.name.endsWith('.md')) {
        const content = fs.readFileSync(fullPath, 'utf-8');
        files.set(relativePath, content);
      }
    }
  }

  walkDir(BRAIN_DIR, 'brain');
  return files;
}

async function syncFileToGitHub(filePath: string, content: string, existingSha?: string) {
  const body: Record<string, string> = {
    message: `🔄 Sync: ${filePath}`,
    content: Buffer.from(content).toString('base64'),
    branch: 'main',
  };

  if (existingSha) {
    body.sha = existingSha;
  }

  const response = await fetch(
    `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
    {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${GH_PAT}`,
        'Content-Type': 'application/json',
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify(body),
    }
  );

  return response.ok;
}

async function deleteFileFromGitHub(filePath: string, sha: string) {
  const response = await fetch(
    `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${GH_PAT}`,
        'Content-Type': 'application/json',
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify({
        message: `🗑️ Sync delete: ${filePath}`,
        sha,
        branch: 'main',
      }),
    }
  );

  return response.ok;
}

// POST - Sync local files to GitHub
export async function POST(request: NextRequest) {
  try {
    // Verify secret
    const authHeader = request.headers.get('authorization');
    const providedSecret = authHeader?.replace('Bearer ', '');
    
    if (providedSecret !== SYNC_SECRET) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    if (!GH_PAT) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    const localFiles = getLocalFiles();
    const githubFiles = await getGitHubFiles();

    const results = {
      created: [] as string[],
      updated: [] as string[],
      deleted: [] as string[],
      errors: [] as string[],
    };

    // Sync local files to GitHub
    for (const [filePath, content] of localFiles) {
      const existingSha = githubFiles.get(filePath);
      
      try {
        const success = await syncFileToGitHub(filePath, content, existingSha);
        if (success) {
          if (existingSha) {
            results.updated.push(filePath);
          } else {
            results.created.push(filePath);
          }
        } else {
          results.errors.push(filePath);
        }
      } catch (error) {
        results.errors.push(filePath);
      }
      
      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Delete files from GitHub that don't exist locally
    for (const [filePath, sha] of githubFiles) {
      if (!localFiles.has(filePath)) {
        try {
          const success = await deleteFileFromGitHub(filePath, sha);
          if (success) {
            results.deleted.push(filePath);
          } else {
            results.errors.push(`delete:${filePath}`);
          }
        } catch (error) {
          results.errors.push(`delete:${filePath}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      summary: {
        created: results.created.length,
        updated: results.updated.length,
        deleted: results.deleted.length,
        errors: results.errors.length,
      },
      details: results,
    });
  } catch (error) {
    console.error('Sync error:', error);
    return NextResponse.json(
      { error: 'Sync failed' },
      { status: 500 }
    );
  }
}

// GET - Check sync status
export async function GET() {
  try {
    const localFiles = getLocalFiles();
    
    return NextResponse.json({
      status: 'ok',
      localFiles: localFiles.size,
      githubConfigured: !!GH_PAT,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Status check failed' },
      { status: 500 }
    );
  }
}

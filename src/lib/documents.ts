import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { Document, DocumentMeta, DocumentType } from './types';

const BRAIN_DIR = path.join(process.cwd(), 'brain');

function getAllMarkdownFiles(dir: string, baseDir: string = dir): string[] {
  const files: string[] = [];
  
  if (!fs.existsSync(dir)) {
    return files;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...getAllMarkdownFiles(fullPath, baseDir));
    } else if (entry.name.endsWith('.md')) {
      files.push(fullPath);
    }
  }

  return files;
}

function filePathToSlug(filePath: string): string {
  const relativePath = path.relative(BRAIN_DIR, filePath);
  return relativePath.replace(/\.md$/, '').replace(/\\/g, '/');
}

export function getAllDocuments(): DocumentMeta[] {
  const files = getAllMarkdownFiles(BRAIN_DIR);
  
  const documents = files.map((filePath) => {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const { data } = matter(fileContent);
    const slug = filePathToSlug(filePath);
    const relativePath = path.relative(BRAIN_DIR, filePath);

    return {
      title: data.title || slug,
      date: data.date || '',
      type: (data.type as DocumentType) || 'note',
      tags: data.tags || [],
      slug,
      path: relativePath,
    };
  });

  // Sort by date descending
  return documents.sort((a, b) => {
    if (!a.date) return 1;
    if (!b.date) return -1;
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });
}

export function getDocumentBySlug(slug: string): Document | null {
  const filePath = path.join(BRAIN_DIR, `${slug}.md`);
  
  if (!fs.existsSync(filePath)) {
    return null;
  }

  const fileContent = fs.readFileSync(filePath, 'utf-8');
  const { data, content } = matter(fileContent);
  const relativePath = path.relative(BRAIN_DIR, filePath);

  return {
    title: data.title || slug,
    date: data.date || '',
    type: (data.type as DocumentType) || 'note',
    tags: data.tags || [],
    slug,
    path: relativePath,
    content,
  };
}

export function getDocumentsByType(type: DocumentType): DocumentMeta[] {
  return getAllDocuments().filter((doc) => doc.type === type);
}

export function getDocumentsByTag(tag: string): DocumentMeta[] {
  return getAllDocuments().filter((doc) => doc.tags.includes(tag));
}

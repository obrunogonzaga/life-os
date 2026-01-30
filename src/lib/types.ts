export type DocumentType = 'concept' | 'decision' | 'journal' | 'note' | 'reference';

export interface DocumentMeta {
  title: string;
  date: string;
  type: DocumentType;
  tags: string[];
  slug: string;
  path: string;
}

export interface Document extends DocumentMeta {
  content: string;
}

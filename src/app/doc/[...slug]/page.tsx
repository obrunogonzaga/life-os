import { notFound } from 'next/navigation';
import { getDocumentBySlug, getAllDocuments } from '@/lib/documents';
import { MarkdownViewer } from '@/components/MarkdownViewer';

interface PageProps {
  params: Promise<{ slug: string[] }>;
}

export async function generateStaticParams() {
  const documents = getAllDocuments();
  return documents.map((doc) => ({
    slug: doc.slug.split('/'),
  }));
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const slugPath = slug.join('/');
  const document = getDocumentBySlug(slugPath);
  
  if (!document) {
    return { title: 'Not Found' };
  }

  return {
    title: `${document.title} — life-os`,
    description: `${document.type} - ${document.tags.join(', ')}`,
  };
}

export default async function DocumentPage({ params }: PageProps) {
  const { slug } = await params;
  const slugPath = slug.join('/');
  const document = getDocumentBySlug(slugPath);

  if (!document) {
    notFound();
  }

  return (
    <div className="p-8">
      <MarkdownViewer document={document} />
    </div>
  );
}

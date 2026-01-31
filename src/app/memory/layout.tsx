import { Sidebar } from '@/components/Sidebar';
import { getAllDocuments } from '@/lib/documents';

export default function MemoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const documents = getAllDocuments();

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <Sidebar documents={documents} basePath="/memory" />
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}

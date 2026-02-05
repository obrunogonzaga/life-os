import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';
import { ThemeProvider } from '@/components/ThemeProvider';
import { getAllDocuments } from '@/lib/documents';

// Force dynamic rendering so sidebar updates after deletions
export const dynamic = 'force-dynamic';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'life-os — Second Brain',
  description: 'Your personal knowledge management system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const documents = getAllDocuments();

  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased transition-colors`}>
        <ThemeProvider>
          <div className="flex min-h-screen">
            <Sidebar documents={documents} />
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

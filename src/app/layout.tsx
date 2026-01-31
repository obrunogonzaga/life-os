import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/ThemeProvider';
import { TopNav } from '@/components/TopNav';

// Force dynamic rendering
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
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 antialiased transition-colors`}>
        <ThemeProvider>
          <div className="flex flex-col min-h-screen">
            <TopNav />
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

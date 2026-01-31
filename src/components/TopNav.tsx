'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from './ThemeToggle';

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const navItems: NavItem[] = [
  { href: '/mission', label: 'Mission Control', icon: '🎯' },
  { href: '/tasks', label: 'Tasks', icon: '✅' },
  { href: '/projects', label: 'Projects', icon: '📁' },
  { href: '/memory', label: 'Memory', icon: '🧠' },
  { href: '/captures', label: 'Captures', icon: '📥' },
];

export function TopNav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/memory') {
      return pathname === '/memory' || pathname.startsWith('/memory/') || pathname.startsWith('/doc/');
    }
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <header className="h-14 bg-neutral-100 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between px-4 transition-colors">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 text-neutral-900 dark:text-white font-semibold">
        <span className="text-xl">🧠</span>
        <span className="hidden sm:inline">life-os</span>
      </Link>

      {/* Navigation */}
      <nav className="flex items-center gap-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`
              flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors
              ${isActive(item.href)
                ? 'bg-neutral-200 dark:bg-neutral-800 text-neutral-900 dark:text-white'
                : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/50 dark:hover:bg-neutral-800/50'
              }
            `}
          >
            <span>{item.icon}</span>
            <span className="hidden md:inline">{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Right side */}
      <div className="flex items-center gap-2">
        <ThemeToggle />
      </div>
    </header>
  );
}

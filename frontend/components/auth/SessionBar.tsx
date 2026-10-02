'use client';

import { useEffect, useState } from 'react';
import { History as HistoryIcon, LogOut, ShieldCheck } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { AUTH_CHANGE_EVENT, clearStoredToken, getStoredToken } from '@/lib/api';

export function SessionBar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const syncAuthentication = () => setIsAuthenticated(Boolean(getStoredToken()));
    syncAuthentication();
    window.addEventListener(AUTH_CHANGE_EVENT, syncAuthentication);
    window.addEventListener('storage', syncAuthentication);
    return () => {
      window.removeEventListener(AUTH_CHANGE_EVENT, syncAuthentication);
      window.removeEventListener('storage', syncAuthentication);
    };
  }, []);

  function handleLogout() {
    clearStoredToken();
    router.replace('/');
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="mx-auto flex h-12 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="flex shrink-0 items-center gap-3 font-bold text-slate-100">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/20 text-sm text-blue-300">CG</span>
          <span>CodeGuard AI</span>
        </Link>
        {pathname === '/' && (
          <nav aria-label="Page sections" className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
            <Link href="#features" className="hover:text-white">Features</Link>
            <Link href="#how-it-works" className="hover:text-white">How it works</Link>
            <Link href="#security" className="hover:text-white">Security</Link>
            <Link href="#faq" className="hover:text-white">FAQ</Link>
          </nav>
        )}
        {isAuthenticated ? (
          <div className="flex items-center gap-2">
            <Link
              href="/history"
              aria-current={pathname === '/history' ? 'page' : undefined}
              className={`inline-flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm transition-colors ${pathname === '/history' ? 'border-blue-400/40 bg-blue-500/10 text-blue-200' : 'border-slate-700 text-slate-300 hover:border-slate-500 hover:bg-slate-800 hover:text-white'}`}
            >
              <HistoryIcon className="h-4 w-4" />
              History
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex items-center gap-2 rounded-md border border-slate-700 px-3 py-1.5 text-sm text-slate-300 transition-colors hover:border-slate-500 hover:bg-slate-800 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
              Log out
            </button>
          </div>
        ) : (
          <nav aria-label="Account" className="flex items-center gap-2">
            <Link href="/login" className="rounded-md px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800">Log in</Link>
            <Link href="/register" className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-500">Register</Link>
          </nav>
        )}
      </div>
    </header>
  );
}

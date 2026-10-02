import './globals.css';
import type { Metadata } from 'next';
import { SessionBar } from '@/components/auth/SessionBar';

export const metadata: Metadata = {
  title: 'CodeGuard AI',
  description: 'AI-driven code review and security analysis platform.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <SessionBar />
        {children}
      </body>
    </html>
  );
}

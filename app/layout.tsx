import './global.css';
import { RootProvider } from 'fumadocs-ui/provider';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';
import type { Metadata } from 'next';

import { Navbar } from '@/components/navbar';

const inter = Inter({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: '数源智能',
  icons: {
    icon: '/favicon1.svg',
  },
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex-1">
          <RootProvider>{children}</RootProvider>
        </div>
      </body>
    </html>
  );
}

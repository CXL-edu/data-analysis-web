import './global.css';
import { RootProvider } from 'fumadocs-ui/provider';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';

import { Navbar } from './components/navbar';

const inter = Inter({
  subsets: ['latin'],
});

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex-1 pt-16">
          <RootProvider>{children}</RootProvider>
        </div>
      </body>
    </html>
  );
}

import { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-neutral-950">
      <Header />
      <main className="pt-16 pb-20 md:pb-8">
        {children}
      </main>
    </div>
  );
}

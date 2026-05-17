import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'FactoryOS — Governed Autonomous SDLC Factory',
  description: 'Enterprise AI command center for governed autonomous software development',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0b0f] text-zinc-100 antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}

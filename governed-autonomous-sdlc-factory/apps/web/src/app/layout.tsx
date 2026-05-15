import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Cognitive Cortex — Governed Autonomous SDLC Factory',
  description: 'Cognitive Command Center for autonomous software engineering',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl" className="dark">
      <body className="bg-zinc-950 text-zinc-100 font-mono antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}

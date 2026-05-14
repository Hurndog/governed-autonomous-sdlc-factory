'use client';

interface CenterPanelProps {
  children: React.ReactNode;
}

export function CenterPanel({ children }: CenterPanelProps) {
  return (
    <main className="flex-1 bg-[var(--bg-primary)] overflow-auto">
      {children}
    </main>
  );
}

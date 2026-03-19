'use client';

import dynamic from 'next/dynamic';

const KanbanBoard = dynamic(
  () => import('@/components/kanban/KanbanBoard').then(mod => ({ default: mod.KanbanBoard })),
  { ssr: false, loading: () => <div>Loading...</div> }
);

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <main className="h-screen">
        <KanbanBoard />
      </main>
    </div>
  );
}

'use client';

import dynamic from 'next/dynamic';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { KanbanProvider } from '@/lib/context/KanbanContext';

const KanbanBoard = dynamic(
  () => import('@/components/kanban/KanbanBoard').then(mod => ({ default: mod.KanbanBoard })),
  { ssr: false, loading: () => <div>Loading...</div> }
);

const ChatSidebar = dynamic(
  () => import('@/components/chat/ChatSidebar').then(mod => ({ default: mod.ChatSidebar })),
  { ssr: false }
);

export default function Home() {
  return (
    <AuthGuard>
      <KanbanProvider>
        <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
          <main className="h-screen">
            <KanbanBoard />
            <ChatSidebar />
          </main>
        </div>
      </KanbanProvider>
    </AuthGuard>
  );
}

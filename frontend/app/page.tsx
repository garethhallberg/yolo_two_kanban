import { KanbanBoard } from '@/components/kanban/KanbanBoard';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <main className="h-screen">
        <KanbanBoard />
      </main>
    </div>
  );
}

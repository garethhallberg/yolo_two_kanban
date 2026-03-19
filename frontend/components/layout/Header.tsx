'use client';

import { useRouter } from 'next/navigation';
import { authService } from '@/lib/services/auth';
import { Button } from '@/components/ui/Button';
import { LogOut } from 'lucide-react';

export function Header() {
  const router = useRouter();

  const handleLogout = () => {
    authService.clearToken();
    router.push('/login');
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-border-light dark:border-border-dark px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-dark-navy dark:text-white">
          Project Kanban
        </h1>
        <Button
          variant="outline"
          onClick={handleLogout}
          className="flex items-center gap-2"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </header>
  );
}
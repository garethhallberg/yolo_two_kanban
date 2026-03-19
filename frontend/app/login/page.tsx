'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService, LoginCredentials } from '@/lib/services/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('[LoginPage] ========== FORM SUBMIT START ==========');
    console.log('[LoginPage] Form submit event triggered');
    e.preventDefault();
    console.log('[LoginPage] Prevented default form submission');
    setError('');
    console.log('[LoginPage] Error state cleared');
    setLoading(true);
    console.log('[LoginPage] Loading state set to true');

    try {
      console.log('[LoginPage] Creating credentials object');
      const credentials: LoginCredentials = { username, password };
      console.log('[LoginPage] Credentials created:', { username, password: '***' });
      
      console.log('[LoginPage] Calling authService.login()');
      const response = await authService.login(credentials);
      console.log('[LoginPage] Login response received:', response);
      
      console.log('[LoginPage] Setting token in localStorage');
      authService.setToken(response.access_token);
      console.log('[LoginPage] Token set, redirecting to home page');
      router.push('/');
      console.log('[LoginPage] Redirect initiated');
    } catch (err) {
      console.error('[LoginPage] ========== LOGIN FAILED ==========');
      console.error('[LoginPage] Login failed with error:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
      console.log('[LoginPage] Error state set');
    } finally {
      console.log('[LoginPage] Setting loading state to false');
      setLoading(false);
      console.log('[LoginPage] Loading state updated');
    }
    console.log('[LoginPage] ========== FORM SUBMIT END ==========');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-950">
      <Card className="w-full max-w-md p-6">
        <h1 className="text-2xl font-bold text-center mb-6 text-dark-navy dark:text-white">
          Project Kanban
        </h1>
        <h2 className="text-xl font-semibold text-center mb-4 text-gray-900 dark:text-gray-100">
          Sign In
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-600 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Username
            </label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => {
                console.log('[LoginPage] Username input changed:', e.target.value);
                setUsername(e.target.value);
                console.log('[LoginPage] Username state updated');
              }}
              required
              disabled={loading}
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                console.log('[LoginPage] Password input changed (length):', e.target.value.length);
                setPassword(e.target.value);
                console.log('[LoginPage] Password state updated');
              }}
              required
              disabled={loading}
              placeholder="Enter your password"
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>Demo credentials: user / password</p>
        </div>
      </Card>
    </div>
  );
}
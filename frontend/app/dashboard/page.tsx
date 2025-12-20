'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Button } from '@/components/ui';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const user = typeof window !== 'undefined' 
    ? JSON.parse(localStorage.getItem('user') || '{}')
    : {};

  return (
    <main className="min-h-screen p-8 bg-bg-primary">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>

        <Card>
          <h2 className="text-2xl font-semibold text-text-primary mb-4">
            Welcome, {user.full_name || 'User'}!
          </h2>
          <p className="text-text-secondary mb-6">
            Phone: {user.phone_number}
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button 
              variant="primary" 
              size="lg"
              onClick={() => router.push('/passenger/request-ride')}
            >
              🚕 Request Ride
            </Button>
            <Button 
              variant="secondary" 
              size="lg"
              onClick={() => router.push('/rides/history')}
            >
              📋 Ride History
            </Button>
          </div>
        </Card>
      </div>
    </main>
  );
}

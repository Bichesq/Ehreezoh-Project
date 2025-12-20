'use client';

import { Button, Card } from '@/components/ui';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [showDemo, setShowDemo] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-2xl w-full">
        {/* Logo/Title */}
        <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-primary via-primary-light to-primary bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-4 duration-700">
          Ehreezoh
        </h1>
        
        <p className="text-text-secondary text-xl mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
          Ride with Ease
        </p>
        
        {/* Main Card */}
        <Card className="max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-text-primary mb-3">
                Welcome to Ehreezoh
              </h2>
              <p className="text-text-secondary">
                Your ride-hailing platform for Cameroon. Fast, reliable, and affordable transportation at your fingertips.
              </p>
            </div>
            
            <div className="flex flex-col gap-3">
              <Button 
                variant="primary" 
                size="lg" 
                className="w-full"
                onClick={() => router.push('/login')}
              >
                Get Started
              </Button>
              
              <Button 
                variant="outline" 
                size="lg" 
                className="w-full"
              >
                Learn More
              </Button>
            </div>
            
            {showDemo && (
              <div className="pt-4 border-t border-white/10 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <p className="text-sm text-text-muted">
                  🎉 UI Components are working!
                </p>
              </div>
            )}
          </div>
        </Card>
        
        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
          <Card glass={false} className="text-center">
            <div className="text-3xl mb-2">🏍️</div>
            <h3 className="font-semibold text-text-primary mb-1">Moto Rides</h3>
            <p className="text-sm text-text-muted">Quick and affordable</p>
          </Card>
          
          <Card glass={false} className="text-center">
            <div className="text-3xl mb-2">🚗</div>
            <h3 className="font-semibold text-text-primary mb-1">Car Rides</h3>
            <p className="text-sm text-text-muted">Comfortable trips</p>
          </Card>
          
          <Card glass={false} className="text-center">
            <div className="text-3xl mb-2">⚡</div>
            <h3 className="font-semibold text-text-primary mb-1">Real-time</h3>
            <p className="text-sm text-text-muted">Live tracking</p>
          </Card>
        </div>
      </div>
    </main>
  );
}

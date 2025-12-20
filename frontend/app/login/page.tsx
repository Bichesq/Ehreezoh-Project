'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Input, Card } from '@/components/ui';
import { authService } from '@/services/auth';

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<'phone' | 'otp' | 'register'>('phone');
  const [phoneNumber, setPhoneNumber] = useState('+237');
  const [otp, setOtp] = useState('');
  const [fullName, setFullName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Initialize reCAPTCHA
    authService.initRecaptcha();
    
    return () => {
      authService.cleanup();
    };
  }, []);

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await authService.sendOTP(phoneNumber);
      setStep('otp');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const firebaseToken = await authService.verifyOTP(otp);
      
      // Try to login first
      try {
        const { access_token, user } = await authService.login(firebaseToken);
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        router.push('/dashboard');
      } catch (loginError: any) {
        // If login fails (user not found), go to registration
        if (loginError.message.includes('not found')) {
          setStep('register');
          // Store firebase token temporarily
          sessionStorage.setItem('firebase_token', firebaseToken);
        } else {
          throw loginError;
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const firebaseToken = sessionStorage.getItem('firebase_token');
      if (!firebaseToken) {
        throw new Error('Session expired. Please try again.');
      }

      const { access_token, user } = await authService.register(firebaseToken, fullName);
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      sessionStorage.removeItem('firebase_token');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-bg-primary">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary-light bg-clip-text text-transparent">
            Ehreezoh
          </h1>
          <p className="text-text-secondary">Ride with Ease</p>
        </div>

        <Card>
          {/* Phone Number Step */}
          {step === 'phone' && (
            <form onSubmit={handleSendOTP} className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold text-text-primary mb-2">
                  Welcome
                </h2>
                <p className="text-text-secondary">
                  Enter your phone number to get started
                </p>
              </div>

              <Input
                type="tel"
                label="Phone Number"
                placeholder="+237 6XX XXX XXX"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                error={error}
                required
                icon={
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                }
              />

              <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={isLoading}>
                Continue
              </Button>

              <p className="text-xs text-text-muted text-center">
                By continuing, you agree to our Terms & Privacy Policy
              </p>
            </form>
          )}

          {/* OTP Verification Step */}
          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div>
                <button
                  type="button"
                  onClick={() => setStep('phone')}
                  className="text-primary hover:text-primary-light mb-4 flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-2xl font-semibold text-text-primary mb-2">
                  Enter Code
                </h2>
                <p className="text-text-secondary">
                  Sent to {phoneNumber}
                </p>
              </div>

              <Input
                type="text"
                label="Verification Code"
                placeholder="6-digit code"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                error={error}
                required
                maxLength={6}
                icon={
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                }
              />

              <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={isLoading}>
                Verify
              </Button>

              <button
                type="button"
                onClick={handleSendOTP}
                className="text-sm text-primary hover:text-primary-light w-full text-center"
              >
                Didn't receive code? Resend
              </button>
            </form>
          )}

          {/* Registration Step */}
          {step === 'register' && (
            <form onSubmit={handleRegister} className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold text-text-primary mb-2">
                  Complete Profile
                </h2>
                <p className="text-text-secondary">
                  Tell us your name to get started
                </p>
              </div>

              <Input
                type="text"
                label="Full Name"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                error={error}
                required
                icon={
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                }
              />

              <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={isLoading}>
                Complete Registration
              </Button>
            </form>
          )}
        </Card>

        {/* reCAPTCHA container */}
        <div id="recaptcha-container"></div>
      </div>
    </main>
  );
}

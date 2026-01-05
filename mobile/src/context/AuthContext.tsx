import React, { createContext, useState, useEffect, useContext } from 'react';
import { useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { authService, User } from '../services/auth';
import axios from 'axios';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (phone: string) => Promise<void>;
  signUp: (phone: string, name: string, email: string) => Promise<void>;
  signOut: () => Promise<void>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

// This hook can be used to access the user info.
export function useAuth() {
  return useContext(AuthContext);
}

// This hook will protect the route access based on user authentication.
function useProtectedRoute(user: User | null, isLoading: boolean) {
  const segments = useSegments();
  const router = useRouter();
  const navigationState = useRootNavigationState();

  useEffect(() => {
    if (isLoading) return;
    if (!navigationState?.key) return;

    // Safety check for segments
    const inAuthGroup = segments[0] === '(auth)';

    if (!user && !inAuthGroup) {
      // Redirect to the sign-in page.
      router.replace('/(auth)/login');
    } else if (user && inAuthGroup) {
      // Redirect away from the sign-in page.
      router.replace('/');
    }
  }, [user, segments, navigationState?.key, isLoading]);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for persisted user
    const checkAuth = async () => {
      try {
        const token = await authService.getToken();
        const savedUser = await authService.getUser();
        
        // Always set Axios default header first if token exists
        if (token) {
           axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }

        if (token && savedUser) {
          setUser(savedUser); // Optimistic update
          
          // Background fetch to get latest status (e.g. is_driver change)
          try {
              const freshUser = await authService.getProfile();
              if (freshUser) {
                  setUser(freshUser);
                  await authService.saveToken(token, freshUser); // Update cache
              }
          } catch (err) {
              console.warn('Background profile refresh failed', err);
          }
        }
      } catch (e) {
        console.error('Auth check failed:', e);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  useProtectedRoute(user, isLoading);

  const signIn = async (phone: string) => {
    try {
      const data = await authService.login(phone);
      setUser(data.user);
      await authService.saveToken(data.access_token, data.user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
    } catch (error) {
      throw error;
    }
  };

  const signUp = async (phone: string, name: string, email: string) => {
    try {
      const data = await authService.register(phone, name, email);
      setUser(data.user);
      await authService.saveToken(data.access_token, data.user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
    } catch (error) {
      throw error;
    }
  };

  const signOut = async () => {
    await authService.logout();
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        signIn,
        signUp,
        signOut,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

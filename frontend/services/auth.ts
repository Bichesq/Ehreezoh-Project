import {
  signInWithPhoneNumber,
  RecaptchaVerifier,
  ConfirmationResult,
  PhoneAuthProvider,
  signInWithCredential,
} from 'firebase/auth';
import { auth } from './firebase';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class AuthService {
  private recaptchaVerifier: RecaptchaVerifier | null = null;
  private confirmationResult: ConfirmationResult | null = null;

  /**
   * Initialize reCAPTCHA verifier
   */
  initRecaptcha(containerId: string = 'recaptcha-container'): void {
    if (typeof window === 'undefined') return;

    // Check if container element exists
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`reCAPTCHA container with id "${containerId}" not found`);
      return;
    }

    // Clean up existing verifier if any
    if (this.recaptchaVerifier) {
      this.recaptchaVerifier.clear();
    }

    this.recaptchaVerifier = new RecaptchaVerifier(auth, containerId, {
      size: 'invisible',
      callback: () => {
        console.log('reCAPTCHA solved');
      },
      'expired-callback': () => {
        console.log('reCAPTCHA expired');
      },
    });
  }

  /**
   * Send OTP to phone number
   */
  async sendOTP(phoneNumber: string): Promise<void> {
    if (!this.recaptchaVerifier) {
      throw new Error('reCAPTCHA not initialized');
    }

    try {
      this.confirmationResult = await signInWithPhoneNumber(
        auth,
        phoneNumber,
        this.recaptchaVerifier
      );
      console.log('OTP sent successfully');
    } catch (error: any) {
      console.error('Error sending OTP:', error);
      throw new Error(error.message || 'Failed to send OTP');
    }
  }

  /**
   * Verify OTP code
   */
  async verifyOTP(code: string): Promise<string> {
    if (!this.confirmationResult) {
      throw new Error('No confirmation result available');
    }

    try {
      const result = await this.confirmationResult.confirm(code);
      const user = result.user;
      
      // Get Firebase ID token
      const idToken = await user.getIdToken();
      
      return idToken;
    } catch (error: any) {
      console.error('Error verifying OTP:', error);
      throw new Error(error.message || 'Invalid OTP code');
    }
  }

  /**
   * Register user with backend
   */
  async register(firebaseToken: string, fullName: string): Promise<{ access_token: string; user: any }> {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        firebase_token: firebaseToken,
        full_name: fullName,
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error);
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  /**
   * Login user with backend
   */
  async login(firebaseToken: string): Promise<{ access_token: string; user: any }> {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        firebase_token: firebaseToken,
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(accessToken: string): Promise<any> {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Get profile error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get profile');
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await auth.signOut();
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    } catch (error: any) {
      console.error('Logout error:', error);
      throw new Error('Logout failed');
    }
  }

  /**
   * Clean up reCAPTCHA
   */
  cleanup(): void {
    if (this.recaptchaVerifier) {
      this.recaptchaVerifier.clear();
      this.recaptchaVerifier = null;
    }
    this.confirmationResult = null;
  }
}

export const authService = new AuthService();

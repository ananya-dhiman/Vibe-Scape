import React, { createContext, useContext, useEffect, useState } from 'react';
import type { User } from 'firebase/auth';
import authService from './authService';

const API_BASE = 'http://localhost:5000';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<{ success: boolean; user?: User; error?: string }>;
  signInWithEmail: (email: string, password: string) => Promise<{ success: boolean; user?: User; error?: string }>;
  signUpWithEmail: (email: string, password: string) => Promise<{ success: boolean; user?: User; error?: string }>;
  signOut: () => Promise<{ success: boolean; error?: string }>;
  resetPassword: (email: string) => Promise<{ success: boolean; error?: string }>;
  getUserToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = authService.onAuthStateChange((user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Helper to ensure user exists in MongoDB after Google sign-in
  const ensureUserInBackend = async (firebaseUser: User | null) => {
    if (!firebaseUser) return;
    const token = await firebaseUser.getIdToken();
    await fetch(`${API_BASE}/api/users`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: firebaseUser.displayName,
        email: firebaseUser.email,
        photo_url: firebaseUser.photoURL,
        email_verified: firebaseUser.emailVerified,
      }),
    });
  };

  const signInWithGoogle = async () => {
    const result = await authService.signInWithGoogle();
    if (result.success && result.user) {
      await ensureUserInBackend(result.user);
    }
    return result;
  };

  const signInWithEmail = async (email: string, password: string) => {
    const result = await authService.signInWithEmail(email, password);
    if (result.success && result.user) {
      await ensureUserInBackend(result.user);
    }
    return result;
  };

  const signUpWithEmail = async (email: string, password: string) => {
    const result = await authService.signUpWithEmail(email, password);
    if (result.success && result.user) {
      await ensureUserInBackend(result.user);
    }
    return result;
  };

  const signOut = async () => {
    return await authService.signOut();
  };

  const resetPassword = async (email: string) => {
    return await authService.resetPassword(email);
  };

  const getUserToken = async () => {
    return await authService.getUserToken();
  };

  const value: AuthContextType = {
    user,
    loading,
    signInWithGoogle,
    signInWithEmail,
    signUpWithEmail,
    signOut,
    resetPassword,
    getUserToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 
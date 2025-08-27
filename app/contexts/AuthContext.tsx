'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: number;
  username: string;
  email: string;
  isEmailVerified: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  sendRegistrationCode: (username: string, email: string, password: string) => Promise<void>;
  verifyRegistrationCode: (email: string, code: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!token;

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user_data');
    
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        let errorMessage = 'Login failed';
        try {
          const error = await response.json();
          if (response.status === 401) {
            errorMessage = error.message || '邮箱或密码错误，请检查后重试';
          } else if (response.status === 404) {
            errorMessage = '用户不存在，请先注册账号';
          } else {
            errorMessage = error.message || `Login failed (${response.status})`;
          }
        } catch (e) {
          if (response.status === 401) {
            errorMessage = '邮箱或密码错误，请检查后重试';
          } else if (response.status === 404) {
            errorMessage = '用户不存在，请先注册账号';
          } else {
            errorMessage = `Login failed: ${response.status} ${response.statusText}`;
          }
        }
        console.error('Login error:', response.status, response.statusText);
        throw new Error(errorMessage);
      }

      const data = await response.json();
      const { user: userData, access_token } = data;

      setUser(userData);
      setToken(access_token);
      
      // Save to localStorage
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('user_data', JSON.stringify(userData));
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string): Promise<void> => {
    // 保留原有方法以兼容
    await sendRegistrationCode(username, email, password);
  };

  const sendRegistrationCode = async (username: string, email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password, confirm_password: password }),
      });

      if (!response.ok) {
        let errorMessage = 'Registration failed';
        try {
          const error = await response.json();
          errorMessage = error.error || `Registration failed (${response.status})`;
        } catch (e) {
          errorMessage = `Registration failed: ${response.status} ${response.statusText}`;
        }
        console.error('Registration error:', response.status, response.statusText);
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Verification code sent:', data.message);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyRegistrationCode = async (email: string, code: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-registration`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, code }),
      });

      if (!response.ok) {
        let errorMessage = 'Verification failed';
        try {
          const error = await response.json();
          errorMessage = error.error || `Verification failed (${response.status})`;
        } catch (e) {
          errorMessage = `Verification failed: ${response.status} ${response.statusText}`;
        }
        console.error('Verification error:', response.status, response.statusText);
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Registration verified:', data.message);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    // Trigger new chat event to clear any existing session data
    window.dispatchEvent(new Event('newChat'));
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    sendRegistrationCode,
    verifyRegistrationCode,
    logout,
    isLoading,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
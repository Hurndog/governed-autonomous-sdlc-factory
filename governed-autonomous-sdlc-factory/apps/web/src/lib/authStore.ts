'use client';

import { create } from 'zustand';
import { api } from '@/lib/api';

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  role: string;
  is_active: boolean;
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkSession: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  loading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/login`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || 'Login failed');
      }
      const data = await res.json();
      set({
        user: data.user,
        token: data.access_token,
        loading: false,
        error: null,
      });
    } catch (err) {
      set({
        user: null,
        token: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Login failed',
      });
    }
  },

  logout: () => {
    set({ user: null, token: null, error: null });
  },

  checkSession: async () => {
    const { token } = get();
    if (!token) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/me`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!res.ok) {
        set({ user: null, token: null });
        return;
      }
      const data = await res.json();
      set({ user: data });
    } catch {
      set({ user: null, token: null });
    }
  },

  clearError: () => set({ error: null }),
}));

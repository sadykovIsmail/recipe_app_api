'use client';
import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/lib/api/auth';
import { getRefreshToken, getAccessToken } from '@/lib/api/client';
import type { LoginPayload, RegisterPayload } from '@/types';

export function useAuth() {
  const router = useRouter();
  const qc = useQueryClient();

  const isAuthenticated = typeof window !== 'undefined' && !!getAccessToken();

  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.getMe,
    enabled: isAuthenticated,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me'] });
      router.push('/recipes');
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: () => {
      router.push('/login');
    },
  });

  const logout = useCallback(async () => {
    const refresh = getRefreshToken() ?? '';
    await authApi.logout(refresh);
    qc.clear();
    router.push('/login');
  }, [qc, router]);

  return {
    user,
    isLoading,
    isAuthenticated,
    login: loginMutation,
    register: registerMutation,
    logout,
  };
}

import { apiClient, setTokens, clearTokens } from './client';
import type { User, LoginPayload, RegisterPayload } from '@/types';

export const authApi = {
  login: async (payload: LoginPayload) => {
    const { data } = await apiClient.post('/api/v1/user/jwt/login/', payload);
    setTokens(data.access, data.refresh);
    return data as { access: string; refresh: string };
  },

  register: async (payload: RegisterPayload) => {
    const { data } = await apiClient.post('/api/v1/user/create/', payload);
    return data as User;
  },

  logout: async (refreshToken: string) => {
    try {
      await apiClient.post('/api/v1/user/logout/', { refresh: refreshToken });
    } finally {
      clearTokens();
    }
  },

  getMe: async () => {
    const { data } = await apiClient.get('/api/v1/user/me/');
    return data as User;
  },

  updateMe: async (payload: Partial<Pick<User, 'name'> & { password: string }>) => {
    const { data } = await apiClient.patch('/api/v1/user/me/', payload);
    return data as User;
  },
};

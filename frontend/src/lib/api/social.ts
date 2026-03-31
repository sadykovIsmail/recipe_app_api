import { apiClient } from './client';
import type {
  UserProfile, Notification, UnreadCount,
  PaginatedResponse,
} from '@/types';

const USER_BASE = '/api/v1/user';

export const socialApi = {
  // ── User search & profiles ─────────────────────────────────────────────────

  searchUsers: async (q: string, page = 1) => {
    const { data } = await apiClient.get<PaginatedResponse<UserProfile>>(
      `${USER_BASE}/search/`,
      { params: { q, page } }
    );
    return data;
  },

  getProfile: async (id: number) => {
    const { data } = await apiClient.get<UserProfile>(`${USER_BASE}/${id}/profile/`);
    return data;
  },

  getMyProfile: async () => {
    const { data } = await apiClient.get<UserProfile>(`${USER_BASE}/me/profile/`);
    return data;
  },

  updateMyProfile: async (payload: Partial<Pick<UserProfile, 'bio' | 'website' | 'location'>>) => {
    const { data } = await apiClient.patch<UserProfile>(`${USER_BASE}/me/profile/`, payload);
    return data;
  },

  uploadAvatar: async (file: File) => {
    const form = new FormData();
    form.append('avatar', file);
    const { data } = await apiClient.post<UserProfile>(
      `${USER_BASE}/me/avatar/`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return data;
  },

  // ── Follow / Unfollow ──────────────────────────────────────────────────────

  follow: async (userId: number) => {
    await apiClient.post(`${USER_BASE}/${userId}/follow/`);
  },

  unfollow: async (userId: number) => {
    await apiClient.delete(`${USER_BASE}/${userId}/follow/`);
  },

  listFollowers: async (userId: number, page = 1) => {
    const { data } = await apiClient.get<PaginatedResponse<UserProfile>>(
      `${USER_BASE}/${userId}/followers/`,
      { params: { page } }
    );
    return data;
  },

  listFollowing: async (userId: number, page = 1) => {
    const { data } = await apiClient.get<PaginatedResponse<UserProfile>>(
      `${USER_BASE}/${userId}/following/`,
      { params: { page } }
    );
    return data;
  },

  // ── Notifications ─────────────────────────────────────────────────────────

  listNotifications: async (page = 1) => {
    const { data } = await apiClient.get<PaginatedResponse<Notification>>(
      `${USER_BASE}/notifications/`,
      { params: { page } }
    );
    return data;
  },

  markAllRead: async () => {
    await apiClient.post(`${USER_BASE}/notifications/mark-read/`);
  },

  getUnreadCount: async (): Promise<UnreadCount> => {
    const { data } = await apiClient.get<UnreadCount>(`${USER_BASE}/notifications/unread-count/`);
    return data;
  },
};

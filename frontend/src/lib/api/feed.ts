import { apiClient } from './client';
import type { Recipe, RecipeComment, PaginatedResponse } from '@/types';

const RECIPE_BASE = '/api/v1/recipe';

export const feedApi = {
  // ── Feed & Discover ───────────────────────────────────────────────────────

  getFeed: async (params?: { page?: number; search?: string; tags?: string; ordering?: string }) => {
    const { data } = await apiClient.get<PaginatedResponse<Recipe>>(
      `${RECIPE_BASE}/feed/`,
      { params }
    );
    return data;
  },

  getDiscover: async (params?: { page?: number; search?: string; tags?: string; ordering?: string }) => {
    const { data } = await apiClient.get<PaginatedResponse<Recipe>>(
      `${RECIPE_BASE}/discover/`,
      { params }
    );
    return data;
  },

  // ── Likes ─────────────────────────────────────────────────────────────────

  likeRecipe: async (recipeId: number) => {
    const { data } = await apiClient.post<{ liked: boolean; likes_count: number }>(
      `${RECIPE_BASE}/recipes/${recipeId}/like/`
    );
    return data;
  },

  unlikeRecipe: async (recipeId: number) => {
    const { data } = await apiClient.delete<{ liked: boolean; likes_count: number }>(
      `${RECIPE_BASE}/recipes/${recipeId}/like/`
    );
    return data;
  },

  // ── Comments ──────────────────────────────────────────────────────────────

  listComments: async (recipeId: number, page = 1) => {
    const { data } = await apiClient.get<PaginatedResponse<RecipeComment>>(
      `${RECIPE_BASE}/recipes/${recipeId}/comments/`,
      { params: { page } }
    );
    return data;
  },

  postComment: async (recipeId: number, text: string) => {
    const { data } = await apiClient.post<RecipeComment>(
      `${RECIPE_BASE}/recipes/${recipeId}/comments/`,
      { text }
    );
    return data;
  },

  deleteComment: async (recipeId: number, commentId: number) => {
    await apiClient.delete(`${RECIPE_BASE}/recipes/${recipeId}/comments/${commentId}/`);
  },
};

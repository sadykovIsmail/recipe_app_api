import { apiClient } from './client';
import type {
  Recipe, RecipeDetail, RecipePayload,
  Tag, Ingredient, PaginatedResponse,
} from '@/types';

const BASE = '/api/v1/recipe';

export const recipesApi = {
  // ── Recipes ───────────────────────────────────────────────────────────────

  list: async (params?: {
    page?: number;
    search?: string;
    tags?: string;
    ingredients?: string;
    ordering?: string;
  }) => {
    const { data } = await apiClient.get<PaginatedResponse<Recipe>>(`${BASE}/recipes/`, { params });
    return data;
  },

  get: async (id: number) => {
    const { data } = await apiClient.get<RecipeDetail>(`${BASE}/recipes/${id}/public/`);
    return data;
  },

  create: async (payload: RecipePayload) => {
    const { data } = await apiClient.post<RecipeDetail>(`${BASE}/recipes/`, payload);
    return data;
  },

  update: async (id: number, payload: Partial<RecipePayload>) => {
    const { data } = await apiClient.patch<RecipeDetail>(`${BASE}/recipes/${id}/`, payload);
    return data;
  },

  delete: async (id: number) => {
    await apiClient.delete(`${BASE}/recipes/${id}/`);
  },

  uploadImage: async (id: number, file: File) => {
    const form = new FormData();
    form.append('image', file);
    const { data } = await apiClient.post<{ id: number; image: string }>(
      `${BASE}/recipes/${id}/upload-image/`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return data;
  },

  // ── Tags ─────────────────────────────────────────────────────────────────

  listTags: async (params?: { search?: string; assigned_only?: 0 | 1 }) => {
    const { data } = await apiClient.get<PaginatedResponse<Tag>>(`${BASE}/tags/`, { params });
    return data;
  },

  deleteTag: async (id: number) => {
    await apiClient.delete(`${BASE}/tags/${id}/`);
  },

  // ── Ingredients ───────────────────────────────────────────────────────────

  listIngredients: async (params?: { search?: string; assigned_only?: 0 | 1 }) => {
    const { data } = await apiClient.get<PaginatedResponse<Ingredient>>(
      `${BASE}/ingredients/`,
      { params }
    );
    return data;
  },

  deleteIngredient: async (id: number) => {
    await apiClient.delete(`${BASE}/ingredients/${id}/`);
  },
};

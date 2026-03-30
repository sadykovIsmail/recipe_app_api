'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recipesApi } from '@/lib/api/recipes';
import type { RecipePayload } from '@/types';

interface ListParams {
  page?: number;
  search?: string;
  tags?: string;
  ingredients?: string;
  ordering?: string;
}

export function useRecipes(params?: ListParams) {
  return useQuery({
    queryKey: ['recipes', params],
    queryFn: () => recipesApi.list(params),
  });
}

export function useRecipe(id: number) {
  return useQuery({
    queryKey: ['recipe', id],
    queryFn: () => recipesApi.get(id),
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RecipePayload) => recipesApi.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipes'] }),
  });
}

export function useUpdateRecipe(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<RecipePayload>) => recipesApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['recipes'] });
      qc.invalidateQueries({ queryKey: ['recipe', id] });
    },
  });
}

export function useDeleteRecipe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => recipesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipes'] }),
  });
}

export function useUploadImage(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => recipesApi.uploadImage(id, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipe', id] }),
  });
}

export function useTags(params?: { search?: string; assigned_only?: 0 | 1 }) {
  return useQuery({
    queryKey: ['tags', params],
    queryFn: () => recipesApi.listTags(params),
  });
}

export function useIngredients(params?: { search?: string; assigned_only?: 0 | 1 }) {
  return useQuery({
    queryKey: ['ingredients', params],
    queryFn: () => recipesApi.listIngredients(params),
  });
}

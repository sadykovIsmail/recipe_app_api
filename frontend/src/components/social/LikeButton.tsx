'use client';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Heart } from 'lucide-react';
import { clsx } from 'clsx';
import { feedApi } from '@/lib/api/feed';

interface LikeButtonProps {
  recipeId: number;
  isLiked: boolean;
  likesCount: number;
  queryKey?: unknown[];
}

export function LikeButton({ recipeId, isLiked, likesCount, queryKey }: LikeButtonProps) {
  const qc = useQueryClient();
  const [animating, setAnimating] = useState(false);

  const mutation = useMutation({
    mutationFn: isLiked
      ? () => feedApi.unlikeRecipe(recipeId)
      : () => feedApi.likeRecipe(recipeId),
    onMutate: async () => {
      if (queryKey) await qc.cancelQueries({ queryKey });
      setAnimating(true);
      setTimeout(() => setAnimating(false), 300);
    },
    onSuccess: () => {
      if (queryKey) qc.invalidateQueries({ queryKey });
    },
  });

  return (
    <button
      onClick={(e) => { e.preventDefault(); mutation.mutate(); }}
      disabled={mutation.isPending}
      className={clsx(
        'flex items-center gap-1 text-sm transition-colors',
        isLiked ? 'text-red-500' : 'text-gray-400 hover:text-red-400'
      )}
      aria-label={isLiked ? 'Unlike' : 'Like'}
    >
      <Heart
        className={clsx(
          'h-4 w-4 transition-transform',
          isLiked && 'fill-current',
          animating && 'scale-125'
        )}
      />
      <span>{likesCount}</span>
    </button>
  );
}

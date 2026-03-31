'use client';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { socialApi } from '@/lib/api/social';
import { Button } from '@/components/ui/Button';

interface FollowButtonProps {
  userId: number;
  isFollowing: boolean;
  onToggle?: (nowFollowing: boolean) => void;
}

export function FollowButton({ userId, isFollowing, onToggle }: FollowButtonProps) {
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: isFollowing
      ? () => socialApi.unfollow(userId)
      : () => socialApi.follow(userId),
    // Optimistic update
    onMutate: async () => {
      await qc.cancelQueries({ queryKey: ['profile', userId] });
      const prev = qc.getQueryData(['profile', userId]);
      qc.setQueryData(['profile', userId], (old: { is_following: boolean; followers_count: number } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          is_following: !isFollowing,
          followers_count: old.followers_count + (isFollowing ? -1 : 1),
        };
      });
      return { prev };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev !== undefined) {
        qc.setQueryData(['profile', userId], ctx.prev);
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['profile', userId] });
      onToggle?.(!isFollowing);
    },
  });

  return (
    <Button
      variant={isFollowing ? 'secondary' : 'primary'}
      size="sm"
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
    >
      {mutation.isPending ? '...' : isFollowing ? 'Unfollow' : 'Follow'}
    </Button>
  );
}

'use client';
import { useState } from 'react';
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Trash2, MessageCircle, Send } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { feedApi } from '@/lib/api/feed';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import type { RecipeComment } from '@/types';

interface CommentThreadProps {
  recipeId: number;
  currentUserId?: number;
  recipeOwnerId?: number;
}

export function CommentThread({ recipeId, currentUserId, recipeOwnerId }: CommentThreadProps) {
  const qc = useQueryClient();
  const [text, setText] = useState('');
  const [open, setOpen] = useState(false);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useInfiniteQuery({
    queryKey: ['comments', recipeId],
    queryFn: ({ pageParam = 1 }) => feedApi.listComments(recipeId, pageParam as number),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
    enabled: open,
  });

  const postMutation = useMutation({
    mutationFn: () => feedApi.postComment(recipeId, text.trim()),
    onSuccess: () => {
      setText('');
      qc.invalidateQueries({ queryKey: ['comments', recipeId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (commentId: number) => feedApi.deleteComment(recipeId, commentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['comments', recipeId] });
    },
  });

  const comments = data?.pages.flatMap((p) => p.results) ?? [];
  const totalCount = data?.pages[0]?.count ?? 0;

  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 transition-colors"
      >
        <MessageCircle className="h-4 w-4" />
        <span>{totalCount > 0 ? totalCount : ''} {open ? 'Hide' : 'Comments'}</span>
      </button>

      {open && (
        <div className="mt-3 space-y-3">
          {/* Post comment */}
          {currentUserId && (
            <form
              onSubmit={(e) => { e.preventDefault(); if (text.trim()) postMutation.mutate(); }}
              className="flex gap-2"
            >
              <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Add a comment…"
                maxLength={1000}
                className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <Button
                type="submit"
                size="sm"
                variant="primary"
                disabled={!text.trim() || postMutation.isPending}
              >
                <Send className="h-3.5 w-3.5" />
              </Button>
            </form>
          )}

          {/* Comment list */}
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex gap-2 items-start">
                  <Skeleton className="h-7 w-7 rounded-full" />
                  <Skeleton className="h-10 flex-1" />
                </div>
              ))}
            </div>
          ) : comments.length === 0 ? (
            <p className="text-sm text-gray-400">No comments yet.</p>
          ) : (
            <div className="space-y-2">
              {comments.map((c: RecipeComment) => (
                <div key={c.id} className="flex items-start gap-2 group">
                  <Avatar src={c.user.avatar} name={c.user.name} size="xs" />
                  <div className="flex-1 bg-gray-50 rounded-lg px-3 py-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-gray-700">{c.user.name}</span>
                      <span className="text-xs text-gray-400">
                        {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-0.5">{c.text}</p>
                  </div>
                  {(c.user.id === currentUserId || recipeOwnerId === currentUserId) && (
                    <button
                      onClick={() => deleteMutation.mutate(c.id)}
                      className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition-all"
                      aria-label="Delete comment"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              ))}
              {hasNextPage && (
                <button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="text-xs text-brand-600 hover:underline"
                >
                  {isFetchingNextPage ? 'Loading…' : 'Load more comments'}
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

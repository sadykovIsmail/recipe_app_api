'use client';
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { Bell, UserPlus, Heart, MessageCircle, CheckCheck } from 'lucide-react';
import Link from 'next/link';
import { clsx } from 'clsx';
import { socialApi } from '@/lib/api/social';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Notification } from '@/types';

const kindIcon = {
  new_follower:    <UserPlus className="h-4 w-4 text-brand-500" />,
  recipe_like:     <Heart className="h-4 w-4 text-red-400" />,
  recipe_comment:  <MessageCircle className="h-4 w-4 text-green-500" />,
};

const kindText = (n: Notification) => {
  switch (n.kind) {
    case 'new_follower':   return 'started following you.';
    case 'recipe_like':    return `liked your recipe "${n.recipe?.title}".`;
    case 'recipe_comment': return `commented on "${n.recipe?.title}".`;
  }
};

export default function NotificationsPage() {
  const qc = useQueryClient();

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useInfiniteQuery({
    queryKey: ['notifications'],
    queryFn: ({ pageParam = 1 }) => socialApi.listNotifications(pageParam as number),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
  });

  const markRead = useMutation({
    mutationFn: socialApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
      qc.invalidateQueries({ queryKey: ['notifications', 'unread-count'] });
    },
  });

  const notifications = data?.pages.flatMap((p) => p.results) ?? [];
  const hasUnread = notifications.some((n) => !n.is_read);

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Bell className="h-6 w-6 text-gray-700" />
          <h1 className="text-xl font-bold text-gray-900">Notifications</h1>
        </div>
        {hasUnread && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => markRead.mutate()}
            disabled={markRead.isPending}
          >
            <CheckCheck className="h-4 w-4 mr-1" />
            Mark all read
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 p-3">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-16">
          <Bell className="h-12 w-12 text-gray-200 mx-auto mb-3" />
          <p className="text-gray-400">No notifications yet.</p>
        </div>
      ) : (
        <div className="space-y-1">
          {notifications.map((n: Notification) => (
            <div
              key={n.id}
              className={clsx(
                'flex items-start gap-3 p-3 rounded-xl transition-colors',
                n.is_read ? 'bg-white' : 'bg-brand-50'
              )}
            >
              <Link href={`/profile/${n.actor.id}`}>
                <Avatar src={n.actor.avatar} name={n.actor.name} size="sm" />
              </Link>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700">
                  <Link
                    href={`/profile/${n.actor.id}`}
                    className="font-semibold hover:text-brand-600"
                  >
                    {n.actor.name}
                  </Link>
                  {' '}
                  {kindText(n)}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                </p>
              </div>
              <span className="mt-0.5 flex-shrink-0">{kindIcon[n.kind]}</span>
            </div>
          ))}

          {hasNextPage && (
            <div className="text-center pt-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
              >
                {isFetchingNextPage ? 'Loading…' : 'Load more'}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

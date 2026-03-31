'use client';
import Link from 'next/link';
import { Bell } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { socialApi } from '@/lib/api/social';

export function NotificationBell() {
  const { data } = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: socialApi.getUnreadCount,
    refetchInterval: 30_000, // poll every 30s
    staleTime: 20_000,
  });

  const count = data?.unread_count ?? 0;

  return (
    <Link href="/notifications" className="relative inline-flex" aria-label="Notifications">
      <Bell className="h-5 w-5 text-gray-500 hover:text-gray-800 transition-colors" />
      {count > 0 && (
        <span className="absolute -top-1.5 -right-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-bold px-0.5">
          {count > 99 ? '99+' : count}
        </span>
      )}
    </Link>
  );
}

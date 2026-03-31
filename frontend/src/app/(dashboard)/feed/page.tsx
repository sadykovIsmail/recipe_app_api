'use client';
import { useRef, useCallback } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Users } from 'lucide-react';
import { feedApi } from '@/lib/api/feed';
import { useAuth } from '@/lib/hooks/useAuth';
import { RecipeCardSocial } from '@/components/social/RecipeCardSocial';
import { RecipeCardSkeleton } from '@/components/ui/Skeleton';

export default function FeedPage() {
  const { user } = useAuth();
  const observerRef = useRef<IntersectionObserver | null>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: ({ pageParam = 1 }) => feedApi.getFeed({ page: pageParam as number }),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
  });

  const sentinelRef = useCallback((node: HTMLDivElement | null) => {
    if (observerRef.current) observerRef.current.disconnect();
    if (!node) return;
    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    });
    observerRef.current.observe(node);
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  const recipes = data?.pages.flatMap((p) => p.results) ?? [];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Feed</h1>

      {isLoading ? (
        <div className="space-y-6">
          {[...Array(3)].map((_, i) => <RecipeCardSkeleton key={i} />)}
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-16">
          <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700">Your feed is empty</h2>
          <p className="text-gray-500 mt-1 mb-6">Follow chefs to see their latest recipes here.</p>
          <Link
            href="/discover"
            className="inline-flex items-center gap-2 bg-brand-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
          >
            Discover Recipes
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {recipes.map((recipe) => (
            <RecipeCardSocial
              key={recipe.id}
              recipe={recipe}
              currentUserId={user?.id}
              queryKey={['feed']}
            />
          ))}
          <div ref={sentinelRef} className="h-4" />
          {isFetchingNextPage && (
            <div className="space-y-6">
              {[...Array(2)].map((_, i) => <RecipeCardSkeleton key={i} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

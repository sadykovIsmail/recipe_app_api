'use client';
import { useRef, useCallback, useState } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { Compass, Search } from 'lucide-react';
import { feedApi } from '@/lib/api/feed';
import { useAuth } from '@/lib/hooks/useAuth';
import { RecipeCardSocial } from '@/components/social/RecipeCardSocial';
import { RecipeCardSkeleton } from '@/components/ui/Skeleton';

export default function DiscoverPage() {
  const { user } = useAuth();
  const [search, setSearch] = useState('');
  const [appliedSearch, setAppliedSearch] = useState('');
  const observerRef = useRef<IntersectionObserver | null>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['discover', appliedSearch],
    queryFn: ({ pageParam = 1 }) =>
      feedApi.getDiscover({ page: pageParam as number, search: appliedSearch || undefined }),
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Compass className="h-7 w-7 text-brand-600" />
        <h1 className="text-2xl font-bold text-gray-900">Discover</h1>
      </div>

      {/* Search */}
      <form
        onSubmit={(e) => { e.preventDefault(); setAppliedSearch(search); }}
        className="relative mb-8"
      >
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search trending recipes…"
          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
        />
      </form>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => <RecipeCardSkeleton key={i} />)}
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-16">
          <Compass className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No trending recipes found.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map((recipe) => (
              <RecipeCardSocial
                key={recipe.id}
                recipe={recipe}
                currentUserId={user?.id}
                queryKey={['discover', appliedSearch]}
              />
            ))}
          </div>
          <div ref={sentinelRef} className="h-4 mt-4" />
          {isFetchingNextPage && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
              {[...Array(3)].map((_, i) => <RecipeCardSkeleton key={i} />)}
            </div>
          )}
        </>
      )}
    </div>
  );
}

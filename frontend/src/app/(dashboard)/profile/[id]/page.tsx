'use client';
import { useState } from 'react';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { useRef, useCallback } from 'react';
import { MapPin, Link as LinkIcon, Users } from 'lucide-react';
import { socialApi } from '@/lib/api/social';
import { recipesApi } from '@/lib/api/recipes';
import { useAuth } from '@/lib/hooks/useAuth';
import { Avatar } from '@/components/ui/Avatar';
import { FollowButton } from '@/components/social/FollowButton';
import { RecipeCardSocial } from '@/components/social/RecipeCardSocial';
import { RecipeCardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import { UserCard } from '@/components/social/UserCard';

type Tab = 'recipes' | 'followers' | 'following';

export default function ProfilePage({ params }: { params: { id: string } }) {
  const { id } = params;
  const userId = parseInt(id, 10);
  const { user: me } = useAuth();
  const [tab, setTab] = useState<Tab>('recipes');
  const observerRef = useRef<IntersectionObserver | null>(null);

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile', userId],
    queryFn: () => socialApi.getProfile(userId),
  });

  const isOwnProfile = me?.id === userId;

  // Recipes (paginated)
  const {
    data: recipesData,
    fetchNextPage: fetchMoreRecipes,
    hasNextPage: hasMoreRecipes,
    isFetchingNextPage: fetchingMoreRecipes,
  } = useInfiniteQuery({
    queryKey: ['profile-recipes', userId],
    queryFn: ({ pageParam = 1 }) => recipesApi.list({ page: pageParam as number }),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
    enabled: tab === 'recipes' && isOwnProfile, // only own recipes via authenticated endpoint
  });

  // Followers
  const {
    data: followersData,
    fetchNextPage: fetchMoreFollowers,
    hasNextPage: hasMoreFollowers,
    isFetchingNextPage: fetchingMoreFollowers,
  } = useInfiniteQuery({
    queryKey: ['followers', userId],
    queryFn: ({ pageParam = 1 }) => socialApi.listFollowers(userId, pageParam as number),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
    enabled: tab === 'followers',
  });

  // Following
  const {
    data: followingData,
    fetchNextPage: fetchMoreFollowing,
    hasNextPage: hasMoreFollowing,
    isFetchingNextPage: fetchingMoreFollowing,
  } = useInfiniteQuery({
    queryKey: ['following', userId],
    queryFn: ({ pageParam = 1 }) => socialApi.listFollowing(userId, pageParam as number),
    getNextPageParam: (last, pages) => last.next ? pages.length + 1 : undefined,
    initialPageParam: 1,
    enabled: tab === 'following',
  });

  const sentinelRef = useCallback((node: HTMLDivElement | null) => {
    if (observerRef.current) observerRef.current.disconnect();
    if (!node) return;
    observerRef.current = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) return;
      if (tab === 'recipes' && hasMoreRecipes && !fetchingMoreRecipes) fetchMoreRecipes();
      if (tab === 'followers' && hasMoreFollowers && !fetchingMoreFollowers) fetchMoreFollowers();
      if (tab === 'following' && hasMoreFollowing && !fetchingMoreFollowing) fetchMoreFollowing();
    });
    observerRef.current.observe(node);
  }, [tab, hasMoreRecipes, fetchingMoreRecipes, fetchMoreRecipes,
      hasMoreFollowers, fetchingMoreFollowers, fetchMoreFollowers,
      hasMoreFollowing, fetchingMoreFollowing, fetchMoreFollowing]);

  const recipes = recipesData?.pages.flatMap((p) => p.results) ?? [];
  const followers = followersData?.pages.flatMap((p) => p.results) ?? [];
  const following = followingData?.pages.flatMap((p) => p.results) ?? [];

  if (profileLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-4">
        <div className="flex items-center gap-4">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-60" />
          </div>
        </div>
      </div>
    );
  }

  if (!profile) return <div className="text-center py-20 text-gray-500">User not found.</div>;

  const tabs: { id: Tab; label: string; count: number }[] = [
    { id: 'recipes', label: 'Recipes', count: profile.recipes_count },
    { id: 'followers', label: 'Followers', count: profile.followers_count },
    { id: 'following', label: 'Following', count: profile.following_count },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      {/* Profile header */}
      <div className="flex items-start gap-5 mb-8">
        <Avatar src={profile.avatar} name={profile.name} size="xl" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900">{profile.name}</h1>
            {!isOwnProfile && me && (
              <FollowButton userId={userId} isFollowing={profile.is_following} />
            )}
          </div>
          {profile.bio && <p className="text-gray-600 mt-1 text-sm">{profile.bio}</p>}
          <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-500">
            {profile.location && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {profile.location}
              </span>
            )}
            {profile.website && (
              <a
                href={profile.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-brand-600 hover:underline"
              >
                <LinkIcon className="h-3.5 w-3.5" />
                {profile.website.replace(/^https?:\/\//, '')}
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
            <span className="ml-1.5 text-xs text-gray-400">({t.count})</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'recipes' && (
        isOwnProfile ? (
          recipes.length === 0 ? (
            <p className="text-gray-400 text-center py-10">No recipes yet.</p>
          ) : (
            <div className="space-y-4">
              {recipes.map((r) => (
                <RecipeCardSocial
                  key={r.id}
                  recipe={r}
                  currentUserId={me?.id}
                  owned
                  queryKey={['profile-recipes', userId]}
                />
              ))}
            </div>
          )
        ) : (
          <div className="text-center py-10 text-gray-400 flex flex-col items-center gap-2">
            <Users className="h-10 w-10" />
            <p>Follow {profile.name} to see their recipes in your feed.</p>
          </div>
        )
      )}

      {tab === 'followers' && (
        followers.length === 0 ? (
          <p className="text-gray-400 text-center py-10">No followers yet.</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {followers.map((u) => (
              <UserCard key={u.id} user={u} currentUserId={me?.id} />
            ))}
          </div>
        )
      )}

      {tab === 'following' && (
        following.length === 0 ? (
          <p className="text-gray-400 text-center py-10">Not following anyone yet.</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {following.map((u) => (
              <UserCard key={u.id} user={u} currentUserId={me?.id} />
            ))}
          </div>
        )
      )}

      {/* Infinite scroll sentinel */}
      <div ref={sentinelRef} className="h-4 mt-4" />
      {(fetchingMoreRecipes || fetchingMoreFollowers || fetchingMoreFollowing) && (
        <div className="space-y-4 mt-4">
          <RecipeCardSkeleton />
        </div>
      )}
    </div>
  );
}

'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Users } from 'lucide-react';
import { socialApi } from '@/lib/api/social';
import { useAuth } from '@/lib/hooks/useAuth';
import { UserCard } from '@/components/social/UserCard';
import { UserCardSkeleton } from '@/components/ui/Skeleton';

export default function PeoplePage() {
  const { user } = useAuth();
  const [search, setSearch] = useState('');
  const [applied, setApplied] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['people', applied],
    queryFn: () => socialApi.searchUsers(applied),
  });

  const users = (data?.results ?? []).filter((u) => u.id !== user?.id);

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-6">
        <Users className="h-6 w-6 text-gray-700" />
        <h1 className="text-xl font-bold text-gray-900">People</h1>
      </div>

      {/* Search */}
      <form
        onSubmit={(e) => { e.preventDefault(); setApplied(search); }}
        className="relative mb-6"
      >
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          value={search}
          onChange={(e) => { setSearch(e.target.value); if (!e.target.value) setApplied(''); }}
          placeholder="Search chefs by name…"
          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
        />
      </form>

      {/* List */}
      {isLoading ? (
        <div className="divide-y divide-gray-100">
          {[...Array(5)].map((_, i) => <UserCardSkeleton key={i} />)}
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-16">
          <Users className="h-12 w-12 text-gray-200 mx-auto mb-3" />
          <p className="text-gray-400">
            {applied ? `No chefs found for "${applied}".` : 'No other chefs yet.'}
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          {users.map((u) => (
            <UserCard key={u.id} user={u} currentUserId={user?.id} />
          ))}
        </div>
      )}
    </div>
  );
}

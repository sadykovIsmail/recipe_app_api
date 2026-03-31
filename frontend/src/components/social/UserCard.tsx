import Link from 'next/link';
import { Avatar } from '@/components/ui/Avatar';
import { FollowButton } from '@/components/social/FollowButton';
import type { UserProfile } from '@/types';

interface UserCardProps {
  user: UserProfile;
  currentUserId?: number;
}

export function UserCard({ user, currentUserId }: UserCardProps) {
  return (
    <div className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors">
      <Link href={`/profile/${user.id}`} className="flex-shrink-0">
        <Avatar src={user.avatar} name={user.name} size="md" />
      </Link>

      <div className="flex-1 min-w-0">
        <Link href={`/profile/${user.id}`} className="block font-medium text-gray-900 truncate hover:text-brand-600">
          {user.name}
        </Link>
        {user.bio && (
          <p className="text-sm text-gray-500 truncate">{user.bio}</p>
        )}
        <div className="flex gap-3 text-xs text-gray-400 mt-0.5">
          <span><strong className="text-gray-600">{user.followers_count}</strong> followers</span>
          <span><strong className="text-gray-600">{user.recipes_count}</strong> recipes</span>
        </div>
      </div>

      {currentUserId && currentUserId !== user.id && (
        <FollowButton userId={user.id} isFollowing={user.is_following} />
      )}
    </div>
  );
}

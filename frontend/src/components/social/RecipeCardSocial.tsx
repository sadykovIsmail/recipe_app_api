import Link from 'next/link';
import Image from 'next/image';
import { Clock, DollarSign, ExternalLink, MessageCircle } from 'lucide-react';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LikeButton } from '@/components/social/LikeButton';
import { CommentThread } from '@/components/social/CommentThread';
import type { Recipe } from '@/types';

interface RecipeCardSocialProps {
  recipe: Recipe;
  currentUserId?: number;
  /** If true, shows Edit/Delete actions (own recipe view) */
  owned?: boolean;
  onDelete?: (id: number) => void;
  /** TanStack Query key to invalidate on like toggle */
  queryKey?: unknown[];
}

export function RecipeCardSocial({
  recipe,
  currentUserId,
  owned,
  onDelete,
  queryKey,
}: RecipeCardSocialProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      {/* Image */}
      <Link href={`/recipes/${recipe.id}`}>
        <div className="relative h-48 bg-gray-100">
          {recipe.image ? (
            <Image
              src={recipe.image}
              alt={recipe.title}
              fill
              className="object-cover"
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-300">
              <svg className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>
      </Link>

      <div className="p-4">
        {/* Author */}
        {recipe.author && (
          <Link href={`/profile/${recipe.author.id}`} className="flex items-center gap-2 mb-2 group">
            <Avatar src={recipe.author.avatar} name={recipe.author.name} size="xs" />
            <span className="text-xs text-gray-500 group-hover:text-brand-600 transition-colors">
              {recipe.author.name}
            </span>
          </Link>
        )}

        {/* Title */}
        <Link href={`/recipes/${recipe.id}`}>
          <h3 className="font-semibold text-gray-900 text-lg leading-snug line-clamp-1 hover:text-brand-600">
            {recipe.title}
          </h3>
        </Link>

        <div className="flex items-center gap-4 mt-1.5 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {recipe.time_minutes} min
          </span>
          <span className="flex items-center gap-1">
            <DollarSign className="h-3.5 w-3.5" />
            {recipe.price}
          </span>
        </div>

        {/* Tags */}
        {recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {recipe.tags.slice(0, 4).map((tag) => (
              <Badge key={tag.id} label={tag.name} variant="tag" />
            ))}
          </div>
        )}

        {/* Social bar */}
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
          <LikeButton
            recipeId={recipe.id}
            isLiked={recipe.is_liked}
            likesCount={recipe.likes_count}
            queryKey={queryKey}
          />
          <span className="flex items-center gap-1 text-sm text-gray-400">
            <MessageCircle className="h-4 w-4" />
            {recipe.comments_count}
          </span>
          {recipe.link && (
            <a
              href={recipe.link}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-auto text-gray-300 hover:text-brand-600"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>

        {/* Comments */}
        <div className="mt-3">
          <CommentThread
            recipeId={recipe.id}
            currentUserId={currentUserId}
            recipeOwnerId={recipe.author?.id}
          />
        </div>

        {/* Owner actions */}
        {owned && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
            <Link href={`/recipes/${recipe.id}/edit`} className="flex-1">
              <Button variant="secondary" size="sm" className="w-full">Edit</Button>
            </Link>
            {onDelete && (
              <Button variant="danger" size="sm" onClick={() => onDelete(recipe.id)}>
                Delete
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

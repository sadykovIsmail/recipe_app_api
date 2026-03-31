'use client';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeft, Clock, DollarSign, ExternalLink, Pencil, Trash2, Upload } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { LikeButton } from '@/components/social/LikeButton';
import { CommentThread } from '@/components/social/CommentThread';
import { Skeleton } from '@/components/ui/Skeleton';
import { useRecipe, useDeleteRecipe, useUploadImage } from '@/lib/hooks/useRecipes';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRef, ChangeEvent } from 'react';

export default function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const recipeId = Number(id);

  const { data: recipe, isLoading } = useRecipe(recipeId);
  const deleteMutation = useDeleteRecipe();
  const uploadMutation = useUploadImage(recipeId);
  const fileInputRef   = useRef<HTMLInputElement>(null);

  const isOwner = user?.id === recipe?.author?.id;

  const handleDelete = async () => {
    if (!confirm('Delete this recipe?')) return;
    await deleteMutation.mutateAsync(recipeId);
    router.push('/recipes');
  };

  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
  };

  if (isLoading) return (
    <div className="max-w-3xl mx-auto space-y-4">
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-72 rounded-2xl" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  );

  if (!recipe) return (
    <div className="text-center py-20 text-gray-400">
      <p className="text-lg font-medium">Recipe not found.</p>
      <Link href="/recipes" className="text-brand-600 text-sm mt-2 inline-block hover:underline">
        Back to recipes
      </Link>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back + owner actions */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-800 text-sm"
        >
          <ArrowLeft className="h-4 w-4" /> Back
        </button>
        {isOwner && (
          <div className="flex items-center gap-2">
            <Link href={`/recipes/${id}/edit`}>
              <Button variant="secondary" size="sm">
                <Pencil className="h-4 w-4 mr-1" /> Edit
              </Button>
            </Link>
            <Button variant="danger" size="sm" loading={deleteMutation.isPending} onClick={handleDelete}>
              <Trash2 className="h-4 w-4 mr-1" /> Delete
            </Button>
          </div>
        )}
      </div>

      {/* Image */}
      <div className={`relative h-72 bg-gray-100 rounded-2xl overflow-hidden mb-6 ${isOwner ? 'group' : ''}`}>
        {recipe.image ? (
          <Image src={recipe.image} alt={recipe.title} fill className="object-cover" sizes="768px" />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-300">
            <svg className="h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        {isOwner && (
          <>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="absolute inset-0 bg-black/0 group-hover:bg-black/30 flex items-center justify-center transition-all"
            >
              <span className="opacity-0 group-hover:opacity-100 text-white flex items-center gap-2 font-medium transition-opacity">
                <Upload className="h-5 w-5" />
                {uploadMutation.isPending ? 'Uploading…' : 'Change photo'}
              </span>
            </button>
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
          </>
        )}
      </div>

      {/* Author */}
      {recipe.author && (
        <Link href={`/profile/${recipe.author.id}`} className="flex items-center gap-2.5 mb-4 group w-fit">
          <Avatar src={recipe.author.avatar} name={recipe.author.name} size="sm" />
          <span className="text-sm text-gray-500 group-hover:text-brand-600 transition-colors">
            {recipe.author.name}
          </span>
        </Link>
      )}

      {/* Title */}
      <h1 className="text-3xl font-bold text-gray-900">{recipe.title}</h1>

      {/* Meta */}
      <div className="flex items-center gap-6 mt-3 text-gray-500">
        <span className="flex items-center gap-1.5 text-sm">
          <Clock className="h-4 w-4" /> {recipe.time_minutes} min
        </span>
        <span className="flex items-center gap-1.5 text-sm">
          <DollarSign className="h-4 w-4" /> ${recipe.price}
        </span>
        {recipe.link && (
          <a href={recipe.link} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-brand-600 hover:underline">
            <ExternalLink className="h-4 w-4" /> Source
          </a>
        )}
        {/* Like button */}
        <div className="ml-auto">
          <LikeButton
            recipeId={recipe.id}
            isLiked={recipe.is_liked}
            likesCount={recipe.likes_count}
            queryKey={['recipe', recipeId]}
          />
        </div>
      </div>

      {/* Description */}
      {recipe.description && (
        <p className="mt-5 text-gray-700 leading-relaxed">{recipe.description}</p>
      )}

      {/* Tags */}
      {recipe.tags.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Tags</h2>
          <div className="flex flex-wrap gap-2">
            {recipe.tags.map((t) => <Badge key={t.id} label={t.name} variant="tag" />)}
          </div>
        </div>
      )}

      {/* Ingredients */}
      {recipe.ingredients.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Ingredients</h2>
          <ul className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {recipe.ingredients.map((ing) => (
              <li key={ing.id} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-500 flex-shrink-0" />
                {ing.name}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Comments */}
      <div className="mt-8 pt-6 border-t border-gray-100">
        <CommentThread
          recipeId={recipe.id}
          currentUserId={user?.id}
          recipeOwnerId={recipe.author?.id}
        />
      </div>
    </div>
  );
}

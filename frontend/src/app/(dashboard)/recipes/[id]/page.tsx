'use client';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeft, Clock, DollarSign, ExternalLink, Pencil, Trash2, Upload } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRecipe, useDeleteRecipe, useUploadImage } from '@/lib/hooks/useRecipes';
import { useRef, ChangeEvent } from 'react';

export default function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const recipeId = Number(id);

  const { data: recipe, isLoading } = useRecipe(recipeId);
  const deleteMutation  = useDeleteRecipe();
  const uploadMutation  = useUploadImage(recipeId);
  const fileInputRef    = useRef<HTMLInputElement>(null);

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
    <div className="max-w-3xl mx-auto animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-1/2" />
      <div className="h-64 bg-gray-200 rounded-2xl" />
      <div className="h-4 bg-gray-200 rounded w-3/4" />
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
      {/* Back + actions */}
      <div className="flex items-center justify-between mb-6">
        <Link href="/recipes" className="flex items-center gap-1.5 text-gray-500 hover:text-gray-800 text-sm">
          <ArrowLeft className="h-4 w-4" /> All recipes
        </Link>
        <div className="flex items-center gap-2">
          <Link href={`/recipes/${id}/edit`}>
            <Button variant="secondary" size="sm"><Pencil className="h-4 w-4 mr-1" /> Edit</Button>
          </Link>
          <Button variant="danger" size="sm" loading={deleteMutation.isPending} onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-1" /> Delete
          </Button>
        </div>
      </div>

      {/* Image */}
      <div className="relative h-72 bg-gray-100 rounded-2xl overflow-hidden mb-6 group">
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
        {/* Upload overlay */}
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
      </div>

      {/* Title + meta */}
      <h1 className="text-3xl font-bold text-gray-900">{recipe.title}</h1>

      <div className="flex items-center gap-6 mt-3 text-gray-500">
        <span className="flex items-center gap-1.5 text-sm">
          <Clock className="h-4 w-4" /> {recipe.time_minutes} minutes
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
    </div>
  );
}

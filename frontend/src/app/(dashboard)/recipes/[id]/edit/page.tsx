'use client';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { RecipeForm } from '@/components/recipes/RecipeForm';
import { useRecipe, useUpdateRecipe } from '@/lib/hooks/useRecipes';
import type { RecipePayload } from '@/types';

export default function EditRecipePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const recipeId = Number(id);

  const { data: recipe, isLoading } = useRecipe(recipeId);
  const updateMutation = useUpdateRecipe(recipeId);

  const handleSubmit = async (data: RecipePayload) => {
    await updateMutation.mutateAsync(data);
    router.push(`/recipes/${id}`);
  };

  if (isLoading) return (
    <div className="max-w-2xl mx-auto animate-pulse space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-10 bg-gray-200 rounded-lg" />
      ))}
    </div>
  );

  if (!recipe) return (
    <div className="text-center py-20 text-gray-400">Recipe not found.</div>
  );

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link href={`/recipes/${id}`} className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Recipe</h1>
      </div>

      {updateMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-5 text-sm text-red-700">
          Failed to update. Please try again.
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 p-6">
        <RecipeForm
          defaultValues={recipe}
          onSubmit={handleSubmit}
          isLoading={updateMutation.isPending}
          submitLabel="Save Changes"
        />
      </div>
    </div>
  );
}

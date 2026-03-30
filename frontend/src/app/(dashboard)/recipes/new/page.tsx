'use client';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { RecipeForm } from '@/components/recipes/RecipeForm';
import { useCreateRecipe } from '@/lib/hooks/useRecipes';
import type { RecipePayload } from '@/types';

export default function NewRecipePage() {
  const router = useRouter();
  const createMutation = useCreateRecipe();

  const handleSubmit = async (data: RecipePayload) => {
    const recipe = await createMutation.mutateAsync(data);
    router.push(`/recipes/${recipe.id}`);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/recipes" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">New Recipe</h1>
      </div>

      {createMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-5 text-sm text-red-700">
          Failed to create recipe. Please try again.
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 p-6">
        <RecipeForm
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending}
          submitLabel="Create Recipe"
        />
      </div>
    </div>
  );
}

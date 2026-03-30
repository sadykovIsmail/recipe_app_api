'use client';
import { useState } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { RecipeCard } from '@/components/recipes/RecipeCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useRecipes, useDeleteRecipe } from '@/lib/hooks/useRecipes';
import type { Metadata } from 'next';

export default function RecipesPage() {
  const [search, setSearch]   = useState('');
  const [page, setPage]       = useState(1);
  const [ordering, setOrdering] = useState('-id');

  const { data, isLoading } = useRecipes({ search, page, ordering });
  const deleteMutation = useDeleteRecipe();

  const handleDelete = (id: number) => {
    if (confirm('Delete this recipe?')) deleteMutation.mutate(id);
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Recipes</h1>
          {data && (
            <p className="text-sm text-gray-500 mt-0.5">{data.count} recipe{data.count !== 1 ? 's' : ''}</p>
          )}
        </div>
      </div>

      {/* Search + filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          <input
            type="search"
            placeholder="Search recipes…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="block w-full pl-9 pr-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <select
          value={ordering}
          onChange={(e) => setOrdering(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="-id">Newest first</option>
          <option value="title">A → Z</option>
          <option value="-title">Z → A</option>
          <option value="price">Cheapest first</option>
          <option value="time_minutes">Quickest first</option>
        </select>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl h-72 animate-pulse border border-gray-200" />
          ))}
        </div>
      ) : !data?.results.length ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg font-medium">No recipes found</p>
          <p className="text-sm mt-1">{search ? 'Try a different search.' : 'Create your first recipe!'}</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.results.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} onDelete={handleDelete} />
            ))}
          </div>

          {/* Pagination */}
          {(data.next || data.previous) && (
            <div className="flex items-center justify-center gap-3 mt-8">
              <Button
                variant="secondary"
                disabled={!data.previous}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-500">Page {page}</span>
              <Button
                variant="secondary"
                disabled={!data.next}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

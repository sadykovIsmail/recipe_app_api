import Link from 'next/link';
import Image from 'next/image';
import { Clock, DollarSign, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { Recipe } from '@/types';

interface RecipeCardProps {
  recipe: Recipe;
  onDelete?: (id: number) => void;
}

export function RecipeCard({ recipe, onDelete }: RecipeCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      {/* Image */}
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

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 text-lg leading-snug line-clamp-1">
          {recipe.title}
        </h3>

        <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
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
          <div className="flex flex-wrap gap-1.5 mt-3">
            {recipe.tags.slice(0, 4).map((tag) => (
              <Badge key={tag.id} label={tag.name} variant="tag" />
            ))}
          </div>
        )}

        {/* Ingredients preview */}
        {recipe.ingredients.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {recipe.ingredients.slice(0, 3).map((ing) => (
              <Badge key={ing.id} label={ing.name} variant="ingredient" />
            ))}
            {recipe.ingredients.length > 3 && (
              <Badge label={`+${recipe.ingredients.length - 3} more`} variant="ingredient" />
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 mt-4">
          <Link href={`/recipes/${recipe.id}`} className="flex-1">
            <Button variant="primary" size="sm" className="w-full">View</Button>
          </Link>
          <Link href={`/recipes/${recipe.id}/edit`}>
            <Button variant="secondary" size="sm">Edit</Button>
          </Link>
          {recipe.link && (
            <a href={recipe.link} target="_blank" rel="noopener noreferrer">
              <Button variant="ghost" size="sm" aria-label="External link">
                <ExternalLink className="h-4 w-4" />
              </Button>
            </a>
          )}
          {onDelete && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => onDelete(recipe.id)}
            >
              Del
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

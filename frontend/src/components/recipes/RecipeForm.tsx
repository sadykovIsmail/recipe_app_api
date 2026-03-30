'use client';
import { useState, KeyboardEvent } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { RecipeDetail, RecipePayload } from '@/types';

const schema = z.object({
  title:        z.string().min(1, 'Title is required').max(255),
  description:  z.string().optional(),
  time_minutes: z.coerce.number().int().min(1, 'Must be at least 1 minute'),
  price:        z.string().regex(/^\d+(\.\d{1,2})?$/, 'Invalid price (e.g. 12.50)'),
  link:         z.string().url('Must be a valid URL').or(z.literal('')).optional(),
});

type FormValues = z.infer<typeof schema>;

interface RecipeFormProps {
  defaultValues?: Partial<RecipeDetail>;
  onSubmit: (data: RecipePayload) => Promise<void>;
  isLoading?: boolean;
  submitLabel?: string;
}

export function RecipeForm({
  defaultValues,
  onSubmit,
  isLoading,
  submitLabel = 'Save Recipe',
}: RecipeFormProps) {
  const [tags, setTags] = useState<string[]>(defaultValues?.tags?.map((t) => t.name) ?? []);
  const [ingredients, setIngredients] = useState<string[]>(
    defaultValues?.ingredients?.map((i) => i.name) ?? []
  );
  const [tagInput, setTagInput]               = useState('');
  const [ingredientInput, setIngredientInput] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title:        defaultValues?.title ?? '',
      description:  defaultValues?.description ?? '',
      time_minutes: defaultValues?.time_minutes ?? 30,
      price:        defaultValues?.price ?? '',
      link:         defaultValues?.link ?? '',
    },
  });

  const addTag = () => {
    const v = tagInput.trim();
    if (v && !tags.includes(v)) setTags((prev) => [...prev, v]);
    setTagInput('');
  };

  const addIngredient = () => {
    const v = ingredientInput.trim();
    if (v && !ingredients.includes(v)) setIngredients((prev) => [...prev, v]);
    setIngredientInput('');
  };

  const handleKey = (e: KeyboardEvent, add: () => void) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      add();
    }
  };

  const handleFormSubmit = async (values: FormValues) => {
    await onSubmit({
      ...values,
      tags:        tags.map((name) => ({ name })),
      ingredients: ingredients.map((name) => ({ name })),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
      <Input
        label="Title *"
        id="title"
        placeholder="e.g. Spaghetti Carbonara"
        error={errors.title?.message}
        {...register('title')}
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          rows={3}
          placeholder="Brief description of the recipe…"
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          {...register('description')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Time (minutes) *"
          id="time_minutes"
          type="number"
          min={1}
          error={errors.time_minutes?.message}
          {...register('time_minutes')}
        />
        <Input
          label="Price *"
          id="price"
          placeholder="12.50"
          error={errors.price?.message}
          {...register('price')}
        />
      </div>

      <Input
        label="Reference link"
        id="link"
        type="url"
        placeholder="https://example.com/recipe"
        error={errors.link?.message}
        {...register('link')}
      />

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
        <div className="flex gap-2">
          <Input
            id="tag-input"
            placeholder="Type and press Enter"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => handleKey(e, addTag)}
          />
          <Button type="button" variant="secondary" size="md" onClick={addTag}>Add</Button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {tags.map((t) => (
              <Badge key={t} label={t} variant="tag" onRemove={() => setTags((p) => p.filter((x) => x !== t))} />
            ))}
          </div>
        )}
      </div>

      {/* Ingredients */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Ingredients</label>
        <div className="flex gap-2">
          <Input
            id="ingredient-input"
            placeholder="Type and press Enter"
            value={ingredientInput}
            onChange={(e) => setIngredientInput(e.target.value)}
            onKeyDown={(e) => handleKey(e, addIngredient)}
          />
          <Button type="button" variant="secondary" size="md" onClick={addIngredient}>Add</Button>
        </div>
        {ingredients.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {ingredients.map((i) => (
              <Badge
                key={i} label={i} variant="ingredient"
                onRemove={() => setIngredients((p) => p.filter((x) => x !== i))}
              />
            ))}
          </div>
        )}
      </div>

      <Button type="submit" loading={isLoading} size="lg" className="w-full">
        {submitLabel}
      </Button>
    </form>
  );
}

'use client';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChefHat } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/lib/hooks/useAuth';

const schema = z.object({
  name:     z.string().min(1, 'Name is required'),
  email:    z.string().email('Invalid email'),
  password: z.string().min(5, 'Password must be at least 5 characters'),
});

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-brand-100 p-3 rounded-full mb-3">
            <ChefHat className="h-8 w-8 text-brand-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create account</h1>
          <p className="text-sm text-gray-500 mt-1">Start your recipe collection today</p>
        </div>

        {registerUser.isError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-5 text-sm text-red-700">
            Registration failed. Email may already be in use.
          </div>
        )}

        {registerUser.isSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-5 text-sm text-green-700">
            Account created! Please sign in.
          </div>
        )}

        <form onSubmit={handleSubmit((data) => registerUser.mutate(data))} className="space-y-4">
          <Input
            id="name"
            label="Full name"
            autoComplete="name"
            placeholder="Jane Doe"
            error={errors.name?.message}
            {...register('name')}
          />
          <Input
            id="email"
            label="Email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            error={errors.email?.message}
            {...register('email')}
          />
          <Input
            id="password"
            label="Password"
            type="password"
            autoComplete="new-password"
            placeholder="At least 5 characters"
            error={errors.password?.message}
            {...register('password')}
          />
          <Button type="submit" loading={registerUser.isPending} size="lg" className="w-full mt-2">
            Create account
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-brand-600 font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

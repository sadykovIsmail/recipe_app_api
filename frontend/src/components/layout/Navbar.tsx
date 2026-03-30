'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import { ChefHat, LogOut, PlusCircle } from 'lucide-react';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/Button';

export function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const links = [
    { href: '/recipes', label: 'Recipes' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/recipes" className="flex items-center gap-2 text-brand-600 font-bold text-lg">
            <ChefHat className="h-6 w-6" />
            RecipeApp
          </Link>

          {/* Nav links */}
          <div className="hidden sm:flex items-center gap-6">
            {links.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className={clsx(
                  'text-sm font-medium transition-colors',
                  pathname.startsWith(href)
                    ? 'text-brand-600'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {label}
              </Link>
            ))}
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-3">
            <Link href="/recipes/new">
              <Button size="sm" variant="primary">
                <PlusCircle className="h-4 w-4 mr-1.5" />
                New Recipe
              </Button>
            </Link>

            {user && (
              <span className="hidden sm:block text-sm text-gray-500">
                {user.name}
              </span>
            )}

            <Button
              size="sm"
              variant="ghost"
              onClick={logout}
              aria-label="Log out"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

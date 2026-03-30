import { redirect } from 'next/navigation';

// Root redirects to /recipes (or /login if not authenticated — handled by middleware)
export default function RootPage() {
  redirect('/recipes');
}

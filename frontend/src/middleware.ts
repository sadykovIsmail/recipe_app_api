import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login', '/register', '/discover'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // NOTE: JWT tokens are stored in localStorage (client-side only) so we
  // cannot read them in the edge middleware. Route protection is handled
  // client-side via the useAuth hook. This middleware only handles
  // cookie-based session tokens if added in the future.
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};

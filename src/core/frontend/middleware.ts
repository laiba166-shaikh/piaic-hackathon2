/**
 * Authentication Middleware
 *
 * Protects routes based on authentication status.
 * - Redirects unauthenticated users to /login for protected routes
 * - Redirects authenticated users to / for /login and /register
 *
 * This middleware runs on all routes except static files and API routes.
 */

import { getSessionCookie } from 'better-auth/cookies';
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

/**
 * Middleware function to handle authentication
 *
 * @param request - Next.js request object
 * @returns NextResponse (redirect or continue)
 */
export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  // Skip middleware for API routes (they handle their own auth)
  if (pathname.startsWith('/api/auth')) {
    return NextResponse.next();
  }

  // Check if user has auth token cookie (Better Auth session)
  // const authToken = request.cookies.get('better-auth.session_token');
  const session = getSessionCookie(request);
  const isAuthenticated = !!session;

  // Public routes (accessible without authentication)
  const publicRoutes = ['/login', '/register'];
  const isPublicRoute = publicRoutes.includes(pathname);

  /**
   * Case 1: User is NOT authenticated and trying to access protected route
   * Action: Redirect to /login
   */
  if (!isAuthenticated && !isPublicRoute) {
    const loginUrl = new URL('/login', request.url);
    // Add redirect query param to return to original page after login
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  /**
   * Case 2: User IS authenticated and trying to access /login or /register
   * Action: Redirect to home page (/)
   */
  if (isAuthenticated && isPublicRoute) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  /**
   * Case 3: User is authenticated on protected route OR on public route without auth
   * Action: Allow request to proceed
   */
  return NextResponse.next();
}

/**
 * Middleware configuration
 *
 * Specify which routes this middleware should run on.
 * Excludes static files, images, and Next.js internal routes.
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};

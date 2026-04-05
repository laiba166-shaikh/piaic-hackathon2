/**
 * Better Auth Client for Frontend with JWT Support
 *
 * This file provides the Better Auth client for client-side components.
 * Use this in Client Components ("use client") for authentication operations.
 *
 * Includes JWT plugin for retrieving tokens for FastAPI authentication.
 *
 * DO NOT use the server-side auth instance (lib/auth.ts) in client components.
 */

import { createAuthClient } from 'better-auth/react';
import { jwtClient } from 'better-auth/client/plugins';

/**
 * Better Auth client for client-side authentication
 *
 * Available methods:
 * - authClient.signIn.email({ email, password }) - Sign in with email/password
 * - authClient.signUp.email({ email, password, name }) - Register new user
 * - authClient.signOut() - Sign out current user
 * - authClient.useSession() - React hook to get current session
 * - authClient.token() - Get JWT token for external API calls (NEW)
 *
 * All methods return { data, error } for consistent error handling.
 */
export const authClient = createAuthClient({
  /**
   * Base URL for Better Auth API routes
   * Defaults to current origin (http://localhost:3000 in dev)
   */
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',

  /**
   * Base path for Better Auth API routes
   * All auth endpoints will be at /api/auth/*
   */
  basePath: '/api/auth',

  /**
   * JWT Client Plugin
   * Enables retrieving JWT tokens for external API authentication
   * Uses EdDSA asymmetric algorithm (default)
   */
  plugins: [
    jwtClient(),
  ],
});

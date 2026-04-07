/**
 * Better Auth Configuration with JWT Plugin
 *
 * This file configures Better Auth for user authentication with:
 * - PostgreSQL database (Neon) for user data storage
 * - Email/password authentication
 * - JWT tokens for external API authentication (FastAPI)
 * - HTTP-only cookies for web session storage
 */

import { betterAuth } from 'better-auth';
import { jwt } from 'better-auth/plugins';
import { Pool } from 'pg';

// Validate required environment variables
const DATABASE_URL = process.env.DATABASE_URL;
const BETTER_AUTH_SECRET = process.env.BETTER_AUTH_SECRET;
const BETTER_AUTH_URL = process.env.BETTER_AUTH_URL;

if (!DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is required for Better Auth');
}

if (!BETTER_AUTH_SECRET) {
  throw new Error('BETTER_AUTH_SECRET environment variable is required for Better Auth');
}

/**
 * PostgreSQL connection pool for Better Auth
 * Uses Neon PostgreSQL database to store user data, sessions, and accounts
 */
const pool = new Pool({
  connectionString: DATABASE_URL,
  ssl: {
    rejectUnauthorized: false, // Required for Neon PostgreSQL
  },
});

/**
 * Better Auth instance configuration
 *
 * This instance handles:
 * - User registration (sign up)
 * - User login (sign in)
 * - Session management
 * - JWT token generation (shared secret with backend)
 * - Password hashing and validation
 */
export const auth = betterAuth({
  /**
   * Database configuration
   * Better Auth uses PostgreSQL to store user data in these tables:
   * - user: User accounts (id, email, name, emailVerified, createdAt, updatedAt)
   * - session: User sessions (id, userId, token, expiresAt, ipAddress, userAgent)
   * - account: Authentication accounts (id, userId, accountId, providerId, password)
   * - verification: Email verification tokens
   */
  database: pool,

  /**
   * Base URL for Better Auth API routes
   * Default: http://localhost:3000
   */
  baseURL: BETTER_AUTH_URL || 'http://localhost:3000',

  /**
   * Base path for Better Auth API routes
   * All auth endpoints will be at /api/auth/*
   */
  basePath: '/api/auth',

  /**
   * Secret key for encryption, signing, and hashing
   * IMPORTANT: This must match the JWT_SECRET used by the backend for token validation
   */
  secret: BETTER_AUTH_SECRET,

  /**
   * Email and password authentication configuration
   */
  emailAndPassword: {
    /**
     * Enable email/password authentication
     */
    enabled: true,

    /**
     * Minimum password length (enforced on sign up)
     */
    minPasswordLength: 8,

    /**
     * Maximum password length
     */
    maxPasswordLength: 128,

    /**
     * Automatically sign in user after successful registration
     */
    autoSignIn: true,

    /**
     * Require email verification before allowing sign in
     * Set to false for Phase 2 (email verification added in Phase 3)
     */
    requireEmailVerification: false,
  },

  /**
   * Session configuration
   */
  session: {
    /**
     * Session duration (24 hours in seconds)
     * Matches JWT_EXPIRATION_HOURS in backend config
     */
    expiresIn: 60 * 60 * 24, // 24 hours

    /**
     * Update session timestamp every hour
     */
    updateAge: 60 * 60, // 1 hour

    /**
     * Store sessions in database (user, session tables)
     */
    storeSessionInDatabase: true,

    /**
     * Use HTTP-only cookies for session storage (prevents XSS attacks)
     */
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },

  /**
   * Advanced options
   */
  advanced: {
    /**
     * Use secure cookies in production (HTTPS only)
     */
    useSecureCookies: process.env.NODE_ENV === 'production',

    /**
     * Cookie options
     */
    cookieOptions: {
      sameSite: 'lax' as const, // CSRF protection
      path: '/', // Cookie available on all paths
      httpOnly: true, // Prevent JavaScript access (XSS protection)
    },
  },

  /**
   * Trusted origins for CORS
   * Allow requests from backend API
   */
  trustedOrigins: [process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'],

  /**
   * JWT Plugin
   * Generates JWT tokens for external API authentication
   * - Uses EdDSA (default) asymmetric algorithm with Ed25519 curve
   * - Tokens contain 'sub' claim with user_id
   * - Public key available at /api/auth/jwks endpoint
   * - Backend verifies tokens using public key from JWKS
   */
  plugins: [
    jwt(),
  ],
});

/**
 * Export type-safe auth methods for server-side usage
 * Use these in Server Components, Server Actions, and API Routes
 */
export type AuthSession = typeof auth.api.getSession;
export type AuthUser = NonNullable<Awaited<ReturnType<AuthSession>>>['user'];

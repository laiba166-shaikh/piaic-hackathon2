/**
 * Better Auth API Route Handler
 *
 * This catch-all route handles all Better Auth API endpoints:
 * - POST /api/auth/sign-up/email - User registration
 * - POST /api/auth/sign-in/email - User login
 * - POST /api/auth/sign-out - User logout
 * - GET /api/auth/get-session - Get current session
 * - And all other Better Auth endpoints
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

/**
 * Export GET and POST handlers for Next.js App Router
 * Better Auth handles routing internally based on the path
 */
export const { GET, POST } = toNextJsHandler(auth);

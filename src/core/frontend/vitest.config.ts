/**
 * Vitest Configuration for Frontend Tests
 *
 * Configures Vitest for testing Next.js React components and utilities.
 */

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    /**
     * Use jsdom environment for React component testing
     */
    environment: "jsdom",

    /**
     * Setup file to run before tests
     */
    setupFiles: ["./__tests__/setup.ts"],

    /**
     * Global test configuration
     */
    globals: true,

    /**
     * Coverage configuration
     */
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "__tests__/",
        "*.config.*",
        ".next/",
        "out/",
      ],
    },

    /**
     * Test matching patterns
     */
    include: ["__tests__/**/*.{test,spec}.{ts,tsx}"],

    /**
     * Exclude patterns
     */
    exclude: [
      "node_modules",
      ".next",
      "out",
      "build",
      "dist",
      "coverage",
    ],
  },

  /**
   * Path resolution for imports
   * Match Next.js tsconfig paths
   */
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});

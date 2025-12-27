/**
 * Vitest Test Setup
 *
 * This file runs before all tests to configure the test environment.
 */

import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";

/**
 * Extend Vitest's expect with React Testing Library matchers
 * Provides matchers like:
 * - toBeInTheDocument()
 * - toHaveTextContent()
 * - toHaveAttribute()
 * - etc.
 */
expect.extend(matchers);

/**
 * Clean up after each test
 * Removes rendered components from the DOM
 */
afterEach((): void => {
  cleanup();
});

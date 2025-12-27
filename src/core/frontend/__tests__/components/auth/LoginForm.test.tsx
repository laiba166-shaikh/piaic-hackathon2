/**
 * LoginForm Component Tests (RED Phase - TDD)
 *
 * Test suite for the LoginForm component following Test-Driven Development.
 * These tests define the expected behavior before implementation.
 *
 * Test Coverage:
 * - Form rendering and UI elements
 * - Client-side validation (email and password required)
 * - Error handling for failed login attempts
 * - Successful login and redirection
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import type { RenderResult } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock Next.js router
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: (): { push: typeof mockPush } => ({
    push: mockPush,
  }),
}));

// Mock Better Auth client
const mockSignIn = vi.fn();
vi.mock("@/lib/auth-client", () => ({
  authClient: {
    signIn: {
      email: mockSignIn,
    },
  },
}));

// Import component (will be created in GREEN phase)
// This import will fail initially - that's expected in RED phase
import LoginForm from "@/components/auth/LoginForm";

describe("LoginForm Component", (): void => {
  beforeEach((): void => {
    // Reset all mocks before each test
    vi.clearAllMocks();
  });

  afterEach((): void => {
    // Clean up after each test
    vi.resetAllMocks();
  });

  /**
   * Test Case 1: Form Rendering
   *
   * Acceptance Criteria:
   * - Form renders with email input field
   * - Form renders with password input field
   * - Form renders with submit button
   * - Email input has proper type="email" attribute
   * - Password input has proper type="password" attribute
   * - Password input has show/hide toggle button
   */
  it("should render login form with all required fields", (): void => {
    // Arrange & Act
    render(<LoginForm />);

    // Assert: Check email input exists and has correct type
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute("type", "email");
    expect(emailInput).toHaveAttribute("required");

    // Assert: Check password input exists and has correct type
    const passwordInput = screen.getByLabelText(
      /^password$/i
    ) as HTMLInputElement;
    expect(passwordInput).toBeInTheDocument();
    expect(passwordInput).toHaveAttribute("type", "password");
    expect(passwordInput).toHaveAttribute("required");

    // Assert: Check submit button exists
    const submitButton = screen.getByRole("button", {
      name: /log in|sign in/i,
    }) as HTMLButtonElement;
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toHaveAttribute("type", "submit");

    // Assert: Check password toggle button exists
    const toggleButton = screen.getByRole("button", {
      name: /show password|hide password|toggle password visibility/i,
    }) as HTMLButtonElement;
    expect(toggleButton).toBeInTheDocument();
  });

  /**
   * Test Case 2: Email Validation
   *
   * Acceptance Criteria:
   * - Form shows error when email field is empty on submit
   * - Form shows error when email format is invalid
   * - Error message is user-friendly
   * - Form does not call sign in API when email is invalid
   */
  it("should validate that email is required", async (): Promise<void> => {
    // Arrange
    const user = userEvent.setup();
    render(<LoginForm />);

    // Act: Try to submit form without entering email
    const passwordInput = screen.getByLabelText(
      /^password$/i
    ) as HTMLInputElement;
    const submitButton = screen.getByRole("button", {
      name: /log in|sign in/i,
    }) as HTMLButtonElement;

    await user.type(passwordInput, "validpassword123");
    await user.click(submitButton);

    // Assert: Email validation error should be displayed
    await waitFor((): void => {
      const errorMessage = screen.getByText(
        /email is required|please enter your email/i
      );
      expect(errorMessage).toBeInTheDocument();
    });

    // Assert: Sign in should not be called
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  /**
   * Test Case 3: Password Validation
   *
   * Acceptance Criteria:
   * - Form shows error when password field is empty on submit
   * - Error message is user-friendly
   * - Form does not call sign in API when password is invalid
   */
  it("should validate that password is required", async (): Promise<void> => {
    // Arrange
    const user = userEvent.setup();
    render(<LoginForm />);

    // Act: Try to submit form without entering password
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const submitButton = screen.getByRole("button", {
      name: /log in|sign in/i,
    }) as HTMLButtonElement;

    await user.type(emailInput, "user@example.com");
    await user.click(submitButton);

    // Assert: Password validation error should be displayed
    await waitFor((): void => {
      const errorMessage = screen.getByText(
        /password is required|please enter your password/i
      );
      expect(errorMessage).toBeInTheDocument();
    });

    // Assert: Sign in should not be called
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  /**
   * Test Case 4: Failed Login Error Handling
   *
   * Acceptance Criteria:
   * - Form shows error message when login fails (invalid credentials)
   * - Error message is user-friendly (not technical)
   * - Form remains interactive after error (user can retry)
   * - Loading state is cleared after error
   */
  it("should display error message when login fails", async (): Promise<void> => {
    // Arrange
    const user = userEvent.setup();
    const errorMessage = "Invalid email or password";

    // Mock failed sign in
    mockSignIn.mockResolvedValueOnce({
      error: {
        message: errorMessage,
      },
    });

    render(<LoginForm />);

    // Act: Submit form with credentials
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(
      /^password$/i
    ) as HTMLInputElement;
    const submitButton = screen.getByRole("button", {
      name: /log in|sign in/i,
    }) as HTMLButtonElement;

    await user.type(emailInput, "wrong@example.com");
    await user.type(passwordInput, "wrongpassword");
    await user.click(submitButton);

    // Assert: Error message should be displayed
    await waitFor((): void => {
      const error = screen.getByText(/invalid email or password/i);
      expect(error).toBeInTheDocument();
    });

    // Assert: Sign in was called with correct credentials
    expect(mockSignIn).toHaveBeenCalledWith({
      email: "wrong@example.com",
      password: "wrongpassword",
    });

    // Assert: Form is still interactive (button is not disabled)
    expect(submitButton).not.toBeDisabled();
  });

  /**
   * Test Case 5: Successful Login and Redirection
   *
   * Acceptance Criteria:
   * - Form calls Better Auth sign in API with correct credentials
   * - Form shows loading state during sign in
   * - Form redirects to home page (/) after successful login
   * - No error messages are shown on success
   */
  it("should redirect to home page on successful login", async (): Promise<void> => {
    // Arrange
    const user = userEvent.setup();

    // Mock successful sign in
    mockSignIn.mockResolvedValueOnce({
      data: {
        user: {
          id: "user-123",
          email: "user@example.com",
          name: "Test User",
        },
        session: {
          id: "session-123",
          token: "valid-token",
          expiresAt: new Date(Date.now() + 86400000).toISOString(),
        },
      },
      error: null,
    });

    render(<LoginForm />);

    // Act: Submit form with valid credentials
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(
      /^password$/i
    ) as HTMLInputElement;
    const submitButton = screen.getByRole("button", {
      name: /log in|sign in/i,
    }) as HTMLButtonElement;

    await user.type(emailInput, "user@example.com");
    await user.type(passwordInput, "validpassword123");

    // Assert: Loading state should appear during submission
    await user.click(submitButton);

    await waitFor((): void => {
      expect(submitButton).toHaveTextContent(/loading|signing in/i);
    });

    // Assert: Sign in was called with correct credentials
    expect(mockSignIn).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "validpassword123",
    });

    // Assert: Router push was called to redirect to home page
    await waitFor((): void => {
      expect(mockPush).toHaveBeenCalledWith("/");
    });

    // Assert: No error messages are displayed
    const errors = screen.queryByRole("alert");
    expect(errors).not.toBeInTheDocument();
  });

  /**
   * Test Case 6: Password Visibility Toggle
   *
   * Acceptance Criteria:
   * - Password is hidden by default (type="password")
   * - Clicking toggle button shows password (type="text")
   * - Clicking toggle button again hides password
   * - Toggle button icon/text changes based on state
   */
  it("should toggle password visibility when toggle button is clicked", async (): Promise<void> => {
    // Arrange
    const user = userEvent.setup();
    render(<LoginForm />);

    const passwordInput = screen.getByLabelText(
      /^password$/i
    ) as HTMLInputElement;
    const toggleButton = screen.getByRole("button", {
      name: /show password|hide password|toggle password visibility/i,
    }) as HTMLButtonElement;

    // Assert: Password is hidden by default
    expect(passwordInput).toHaveAttribute("type", "password");

    // Act: Click toggle to show password
    await user.click(toggleButton);

    // Assert: Password is now visible
    await waitFor((): void => {
      expect(passwordInput).toHaveAttribute("type", "text");
    });

    // Act: Click toggle again to hide password
    await user.click(toggleButton);

    // Assert: Password is hidden again
    await waitFor((): void => {
      expect(passwordInput).toHaveAttribute("type", "password");
    });
  });
});

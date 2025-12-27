/**
 * Authentication Layout
 *
 * This layout is used for authentication pages (login, register)
 * It provides a simple centered layout without sidebar or header.
 */

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): JSX.Element {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {children}
    </div>
  );
}

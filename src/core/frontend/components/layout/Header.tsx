import LogoutButton from "@/components/auth/LogoutButton";

/**
 * Header Component
 *
 * Main header with app title and logout button.
 *
 * @returns JSX.Element
 */
export function Header(){
  return (
    <header className="bg-paper-white border-b border-sepia-brown shadow-journal">
      <div className="px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-serif text-ink-black">My Journal</h1>
        <LogoutButton />
      </div>
    </header>
  );
}

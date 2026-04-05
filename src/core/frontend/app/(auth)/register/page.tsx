import RegisterForm from "@/components/auth/RegisterForm";
import Link from "next/link";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left pane — 40% */}
      <div className="hidden md:flex md:w-2/5 bg-sidebar-background flex-col p-10">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 shrink-0">
            <svg width="40" height="40" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
              <rect width="96" height="96" rx="22" fill="hsl(var(--sidebar-accent))"/>
              <circle cx="48" cy="45" r="26" fill="none" stroke="hsl(var(--sidebar-foreground) / 0.4)" strokeWidth="3"/>
              <circle cx="48" cy="45" r="26" fill="none" stroke="hsl(var(--sidebar-foreground))" strokeWidth="3"
                strokeDasharray="40 123" strokeDashoffset="20" strokeLinecap="round"/>
              <polyline points="40,45 46,52 58,38" fill="none" stroke="hsl(var(--sidebar-foreground))"
                strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="text-sidebar-foreground font-semibold text-xl">Task Mate</span>
        </div>

        {/* Tagline */}
        <div className="mt-16">
          <h2 className="text-white font-bold text-3xl leading-tight">
            Your productivity, organised
          </h2>
          <p className="mt-4 text-sidebar-foreground/70 text-base leading-relaxed">
            Join Task Mate and start building your focused, clutter-free workflow today.
          </p>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Stats + dots */}
        <div>
          <div className="flex gap-3 mb-6">
            <div className="bg-sidebar-accent rounded-lg p-4 flex-1">
              <p className="text-white font-bold text-xl">2k+</p>
              <p className="text-sidebar-foreground/70 text-sm">Active users</p>
            </div>
            <div className="bg-sidebar-accent rounded-lg p-4 flex-1">
              <p className="text-white font-bold text-xl">4.9★</p>
              <p className="text-sidebar-foreground/70 text-sm">User rating</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right pane — 60% */}
      <div className="flex-1 bg-background flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <h1 className="text-3xl font-semibold text-foreground mb-1">Create account</h1>
          <p className="text-muted-foreground mb-8">Get started — it&apos;s completely free</p>

          <RegisterForm />

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already a member?{" "}
            <Link href="/login" className="text-primary font-semibold hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

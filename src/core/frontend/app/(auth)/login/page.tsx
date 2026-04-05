import LoginForm from "@/components/auth/LoginForm";
import Link from "next/link";

export default function LoginPage() {
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
            Clarity for every task ahead
          </h2>
          <p className="mt-4 text-sidebar-foreground/70 text-base leading-relaxed">
            Organise your day, track your progress, and get things done — all in one place.
          </p>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Quote + dots */}
        <div>
          <p className="text-sidebar-foreground/60 text-sm italic">
            &ldquo;The secret of getting ahead is getting started.&rdquo;
          </p>
        </div>
      </div>

      {/* Right pane — 60% */}
      <div className="flex-1 bg-background flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <h1 className="text-3xl font-semibold text-foreground mb-1">Welcome back</h1>
          <p className="text-muted-foreground mb-8">Sign in to continue to Task Mate</p>

          <LoginForm />

          <p className="mt-6 text-center text-sm text-muted-foreground">
            New here?{" "}
            <Link href="/register" className="text-primary font-semibold hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

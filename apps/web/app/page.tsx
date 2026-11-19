import { Dashboard } from "@/components/Dashboard";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.3em] text-accent">ShortsFactory AI</p>
        <h1 className="text-3xl font-semibold sm:text-4xl">Local operator dashboard</h1>
        <p className="max-w-2xl text-sm text-slate-400">
          Phase 1 scaffold. Local-first, mock providers by default, no paid API calls and no
          publishing. Sign in to inspect service connectivity and provider modes.
        </p>
      </header>
      <Dashboard />
      <footer className="mt-auto text-xs text-slate-500">
        Safety: dry-run by default · uploads disabled · public publishing disabled · human
        approval required.
      </footer>
    </main>
  );
}

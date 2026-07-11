"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { apiClient } from "@/lib/api/client";
import { useScanStore } from "@/lib/store/scan-store";
import { Button } from "@/components/ui/button";
import { Lock, Shield } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const { refreshUser } = useAuth();
  const resetWorkspace = useScanStore((state) => state.resetWorkspace);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await apiClient.post("/api/v1/auth/login", {
        email: email.trim().toLowerCase(),
        password,
      });
      await refreshUser();
      resetWorkspace();
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Login failed");
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-7rem)] max-w-5xl items-center justify-center">
      <form onSubmit={handleLogin} className="grid w-full overflow-hidden rounded-lg border border-border bg-surface-panel shadow-md md:grid-cols-[1fr_420px]">
        <section className="hidden border-r border-border bg-surface-subtle p-8 md:block">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg border border-primary/30 bg-primary/10 text-primary">
            <Shield className="h-5 w-5" />
          </div>
          <h1 className="mt-6 text-2xl font-semibold text-text-primary">Vulnerable Scanner</h1>
          <p className="mt-3 max-w-sm text-sm leading-6 text-text-muted">
            Authenticated workspace for source analysis, scan history, and security operations.
          </p>
        </section>

        <section className="p-6 md:p-8">
          <div className="mb-6">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">Access Control</p>
            <h2 className="mt-2 text-xl font-semibold text-text-primary">Login</h2>
          </div>
          {error && (
            <div className="mb-4 rounded-lg border border-severity-critical/30 bg-severityBg-critical p-3 text-sm text-severity-critical" role="alert">
              {error}
            </div>
          )}
        <div className="mb-4">
          <label className="block text-sm font-medium text-text-secondary">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-text-primary outline-none focus-visible:ring-2 focus-visible:ring-primary"
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-text-secondary">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-text-primary outline-none focus-visible:ring-2 focus-visible:ring-primary"
            required
          />
        </div>
        <Button type="submit" className="w-full">
          <Lock className="h-4 w-4" />
          Login
        </Button>
        <p className="mt-4 text-sm text-text-muted">
          Don&apos;t have an account? <a href="/register" className="text-blue-500 hover:underline">Register</a>
        </p>
        </section>
      </form>
    </div>
  );
}

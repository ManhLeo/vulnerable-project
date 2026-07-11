"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { UserPlus } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("The confirm password does not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      await apiClient.post("/api/v1/auth/register", {
        email: email.trim().toLowerCase(),
        password,
      });
      setSuccess("Registration successful. Please log in.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-7rem)] max-w-md items-center justify-center">
      <form onSubmit={handleRegister} className="w-full rounded-lg border border-border bg-surface-panel p-6 shadow-md">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">Provision User</p>
        <h2 className="mt-2 text-xl font-semibold text-text-primary">Register</h2>
        {error && <p className="mt-4 rounded-lg border border-severity-critical/30 bg-severityBg-critical p-3 text-sm text-severity-critical">{error}</p>}
        {success && <p className="mt-4 rounded-lg border border-severity-safe/30 bg-severityBg-safe p-3 text-sm text-severity-safe">{success}</p>}
        <div className="mb-4">
          <label className="mt-5 block text-sm font-medium text-text-secondary">Email</label>
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-text-primary outline-none focus-visible:ring-2 focus-visible:ring-primary"
            placeholder="8+ chars, 1 uppercase, 1 lowercase, 1 number"
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-text-secondary">Confirm password</label>
          <input
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-text-primary outline-none focus-visible:ring-2 focus-visible:ring-primary"
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          <UserPlus className="h-4 w-4" />
          {isSubmitting ? "Registering..." : "Register"}
        </Button>
        <p className="mt-4 text-sm text-text-muted">
          Already have an account? <a href="/login" className="text-blue-500 hover:underline">Login</a>
        </p>
      </form>
    </div>
  );
}

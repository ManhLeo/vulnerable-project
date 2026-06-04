"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/client";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await apiClient.post("/api/v1/auth/register", { email, password });
      setSuccess("Registration successful. Please log in.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      setError(err.message || "Registration failed");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <form onSubmit={handleRegister} className="w-full max-w-sm rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
        <h2 className="mb-4 text-2xl font-bold dark:text-white">Register</h2>
        {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
        {success && <p className="mb-4 text-sm text-green-500">{success}</p>}
        <div className="mb-4">
          <label className="block text-sm font-medium dark:text-gray-300">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border p-2 dark:bg-gray-700 dark:text-white"
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium dark:text-gray-300">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-md border p-2 dark:bg-gray-700 dark:text-white"
            placeholder="8+ chars, 1 uppercase, 1 lowercase, 1 number"
            required
          />
        </div>
        <button type="submit" className="w-full rounded-md bg-green-600 p-2 text-white hover:bg-green-700">
          Register
        </button>
        <p className="mt-4 text-sm dark:text-gray-400">
          Already have an account? <a href="/login" className="text-blue-500 hover:underline">Login</a>
        </p>
      </form>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiClient } from "@/lib/api/client";

interface AdminStats {
  users: {
    total_active: number;
  };
  scans: {
    total_scans: number;
    vulnerable_scans: number;
    safe_scans: number;
    vulnerable_ratio: number;
    average_confidence: number;
    risk_distribution: Record<string, number>;
  };
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get<AdminStats>("/api/v1/admin/stats");
        setStats(response.data);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard stats");
      }
    };
    fetchStats();
  }, []);

  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <div className="container mx-auto p-6">
        <h1 className="mb-6 text-3xl font-bold dark:text-white">Admin Dashboard</h1>
        {error && <div className="mb-4 text-red-500">{error}</div>}
        
        {stats ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* User Analytics */}
            <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
              <h2 className="mb-2 text-xl font-semibold dark:text-gray-200">User Analytics</h2>
              <p className="text-3xl font-bold text-blue-600">{stats.users.total_active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Active Users</p>
            </div>

            {/* Scan Analytics */}
            <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
              <h2 className="mb-2 text-xl font-semibold dark:text-gray-200">Scan Analytics</h2>
              <p className="text-gray-700 dark:text-gray-300">Total Scans: <span className="font-bold">{stats.scans.total_scans}</span></p>
              <p className="text-gray-700 dark:text-gray-300">Vulnerable: <span className="font-bold text-red-500">{stats.scans.vulnerable_scans}</span></p>
              <p className="text-gray-700 dark:text-gray-300">Safe: <span className="font-bold text-green-500">{stats.scans.safe_scans}</span></p>
              <p className="mt-2 text-sm text-gray-500">Vulnerable Ratio: {(stats.scans.vulnerable_ratio * 100).toFixed(2)}%</p>
            </div>

            {/* AI Monitoring */}
            <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
              <h2 className="mb-2 text-xl font-semibold dark:text-gray-200">AI Monitoring</h2>
              <p className="text-gray-700 dark:text-gray-300">Avg Confidence: <span className="font-bold">{(stats.scans.average_confidence * 100).toFixed(2)}%</span></p>
              <div className="mt-2">
                <p className="text-sm font-medium text-gray-500">Risk Distribution:</p>
                <ul className="text-sm text-gray-700 dark:text-gray-300">
                  {Object.entries(stats.scans.risk_distribution).map(([level, count]) => (
                    <li key={level}>{level}: {count}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div>Loading stats...</div>
        )}
      </div>
    </ProtectedRoute>
  );
}

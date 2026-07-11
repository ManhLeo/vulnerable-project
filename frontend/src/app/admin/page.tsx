"use client";

import type { ComponentType } from "react";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Database, Download, Lock, ShieldCheck, Sparkles, Trash2, Users } from "lucide-react";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/common/error-state";
import { useAuth } from "@/hooks/useAuth";
import { useHealthQuery } from "@/hooks/use-health-query";
import { useModelInfoQuery } from "@/hooks/use-model-info-query";
import { queryKeys } from "@/lib/query/query-keys";
import { deleteAdminUser, exportScanSourcesCsv, getAdminStats, getAdminUsers } from "@/services/admin.service";
import type { AdminStatsDto, AdminUserDto } from "@/types/api";
import { ModelSelector } from "@/features/scan-workspace/components/model-selector";

function StatTile({
  title,
  value,
  subtitle,
  icon: Icon,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: ComponentType<{ className?: string }>;
}): JSX.Element {
  return (
    <div className="rounded-xl border border-border bg-surface-panel p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-text-muted">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-text-primary">{value}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface-elevated p-2 text-primary">
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className="text-xs text-text-muted">{subtitle}</p>
    </div>
  );
}

export default function AdminDashboardPage(): JSX.Element {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedModelValue, setSelectedModelValue] = useState("");

  const statsQuery = useQuery<AdminStatsDto>({
    queryKey: queryKeys.admin.stats,
    queryFn: getAdminStats,
  });

  const usersQuery = useQuery<AdminUserDto[]>({
    queryKey: queryKeys.admin.users,
    queryFn: getAdminUsers,
  });

  const healthQuery = useHealthQuery();
  const modelInfoQuery = useModelInfoQuery();

  const deleteMutation = useMutation({
    mutationFn: deleteAdminUser,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.all });
      await queryClient.invalidateQueries({ queryKey: queryKeys.health.all });
      await queryClient.invalidateQueries({ queryKey: queryKeys.model.all });
    },
  });

  const exportMutation = useMutation({
    mutationFn: exportScanSourcesCsv,
    onSuccess: (blob) => {
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `scan_sources_export_${timestamp}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    },
  });

  const stats = statsQuery.data;
  const users = usersQuery.data ?? [];
  const activeUsers = users.filter((item) => item.is_active && !item.is_deleted).length;
  const totalUsers = users.filter((item) => !item.is_deleted).length;
  const modelInfo = modelInfoQuery.data?.data;
  const health = healthQuery.data?.data;
  const healthSummary = health?.degraded ? "Degraded" : "Healthy";

  const handleDeleteUser = async (userId: string, email: string) => {
    const confirmed = window.confirm(`Soft delete user ${email}?`);
    if (!confirmed) {
      return;
    }
    await deleteMutation.mutateAsync(userId);
  };

  const handleExportCsv = async () => {
    await exportMutation.mutateAsync();
  };

  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <div className="space-y-6">
        <section className="space-y-2 border-b border-border pb-4">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">Privileged Console</p>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Admin Console</h1>
          <p className="max-w-3xl text-sm text-text-muted">
            Administrative controls for user management, system health, model configuration, and secure export operations.
          </p>
        </section>

        {statsQuery.isError ? (
          <ErrorState
            title="Unable to load admin stats"
            message={statsQuery.error?.message ?? "Admin statistics request failed."}
          />
        ) : null}

        {usersQuery.isError ? (
          <ErrorState
            title="Unable to load users"
            message={usersQuery.error?.message ?? "Admin user list request failed."}
          />
        ) : null}

        {healthQuery.isError ? (
          <ErrorState
            title="Unable to load health"
            message={healthQuery.error?.message ?? "Health request failed."}
          />
        ) : null}

        {exportMutation.isError ? (
          <ErrorState
            title="Unable to export scanned source CSV"
            message={exportMutation.error?.message ?? "CSV export request failed."}
          />
        ) : null}

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatTile
            title="System health"
            value={healthSummary}
            subtitle="Current database and model service condition."
            icon={Database}
          />
          <StatTile
            title="Active users"
            value={stats?.users.total_active ?? 0}
            subtitle="Active non-deleted accounts reported by backend."
            icon={Users}
          />
          <StatTile
            title="Total users"
            value={totalUsers}
            subtitle="Visible accounts returned by admin user listing."
            icon={ShieldCheck}
          />
          <StatTile
            title="Total scans"
            value={stats?.scans.total_scans ?? 0}
            subtitle="Global scan count across the system."
            icon={Activity}
          />
        </section>

        <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="rounded-xl border border-border bg-surface-panel p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-text-muted">System health</p>
                  <h2 className="mt-1 text-base font-semibold text-text-primary">Health and model status</h2>
                </div>
                <Database className="h-4 w-4 text-primary" />
              </div>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Database</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">
                    {health?.database.mode?.toUpperCase() ?? "UNKNOWN"}
                  </p>
                  <p className="text-xs text-text-muted">
                    Status: {health?.database.status ?? "unknown"}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Model</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">
                    {health?.model.status ?? "unknown"}
                  </p>
                  <p className="text-xs text-text-muted">
                    {health?.model.checkpoint ? `Checkpoint: ${health.model.checkpoint}` : "No active checkpoint"}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Degraded</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">{health?.degraded ? "Yes" : "No"}</p>
                  <p className="text-xs text-text-muted">{health?.status ?? "unknown"} state</p>
                </div>
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Admin identity</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">{user?.email ?? "unknown"}</p>
                  <p className="text-xs text-text-muted">Currently authenticated admin</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-surface-panel p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-text-muted">Model control</p>
                  <h2 className="mt-1 text-base font-semibold text-text-primary">Global checkpoint selector</h2>
                </div>
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <ModelSelector mode="global" value={selectedModelValue} onChange={setSelectedModelValue} />
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-xl border border-border bg-surface-panel p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-text-muted">User management</p>
                  <h2 className="mt-1 text-base font-semibold text-text-primary">Accounts</h2>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    className="gap-2"
                    disabled={exportMutation.isPending}
                    onClick={() => void handleExportCsv()}
                  >
                    <Download className="h-4 w-4" />
                    {exportMutation.isPending ? "Exporting..." : "Export CSV"}
                  </Button>
                  <Users className="h-4 w-4 text-primary" />
                </div>
              </div>

              <div className="mb-4 flex flex-wrap gap-2">
                <Badge variant="neutral">Visible users: {totalUsers}</Badge>
                <Badge variant="safe">Active users: {activeUsers}</Badge>
                <Badge variant="neutral">Deleted filtered out</Badge>
              </div>

              <div className="overflow-hidden rounded-lg border border-border">
                <table className="w-full border-collapse text-left text-sm">
                  <thead className="bg-surface-elevated text-text-muted">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Email</th>
                      <th className="px-4 py-3 font-semibold">Role</th>
                      <th className="px-4 py-3 font-semibold">Active</th>
                      <th className="px-4 py-3 font-semibold">Created</th>
                      <th className="px-4 py-3 font-semibold">Last login</th>
                      <th className="px-4 py-3 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border bg-surface-panel">
                    {usersQuery.isLoading ? (
                      <tr>
                        <td className="px-4 py-4 text-text-muted" colSpan={6}>
                          Loading users...
                        </td>
                      </tr>
                    ) : users.length === 0 ? (
                      <tr>
                        <td className="px-4 py-4 text-text-muted" colSpan={6}>
                          No users found.
                        </td>
                      </tr>
                    ) : (
                      users.map((item) => (
                        <tr key={item.id}>
                          <td className="px-4 py-3 font-medium text-text-primary">{item.email}</td>
                          <td className="px-4 py-3 text-text-secondary">{item.role}</td>
                          <td className="px-4 py-3">
                            <Badge variant={item.is_active ? "safe" : "neutral"}>
                              {item.is_active ? "Yes" : "No"}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-text-secondary">
                            {new Date(item.created_at).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-text-secondary">
                            {item.last_login_at ? new Date(item.last_login_at).toLocaleString() : "Never"}
                          </td>
                          <td className="px-4 py-3">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="gap-2 text-severity-critical hover:text-severity-critical"
                              disabled={deleteMutation.isPending || item.id === user?.id}
                              onClick={() => void handleDeleteUser(item.id, item.email)}
                            >
                              <Trash2 className="h-4 w-4" />
                              Delete
                            </Button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-surface-panel p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-text-muted">Model status</p>
                  <h2 className="mt-1 text-base font-semibold text-text-primary">Backend model inventory</h2>
                </div>
                <Lock className="h-4 w-4 text-primary" />
              </div>
              <div className="grid grid-cols-1 gap-3">
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Active checkpoint</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">{modelInfo?.active_checkpoint ?? "unknown"}</p>
                </div>
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Available checkpoints</p>
                  <p className="mt-2 text-sm text-text-primary">
                    {modelInfo?.available_checkpoints?.length
                      ? modelInfo.available_checkpoints.join(", ")
                      : "None reported"}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-elevated p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Supported modes</p>
                  <p className="mt-2 text-sm text-text-primary">
                    {modelInfo?.supported_modes?.length ? modelInfo.supported_modes.join(", ") : "single"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </ProtectedRoute>
  );
}

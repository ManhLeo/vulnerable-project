"use client";

import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, BarChart3, FileSearch, History, Lock, LogIn, LogOut, Menu, ShieldCheck, X } from "lucide-react";

import { SidebarNav } from "@/components/layout/sidebar-nav";
import { TopbarStatus } from "@/components/layout/topbar-status";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useScanStore } from "@/lib/store/scan-store";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps): JSX.Element {
  const [mobileOpen, setMobileOpen] = useState(false);
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const resetWorkspace = useScanStore((state) => state.resetWorkspace);
  const previousRoleRef = useRef<string | null>(null);

  useEffect(() => {
    if (isLoading) {
      return;
    }

    const currentRole = user?.role ?? "guest";
    if (previousRoleRef.current === null) {
      previousRoleRef.current = currentRole;
      return;
    }

    if (previousRoleRef.current !== currentRole) {
      resetWorkspace();
      previousRoleRef.current = currentRole;
    }
  }, [isLoading, resetWorkspace, user?.role]);

  const handleLogout = async (): Promise<void> => {
    await logout();
    router.push("/");
  };

  const navItems = [
    { href: "/", label: "Workspace", shortLabel: "WS", icon: FileSearch },
    { href: "/scan/result", label: "Scan Result", shortLabel: "SR", icon: Activity },
    ...(isAuthenticated ? [
      { href: "/scan/history", label: "History", shortLabel: "HS", icon: History }
    ] : []),
    ...(user?.role === "admin" ? [
      { href: "/dashboard", label: "Analytics", shortLabel: "AN", icon: BarChart3 }
    ] : []),
    ...(user?.role === "admin" ? [
      { href: "/admin", label: "Admin Console", shortLabel: "AC", icon: ShieldCheck }
    ] : []),
    ...(isAuthenticated ? [
      { href: "#", label: "Logout", shortLabel: "LO", icon: LogOut, onClick: () => { void handleLogout(); } }
    ] : [
      { href: "/login", label: "Login", shortLabel: "LI", icon: LogIn }
    ])
  ];

  return (
    <div className="min-h-screen bg-surface-page text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-[260px] shrink-0 border-r border-border bg-surface-panel/95 md:block">
          <div className="border-b border-border px-4 py-5">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-primary/30 bg-primary/10 text-primary">
                <Lock className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-semibold tracking-tight text-text-primary">Vulnerable Scanner</p>
                <p className="text-[11px] text-text-muted">Security Workspace</p>
              </div>
            </div>
          </div>
          <SidebarNav items={navItems} />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="border-b border-border bg-surface-panel px-4 py-3 md:hidden">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-primary" />
                <p className="text-sm font-semibold text-text-primary">Vulnerable Scanner</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMobileOpen((v) => !v)}
                aria-expanded={mobileOpen}
                aria-controls="mobile-nav"
                aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
              >
                {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              </Button>
            </div>
            {mobileOpen ? (
              <div
                id="mobile-nav"
                className="mt-3 rounded-lg border border-border bg-surface-panel"
                aria-label="Mobile navigation"
              >
                <SidebarNav items={navItems} onNavigate={() => setMobileOpen(false)} />
              </div>
            ) : null}
          </div>

          <TopbarStatus />

          <main className="w-full flex-1 px-4 py-5 md:px-6 md:py-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}

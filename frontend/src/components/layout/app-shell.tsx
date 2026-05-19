"use client";

import type { ReactNode } from "react";
import { useState } from "react";

import { SidebarNav } from "@/components/layout/sidebar-nav";
import { TopbarStatus } from "@/components/layout/topbar-status";
import { Button } from "@/components/ui/button";

interface AppShellProps {
  children: ReactNode;
}

const navItems = [
  { href: "/", label: "Home", shortLabel: "H" },
  { href: "/scan/result", label: "Scan Result", shortLabel: "SR" },
  { href: "/scan/history", label: "Scan History", shortLabel: "SH" },
  { href: "/dashboard", label: "Dashboard", shortLabel: "DB" },
];

export function AppShell({ children }: AppShellProps): JSX.Element {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface-page text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-[240px] shrink-0 border-r border-border bg-surface-panel md:block">
          <div className="border-b border-border px-4 py-4">
            <p className="text-sm font-semibold tracking-tight text-text-primary">VulnDetect</p>
            <p className="text-xs text-text-muted">Enterprise security workspace</p>
          </div>
          <SidebarNav items={navItems} />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="border-b border-border bg-surface-panel px-4 py-2 md:hidden">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-text-primary">VulnDetect</p>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setMobileOpen((v) => !v)}
                aria-expanded={mobileOpen}
                aria-controls="mobile-nav"
                aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
              >
                {mobileOpen ? "Close" : "Menu"}
              </Button>
            </div>
            {mobileOpen ? (
              <div
                id="mobile-nav"
                className="mt-2 rounded-md border border-border bg-surface-panel"
                aria-label="Mobile navigation"
              >
                <SidebarNav items={navItems} onNavigate={() => setMobileOpen(false)} />
              </div>
            ) : null}
          </div>

          <TopbarStatus />

          <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 md:px-6 md:py-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}

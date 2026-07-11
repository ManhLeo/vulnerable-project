"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

export interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
  icon?: LucideIcon;
  onClick?: () => void;
}

interface SidebarNavProps {
  items: NavItem[];
  onNavigate?: () => void;
}

export function SidebarNav({ items, onNavigate }: SidebarNavProps): JSX.Element {
  const pathname = usePathname();

  return (
    <nav className="flex h-full flex-col px-3 py-4" aria-label="Primary">
      <div className="mb-4 px-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-text-muted">Navigation</p>
      </div>

      <ul className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={(e) => {
                  if (item.onClick) {
                    e.preventDefault();
                    item.onClick();
                  }
                  if (onNavigate) onNavigate();
                }}
                className={cn(
                  "group flex items-center justify-between rounded-md px-3 py-2.5 text-sm font-medium transition-colors duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30",
                  isActive
                    ? "border border-primary/25 bg-primary/10 text-primary shadow-[inset_0_0_0_1px_hsl(var(--primary)/0.05)]"
                    : "border border-transparent text-text-secondary hover:border-border hover:bg-surface-subtle hover:text-text-primary"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <span className="flex min-w-0 items-center gap-2">
                  {Icon ? <Icon className="h-4 w-4 shrink-0" /> : null}
                  <span className="truncate">{item.label}</span>
                </span>
                <span
                  className={cn(
                    "rounded border px-1.5 py-0 text-[10px] font-semibold tracking-wide",
                    isActive
                      ? "border-primary/30 bg-primary/10 text-primary"
                      : "border-border bg-surface-elevated text-text-muted group-hover:text-text-secondary"
                  )}
                >
                  {item.shortLabel}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

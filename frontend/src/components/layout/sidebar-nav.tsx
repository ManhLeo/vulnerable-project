"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

export interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
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
        <p className="text-xs font-semibold uppercase tracking-[0.08em] text-text-muted">Platform</p>
      </div>

      <ul className="space-y-1">
        {items.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30",
                  isActive
                    ? "bg-primary-subtle text-primary"
                    : "text-text-secondary hover:bg-surface-subtle hover:text-text-primary"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <span>{item.label}</span>
                <span
                  className={cn(
                    "rounded border px-1.5 py-0 text-[10px] font-semibold tracking-wide",
                    isActive
                      ? "border-primary/30 bg-white text-primary"
                      : "border-border bg-white text-text-muted group-hover:text-text-secondary"
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

"use client";

import { usePathname, useRouter } from "next/navigation";
import { Cpu, LogIn, LogOut, UserCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useModelInfoQuery } from "@/hooks/use-model-info-query";

const PAGE_TITLES: Record<string, string> = {
  "/": "Workspace",
  "/dashboard": "Analytics",
  "/scan/result": "Scan Result",
  "/scan/history": "History",
  "/login": "Login",
  "/register": "Register",
  "/admin": "Admin Console",
};

export function TopbarStatus(): JSX.Element {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuth();
  const { data, isLoading } = useModelInfoQuery();
  const model = data?.data;
  const pageTitle = PAGE_TITLES[pathname] ?? "Vulnerable Scanner";
  const handleLogout = async (): Promise<void> => {
    await logout();
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-30 flex min-h-14 items-center justify-between gap-3 border-b border-border bg-surface-panel/90 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-3">
        <p className="text-sm font-semibold text-text-primary">{pageTitle}</p>
        <span className="hidden text-xs text-text-muted sm:inline">Vulnerability analysis workspace</span>
      </div>

      <div className="flex min-w-0 items-center gap-2">
        <Badge variant={model?.model_loaded ? "safe" : "medium"} className="hidden sm:inline-flex">
          <Cpu className="mr-1 h-3 w-3" />
          {isLoading ? "Model: loading" : model?.model_loaded ? "Model: online" : "Model: offline"}
        </Badge>
        <Badge variant={isAuthenticated ? "low" : "neutral"} className="hidden md:inline-flex">
          <UserCircle className="mr-1 h-3 w-3" />
          {user ? `${user.email}` : "Guest"}
        </Badge>
        {isAuthenticated ? (
          <Button variant="ghost" size="sm" onClick={() => { void handleLogout(); }} aria-label="Logout">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Logout</span>
          </Button>
        ) : (
          <Button variant="secondary" size="sm" onClick={() => { window.location.href = "/login"; }} aria-label="Login">
            <LogIn className="h-4 w-4" />
            <span className="hidden sm:inline">Login</span>
          </Button>
        )}
      </div>
    </header>
  );
}

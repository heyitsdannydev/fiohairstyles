"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";

/**
 * Static-export stand-in for Next.js middleware (unavailable with `output:
 * "export"`). Redirects client-side once the session check settles:
 * signed-out users get bounced to /login, and a signed-in user who lands on
 * /login gets bounced to /.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated && pathname !== "/login") {
      router.replace("/login");
    } else if (isAuthenticated && pathname === "/login") {
      router.replace("/");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  return <>{children}</>;
}

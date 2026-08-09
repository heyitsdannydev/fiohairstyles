"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { AuthProvider } from "@/lib/AuthContext";
import { AuthGate } from "./AuthGate";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

function AppShellContent({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const isAuthPage = pathname === "/login";

  return (
    <AuthGate>
      {isAuthPage ? (
        children
      ) : (
        <div className="flex min-h-screen">
          <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />

          <div className="flex min-w-0 flex-1 flex-col">
            <Navbar onMenuClick={() => setSidebarOpen(true)} />
            <main className="flex-1 overflow-x-hidden px-4 py-6 sm:px-6">{children}</main>
          </div>
        </div>
      )}
    </AuthGate>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AppShellContent>{children}</AppShellContent>
    </AuthProvider>
  );
}

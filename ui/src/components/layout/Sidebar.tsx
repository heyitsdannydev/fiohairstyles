"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Scissors,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const NAV_ITEMS = [
  { label: "Home", icon: LayoutDashboard, href: "/" },
  { label: "Appointments", icon: Scissors, href: "/appointments" },
  { label: "Calendar", icon: CalendarDays, href: "/calendar" },
  { label: "Clients", icon: Users, href: "/clients" },
  { label: "Services", icon: Sparkles, href: "/services" },
];

const COLLAPSED_STORAGE_KEY = "fio.sidebarCollapsed";

function isActivePath(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setCollapsed] = useState(false);
  const { logout } = useAuth();

  async function handleLogout() {
    await logout();
  }

  useEffect(() => {
    // Hydrate from localStorage after mount — unavailable at build/SSR time.
    const saved = localStorage.getItem(COLLAPSED_STORAGE_KEY);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (saved !== null) setCollapsed(saved === "true");
  }, []);

  useEffect(() => {
    localStorage.setItem(COLLAPSED_STORAGE_KEY, String(isCollapsed));
  }, [isCollapsed]);

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-64 shrink-0 transform flex-col bg-sidebar px-4 py-6 transition-transform duration-200 ease-in-out md:sticky md:top-0 md:h-screen md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"
          } ${isCollapsed ? "md:w-20 md:px-2" : "md:w-64"}`}
      >
        <button
          type="button"
          onClick={onClose}
          className="self-end rounded-md p-1 text-sidebar-muted hover:text-sidebar-foreground md:hidden"
          aria-label="Close menu"
        >
          <X size={20} />
        </button>

        <Link
          href="/"
          onClick={onClose}
          className={`mb-6 flex items-center justify-center gap-2 border-b border-sidebar-border pb-6 ${isCollapsed ? "md:justify-center" : ""}`}
        >
          <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-accent text-accent-foreground">
            <Scissors size={28} />
          </span>
        </Link>

        <nav className="mt-6 flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto">
          {NAV_ITEMS.map(({ label, icon: Icon, href }) => {
            const isActive = isActivePath(pathname, href);
            return (
              <Link
                key={label}
                href={href}
                onClick={onClose}
                title={isCollapsed ? label : undefined}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors ${isCollapsed ? "md:justify-center" : ""
                  } ${isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-sidebar-muted hover:bg-sidebar-border hover:text-sidebar-foreground"
                  }`}
              >
                <Icon size={18} className="shrink-0" />
                <span className={isCollapsed ? "md:hidden" : ""}>{label}</span>
              </Link>
            );
          })}
        </nav>

        <button
          type="button"
          onClick={handleLogout}
          title={isCollapsed ? "Log out" : undefined}
          className={`mt-4 flex items-center gap-2 rounded-lg py-2 text-sidebar-muted hover:bg-sidebar-border hover:text-sidebar-foreground ${isCollapsed ? "justify-center" : "px-3"
            }`}
        >
          <LogOut size={18} />
          <span className={isCollapsed ? "md:hidden" : ""}>Log out</span>
        </button>

        <button
          type="button"
          onClick={() => setCollapsed((prev) => !prev)}
          className={`mt-1 hidden items-center gap-2 rounded-lg py-2 text-sidebar-muted hover:bg-sidebar-border hover:text-sidebar-foreground md:flex ${isCollapsed ? "justify-center" : "px-3"
            }`}
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          <span className={isCollapsed ? "hidden" : ""}>Collapse</span>
        </button>
      </aside>
    </>
  );
}

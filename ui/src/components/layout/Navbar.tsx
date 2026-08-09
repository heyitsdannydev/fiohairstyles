"use client";

import { Menu, Scissors } from "lucide-react";

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <header className="flex shrink-0 items-center justify-between border-b border-border bg-card px-4 py-5 sm:px-6">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-md p-2 text-text-muted hover:bg-page-bg md:hidden"
        aria-label="Open menu"
      >
        <Menu size={22} />
      </button>
      <div className="flex-1" />
      <div className="flex items-center gap-2 text-text-muted md:hidden">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-accent text-accent-foreground">
          <Scissors size={13} />
        </span>
        <span className="text-sm font-medium text-text">Fio Hairstyles</span>
      </div>
    </header>
  );
}

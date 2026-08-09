import { Loader2 } from "lucide-react";

/** Full-page spinner shown while a page's data isn't fully loaded yet. */
export function PageLoader() {
  return (
    <div className="flex flex-1 items-center justify-center py-24">
      <Loader2 size={28} className="animate-spin text-text-muted" />
    </div>
  );
}

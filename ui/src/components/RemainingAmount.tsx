import { CheckCircle2 } from "lucide-react";
import { formatMoney } from "@/lib/format";

interface RemainingAmountProps {
  remaining: number;
}

export function RemainingAmount({ remaining }: RemainingAmountProps) {
  if (remaining <= 0) {
    return (
      <span className="flex items-center gap-1.5 text-base font-bold text-green-600">
        <CheckCircle2 size={18} />
        Paid in full
      </span>
    );
  }

  return <span className="text-sm font-semibold text-text">{formatMoney(remaining)}</span>;
}

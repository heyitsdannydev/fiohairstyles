"use client";

import { Pencil, Trash2 } from "lucide-react";
import type { Service } from "@/lib/types";

interface ServiceTableProps {
  services: Service[];
  onEdit: (service: Service) => void;
  onDelete: (service: Service) => void;
}

export function ServiceTable({ services, onEdit, onDelete }: ServiceTableProps) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-card">
      <table className="w-full min-w-[420px] text-left text-sm">
        <thead>
          <tr className="border-b border-border text-text-muted">
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          {services.map((service) => (
            <tr key={service.sk} className="border-b border-border last:border-0">
              <td className="px-4 py-3 font-medium">{service.Name}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(service)}
                    aria-label="Edit service"
                    className="flex items-center justify-center rounded-lg border border-border p-1.5 text-text transition-colors hover:bg-page-bg"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(service)}
                    aria-label="Delete service"
                    className="flex items-center justify-center rounded-lg border border-border p-1.5 text-red-600 transition-colors hover:bg-red-50"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

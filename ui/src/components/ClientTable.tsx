"use client";

import { Pencil, Trash2 } from "lucide-react";
import type { Client } from "@/lib/types";

interface ClientTableProps {
  clients: Client[];
  onEdit: (client: Client) => void;
  onDelete: (client: Client) => void;
}

export function ClientTable({ clients, onEdit, onDelete }: ClientTableProps) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-card">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead>
          <tr className="border-b border-border text-text-muted">
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium">Phone</th>
            <th className="px-4 py-3 font-medium">Instagram</th>
            <th className="px-4 py-3 font-medium">Source</th>
            <th className="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr key={client.sk} className="border-b border-border last:border-0">
              <td className="px-4 py-3 font-medium">{client.Name}</td>
              <td className="px-4 py-3">{client.Phone || "—"}</td>
              <td className="px-4 py-3">{client.Instagram || "—"}</td>
              <td className="px-4 py-3">{client.Source}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(client)}
                    aria-label="Edit client"
                    className="flex items-center justify-center rounded-lg border border-border p-1.5 text-text transition-colors hover:bg-page-bg"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(client)}
                    aria-label="Delete client"
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

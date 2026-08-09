"use client";

import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from "@headlessui/react";
import { Check, ChevronDown } from "lucide-react";

interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
}

export function Select({ label, value, onChange, options }: SelectProps) {
  const selectedLabel = options.find((option) => option.value === value)?.label ?? value;

  return (
    <div className="flex flex-col gap-1 text-sm text-text-muted">
      <span>{label}</span>
      <Listbox value={value} onChange={onChange}>
        <div className="relative">
          <ListboxButton className="w-full rounded-lg border border-border bg-card px-3 py-2 pr-9 text-left text-text outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20 data-[open]:border-accent data-[open]:ring-2 data-[open]:ring-accent/20">
            {selectedLabel}
            <ChevronDown
              size={16}
              className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-text-muted"
            />
          </ListboxButton>

          <ListboxOptions
            anchor={{ to: "bottom start", gap: 4 }}
            transition
            className="z-50 w-[var(--button-width)] rounded-lg border border-border bg-card p-1 shadow-lg outline-none transition duration-100 ease-out data-[closed]:scale-95 data-[closed]:opacity-0"
          >
            {options.map((option) => (
              <ListboxOption
                key={option.value}
                value={option.value}
                className="flex cursor-pointer items-center justify-between rounded-md px-3 py-2 text-text select-none data-[focus]:bg-page-bg"
              >
                {({ selected }) => (
                  <>
                    {option.label}
                    <Check size={16} className={selected ? "text-accent" : "invisible"} />
                  </>
                )}
              </ListboxOption>
            ))}
          </ListboxOptions>
        </div>
      </Listbox>
    </div>
  );
}

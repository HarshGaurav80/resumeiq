// Native <select> styled like shadcn/ui inputs (accessible and mobile-friendly).
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function NativeSelect({ className, children, ...props }) {
  return (
    <div className="relative">
      <select
        className={cn(
          "h-10 w-full appearance-none rounded-lg border border-input bg-background pl-3 pr-9 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          className,
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
    </div>
  );
}

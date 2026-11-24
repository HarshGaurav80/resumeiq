// shadcn/ui Table primitives.
import { cn } from "@/lib/utils";

export function Table({ className, ...props }) {
  return (
    <div className="relative w-full overflow-x-auto">
      <table className={cn("w-full caption-bottom text-sm", className)} {...props} />
    </div>
  );
}
export const TableHeader = ({ className, ...p }) => <thead className={cn("[&_tr]:border-b", className)} {...p} />;
export const TableBody = ({ className, ...p }) => <tbody className={cn("[&_tr:last-child]:border-0", className)} {...p} />;
export const TableRow = ({ className, ...p }) => <tr className={cn("border-b transition-colors hover:bg-muted/50", className)} {...p} />;
export const TableHead = ({ className, ...p }) => (
  <th className={cn("h-11 px-4 text-left align-middle text-xs font-semibold uppercase tracking-wide text-muted-foreground", className)} {...p} />
);
export const TableCell = ({ className, ...p }) => <td className={cn("px-4 py-3 align-middle", className)} {...p} />;

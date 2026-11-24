// shadcn/ui Badge with success / danger variants used for skill tags.
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors", {
  variants: {
    variant: {
      default: "border-transparent bg-accent text-accent-foreground",
      outline: "text-foreground",
      success: "border-green-200 bg-green-50 text-green-700 dark:border-green-900 dark:bg-green-950/50 dark:text-green-300",
      danger: "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/50 dark:text-red-300",
    },
  },
  defaultVariants: { variant: "default" },
});

export function Badge({ className, variant, ...props }) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

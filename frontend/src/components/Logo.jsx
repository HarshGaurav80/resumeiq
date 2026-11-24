// Brand mark + wordmark.
import { FileCheck2 } from "lucide-react";

export default function Logo() {
  return (
    <span className="flex items-center gap-2 font-bold tracking-tight">
      <span className="bg-brand grid size-8 place-items-center rounded-lg text-white shadow-md shadow-indigo-500/30">
        <FileCheck2 className="size-4.5" />
      </span>
      <span className="text-lg">
        Resume<span className="text-gradient">IQ</span>
      </span>
    </span>
  );
}

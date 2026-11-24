import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** shadcn/ui helper: merge conditional class names and resolve Tailwind conflicts. */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/** Colour band for a 0–100 score: red < 50, yellow 50–75, green > 75. */
export function scoreBand(score) {
  if (score > 75) return { label: "Strong match", color: "#16a34a", text: "text-green-600 dark:text-green-400", bg: "bg-green-500" };
  if (score >= 50) return { label: "Moderate match", color: "#eab308", text: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-500" };
  return { label: "Needs work", color: "#dc2626", text: "text-red-600 dark:text-red-400", bg: "bg-red-500" };
}

/** Human-readable label for the analysis engine stored with each result. */
export function methodLabel(method) {
  return { gemini: "Google Gemini", openai: "OpenAI" }[method] || "Offline (Keyword + TF-IDF)";
}

export function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return iso;
  }
}

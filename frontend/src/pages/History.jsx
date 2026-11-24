// History page: table of past analyses stored in SQLite.
import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Eye, FileText, History as HistoryIcon, Search, Trash2 } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { cn, formatDate, scoreBand } from "@/lib/utils";

function ScorePill({ score }) {
  const band = scoreBand(score);
  return (
    <span className="inline-flex items-center gap-2 font-semibold tabular-nums">
      <span className={cn("size-2 rounded-full", band.bg)} />
      <span className={band.text}>{score}</span>
    </span>
  );
}

export default function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.history().then((d) => setItems(d.items)).catch((e) => {
      toast.error(e.message);
      setItems([]);
    });
  }, []);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    if (!items || !q) return items;
    return items.filter((i) => i.file_name.toLowerCase().includes(q) || i.job_role.toLowerCase().includes(q));
  }, [items, query]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this analysis from your history?")) return;
    try {
      await api.deleteAnalysis(id);
      setItems((list) => list.filter((i) => i.id !== id));
      toast.success("Analysis deleted");
    } catch (e) {
      toast.error(e.message);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analysis history</h1>
          <p className="mt-1 text-muted-foreground">All your previous resume analyses.</p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search file or role…"
            aria-label="Search history"
            className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {filtered === null ? (
            <div className="space-y-3 p-6">
              {[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-10" />)}
            </div>
          ) : items.length === 0 ? (
            <div className="flex flex-col items-center px-6 py-16 text-center">
              <div className="grid size-14 place-items-center rounded-full bg-accent">
                <HistoryIcon className="size-6 text-violet-500" />
              </div>
              <h2 className="mt-4 font-semibold">No analyses yet</h2>
              <p className="mt-1 text-sm text-muted-foreground">Analyze your first resume to see it here.</p>
              <Link to="/analyze" className={buttonVariants({ variant: "gradient", className: "mt-6" })}>Analyze My Resume</Link>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Date</TableHead>
                  <TableHead>File name</TableHead>
                  <TableHead className="hidden md:table-cell">Job role</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead className="hidden sm:table-cell">ATS</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((item, i) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(i * 0.03, 0.3) }}
                    className="border-b transition-colors hover:bg-muted/50"
                  >
                    <TableCell className="whitespace-nowrap text-muted-foreground">{formatDate(item.created_at)}</TableCell>
                    <TableCell>
                      <span className="flex max-w-[220px] items-center gap-2 font-medium">
                        <FileText className="size-4 shrink-0 text-violet-500" />
                        <span className="truncate">{item.file_name}</span>
                      </span>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">{item.job_role || <span className="text-muted-foreground">—</span>}</TableCell>
                    <TableCell><ScorePill score={item.match_score} /></TableCell>
                    <TableCell className="hidden sm:table-cell"><ScorePill score={item.ats_score} /></TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button size="sm" variant="outline" onClick={() => navigate(`/results/${item.id}`)}>
                          <Eye /> View
                        </Button>
                        <Button size="icon" variant="ghost" onClick={() => handleDelete(item.id)} aria-label={`Delete ${item.file_name}`}>
                          <Trash2 className="text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </motion.tr>
                ))}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="py-10 text-center text-muted-foreground">No results match “{query}”.</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

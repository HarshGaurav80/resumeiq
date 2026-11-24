// Results dashboard for a single analysis.
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useLocation, useParams } from "react-router-dom";
import { toast } from "sonner";
import {
  ArrowRight, Award, Briefcase, CircleCheck, CircleX, Cpu, Download, FolderGit2, GraduationCap,
  Lightbulb, Mail, Phone, RotateCcw, Star, User,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import ScoreRing from "@/components/ScoreRing.jsx";
import SectionChart from "@/components/SectionChart.jsx";
import { api } from "@/lib/api";
import { cn, formatDate, methodLabel } from "@/lib/utils";

// Fade-up animation shared by the dashboard cards
const fade = (i = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: 0.06 * i, duration: 0.4 },
});

// Detect "Rewrite "old" → "new"" suggestions so we can show a before/after view
const REWRITE_RE = /^rewrite[^"“]*["“](.+?)["”]\s*(?:→|->)\s*["“](.+?)["”]\.?$/i;

function Suggestion({ text, index }) {
  const m = text.match(REWRITE_RE);
  return (
    <li className="flex gap-3">
      <span className="bg-brand mt-0.5 grid size-6 shrink-0 place-items-center rounded-full text-xs font-bold text-white">{index + 1}</span>
      {m ? (
        <div className="min-w-0 flex-1 space-y-1.5">
          <p className="text-sm font-medium">Rewrite this bullet point</p>
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800 line-through decoration-red-300 dark:bg-red-950/40 dark:text-red-300 dark:decoration-red-800">{m[1]}</p>
          <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-800 dark:bg-green-950/40 dark:text-green-300">{m[2]}</p>
        </div>
      ) : (
        <p className="text-sm leading-relaxed">{text}</p>
      )}
    </li>
  );
}

function DetailList({ icon: Icon, title, items }) {
  return (
    <div>
      <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold">
        <Icon className="size-4 text-violet-500" /> {title}
      </h4>
      {items?.length ? (
        <ul className="space-y-1.5 text-sm text-muted-foreground">
          {items.map((x, i) => (
            <li key={i} className="border-l-2 border-violet-200 pl-3 dark:border-violet-900">{x}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm italic text-muted-foreground">Not found in resume</p>
      )}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-10 sm:px-6">
      <Skeleton className="h-10 w-72" />
      <div className="grid gap-6 md:grid-cols-3">
        {[0, 1, 2].map((i) => <Skeleton key={i} className="h-64" />)}
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-80" />
        <Skeleton className="h-80" />
      </div>
    </div>
  );
}

export default function Results() {
  const { id } = useParams();
  const location = useLocation();
  // Use the record passed from the Analyze page if available, otherwise fetch it
  const initial = location.state?.record?.id === Number(id) ? location.state.record : null;
  const [record, setRecord] = useState(initial);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (record) return;
    api.getAnalysis(id).then(setRecord).catch((e) => {
      setError(e.message);
      toast.error(e.message);
    });
  }, [id, record]);

  if (error) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <h1 className="text-xl font-semibold">Couldn't load this analysis</h1>
        <p className="mt-2 text-muted-foreground">{error}</p>
        <Link to="/history" className={buttonVariants({ variant: "outline", className: "mt-6" })}>Back to history</Link>
      </div>
    );
  }
  if (!record) return <LoadingState />;

  const r = record.result;
  const c = r.candidate || {};

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      {/* ---------------- Header ---------------- */}
      <motion.div {...fade(0)} className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Analysis report</p>
          <h1 className="mt-1 break-all text-2xl font-bold tracking-tight sm:text-3xl">{record.file_name}</h1>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            {record.job_role && <Badge>{record.job_role}</Badge>}
            <Badge variant="outline" className="gap-1.5"><Cpu className="size-3" /> {methodLabel(record.method)}</Badge>
            <span>{formatDate(record.created_at)}</span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/analyze" className={buttonVariants({ variant: "outline" })}>
            <RotateCcw /> Analyze another
          </Link>
          <a
            href={api.reportUrl(record.id)}
            download
            onClick={() => toast.success("Downloading PDF report…")}
            className={buttonVariants({ variant: "gradient" })}
          >
            <Download /> Download PDF
          </a>
        </div>
      </motion.div>

      {/* ---------------- Scores + summary ---------------- */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <motion.div {...fade(1)}>
          <Card className="h-full">
            <CardContent className="flex h-full items-center justify-center p-6">
              <ScoreRing score={r.match_score} label="Overall Match Score" />
            </CardContent>
          </Card>
        </motion.div>
        <motion.div {...fade(2)}>
          <Card className="h-full">
            <CardContent className="flex h-full items-center justify-center p-6">
              <ScoreRing score={r.ats_score} label="ATS Compatibility" />
            </CardContent>
          </Card>
        </motion.div>
        <motion.div {...fade(3)} className="md:col-span-2 lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle><Star className="size-4 text-violet-500" /> Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm leading-relaxed text-muted-foreground">{r.summary || "No summary available."}</p>
              {r.strengths?.length > 0 && (
                <div>
                  <h4 className="mb-2 text-sm font-semibold">Strengths</h4>
                  <ul className="space-y-1.5">
                    {r.strengths.map((s, i) => (
                      <li key={i} className="flex gap-2 text-sm">
                        <CircleCheck className="mt-0.5 size-4 shrink-0 text-green-600 dark:text-green-400" /> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* ---------------- Chart + skills ---------------- */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <motion.div {...fade(4)}>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Section-wise scores</CardTitle>
              <CardDescription>How each part of your resume performs (0–100).</CardDescription>
            </CardHeader>
            <CardContent>
              <SectionChart scores={r.section_scores} />
            </CardContent>
          </Card>
        </motion.div>
        <motion.div {...fade(5)}>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Skills analysis</CardTitle>
              <CardDescription>Compared against the job description.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-green-700 dark:text-green-400">
                  <CircleCheck className="size-4" /> Skills found ({r.skills_found.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {r.skills_found.length ? r.skills_found.map((s) => <Badge key={s} variant="success">{s}</Badge>)
                    : <p className="text-sm italic text-muted-foreground">No matching skills detected.</p>}
                </div>
              </div>
              <div>
                <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-700 dark:text-red-400">
                  <CircleX className="size-4" /> Missing skills ({r.missing_skills.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {r.missing_skills.length ? r.missing_skills.map((s) => <Badge key={s} variant="danger">{s}</Badge>)
                    : <p className="text-sm italic text-muted-foreground">Great — no key skills missing!</p>}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* ---------------- Candidate details ---------------- */}
      <motion.div {...fade(6)} className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle><User className="size-4 text-violet-500" /> Extracted candidate details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { icon: User, label: "Name", value: c.name },
                { icon: Mail, label: "Email", value: c.email },
                { icon: Phone, label: "Phone", value: c.phone },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="flex items-center gap-3 rounded-lg bg-muted/60 p-3">
                  <Icon className="size-4 shrink-0 text-muted-foreground" />
                  <div className="min-w-0">
                    <p className="text-xs text-muted-foreground">{label}</p>
                    <p className={cn("truncate text-sm font-medium", !value && "italic text-muted-foreground")}>{value || "Not found"}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <DetailList icon={GraduationCap} title="Education" items={c.education} />
              <DetailList icon={Briefcase} title="Experience" items={c.experience} />
              <DetailList icon={FolderGit2} title="Projects" items={c.projects} />
              <DetailList icon={Award} title="Certifications" items={c.certifications} />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* ---------------- Suggestions ---------------- */}
      <motion.div {...fade(7)} className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle><Lightbulb className="size-4 text-amber-500" /> AI suggestions</CardTitle>
            <CardDescription>Specific improvements to raise your score.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4">
              {r.suggestions.map((s, i) => <Suggestion key={i} text={s} index={i} />)}
            </ol>
          </CardContent>
        </Card>
      </motion.div>

      <div className="mt-8 flex justify-center">
        <Link to="/history" className={buttonVariants({ variant: "link" })}>
          View all past analyses <ArrowRight />
        </Link>
      </div>
    </div>
  );
}
